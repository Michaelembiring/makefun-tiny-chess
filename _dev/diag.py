import os
os.environ["MAKEFUN_ENV_URL"] = "http://dummy"
import chess
src = open('/Users/user/bounty/tiny-chess/main.py').read().split('while 1:')[0]
ns = {}
exec(src, ns)
P = ns['P']; best = ns['best']

def engine_move(fen):
    s = P(fen); s.n = 0
    legal = [m.uci() for m in chess.Board(fen).legal_moves]
    mv = best(s, legal)
    return mv, s.n

tests = [
  ("mate_in_1_backrank", "6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1", "d1d8"),
  ("free_queen", "4k3/8/8/3q4/4P3/8/8/4K3 w - - 0 1", "e4d5"),
  ("mate_in_1_Qe8", "6k1/5ppp/8/8/8/8/5PPP/4Q1K1 w - - 0 1", "e1e8"),
  ("hanging_rook", "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1", "e1e2"),  # Kxe2? no, Kxe2 not adjacent? e1 to e2 adjacent yes
  ("mate_in_2", "r1bq2kr/pppp1ppp/2n5/8/2B1Q3/8/PPPP1PPP/RNB2RK1 w - - 0 1", None),
]
for name, fen, expect in tests:
    mv, n = engine_move(fen)
    b = chess.Board(fen)
    legal = set(m.uci() for m in b.legal_moves)
    norm = set(x[:4] for x in legal)
    ok = mv in legal or mv[:4] in norm
    print(f"{name}: played {mv} expect {expect} nodes={n} legal={ok}")
    try:
        m2 = chess.Move.from_uci(mv if mv in legal else mv+'q')
        b.push(m2)
        print(f"   replies={b.legal_moves.count()} checkmate={b.is_checkmate()} check={b.is_check()}")
    except Exception as e:
        print("   err", e)
    print()