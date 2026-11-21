# Local gauntlet runner: plays an engine against the kit's house engines through
# the kit's own env (program/env/server.mjs, process driver), on many book
# openings, and prints the score, the Elo vs the anchors and the slowest move.
# usage: python3 dev/match.py ENGINE.py [--units N] [--jobs J] [--opp a,b,..] [--offset K]
import argparse,json,os,re,subprocess,sys,tempfile,time,signal,math
from concurrent.futures import ThreadPoolExecutor
KIT=os.environ.get('KIT',os.path.expanduser('~/work/kit/tiny-chess-01-kit'))
SERVER=os.path.join(KIT,'program/env/server.mjs')
ANCH={'depth-2':855,'depth-3':1073,'depth-4':1199,'nodes-100k':1392,'nodes-250k':1497,'nodes-500k':1596,'nodes-1M':1667,'nodes-2M':1712}
src=open(SERVER).read()
BOOK=[(a,b,c.split()) for a,b,c in re.findall(r'line\("([^"]+)", "([^"]+)", "([^"]+)"\)',src)]

def elo(games):
 pts=sum(s for _,s in games)
 f=lambda R:sum(1/(1+10**((ANCH[o]-R)/400)) for o,_ in games)
 lo,hi=0.0,2112.0
 if pts<=f(lo):return 0
 if pts>=f(hi):return 2112
 for _ in range(60):
  m=(lo+hi)/2
  if f(m)<pts:lo=m
  else:hi=m
 return round((lo+hi)/2)

def unit(engine,u,opps,offset,port,save=''):
 games=[]
 k=0
 for o in opps:
  for col in ('white','black'):
   a,b,mv=BOOK[(offset+u*7+k*3)%len(BOOK)];k+=1
   games.append({'game':len(games)+1,'opponent':o,'colour':col,'opening':{'id':a,'name':b,'moves':mv}})
 d=tempfile.mkdtemp(prefix=f'm{u}_')
 os.makedirs(d+'/data');os.makedirs(d+'/state')
 json.dump({'schema':'tiny-chess-01/gauntlet/v1','house_seed':'%064x'%(u+1),'max_plies':200,'adjudication_margin':5,'move_limit_ms':10000,'games':games},open(d+'/data/gauntlet.json','w'))
 env=dict(os.environ,MAKEFUN_STATE_DIR=d+'/state',MAKEFUN_ENV_DATA_DIR=d+'/data',MAKEFUN_ENV_PORT=str(port))
 srv=subprocess.Popen(['node',SERVER],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 while not os.path.exists(d+'/state/ready'):
  if srv.poll() is not None:raise SystemExit('env failed to start (port in use?)')
  time.sleep(0.05)
 t=time.time()
 r=subprocess.run(['python3','-P','-s',engine],env=dict(os.environ,MAKEFUN_ENV_URL=f'http://127.0.0.1:{port}'),capture_output=True,text=True)
 wall=time.time()-t
 srv.send_signal(signal.SIGTERM);srv.wait()
 st=json.load(open(d+'/state/export/state.json'))
 if save:os.makedirs(save,exist_ok=True);json.dump(st,open(f'{save}/unit{u}.json','w'))
 think=[json.loads(l)['think_ms'] for l in open(d+'/state/calls.ndjson') if '"/move"' in l]
 think=[x for x in think if x is not None]
 res=[]
 for g in st['games']:
  s={'win':1,'draw':.5,'loss':0}[g['outcome']]
  res.append((g['opponent'],s,g['colour'],g['reason'],len(g['moves']),g['opening']))
 return res,max(think or[0]),sum(think)/max(1,len(think)),wall,r.returncode,r.stderr[-300:]

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('engine');ap.add_argument('--units',type=int,default=4);ap.add_argument('--jobs',type=int,default=4)
 ap.add_argument('--opp',default='depth-2,depth-3,depth-4,nodes-100k,nodes-250k,nodes-500k');ap.add_argument('--offset',type=int,default=0);ap.add_argument('--port',type=int,default=18100);ap.add_argument('--save',default='')
 a=ap.parse_args();opps=a.opp.split(',')
 with ThreadPoolExecutor(a.jobs) as ex:
  outs=list(ex.map(lambda u:unit(os.path.abspath(a.engine),u,opps,a.offset,a.port+u,a.save),range(a.units)))
 allg=[];mx=0
 per={o:[0,0] for o in opps}
 for res,tmax,tavg,wall,rc,err in outs:
  mx=max(mx,tmax);allg+=[(o,s) for o,s,*_ in res]
  for o,s,*_ in res:per[o][0]+=s;per[o][1]+=1
  if rc:print('engine exit',rc,err)
  print(f'unit: {sum(s for _,s,*_ in res)}/{len(res)} wall {wall:.0f}s max think {tmax}ms avg {tavg:.0f}ms; '+' '.join(f"{o[:6]}{c[0]}:{s}:{r[:5]}" for o,s,c,r,*_ in res))
 print('per opponent:',' '.join(f'{o}={v[0]}/{v[1]}' for o,v in per.items()))
 print(f'TOTAL {sum(s for _,s in allg)}/{len(allg)}  Elo {elo(allg)}  max think {mx}ms')
main()
