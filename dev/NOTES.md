# Engine design notes (dev/engine.py)

`main.py` is `makefun compress dev/engine.py` (an LZMA payload with the kit's
unpacker). Comments live here, not in the source, to keep main.py under 4,096
bytes.

## Board
- 120-char string, 10x12 mailbox; rows 0-1 and 10-11 and columns 0 and 9 are
  padding (' ' / '\n'). a1 = 91, h1 = 98, a8 = 21, h8 = 28.
- Always seen from the side to move: upper case = side to move. After a move
  the board is rotated (`b[::-1].swapcase()`), the score negated and the
  castling pairs swapped. Rotation mirrors files, so every table is symmetric
  left-right.
- Position tuple: (board, score, own castling (a1-rook, h1-rook),
  their castling, en-passant square in the mover's coordinates or 0).

## Moves
- `gen(pos, c)`: pseudo-legal moves; `c=1` yields only captures and
  promotions (queen promotion for quiet pushes) for quiescence.
- `mk(pos, m, k)`: makes the move, returns None when it leaves our king
  attacked. When we are not in check (`k` = king square) a move from a square
  off every line through the king (and not a king move or en passant) cannot
  expose the king, so the attack test is skipped.
- `att(b, s)`: is square s attacked by a lower-case piece.

## Evaluation
- Piece values P100 N300 B320 R500 Q950 inside piece-square tables generated
  by formulas (`tables(ph)`), tapered once per root position by the phase
  (non-pawn material / 6400). King: back-rank shelter squares in the
  middlegame, centralisation in the endgame. Pawns: advance bonus, centre
  pawns, wing (shelter) pawns held back in the middlegame.
- `ev(pos)`: PST score kept incrementally + a structure term cached on the
  pawn/king placement: passed pawns by rank (doubled in the endgame),
  doubled -12, isolated -10, king shelter -18 per missing pawn in front of a
  back-rank king (middlegame weight).

## Search
- Negamax alpha-beta with PVS, iterative deepening, fixed node budget `LIM`
  (search + quiescence nodes); when the budget runs out the search raises
  `Stop` and the best root move of the last completed (or improved) iteration
  is played. No clock anywhere.
- Transposition table (cleared every move, so a position and its game history
  alone decide the move), killer per ply, history heuristic, MVV-LVA.
- Check extension, null move (R=2, not in check, with pieces), reverse
  futility (d<4, non-PV), futility for quiet moves (d<3), LMR (1 ply after the
  3rd move at d>2, 2 plies after the 9th at d>4).
- Quiescence: stand pat, captures and promotions with delta pruning and a
  skip for captures a defending pawn wins back at a loss; in check, every
  evasion (mate detected).
- Repetition: any position of the game history or the current path scores 0.

## Root
- The root move is always one of the env's `legal_moves`; the search's own
  generation is intersected with it (fallback: the env's first move).
