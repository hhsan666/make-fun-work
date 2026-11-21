# Correctness gate for dev/engine.py (or a built main.py): perft + tactics.
# usage: python3 dev/test_engine.py [path-to-engine-source-or-main.py]
import sys,time,importlib.util,os
path=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'engine.py')
src=open(path,'rb').read()
g={'__name__':'engine_test'}
if src.startswith(b'#coding:l1'):  # packed main.py: unpack its payload the way it runs
 import lzma
 code=src.decode('latin-1').split('\n',1)[1]
 code=code.replace('exec(','_payload=(',1)
 h={};exec(code,h);src=h['_payload']
exec(compile(src,path,'exec'),g)
e=type('E',(),g)

def perft(pos,d):
 if d==0:return 1
 n=0
 for m in e.gen(pos):
  np=e.mk(pos,m)
  if np:n+=1 if d==1 else perft(np,d-1)
 return n

def root(fen):
 e.tables(1.0)
 p,w=e.parse(fen)
 return (p[0],e.score(p[0]))+p[2:],w

def legal_uci(fen):
 p,w=root(fen)
 return [e.sq(m[0],w)+e.sq(m[1],w)+m[2].lower() for m in e.gen(p) if e.mk(p,m)]

START='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
CASES=[
 (START,3,8902),(START,4,197281),
 ('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1',3,97862),
 ('8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1',4,43238),
 # extra coverage: black to move, en passant, promotions, castling for black
 ('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R b KQkq - 0 1',2,None),
 ('n1n5/PPPk4/8/8/8/8/4Kppp/5N1N b - - 0 1',3,9483),
 ('r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1',3,9467),
]
ok=True
for fen,d,want in CASES:
 if want is None:continue
 t=time.time();p,_=root(fen);n=perft(p,d)
 good=n==want;ok&=good
 print(f"perft {'OK ' if good else 'BAD'} d{d} {n} (want {want}) {time.time()-t:.1f}s  {fen}")

def best(fen,moves=(),lim=20000):
 e.LIM=lim
 return e.think(fen,fen,[],legal_uci(fen))

def check(name,cond):
 global ok
 ok&=bool(cond);print(('OK  ' if cond else 'BAD ')+name)

# 1. mate in one (back rank): Ra1-a8#
check('mate in one Ra8#',best('6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1')=='a1a8')
# mate in one for black (rotated board): ...Qh2# style
check('mate in one (black) Ra1#',best('r5k1/8/8/8/8/8/5PPP/6K1 b - - 0 1')=='a8a1')
# 2. take the hanging queen
check('take hanging queen',best('4k3/8/8/3q4/8/8/3R4/4K3 w - - 0 1')=='d2d5')
check('take hanging queen (black)',best('4k3/8/8/3r4/8/8/3Q4/4K3 b - - 0 1')=='d5d2')
# 3. evade check: every root move must be an evasion, engine picks a legal one
fen='4k3/4r3/8/8/8/8/8/R3K3 w Q - 0 1'
ev=legal_uci(fen)
check('check evasions = king steps only',sorted(ev)==['e1d1','e1d2','e1f1','e1f2'] and best(fen) in ev)
fen='4k3/8/8/8/1b6/8/8/R3K3 w Q - 0 1'
ev=legal_uci(fen);b=best(fen)
check('in check: no castling, engine move legal',('e1c1' not in ev) and b in ev and len(ev)>0)
# 4. promotions incl. underpromotion generated; and engine knights-fork underpromotion
ev=legal_uci('8/1P6/8/8/8/8/8/k1K5 w - - 0 1')
check('promotions generated q,r,b,n',all('b7b8'+c in ev for c in 'qrbn'))
ev=legal_uci('8/8/8/8/8/8/1p6/K1k5 b - - 0 1')
check('black promotions generated',all('b2b1'+c in ev for c in 'qrbn'))
# underpromotion is best: e8=N+ forks king and queen... d7d8n is check and wins queen
check('capture-promotion e7xd8=Q',best('3q1k2/4P3/2K5/8/8/8/8/8 w - - 0 1')=='e7d8q')
check('underpromotion e8=N+ forks K and Q',best('8/2q1P1k1/8/8/8/8/8/7K w - - 0 1')=='e7e8n')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
