"""Engine v2 (dev): check-aware qsearch + iterative deepening w/ node budget.
Reuses the verified 0x88 movegen/make/unmake from engine_full, adds improvements."""
import sys, time
MATE = 100000
INF = 1 << 30
VAL = [0, 100, 320, 330, 500, 900, 20000]
N_OFF = [-33, -31, -18, -14, 14, 18, 31, 33]
B_OFF = [-17, -15, 15, 17]
R_OFF = [-16, -1, 1, 16]
K_OFF = [-17, -16, -15, -1, 1, 15, 16, 17]

PST = {
 1:[0,0,0,0,0,0,0,0, 5,10,10,-20,-20,10,10,5, 5,-5,-10,0,0,-10,-5,5, 0,0,0,20,20,0,0,0,
    5,5,10,25,25,10,5,5, 10,10,20,30,30,20,10,10, 50,50,50,50,50,50,50,50, 0,0,0,0,0,0,0,0],
 2:[-50,-40,-30,-30,-30,-30,-40,-50, -40,-20,0,5,5,0,-20,-40, -30,5,10,15,15,10,5,-30,
    -30,0,15,20,20,15,0,-30, -30,5,15,20,20,15,5,-30, -30,0,10,15,15,10,0,-30,
    -40,-20,0,0,0,0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50],
 3:[-20,-10,-10,-10,-10,-10,-10,-20, -10,5,0,0,0,0,5,-10, -10,10,10,10,10,10,10,-10,
    -10,0,10,10,10,10,0,-10, -10,0,5,10,10,5,0,-10, -10,0,5,5,5,5,0,-10,
    -10,0,0,0,0,0,0,-10, -20,-10,-10,-10,-10,-10,-10,-20],
 4:[0,0,0,5,5,0,0,0, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, 5,10,10,10,10,10,10,5, 0,0,0,0,0,0,0,0],
 5:[-20,-10,-10,-5,-5,-10,-10,-20, -10,0,5,0,0,0,0,-10, -10,5,5,5,5,5,0,-10,
    -5,0,5,5,5,5,0,-5, 0,0,5,5,5,5,0,-5, -10,0,5,5,5,5,0,-10,
    -10,0,0,0,0,0,0,-10, -20,-10,-10,-5,-5,-10,-10,-20],
 6:[20,30,10,0,0,10,30,20, 20,20,0,0,0,0,20,20, -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30],
}
# endgame king table (centralization)
PST_KING_EG = [
  -50,-30,-30,-30,-30,-30,-30,-50,
  -30,-30,  0,  0,  0,  0,-30,-30,
  -30,-10, 20, 30, 30, 20,-10,-30,
  -30, -5, 20, 40, 40, 20, -5,-30,
  -30, -5, 20, 40, 40, 20, -5,-30,
  -30,-10, 20, 30, 30, 20,-10,-30,
  -30,-30,  0,  0,  0,  0,-30,-30,
  -50,-30,-30,-30,-30,-30,-30,-50]


def on(sq):
    return 0 <= sq < 128 and (sq & 0x88) == 0


class Pos:
    def __init__(self, fen):
        self.b = [0]*128; self.c = 1; self.cr = 0; self.ep = -1
        z = fen.split()
        for i, row in enumerate(z[0].split("/")):
            k = 7-i; f = 0
            for ch in row:
                if ch.isdigit(): f += int(ch)
                else:
                    t = "pnbrqk".index(ch.lower())+1
                    self.b[k*16+f] = t if ch.isupper() else -t; f += 1
        self.c = 1 if z[1] == "w" else -1
        if len(z) > 3 and z[3] != "-":
            self.ep = "abcdefgh".index(z[3][0]) + (int(z[3][1])-1)*16
        if len(z) > 2:
            self.cr = ("K" in z[2]) | ("Q" in z[2]) << 1 | ("k" in z[2]) << 2 | ("q" in z[2]) << 3
        self.wk = self.b.index(6); self.bk = self.b.index(-6)

    def atk(self, q, by):
        b = self.b
        if by > 0:
            for o in (-17, -15):
                t = q+o
                if on(t) and b[t] == 1: return 1
        else:
            for o in (15, 17):
                t = q+o
                if on(t) and b[t] == -1: return 1
        for o in N_OFF:
            t = q+o
            if on(t) and b[t] == 2*by: return 1
        for o in K_OFF:
            t = q+o
            if on(t) and b[t] == 6*by: return 1
        for os, ts in ((R_OFF, (4, 5)), (B_OFF, (3, 5))):
            for o in os:
                t = q+o
                while on(t):
                    p = b[t]
                    if p:
                        if p*by > 0 and abs(p) in ts: return 1
                        break
                    t += o
        return 0

    def chk(self, c):
        return self.atk(self.wk if c > 0 else self.bk, -c)

    def gen(self):
        b = self.b; c = self.c; M = []
        for q in range(128):
            p = b[q]
            if not p or p*c < 0: continue
            t = abs(p)
            if t == 1:
                d = 16*c; fw = q+d
                if on(fw) and b[fw] == 0:
                    M.append(q*128+fw)
                    if q >> 4 == (1 if c > 0 else 6) and on(q+2*d) and b[q+2*d] == 0:
                        M.append(q*128+q+2*d)
                for df in (-1, 1):
                    to = fw+df
                    if on(to) and ((b[to] and b[to]*c < 0) or (to == self.ep and not b[to])):
                        M.append(q*128+to)
            elif t == 2:
                for o in N_OFF:
                    to = q+o
                    if on(to) and b[to]*c <= 0: M.append(q*128+to)
            elif t < 6:
                for o in (B_OFF if t == 3 else R_OFF if t == 4 else K_OFF):
                    to = q+o
                    while on(to):
                        p = b[to]
                        if p:
                            if p*c < 0: M.append(q*128+to)
                            break
                        M.append(q*128+to); to += o
            else:
                for o in K_OFF:
                    to = q+o
                    if on(to) and b[to]*c <= 0: M.append(q*128+to)
                if c > 0 and q == 4:
                    if self.cr & 1 and not b[5] and not b[6] and b[7] == 4 and not self.atk(4, -1) and not self.atk(5, -1) and not self.atk(6, -1):
                        M.append(4*128+6)
                    if self.cr & 2 and not b[3] and not b[2] and not b[1] and b[0] == 4 and not self.atk(4, -1) and not self.atk(3, -1) and not self.atk(2, -1):
                        M.append(4*128+2)
                elif c < 0 and q == 116:
                    if self.cr & 4 and not b[117] and not b[118] and b[119] == -4 and not self.atk(116, 1) and not self.atk(117, 1) and not self.atk(118, 1):
                        M.append(116*128+118)
                    if self.cr & 8 and not b[115] and not b[114] and not b[113] and b[112] == -4 and not self.atk(116, 1) and not self.atk(115, 1) and not self.atk(114, 1):
                        M.append(116*128+114)
        return M

    def mk(self, m):
        f = m >> 7; to = m & 127; b = self.b; c = self.c; p = b[f]
        u = (b[to], self.ep, self.cr, self.wk, self.bk, p); b[f] = 0; cs = to
        if abs(p) == 1 and (f & 7) != (to & 7) and not b[to]: cs = to-16*c
        cap = b[cs]; b[cs] = 0
        if abs(p) == 1 and (to >> 4 in (0, 7)): p = 5*c
        b[to] = p
        if abs(p) == 6 and abs(to-f) == 2:
            if to > f: b[to-1] = b[to+1]; b[to+1] = 0
            else: b[to+1] = b[to-2]; b[to-2] = 0
        if p == 6: self.wk = to
        elif p == -6: self.bk = to
        if abs(p) == 6: self.cr &= ~3 if c > 0 else ~12
        if f == 0 or to == 0: self.cr &= ~2
        if f == 7 or to == 7: self.cr &= ~1
        if f == 112 or to == 112: self.cr &= ~8
        if f == 119 or to == 119: self.cr &= ~4
        self.ep = (f+to)//2 if abs(p) == 1 and abs(to-f) == 32 else -1
        self.c = -c
        return (cap, cs, u)

    def uk(self, m, u):
        cap, cs, u = u; self.c = -self.c; f = m >> 7; to = m & 127; b = self.b; p = b[to]
        b[to] = 0; b[cs] = cap; b[f] = u[5]
        if abs(p) == 6 and abs(to-f) == 2:
            if to > f: b[to+1] = b[to-1]; b[to-1] = 0
            else: b[to-2] = b[to+1]; b[to+1] = 0
        self.ep = u[1]; self.cr = u[2]; self.wk = u[3]; self.bk = u[4]

    def ev(self):
        b = self.b; sc = 0; nonpawn = 0; bishop = [0, 0]
        for q in range(128):
            if q & 0x88: continue
            p = b[q]
            if not p: continue
            t = abs(p)
            idx = (q >> 4)*8+(q & 7) if p > 0 else (7-(q >> 4))*8+(q & 7)
            if t == 6:
                continue  # king handled after phase known
            v = VAL[t]+PST[t][idx]
            sc += v if p > 0 else -v
            if t != 1: nonpawn += VAL[t]
            if t == 3: bishop[0 if p > 0 else 1] += 1
        # king phase interpolation
        phase = min(nonpawn, 6800)
        wki = (self.wk >> 4)*8+(self.wk & 7)
        bki = (7-(self.bk >> 4))*8+(self.bk & 7)
        wk = (PST[6][wki]*phase + PST_KING_EG[wki]*(6800-phase))//6800
        bk = (PST[6][bki]*phase + PST_KING_EG[bki]*(6800-phase))//6800
        sc += wk - bk
        if bishop[0] >= 2: sc += 30
        if bishop[1] >= 2: sc -= 30
        return sc*self.c


class Search:
    def __init__(self, pos, budget):
        self.p = pos
        self.nodes = 0
        self.budget = budget
        self.abort = False
        self.killers = {}
        self.hists = {}

    def qsearch(self, al, be, pc):
        self.nodes += 1
        if self.nodes >= self.budget:
            self.abort = True
            return 0
        p = self.p
        chk = p.chk(p.c)
        best = -MATE-1
        if pc >= 40:
            return p.ev()
        if not chk:
            st = p.ev()
            if st >= be: return st
            best = st
            if st > al: al = st
        b = p.b; c = p.c
        moves = []
        for m in p.gen():
            f = m >> 7; to = m & 127; tp = b[to]
            cap = (tp and tp*c < 0) or (abs(b[f]) == 1 and (f & 7) != (to & 7) and not tp)
            promo = abs(b[f]) == 1 and (to >> 4 in (0, 7))
            if chk or cap or promo:
                moves.append(m)
        moves.sort(key=lambda m: self.mvv(m), reverse=True)
        legal = 0
        for m in moves:
            u = p.mk(m)
            if p.chk(c):
                p.uk(m, u); continue
            legal += 1
            sc = -self.qsearch(-be, -al, pc+1)
            p.uk(m, u)
            if self.abort: return 0
            if sc > best: best = sc
            if sc >= be: return sc
            if sc > al: al = sc
        if chk and legal == 0:
            return -MATE+pc
        return best

    def mvv(self, m):
        p = self.p; f = m >> 7; to = m & 127
        v = p.b[to]; a = abs(p.b[f])
        if not v and a == 1 and (f & 7) != (to & 7): v = 1
        return VAL[abs(v)]*16 - VAL[a]

    def negamax(self, d, al, be, pc):
        if d <= 0:
            return self.qsearch(al, be, pc)
        self.nodes += 1
        if self.nodes >= self.budget:
            self.abort = True
            return 0
        p = self.p
        chk = p.chk(p.c)
        if chk: d += 1  # check extension
        c = p.c
        L = []
        for m in p.gen():
            u = p.mk(m)
            if not p.chk(c): L.append(m)
            p.uk(m, u)
        if not L:
            return -MATE+pc if chk else 0
        k0, k1 = self.killers.get(pc, (0, 0))
        def od(m):
            f = m >> 7; to = m & 127
            cap = p.b[to] or (abs(p.b[f]) == 1 and (f & 7) != (to & 7) and not p.b[to])
            if cap or (abs(p.b[f]) == 1 and to >> 4 in (0, 7)):
                return (2, self.mvv(m))
            if m == k0: return (1, 0)
            if m == k1: return (1, 0)
            return (0, self.hists.get(m, 0))
        L.sort(key=od, reverse=True)
        best = -INF
        for m in L:
            u = p.mk(m)
            sc = -self.negamax(d-1, -be, -al, pc+1)
            p.uk(m, u)
            if self.abort: return 0
            if sc > best: best = sc
            if sc > al:
                al = sc
                if not (p.b[m & 127] or (abs(p.b[m >> 7]) == 1 and (m & 127) >> 4 in (0, 7))):
                    self.hists[m] = self.hists.get(m, 0) + d*d
            if al >= be:
                if not (p.b[m & 127]):
                    self.killers[pc] = (m, k0)
                break
        return best

    def run(self, maxdepth):
        p = self.p
        L = []
        c = p.c
        for m in p.gen():
            u = p.mk(m)
            if not p.chk(c): L.append(m)
            p.uk(m, u)
        if not L:
            return None
        bm = L[0]
        for d in range(1, maxdepth+1):
            al = -INF; lb = None; sc = []
            self.nodes = 0  # reset per-iteration budget? No — budget is per move.
            for m in L:
                u = p.mk(m)
                v = -self.negamax(d-1, -INF, -al, 1)
                p.uk(m, u)
                if self.abort: break
                sc.append((v, m))
                if v > al: al = v; lb = m
            if self.abort:
                break
            sc.sort(reverse=True)
            L = [m for _, m in sc]
            if lb is not None:
                bm = lb
            if bm and -al >= MATE-100:
                break
        return bm


def sq(s): return "abcdefgh"[s & 7]+str((s >> 4)+1)
def uci(s, m):
    f = m >> 7; to = m & 127
    pr = "q" if abs(s.b[f]) == 1 and to >> 4 in (0, 7) else ""
    return sq(f)+sq(to)+pr

if __name__ == "__main__":
    import chess
    fen = chess.STARTING_FEN
    board = chess.Board()
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    for i in range(8):
        pos = Pos(board.fen())
        s = Search(pos, budget)
        t0 = time.time()
        bm = s.run(64)
        dt = time.time()-t0
        u = uci(pos, bm)
        m = chess.Move.from_uci(u)
        assert m in board.legal_moves, f"illegal {u}"
        board.push(m)
        print(f"move {i}: {u} nodes={s.nodes} {dt:.2f}s eval={pos.ev()}")
    print("self-play legal OK")