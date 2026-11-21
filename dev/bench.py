# Time a move on representative middlegame positions at a node budget.
# usage: python3 dev/bench.py [LIM] [engine path] [--hard]
import sys,time,os
A=[x for x in sys.argv[1:] if x!='--hard']
lim=int(A[0]) if A else 10000
path=A[1] if len(A)>1 else os.path.join(os.path.dirname(__file__),'engine.py')
g={'__name__':'bench'};exec(compile(open(path).read(),path,'exec'),g)
FENS=[
 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1',
 'r1bq1rk1/pp2bppp/2n1pn2/3p4/2PP4/2N1PN2/PP2BPPP/R2QKB1R w KQ - 0 8',
 'r2q1rk1/1b2bppp/p1n1pn2/1p6/3P4/P1NBPN2/1P3PPP/R1BQ1RK1 w - - 0 12',
 'r1bqk2r/pp1nbppp/2p1pn2/3p4/2PP4/2NBPN2/PP3PPP/R1BQK2R b KQkq - 0 7',
 '2rq1rk1/pp1bppbp/3p1np1/4n3/3NP3/1BN1BP2/PPPQ2PP/2KR3R w - - 0 12',
 'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10',
 '3r1rk1/p4ppp/1qp1b3/4p3/4P3/1PN1QP2/P5PP/2RR2K1 b - - 0 20',
 'r1b2rk1/2q1bppp/p2p1n2/np2p3/3PP3/5N1P/PPBN1PP1/R1BQR1K1 w - - 0 13',
]
# slowest positions seen in grade-local games (heavy material, many checks)
HARD=[
 '8/P7/P5R1/4K3/1Q2Q3/8/8/3k4 w - - 0 1',
 'Q4Q2/P7/P5R1/4K3/8/3k4/8/8 w - - 0 1',
 '2rk3r/1p2bQp1/8/p3P1Bp/1p6/6P1/PPq4P/R4RK1 w - - 0 1',
 '4k3/8/6P1/3Q2B1/8/1p2P3/1P3P2/6K1 w - - 0 1',
 'r1bq1rk1/1p2b2p/4p2Q/3pNpp1/1ppP4/4P1P1/PPP1BP1P/R3R1K1 w - - 0 1',
]
if '--hard' in sys.argv:FENS=HARD
worst=0;tot=0
for f in FENS:
 legal=None
 g['LIM']=lim
 g['tables'](1.0);p,w=g['parse'](f);p=(p[0],g['score'](p[0]))+p[2:]
 lu=[g['sq'](m[0],w)+g['sq'](m[1],w)+m[2].lower() for m in g['gen'](p) if g['mk'](p,m)]
 t=time.perf_counter();m=g['think'](f,f,[],lu);dt=time.perf_counter()-t
 worst=max(worst,dt);tot+=dt
 print(f'{dt:6.3f}s {m}  {f}')
print(f'LIM={lim} worst={worst:.3f}s mean={tot/len(FENS):.3f}s')
