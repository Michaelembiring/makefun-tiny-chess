"""Verify golf2.py: eval symmetry, plays legal chess, root castling works via env moves."""
import os
os.environ["MAKEFUN_ENV_URL"]="http://dummy"
import chess
src=open('/Users/user/bounty/tiny-chess/_dev/golf2.py').read().split('while 1:')[0]
ns={};exec(src,ns)
P=ns['P'];best=ns['best']

print("bytes:", len(open('/Users/user/bounty/tiny-chess/_dev/golf2.py').read().encode()))
# eval symmetry
print("start eval:",P(chess.STARTING_FEN).ev(),"(want 0)")
print("Qup w:",P("4k3/8/8/8/8/8/8/3QK3 w - - 0 1").ev(),"(want ~+900)")
print("Qup b:",P("4k3/8/8/8/8/8/8/3QK3 b - - 0 1").ev(),"(want ~-900)")

# plays legal chess from start
b=chess.Board()
for i in range(8):
    s=P(b.fen());s.bud=30000;s.n=0;s.ab=0
    legal=[m.uci() for m in b.legal_moves]
    u=best(s,legal,30000)
    m=chess.Move.from_uci(u if len(u)==5 else u+'q' if u+'q' in legal else u)
    assert m in b.legal_moves, f"illegal {u} not in {legal[:5]}..."
    b.push(m)
print("plays 8 legal moves from start: OK")

# castling via env legal_moves: a position where white can castle both ways
# After 1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.d3 (white can castle next) - use a clear one:
fen="r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
b=chess.Board(fen)
legal=[m.uci() for m in b.legal_moves]
print("castling in legal_moves?", 'e1g1' in legal, 'e1c1' in legal)
s=P(b.fen());s.bud=30000;s.n=0;s.ab=0
u=best(s,legal,30000)
print("engine chose in castling position:", u, "(legal:", u in legal or u+'q' in legal, ")")
# verify engine's internal make handles the castling move if chosen
if u in ('e1g1','e1c1'):
    f="abcdefgh".index(u[0])+(int(u[1])-1)*16;t="abcdefgh".index(u[2])+(int(u[3])-1)*16
    m=f*128+t; u2=s.mk(m)
    print("  after make, white king g1/c1?", s.b[6]==6 or s.b[2]==6, "rook moved?", s.b[5]==4 or s.b[3]==4)
    s.uk(m,u2)
    print("  unmake restores king e1?", s.b[4]==6)

# mate in 1
s=P("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1");s.bud=30000;s.n=0;s.ab=0
print("mate1:",best(s,[m.uci() for m in chess.Board("6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1").legal_moves],30000),"(want d1d8)")
print("ALL CHECKS DONE")