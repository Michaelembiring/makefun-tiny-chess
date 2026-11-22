"""Verify the engine's search returns the minimax-optimal move at its own eval.
Compare engine best() vs an independent reference negamax on the SAME eval."""
import os
os.environ["MAKEFUN_ENV_URL"] = "http://dummy"
import chess
src = open('/Users/user/bounty/tiny-chess/main.py').read().split('while 1:')[0]
ns = {}
exec(src, ns)
P = ns['P']; best = ns['best']; nm = ns['nm']; qs = ns['qs']; INF = ns['INF']; MATE = ns['MATE']

# Independent reference negamax using the engine's OWN P/eval/make/unmake/gen,
# but written fresh (no killers, no check extension) to cross-check nm().
def ref_nm(s, d, al, be, pc):
    if d <= 0:
        return qs(s, al, be, pc)
    c = s.c
    L = []
    for m in s.gen():
        u = s.mk(m)
        if not s.chk(c):
            L.append(m)
        s.uk(m, u)
    if not L:
        return -MATE + pc if s.chk(s.c) else 0
    # plain: no ordering
    for m in L:
        u = s.mk(m)
        v = -ref_nm(s, d-1, -be, -al, pc+1)
        s.uk(m, u)
        if v > al:
            al = v
        if al >= be:
            break
    return al

def ref_best(s, moves_uci, depth):
    L = []
    for u in moves_uci:
        f = "abcdefgh".index(u[0]) + (int(u[1])-1)*16
        t = "abcdefgh".index(u[2]) + (int(u[3])-1)*16
        L.append(f*128+t)
    bestm = None; bestv = -INF
    for m in L:
        u = s.mk(m)
        v = -ref_nm(s, depth-1, -INF, INF, 1)
        s.uk(m, u)
        if v > bestv:
            bestv = v; bestm = m
    return bestm, bestv

def eng_best(s, moves_uci, depth):
    # temporarily patch best() to use a given max depth
    L = []
    for u in moves_uci:
        f = "abcdefgh".index(u[0]) + (int(u[1])-1)*16
        t = "abcdefgh".index(u[2]) + (int(u[3])-1)*16
        L.append(f*128+t)
    bm = L[0]
    for d in range(1, depth+1):
        al = -INF; lb = None; sc = []
        for m in L:
            u = s.mk(m); v = -nm(s, d-1, -INF, -al, 1); s.uk(m, u); sc.append((v, m))
            if v > al: al = v; lb = m
        sc.sort(reverse=1); L = [m for _, m in sc]
        if lb is not None: bm = lb
    return bm

positions = [
  chess.STARTING_FEN,
  "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
  "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
  "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
  "r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1",
]
for depth in (2, 3):
    print(f"\n===== depth {depth} =====")
    for fen in positions:
        board = chess.Board(fen)
        moves = [m.uci() for m in board.legal_moves]
        s1 = P(fen); s1.n = 0
        eb = eng_best(s1, moves, depth)
        s2 = P(fen); s2.n = 0
        rb, rv = ref_best(s2, moves, depth)
        # compare move (engine may have multiple optimal; check value match too)
        s3 = P(fen); s3.n = 0
        u = s3.mk(eb); ev_eng = -ref_nm(s3, depth-1, -INF, INF, 1); s3.uk(eb, u)
        match = (eb == rb)
        valmatch = (ev_eng == rv)
        print(f"  {'OK ' if match and valmatch else 'DIFF'} eng={eb} ref={rb}  eng_val={ev_eng} ref_val={rv}  fen={fen[:40]}")