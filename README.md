# make-fun-work

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/hhsan666/make-fun-work/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard)
[![reward](https://make.fun/badge/tiny-chess-01/hhsan666/make-fun-work/reward.svg)](https://make.fun/bounty/tiny-chess-01)

A chess engine in at most 4,096 bytes of Python 3.13 (standard library only):
negamax alpha-beta with PVS, a transposition table, null-move pruning, late
move reductions, killer moves, MVV-LVA ordering and a quiescence search
(captures and promotions; every evasion when in check), deepened one ply at a
time under a fixed node budget. No clock and no randomness: the same position
and history always give the same move.

## Run it

```sh
MAKEFUN_ENV_URL=http://store:8080 python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/bounty/tiny-chess-01)</sub>
