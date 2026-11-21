#!/bin/sh
# Rebuild main.py from dev/engine.py with the kit's `makefun compress`,
# then run the correctness gate on the packed main.py.
# usage: dev/build.sh <unpacked kit dir>
set -e
KIT=${1:-$HOME/work/kit33/tiny-chess-01-kit}
cd "$(dirname "$0")/.."
node "$KIT/cli/makefun.mjs" compress dev/engine.py --out main.py
wc -c main.py
python3 dev/test_engine.py main.py
