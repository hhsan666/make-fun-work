# Texel tuning of the evaluation's parameters on positions from dev/texel_data.py.
# usage: python3 dev/texel.py DATA.jsonl [DATA2.jsonl ...] --out params.json
# Model (side-to-move view, mg/eg tapered by phase ph):
#   piece p on square (rk 0..7 from own side, fd = file distance from the edge 0..3):
#     pawns: MAT_P + PP[ph][rk][fd];  others: MAT_p[ph] + RK_p[ph][rk] + FL_p[ph][fd]
#   structure: passed[ph][rk], doubled, isolated, missing shelter pawn (mg), bishop pair
import json,sys,math
import numpy as np
args=[a for a in sys.argv[1:] if not a.startswith('--')]
out=sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else '/tmp/params.json'
args=[a for a in args if a!=out]
PIECES='PNBRQK'
names=[]
def add(n,k):
 i=len(names);names.extend(f'{n}{j}' for j in range(k));return i
IDX={}
for ph in(0,1):
 IDX['PP',ph]=add(f'PP{ph}_',48)
 for p in'NBRQK':
  IDX['RK',p,ph]=add(f'RK{p}{ph}_',8);IDX['FL',p,ph]=add(f'FL{p}{ph}_',4)
 for p in'NBRQ':IDX['MAT',p,ph]=add(f'MAT{p}{ph}_',1)
 IDX['PASS',ph]=add(f'PASS{ph}_',7)
 IDX['DBL',ph]=add(f'DBL{ph}_',1);IDX['ISO',ph]=add(f'ISO{ph}_',1)
 IDX['BP',ph]=add(f'BP{ph}_',1)
IDX['SH']=add('SH',1)
NP=len(names)

def rot(b):return b[::-1].swapcase()
def feats(b,ph,x):
 # accumulate +features for upper case side, - for lower case side
 for sgn,bb in((1,b),(-1,rot(b))):
  w=(1-ph,ph)  # phase 0 = endgame weight, phase 1 = middlegame weight
  const=0
  for i,c in enumerate(bb):
   if not c.isupper():continue
   r=i//10-2;col=i%10-1;rk=7-r;fd=min(col,7-col)
   for ph_,wt in((0,w[0]),(1,w[1])):
    if c=='P':x[IDX['PP',ph_]+rk*4+fd]+=sgn*wt;const+=0
    else:
     x[IDX['RK',c,ph_]+rk]+=sgn*wt;x[IDX['FL',c,ph_]+fd]+=sgn*wt
     if c!='K':x[IDX['MAT',c,ph_]]+=sgn*wt
  if c:pass
  # structure (same rules as engine side())
  C=['']+[bb[c+20:100:10]for c in range(1,9)]+['']
  for f in range(1,9):
   F=C[f];t=F.find('P')
   while t>=0:
    for ph_,wt in((0,w[0]),(1,w[1])):
     if'p'not in C[f-1][:t]+F[:t]+C[f+1][:t]:x[IDX['PASS',ph_]+7-t]+=sgn*wt
     if'P'in F[:t]:x[IDX['DBL',ph_]]+=sgn*wt
     if'P'not in C[f-1]+C[f+1]:x[IDX['ISO',ph_]]+=sgn*wt
    t=F.find('P',t+1)
  k=bb.find('K')
  if k>80:
   for f in(-1,0,1):
    if bb[k+f-10]!='P'and bb[k+f-20]!='P':x[IDX['SH']]+=sgn*ph
  if bb.count('B')>1:
   for ph_,wt in((0,w[0]),(1,w[1])):x[IDX['BP',ph_]]+=sgn*wt
 return x

rows=[];ys=[];pawnconst=[]
for fn in args:
 for l in open(fn):
  b,wtm,res,ph=json.loads(l)
  x=np.zeros(NP,np.float32);feats(b,ph,x)
  rows.append(x);ys.append(res)
  pawnconst.append(100*(b.count('P')-b.count('p')))
X=np.array(rows);y=np.array(ys,np.float32);c0=np.array(pawnconst,np.float32)
print('positions',len(y),'params',NP)

def init():
 th=np.zeros(NP,np.float32)
 for ph in(0,1):
  th[IDX['MAT','N',ph]]=300;th[IDX['MAT','B',ph]]=320;th[IDX['MAT','R',ph]]=500;th[IDX['MAT','Q',ph]]=950
 return th
th=init();th0=th.copy()
rng=np.random.default_rng(1);perm=rng.permutation(len(y));nv=len(y)//10
va,tr=perm[:nv],perm[nv:]
def loss(th,K,idx):
 e=X[idx]@th+c0[idx]
 p=1/(1+np.exp(-K*e))
 return float(np.mean((p-y[idx])**2))
# scale K for the initial (material only) model, then for the tuned one
def fitK(th):
 best=None
 for K in np.linspace(0.001,0.02,40):
  l=loss(th,K,tr)
  if best is None or l<best[0]:best=(l,K)
 return best[1]
K=fitK(th);print('K',K,'loss tr',loss(th,K,tr),'va',loss(th,K,va))
lr=2.0;m=np.zeros(NP);v=np.zeros(NP);lam=1e-7
for it in range(1,3001):
 idx=tr
 e=X[idx]@th+c0[idx];p=1/(1+np.exp(-K*e))
 g=X[idx].T@((p-y[idx])*p*(1-p)*K*2)/len(idx)+lam*(th-th0)
 m=.9*m+.1*g;v=.999*v+.001*g*g
 th-= lr*(m/(1-.9**it))/(np.sqrt(v/(1-.999**it))+1e-12)
 if it%500==0:print(it,'tr',loss(th,K,tr),'va',loss(th,K,va))
K2=fitK(th);print('refit K',K2,'va',loss(th,K2,va))
json.dump({'names':names,'theta':[round(float(t),1) for t in th],'K':float(K)},open(out,'w'))
def show(key,n,shape=None):
 i=IDX[key];a=np.round(th[i:i+n]).astype(int)
 print(key,a.reshape(shape).tolist() if shape else a.tolist())
for ph in(0,1):
 show(('PP',ph),48,(12,4))
 for p in'NBRQK':show(('RK',p,ph),8);show(('FL',p,ph),4)
 for p in'NBRQ':show(('MAT',p,ph),1)
 show(('PASS',ph),7);show(('DBL',ph),1);show(('ISO',ph),1);show(('BP',ph),1)
show('SH',1)
