"""Fast head-to-head between engine variants using python-chess for legality.
Each plays a fixed number of moves from equal positions; report who's better by eval.
Actually: play full games but with a SMALL fixed depth to keep it fast."""
import os
os.environ["MAKEFUN_ENV_URL"]="http://dummy"
import chess, sys

def load(path, split='while 1:'):
    src=open(path).read().split(split)[0]
    ns={};exec(src,ns);return ns

# v1 = the ORIGINAL depth-4 engine (reconstruct from git-less: use engine_full logic via main_candidate w/o budget)
# We'll just test main_candidate at a given budget vs a plain depth-N.
import importlib.util
def get_candidate():
    return load('/Users/user/bounty/tiny-chess/_dev/main_candidate.py')

def candidate_move(ns, fen, budget):
    s=ns['P'](fen);s.bud=budget;s.n=0;s.ab=0
    legal=[m.uci() for m in chess.Board(fen).legal_moves]
    return ns['best'](s,legal,budget)

def play(white_ns, white_budget, black_ns, black_budget, maxplies=100):
    b=chess.Board()
    while not b.is_game_over() and b.ply()<maxplies:
        fen=b.fen()
        if b.turn==chess.WHITE:
            u=candidate_move(white_ns,fen,white_budget)
        else:
            u=candidate_move(black_ns,fen,black_budget)
        legal=[m.uci() for m in b.legal_moves]
        m=chess.Move.from_uci(u if len(u)==5 else u+'q' if u+'q' in legal else u)
        if m not in b.legal_moves: m=list(b.legal_moves)[0]
        b.push(m)
    return b.result()

if __name__=="__main__":
    ns=get_candidate()
    # compare budget 30k vs budget 100k (both same engine, diff budget) to see if budget helps
    b1=int(sys.argv[1]); b2=int(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 2
    w=d=l=0
    for g in range(n):
        # alternate colors; "A"=b1 white on even games
        if g%2==0:
            r=play(ns,b1,ns,b2)  # b1 white
            res='A' 
        else:
            r=play(ns,b2,ns,b1)  # b2 white
            res='B'
        print(f"game {g} ({res}=b1 {'white' if g%2==0 else 'black'}): {r}",flush=True)
    print("done")