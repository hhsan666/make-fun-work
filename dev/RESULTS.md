# Measurements

All times are this container (Intel Xeon 2.10GHz); grade-local runs the bot in docker with 1 CPU.
Sunfish 4k baseline on the 6-game practice trials (RULES.txt, "The house baseline"): 1364 / 1451 / 1279, mean 1365.

| version | LIM | trial-0 | trial-1 | trial-2 | mean | max think (ms) | notes |
|---|---|---|---|---|---|---|---|
| v1 (deb9496) | 25000 | 1451 | 1451 | 1545 | 1482 | 546 / 553 / 521 | all finished, replay matched, 0 time losses |

bench (dev/bench.py, 8 middlegame positions): LIM 10000 worst 0.227s; 20000 worst 0.404s; 25000 worst 0.444s.
