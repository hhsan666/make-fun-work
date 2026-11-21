# Measurements

All times are this container (Intel Xeon 2.10GHz); grade-local runs the bot in docker with 1 CPU.
Sunfish 4k baseline on the 6-game practice trials (RULES.txt, "The house baseline"): 1364 / 1451 / 1279, mean 1365.

| version | LIM | trial-0 | trial-1 | trial-2 | mean | max think (ms) | notes |
|---|---|---|---|---|---|---|---|
| v1 (deb9496) | 25000 | 1451 | 1451 | 1545 | 1482 | 546 / 553 / 521 | all finished, replay matched, 0 time losses |

bench (dev/bench.py, 8 middlegame positions): LIM 10000 worst 0.227s; 20000 worst 0.404s; 25000 worst 0.444s.
| v6 (9affcfd, LIM 21000 nodes) | 21000 | 1364 | 1279 | 1279 | 1307 | 743 / 540 / 632 | finished, replay matched; slowest moves in multi-queen / mating positions |

| v14 (LIM 350000 work units) | 350000 | 1654 | 1451 | 1545 | 1550 | 681 / 688 / 953 | finished, replay matched, 0 time losses; avg think 483/459/512 ms in docker; the slowest positions take 0.36-0.52 s re-timed outside docker (trial 2 ran ~2x slower) |
| v18 (LIM 375000) | 375000 | 1279 | 1451 | 1451 | 1394 | 688 / 586 / 658 | same search as v14 plus speedups; practice results swing widely between near-identical builds |
| v18 (LIM 340000) | 340000 | 1451 | 1451 | 1451 | 1451 | - | |
| **candidate 1** (submission 56eed0f, v18 search, LIM 360000) | 360000 | 1451 | 1654 | 1545 | 1550 | 735 / 734 / 658 | finished x3, replay matched x3, 0 time losses, avg think 482/471/446 ms in docker; every trial above sunfish's 1364/1451/1279 |

## Local matches (dev/match.py, kit env + house engines, process driver)
6 opponents (depth-2 .. nodes-500k) x 2 colours x 8 units = 96 games, offset 0 (same openings for every row). Elo = the scorer's formula on all games.

| version | change | score | Elo |
|---|---|---|---|
| v1 | first engine | 49.5/96 | 1295 |
| v6 | + RFP, history, futility, qsearch pawn-SEE, faster gen, structure eval (21k nodes) | 50.5/96 | 1305 |
| v6 x2 | same at 42k nodes (2x) | 68.5/96 | 1503 |
| v8 | work-unit budget (time-calibrated) + TT move first | 60.0/96 | 1407 |
| v10 | + LMP, prune before make, refitted work weights (LIM 370000) | 52.0/96 | 1321 |
| v11 | v10 + null move R=3 at d>3 | 53.5/96 | 1338 |
| v12 | v10 + stronger LMR | 60.0/96 | 1407 |

Doubling the search is worth about +200 Elo here, so speed / search efficiency comes first.
| v13 | v10, but futility/LMP never prune a move that gives check | 60.5/96 | 1413 |
| v14 | v13 + stronger LMR | 64.0/96 | 1451 |

v14 timing (dev tcal, LIM 350000, outside docker): middlegame worst 0.436 s mean 0.388 s; game positions worst 0.543 s; hard set worst 0.440 s.
| v15c | v14 + two killers per ply | 60.0/96 | 1407 |
| v15d | v14 + rooks on open/half-open files (cache keyed with rooks, ~20% slower) | 62.0/96 | 1429 |
| v16 | v14 + king tropism toward the root's enemy king (side-specific tables) | 59.0/96 | 1397 |
| v16b | same, tropism weights x2 | 60.0/96 | 1407 |
| v17a | v14 + razoring (d<3) | 61.0/96 | 1418 |
| v17b | v14 + smaller margins (RFP 85*d, futility 95*d) | 64.5/96 | 1457 |

Rejected (no gain over v14 within noise): v15c, v15d, v16, v16b, v17a. A lazy MVV-LVA capture generator was slower (mean 0.388 s -> 0.457 s) and was dropped before any match.
| v17c | v14 + skip captures of a defended piece by a more valuable one in quiescence (-41% work to depth 7) | 59.5/96 | 1402 |
| v17d | v17c + smaller margins | 62.5/96 | 1435 |
| v18 | v14 search + speedups (~7% faster), LIM 375000 | 64.5/96 | 1457 |

Candidate 1 timing outside docker (LIM 360000): dev/bench.py middlegame worst 0.41-0.46 s, mean 0.39-0.41 s; tcal middlegame worst 0.52-0.55 s on noisier runs, mean 0.42-0.43 s.
check (kit level 33) with the bundle: 16 passed, 0 failed (thinking_reproduces 239/253 lines = 94.4%).
