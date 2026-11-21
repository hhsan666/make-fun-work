# tiny-chess-01 engine (MIT); design notes in dev/NOTES.md
import json,os,re,sys,urllib.request as U
N,E,S,W=-10,1,10,-1
R4=(N,E,S,W);B4=(N+E,S+E,S+W,N+W);K8=R4+B4
NJ=(N+N+E,E+N+E,E+S+E,S+S+E,S+S+W,W+S+W,W+N+W,N+N+W)
D={'N':NJ,'B':B4,'R':R4,'Q':K8,'K':K8}
OWN=' \nPNBRQK'
V={'P':100,'N':300,'B':320,'R':500,'Q':950,'K':0}
LIM=350000
MATE=99999
TW={'N':3,'B':1,'R':2,'Q':4}
T=[{},{}];PC={}
PK=str.maketrans('NBRQnbrq','........')

def tables(ph,K=(0,0)):
 global PH;PH=ph;PC.clear()
 for x in(0,1):
  for p in V:
   t=[0]*120;e=K[x]
   for r in range(8):
    for c in range(8):
     k=r+1;fx=abs(c-3.5);fy=abs(r-3.5);m=fx+fy;rk=7-r
     if p=='P':
      wg=c<3 or c>4
      v=(0,0,3,8,16,30,55,0)[rk]*(2-ph)*(1-.8*ph*wg)+(c in(3,4))*(1<rk<5)*14*ph-(c in(3,4))*(rk<2)*10*ph+wg*(rk==1)*10*ph-wg*(rk>2)*8*ph
     elif p=='N':v=18-7*m-(rk==0)*8
     elif p=='B':v=10-3*m-(rk==0)*6
     elif p=='R':v=(rk==6)*18+(c in(3,4))*(rk==0)*6
     elif p=='Q':v=4-2*m
     else:v=ph*((rk==0)*(20,30,10,0,0,10,30,20)[c]-rk*16)+(1-ph)*(28-9*m)
     if e and p in TW:v+=ph*TW[p]*(7-max(abs(r+2-e//10),abs(c+1-e%10)))
     t[k*10+10+c+1]=V[p]+round(v)
   T[x][p]=t

def rot(b):return b[::-1].swapcase()

def side(b):
 v=0;k=b.find('K');C=['']+[b[c+20:100:10]for c in range(1,9)]+['']
 for f in range(1,9):
  F=C[f];t=F.find('P')
  while t>=0:
   if'p'not in C[f-1][:t]+F[:t]+C[f+1][:t]:v+=(0,0,8,14,24,40,64)[7-t]*(2-PH)
   if'P'in F[:t]:v-=12
   if'P'not in C[f-1]+C[f+1]:v-=10
   t=F.find('P',t+1)
 if k>80:
  for f in(-1,0,1):
   if b[k+f-10]!='P'and b[k+f-20]!='P':v-=18*PH
 return round(v)

def ev(pos):
 b=pos[0].translate(PK);v=PC.get(b)
 if v is None:v=PC[b]=side(b)-side(rot(b))
 b=pos[0];return pos[1]+v+30*((b.count('B')>1)-(b.count('b')>1))

def att(b,s):
 if b[s-11]=='p' or b[s-9]=='p':return 1
 for d in NJ:
  if b[s+d]=='n':return 1
 for d in K8:
  k=s+d;q=b[k]
  if q=='k':return 1
  while q=='.':k+=d;q=b[k]
  if q=='q' or q==('r' if d in R4 else 'b'):return 1
 return 0

def gen(pos,c=0):
 b,_,wc,bc,ep,_=pos
 for x in re.finditer('[PNBRQK]',b):
  i=x.start();p=b[i]
  if p=='P':
   L=[]
   if b[i+N]=='.'and(not c or i<39):
    L.append(i+N)
    if 80<i<89 and b[i+N+N]=='.'and not c:L.append(i+N+N)
   for j in(i+N+W,i+N+E):
    if b[j].islower() or j==ep:L.append(j)
   for j in L:
    if j<29:
     for pr in'QNRB'[:4-3*(c and b[j]=='.')]:yield(i,j,pr)
    else:yield(i,j,'')
   continue
  for d in D[p]:
   j=i+d
   while 1:
    q=b[j]
    if q in OWN:break
    if q!='.':yield(i,j,'');break
    if not c:yield(i,j,'')
    if p in'NK':break
    j+=d
  if p=='K'and not c:
   for r,ok in((91,wc[0]),(98,wc[1])):
    if ok and b[r]=='R':
     d=1 if r>i else-1
     if all(b[x]=='.'for x in range(i+d,r,d))and not att(b,i)and not att(b,i+d):yield(i,i+d+d,'')

def put(b,i,p):return b[:i]+p+b[i+1:]

def mk(pos,m,k=0):
 b,sc,wc,bc,ep,sd=pos;i,j,pr=m;p=b[i];q=b[j];o=T[1-sd]
 nb=b[:i]+'.'+b[i+1:j]+(pr or p)+b[j+1:]if i<j else b[:j]+(pr or p)+b[j+1:i]+'.'+b[i+1:]
 t=T[sd][p];v=t[j]-t[i];ne=0
 if p=='K':
  wc=(0,0)
  if abs(j-i)==2:
   r=91 if j<i else 98;nb=put(put(nb,r,'.'),(i+j)//2,'R');t=T[sd]['R'];v+=t[(i+j)//2]-t[r]
 elif p=='P':
  if pr:v+=T[sd][pr][j]-t[j]
  if j-i==N+N:ne=119-i-N
  if j==ep:nb=put(nb,j+S,'.');v+=o['P'][119-j-S]
 x=i-k
 if(not k or p=='K'or j==ep or i//10==k//10 or x%10==0 or x%9==0 or x%11==0)and att(nb,nb.find('K')):return None
 if q!='.':v+=o[q.upper()][119-j]
 if i==91:wc=(0,wc[1])
 if i==98:wc=(wc[0],0)
 if j==21:bc=(bc[0],0)
 if j==28:bc=(0,bc[1])
 return(rot(nb),-sc-v,bc,wc,ne,1-sd)

def legal(pos):return[m for m in gen(pos)if mk(pos,m)]

class Stop(Exception):pass

class Search:
 def __init__(s,hist):
  s.tt={};s.kill={};s.h={};s.n=0;s.rep=dict(hist)
 def qs(s,pos,a,bt,ply):
  if s.n>LIM:raise Stop
  b=pos[0];kk=b.find('K');chk=att(b,kk);kk*=not chk
  if chk:best=-MATE+ply;ms=list(gen(pos))
  else:
   best=ev(pos)
   if best>=bt or ply>60:return best
   if best>a:a=best
   ms=list(gen(pos,1))
  s.n+=22;ms.sort(key=lambda m:-V[b[m[1]].upper()]*10+V[b[m[0]]]-(m[2]=='Q')*900 if b[m[1]]!='.'else-(m[2]=='Q')*900)
  for m in ms:
   if not chk and b[m[1]]!='.'and not m[2]:
    j=m[1];x=V[b[j].upper()]
    if best+x+200<a or V[b[m[0]]]>x+50 and(b[j-11]=='p'or b[j-9]=='p'):continue
   np=mk(pos,m,kk);s.n+=2
   if not np:continue
   v=-s.qs(np,-bt,-a,ply+1)
   if v>best:
    best=v
    if v>a:
     a=v
     if v>=bt:break
  return best
 def go(s,pos,d,a,bt,ply,nul=1):
  s.n+=8
  if s.n>LIM:raise Stop
  b=pos[0]
  if ply and s.rep.get(b):return 0
  kk=b.find('K');chk=att(b,kk);kk*=not chk
  if chk:d+=1
  if d<=0:return s.qs(pos,a,bt,ply)
  a0=a;e=s.tt.get(pos);tm=None
  if e:
   ed,es,ef,tm=e
   if es>MATE-500:es-=ply
   if es<500-MATE:es+=ply
   if ed>=d and ply and(ef==0 or ef==1 and es>=bt or ef==2 and es<=a):return es
  se=0 if chk else ev(pos)
  if not chk and bt-a==1 and d<4 and se-110*d>=bt:return se
  if nul and not chk and d>2 and se>=bt and abs(bt)<MATE-500 and any(c in b for c in'NBRQ'):
   v=-s.go((rot(b),-pos[1],pos[3],pos[2],0,1-pos[5]),d-3,-bt,1-bt,ply+1,0)
   if v>=bt:return v
  k=s.kill.get(ply)
  def key(m):
   i,j,pr=m;q=b[j]
   if q!='.':return-1e5-V[q.upper()]*10+V[b[i]]
   if pr:return-9e4-V[pr]
   if m==k:return-8e4
   t=T[pos[5]][b[i]];return t[i]-t[j]-s.h.get((b[i],j),0)
  def mv():
   if tm:yield tm
   L=sorted(gen(pos),key=key);s.n+=len(L)//2
   for m in L:
    if m!=tm:yield m
  ms=mv()
  best=-MATE;bm=None;n=0
  s.rep[b]=1
  try:
   for m in ms:
    q=b[m[1]]=='.'and not m[2]
    np=mk(pos,m,kk);s.n+=2
    if not np:continue
    if n and q and not chk and(d<3 and se+120*d<=a or d<4 and n>2+d*d and bt-a==1)and not att(np[0],np[0].find('K')):continue
    n+=1
    if n==1:v=-s.go(np,d-1,-bt,-a,ply+1)
    else:
     r=1 if d>1 and n>2 and q and not chk else 0
     if r and n>6 and d>3:r=2+(n>15 and d>5)
     v=-s.go(np,d-1-r,-a-1,-a,ply+1)
     if v>a and(r or v<bt):v=-s.go(np,d-1,-bt,-a,ply+1)
    if v>best:
     best=v;bm=m
     if ply==0:s.best=m
     if v>a:
      a=v
      if v>=bt:
       if q:s.kill[ply]=m;y=(b[m[0]],m[1]);s.h[y]=s.h.get(y,0)+d*d
       break
  finally:
   del s.rep[b]
  if not n:return-MATE+ply if chk else 0
  es=best
  if es>MATE-500:es+=ply
  if es<500-MATE:es-=ply
  s.tt[pos]=(d,es,1 if best>=bt else 2 if best<=a0 else 0,bm)
  return best

def sq(i,w):
 if not w:i=119-i
 return'abcdefgh'[i%10-1]+str(10-i//10)

def parse(f):
 pl,side,cs,ep=f.split()[:4]
 b='         \n'*2
 for r in pl.split('/'):
  b+=' '+''.join('.'*int(c)if c.isdigit()else c for c in r)+'\n'
 b+='         \n'*2
 w=side=='w'
 e=0
 if ep!='-':e=10*(10-int(ep[1]))+'abcdefgh'.index(ep[0])+1
 pos=(b,0,('Q'in cs,'K'in cs),('k'in cs,'q'in cs),e,0)
 if not w:pos=(rot(b),0,pos[3],pos[2],119-e if e else 0,0)
 return pos,w

def score(b):
 return sum(T[0][p][i]for i,p in enumerate(b)if p.isupper())-sum(T[1][p.upper()][119-i]for i,p in enumerate(b)if p.islower())

def think(fen,start,moves,legal_uci):
 ph=sum(V[c.upper()]for c in fen.split()[0]if c in'nbrqNBRQ')
 b=parse(fen)[0][0];tables(min(ph,6400)/6400,(b.find('k'),119-b.find('K')))
 p,w=parse(start);hist={}
 for u in moves:
  hist[p[0]]=1
  for m in gen(p):
   if sq(m[0],w)+sq(m[1],w)+m[2].lower()==u:p=mk(p,m);break
  w=not w
 pos,w=parse(fen);pos=(pos[0],score(pos[0]))+pos[2:]
 rm=[m for m in gen(pos)if sq(m[0],w)+sq(m[1],w)+m[2].lower()in legal_uci and mk(pos,m)]
 if not rm:return legal_uci[0]
 if len(rm)==1:return sq(rm[0][0],w)+sq(rm[0][1],w)+rm[0][2].lower()
 s=Search(hist);best=rm[0]
 try:
  for d in range(1,40):
   s.best=None
   s.go(pos,d,-MATE,MATE,0)
   best=s.best or best
 except Stop:
  if s.best:best=s.best
 if best not in rm:best=rm[0]
 return sq(best[0],w)+sq(best[1],w)+best[2].lower()

def post(path,o):
 for _ in range(9):
  try:
   return json.load(U.urlopen(U.Request(os.environ['MAKEFUN_ENV_URL']+path,json.dumps(o).encode(),{'content-type':'application/json'})))
  except U.HTTPError:return None
  except Exception:pass
 sys.exit(1)

if __name__=='__main__':
 g=post('/game',{});bad=0
 while g['status']!='done':
  if g['status']=='your_move':
   m=g['legal_moves'][0]if bad else think(g['fen'],g['start_fen'],g['moves'],g['legal_moves'])
   n=post('/move',{'game':g['game'],'move':m})
   bad=n is None;g=n or post('/game',{})
  else:g=post('/game',{})
