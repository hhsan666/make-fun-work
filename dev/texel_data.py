# Collect quiet positions with game results from local match runs (dev/match.py
# leaves each run's env export under /tmp/m*_*/state/export/state.json).
# usage: python3 dev/texel_data.py OUT.jsonl [engine.py]
# Each line: [board (side-to-move view, 120 chars), white_to_move, result for the side to move (1/.5/0), phase]
import glob,json,sys,os
path=sys.argv[2] if len(sys.argv)>2 else os.path.join(os.path.dirname(__file__),'engine.py')
g={'__name__':'x'};exec(open(path).read(),g)
g['LIM']=10**9
START='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
seen=set();out=open(sys.argv[1],'w');n=0;games=0
for f in sorted(glob.glob('/tmp/m*_*/state/export/state.json')):
 for gm in json.load(open(f))['games']:
  if gm['reason'] in('unplayed','abandoned','time'):continue
  key=' '.join(gm['moves'])
  if key in seen:continue
  seen.add(key);games+=1
  res={'1-0':1.0,'0-1':0.0,'1/2-1/2':0.5}[gm['result']]
  g['tables'](1.0)
  p,w=g['parse'](START)
  for k,u in enumerate(gm['moves']):
   if k>=10:
    b=p[0];ph=sum(g['V'][c.upper()]for c in b if c in'nbrqNBRQ')
    g['tables'](min(ph,6400)/6400)
    q=(b,g['score'](b))+p[2:]
    s=g['Search']({})
    st=g['ev'](q)
    try:qv=s.qs(q,-g['MATE'],g['MATE'],0)
    except Exception:qv=None
    if qv is not None and abs(qv-st)<20 and not g['att'](b,b.find('K')):
     out.write(json.dumps([b,w,res if w else 1-res,min(ph,6400)/6400])+'\n');n+=1
   for m in g['gen'](p):
    if g['sq'](m[0],w)+g['sq'](m[1],w)+m[2].lower()==u:p=g['mk'](p,m);break
   w=not w
print(games,'games',n,'positions')
