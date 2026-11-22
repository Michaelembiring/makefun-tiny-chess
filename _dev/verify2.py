"""Verify new main.py: eval symmetry + search correctness vs reference."""
import os
os.environ["MAKEFUN_ENV_URL"] = "http://dummy"
import chess
src = open('/Users/user/bounty/tiny-chess/main.py').read().split('while 1:')[0]
ns = {}; exec(src, ns)
P = ns['P']; nm = ns['nm']; qs = ns['qs']; INF = ns['INF']; MATE = ns['MATE']

# 1. Eval symmetry: eval(pos) from white's view must equal -eval(mirrored colors)
# Simpler: eval of start position (symmetric) must be 0.
s = P(chess.STARTING_FEN)
print("start eval (should be 0):", s.ev())

# eval of a position where white is up a queen should be ~+900 from white to move
s2 = P("4k3/8/8/8/8/8/8/3QK3 w - - 0 1")  # white Ke1 Qd1, black Ke8
print("white up queen, white to move eval:", s2.ev(), "(should be ~+900)")
s3 = P("4k3/8/8/8/8/8/8/3QK3 b - - 0 1")  # same, black to move
print("white up queen, black to move eval:", s3.ev(), "(should be ~-900)")

# 2. Search correctness vs reference (check-aware) at depth 2,3
def ref_qs(s, al, be, pc):
    chk = s.chk(s.c); best = -MATE-1
    if pc >= 40: return s.ev()
    if not chk:
        st = s.ev()
        if st >= be: return st
        best = st
        if st > al: al = st
    b=s.b;c=s.c;cp=[]
    for m in s.gen():
        f=m>>7;to=m&127;tp=b[to]
        if chk or(tp and tp*c<0)or(abs(b[f])==1 and(f&7)!=(to&7)and not tp)or(abs(b[f])==1 and to>>4 in(0,7)):cp.append(m)
    cp.sort(key=lambda m: ns['mvv'](s,m), reverse=True)
    legal=0
    for m in cp:
        u=s.mk(m)
        if s.chk(c):s.uk(m,u);continue
        legal+=1;sc=-ref_qs(s,-be,-al,pc+1);s.uk(m,u)
        if sc>best:best=sc
        if sc>=be:return sc
        if sc>al:al=sc
    if chk and legal==0:return -MATE+pc
    return best

def ref_nm(s,d,al,be,pc):
    if d<=0:return ref_qs(s,al,be,pc)
    c=s.c;L=[]
    for m in s.gen():
        u=s.mk(m)
        if not s.chk(c):L.append(m)
        s.uk(m,u)
    if not L:return -MATE+pc if s.chk(s.c) else 0
    for m in L:
        u=s.mk(m);v=-ref_nm(s,d-1,-be,-al,pc+1);s.uk(m,u)
        if v>al:al=v
        if al>=be:break
    return al

def ref_best(s, moves, depth):
    L=[]
    for u in moves:
        f="abcdefgh".index(u[0])+(int(u[1])-1)*16;t="abcdefgh".index(u[2])+(int(u[3])-1)*16;L.append(f*128+t)
    bm=None;bv=-INF
    for m in L:
        u=s.mk(m);v=-ref_nm(s,depth-1,-INF,INF,1);s.uk(m,u)
        if v>bv:bv=v;bm=m
    return bm,bv

def eng_best(s, moves, depth):
    L=[]
    for u in moves:
        f="abcdefgh".index(u[0])+(int(u[1])-1)*16;t="abcdefgh".index(u[2])+(int(u[3])-1)*16;L.append(f*128+t)
    bm=L[0]
    s.bud=10**9;s.n=0;s.ab=0
    for d in range(1,depth+1):
        al=-INF;lb=None;sc=[]
        for m in L:
            u=s.mk(m);v=-nm(s,d-1,-INF,-al,1);s.uk(m,u);sc.append((v,m))
            if v>al:al=v;lb=m
        sc.sort(reverse=1);L=[m for _,m in sc]
        if lb is not None:bm=lb
    return bm

positions = [
  chess.STARTING_FEN,
  "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
  "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
  "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
]
allok=True
for depth in (2,3):
    print(f"\n=== depth {depth} ===")
    for fen in positions:
        board=chess.Board(fen);moves=[m.uci() for m in board.legal_moves]
        s1=P(fen);eb=eng_best(s1,moves,depth)
        s2=P(fen);rb,rv=ref_best(s2,moves,depth)
        s3=P(fen);u=s3.mk(eb);ev=-ref_nm(s3,depth-1,-INF,INF,1);s3.uk(eb,u)
        ok=(eb==rb and ev==rv)
        allok&=ok
        print(f"  {'OK ' if ok else 'DIFF'} eng={eb} ref={rb} val {ev}=={rv}  {fen[:32]}")
print("\nALL OK" if allok else "\nFAILURES")