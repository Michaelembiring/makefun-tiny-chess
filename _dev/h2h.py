"""Head-to-head: v1 (old main.py logic) vs v2 (check-aware qsearch + king eval).
Plays N games at a fixed node budget each, reports result. Dev only."""
import os
os.environ["MAKEFUN_ENV_URL"] = "http://dummy"
import chess, sys

# load v1
src1 = open('/Users/user/bounty/tiny-chess/main.py').read().split('while 1:')[0]
ns1 = {}; exec(src1, ns1)
P1 = ns1['P']; nm1 = ns1['nm']; INF1 = ns1['INF']

# load v2
import engine_v2 as E2

def v1_move(fen, depth=4):
    s = P1(fen); s.n = 0
    legal = [m.uci() for m in chess.Board(fen).legal_moves]
    L = []
    for u in legal:
        f="abcdefgh".index(u[0])+(int(u[1])-1)*16; t="abcdefgh".index(u[2])+(int(u[3])-1)*16
        L.append(f*128+t)
    bm=L[0]
    for d in range(1,depth+1):
        al=-INF1; lb=None; sc=[]
        for m in L:
            u=s.mk(m); v=-nm1(s,d-1,-INF1,-al,1); s.uk(m,u); sc.append((v,m))
            if v>al: al=v; lb=m
        sc.sort(reverse=1); L=[m for _,m in sc]
        if lb is not None: bm=lb
    return ns1['uci'](s,bm)

def v2_move(fen, budget):
    s = E2.Search(E2.Pos(fen), budget)
    bm = s.run(64)
    return E2.uci(s.p, bm)

def play_game(budget, v2_white=True, maxplies=120):
    board = chess.Board()
    while not board.is_game_over() and board.ply() < maxplies:
        fen = board.fen()
        if (board.turn == chess.WHITE) == v2_white:
            u = v2_move(fen, budget)
        else:
            u = v1_move(fen, 4)
        m = chess.Move.from_uci(u if len(u)==5 else u+'q' if u+'q' in [x.uci() for x in board.legal_moves] else u)
        if m not in board.legal_moves:
            # fallback first legal
            m = list(board.legal_moves)[0]
        board.push(m)
    return board.result()

if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv)>1 else 40000
    ngames = int(sys.argv[2]) if len(sys.argv)>2 else 4
    import time
    w=d=l=0
    for g in range(ngames):
        v2_white = (g % 2 == 0)
        t0=time.time()
        r = play_game(budget, v2_white)
        # v2 score
        if r == '1/2-1/2': d+=1; res='draw'
        elif (r=='1-0')==v2_white: w+=1; res='v2 win'
        else: l+=1; res='v2 loss'
        print(f"game {g}: v2_white={v2_white} -> {r} ({res}) {time.time()-t0:.1f}s", flush=True)
    print(f"\nv2 vs v1: W{w} D{d} L{l}  (budget {budget})")