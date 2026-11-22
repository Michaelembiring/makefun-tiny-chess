"""Full engine with search (readable dev version). 0x88, negamax a-b, PST, qsearch."""
import sys
MATE = 100000
INF = 1000000
VAL = [0, 100, 320, 330, 500, 900, 20000]
N_OFF = [-33, -31, -18, -14, 14, 18, 31, 33]
B_OFF = [-17, -15, 15, 17]
R_OFF = [-16, -1, 1, 16]
K_OFF = [-17, -16, -15, -1, 1, 15, 16, 17]

# Piece-square tables (from white's view, index 0 = a1 ... 63 = h8), standard simplified tables.
# We index by (rank*8+file) with rank 0 = rank1. For black, mirror vertically.
PST = {
    1: [  # pawn
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10,-20,-20, 10, 10,  5,
        5, -5,-10,  0,  0,-10, -5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5,  5, 10, 25, 25, 10,  5,  5,
       10, 10, 20, 30, 30, 20, 10, 10,
       50, 50, 50, 50, 50, 50, 50, 50,
        0,  0,  0,  0,  0,  0,  0,  0],
    2: [  # knight
      -50,-40,-30,-30,-30,-30,-40,-50,
      -40,-20,  0,  5,  5,  0,-20,-40,
      -30,  5, 10, 15, 15, 10,  5,-30,
      -30,  0, 15, 20, 20, 15,  0,-30,
      -30,  5, 15, 20, 20, 15,  5,-30,
      -30,  0, 10, 15, 15, 10,  0,-30,
      -40,-20,  0,  0,  0,  0,-20,-40,
      -50,-40,-30,-30,-30,-30,-40,-50],
    3: [  # bishop
      -20,-10,-10,-10,-10,-10,-10,-20,
      -10,  5,  0,  0,  0,  0,  5,-10,
      -10, 10, 10, 10, 10, 10, 10,-10,
      -10,  0, 10, 10, 10, 10,  0,-10,
      -10,  0,  5, 10, 10,  5,  0,-10,
      -10,  0,  5,  5,  5,  5,  0,-10,
      -10,  0,  0,  0,  0,  0,  0,-10,
      -20,-10,-10,-10,-10,-10,-10,-20],
    4: [  # rook
        0,  0,  0,  5,  5,  0,  0,  0,
       -5,  0,  0,  0,  0,  0,  0, -5,
       -5,  0,  0,  0,  0,  0,  0, -5,
       -5,  0,  0,  0,  0,  0,  0, -5,
       -5,  0,  0,  0,  0,  0,  0, -5,
       -5,  0,  0,  0,  0,  0,  0, -5,
        5, 10, 10, 10, 10, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0],
    5: [  # queen
      -20,-10,-10, -5, -5,-10,-10,-20,
      -10,  0,  5,  0,  0,  0,  0,-10,
      -10,  5,  5,  5,  5,  5,  0,-10,
       -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
      -10,  0,  5,  5,  5,  5,  0,-10,
      -10,  0,  0,  0,  0,  0,  0,-10,
      -20,-10,-10, -5, -5,-10,-10,-20],
    6: [  # king (middlegame)
       20, 30, 10,  0,  0, 10, 30, 20,
       20, 20,  0,  0,  0,  0, 20, 20,
      -10,-20,-20,-20,-20,-20,-20,-10,
      -20,-30,-30,-40,-40,-30,-30,-20,
      -30,-40,-40,-50,-50,-40,-40,-30,
      -30,-40,-40,-50,-50,-40,-40,-30,
      -30,-40,-40,-50,-50,-40,-40,-30,
      -30,-40,-40,-50,-50,-40,-40,-30],
}


def on(sq):
    return 0 <= sq < 128 and (sq & 0x88) == 0


class Pos:
    def __init__(self, fen):
        self.b = [0] * 128
        self.c = 1
        self.cr = 0
        self.ep = -1
        parts = fen.split()
        for i, row in enumerate(parts[0].split("/")):
            rank = 7 - i
            file = 0
            for ch in row:
                if ch.isdigit():
                    file += int(ch)
                else:
                    t = "pnbrqk".index(ch.lower()) + 1
                    self.b[rank * 16 + file] = t if ch.isupper() else -t
                    file += 1
        self.c = 1 if parts[1] == "w" else -1
        if len(parts) > 3 and parts[3] != "-":
            self.ep = "abcdefgh".index(parts[3][0]) + (int(parts[3][1]) - 1) * 16
        if len(parts) > 2:
            self.cr = ("K" in parts[2]) | ("Q" in parts[2]) << 1 | ("k" in parts[2]) << 2 | ("q" in parts[2]) << 3
        self.wk = self._find(6)
        self.bk = self._find(-6)

    def _find(self, p):
        for sq in range(128):
            if self.b[sq] == p:
                return sq
        return -1

    def attacked(self, sq, by):
        b = self.b
        if by == 1:
            for o in (-17, -15):
                t = sq + o
                if on(t) and b[t] == 1:
                    return True
        else:
            for o in (15, 17):
                t = sq + o
                if on(t) and b[t] == -1:
                    return True
        for o in N_OFF:
            t = sq + o
            if on(t) and b[t] == 2 * by:
                return True
        for o in K_OFF:
            t = sq + o
            if on(t) and b[t] == 6 * by:
                return True
        for offs, types in ((R_OFF, (4, 5)), (B_OFF, (3, 5))):
            for o in offs:
                t = sq + o
                while on(t):
                    p = b[t]
                    if p:
                        if p * by > 0 and abs(p) in types:
                            return True
                        break
                    t += o
        return False

    def in_check(self, c):
        k = self.wk if c == 1 else self.bk
        return self.attacked(k, -c)

    def gen(self):
        b = self.b
        c = self.c
        moves = []
        for sq in range(128):
            p = b[sq]
            if p == 0 or p * c <= 0:
                continue
            t = abs(p)
            if t == 1:
                d = 16 * c
                fwd = sq + d
                if on(fwd) and b[fwd] == 0:
                    moves.append(sq * 128 + fwd)
                    start = sq + 2 * d
                    if (sq >> 4) == (1 if c == 1 else 6) and on(start) and b[start] == 0:
                        moves.append(sq * 128 + start)
                for df in (-1, 1):
                    to = fwd + df
                    if not on(to):
                        continue
                    tp = b[to]
                    if (tp != 0 and tp * c < 0) or (to == self.ep and tp == 0):
                        moves.append(sq * 128 + to)
            elif t == 2:
                for o in N_OFF:
                    to = sq + o
                    if on(to) and b[to] * c <= 0:
                        moves.append(sq * 128 + to)
            elif t == 3 or t == 4 or t == 5:
                offs = B_OFF if t == 3 else R_OFF if t == 4 else K_OFF
                for o in offs:
                    to = sq + o
                    while on(to):
                        tp = b[to]
                        if tp == 0:
                            moves.append(sq * 128 + to)
                        else:
                            if tp * c < 0:
                                moves.append(sq * 128 + to)
                            break
                        to += o
            elif t == 6:
                for o in K_OFF:
                    to = sq + o
                    if on(to) and b[to] * c <= 0:
                        moves.append(sq * 128 + to)
                if c == 1 and sq == 4:
                    if self.cr & 1 and b[5] == 0 and b[6] == 0 and b[7] == 4 \
                       and not self.attacked(4, -1) and not self.attacked(5, -1) and not self.attacked(6, -1):
                        moves.append(4 * 128 + 6)
                    if self.cr & 2 and b[3] == 0 and b[2] == 0 and b[1] == 0 and b[0] == 4 \
                       and not self.attacked(4, -1) and not self.attacked(3, -1) and not self.attacked(2, -1):
                        moves.append(4 * 128 + 2)
                elif c == -1 and sq == 116:
                    if self.cr & 4 and b[117] == 0 and b[118] == 0 and b[119] == -4 \
                       and not self.attacked(116, 1) and not self.attacked(117, 1) and not self.attacked(118, 1):
                        moves.append(116 * 128 + 118)
                    if self.cr & 8 and b[115] == 0 and b[114] == 0 and b[113] == 0 and b[112] == -4 \
                       and not self.attacked(116, 1) and not self.attacked(115, 1) and not self.attacked(114, 1):
                        moves.append(116 * 128 + 114)
        return moves

    def make(self, m):
        f = m >> 7
        to = m & 127
        b = self.b
        c = self.c
        p = b[f]
        undo = (b[to], self.ep, self.cr, self.wk, self.bk, p)
        b[f] = 0
        captured_sq = to
        if abs(p) == 1 and (f & 7) != (to & 7) and b[to] == 0:
            captured_sq = to - 16 * c
        cap = b[captured_sq]
        b[captured_sq] = 0
        if abs(p) == 1 and (to >> 4 == 7 or to >> 4 == 0):
            p = 5 * c
        b[to] = p
        if abs(p) == 6 and abs(to - f) == 2:
            if to > f:
                b[to - 1] = b[to + 1]
                b[to + 1] = 0
            else:
                b[to + 1] = b[to - 2]
                b[to - 2] = 0
        if p == 6:
            self.wk = to
        elif p == -6:
            self.bk = to
        if abs(p) == 6:
            self.cr &= ~3 if c == 1 else ~12
        if f == 0 or to == 0:
            self.cr &= ~2
        if f == 7 or to == 7:
            self.cr &= ~1
        if f == 112 or to == 112:
            self.cr &= ~8
        if f == 119 or to == 119:
            self.cr &= ~4
        self.ep = (f + to) // 2 if abs(p) == 1 and abs(to - f) == 32 else -1
        self.c = -c
        return (cap, captured_sq, undo)

    def unmake(self, m, u):
        cap, captured_sq, undo = u
        self.c = -self.c
        f = m >> 7
        to = m & 127
        b = self.b
        p = b[to]
        b[to] = 0
        b[captured_sq] = cap
        b[f] = undo[5]
        if abs(p) == 6 and abs(to - f) == 2:
            if to > f:
                b[to + 1] = b[to - 1]
                b[to - 1] = 0
            else:
                b[to - 2] = b[to + 1]
                b[to + 1] = 0
        old_cap, old_ep, old_cr, old_wk, old_bk, old_p = undo
        self.ep = old_ep
        self.cr = old_cr
        self.wk = old_wk
        self.bk = old_bk

    def evaluate(self):
        """Static eval from the side-to-move's perspective."""
        b = self.b
        score = 0
        for sq in range(128):
            if sq & 0x88:
                continue
            p = b[sq]
            if p == 0:
                continue
            t = abs(p)
            rank = sq >> 4
            file = sq & 7
            idx = rank * 8 + file if p > 0 else (7 - rank) * 8 + file
            v = VAL[t] + PST[t][idx]
            score += v if p > 0 else -v
        return score * self.c

    def move_to_uci(self, m):
        f = m >> 7
        to = m & 127
        sq = lambda s: "abcdefgh"[s & 7] + str((s >> 4) + 1)
        promo = ""
        p = self.b[f]
        if abs(p) == 1 and (to >> 4 == 7 or to >> 4 == 0):
            promo = "q"
        return sq(f) + sq(to) + promo


# ---- search ----
class Search:
    def __init__(self, pos):
        self.pos = pos
        self.nodes = 0
        self.killers = {}

    def qsearch(self, alpha, beta, ply):
        self.nodes += 1
        p = self.pos
        stand = p.evaluate()
        if stand >= beta:
            return beta
        if stand > alpha:
            alpha = stand
        # generate captures only
        b = p.b
        c = p.c
        caps = []
        for m in p.gen():
            f = m >> 7
            to = m & 127
            tp = b[to]
            is_cap = tp != 0 and tp * c < 0
            is_ep = abs(b[f]) == 1 and (f & 7) != (to & 7) and tp == 0
            is_promo = abs(b[f]) == 1 and (to >> 4 == 7 or to >> 4 == 0)
            if is_cap or is_ep or is_promo:
                caps.append(m)
        caps.sort(key=lambda m: self.mvv(m), reverse=True)
        for m in caps:
            u = p.make(m)
            if p.in_check(c):
                p.unmake(m, u)
                continue
            score = -self.qsearch(-beta, -alpha, ply + 1)
            p.unmake(m, u)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def mvv(self, m):
        p = self.pos
        f = m >> 7
        to = m & 127
        victim = p.b[to]
        attacker = abs(p.b[f])
        if victim == 0 and attacker == 1 and (f & 7) != (to & 7):
            victim = 1  # ep
        return VAL[abs(victim)] * 16 - VAL[attacker]

    def negamax(self, depth, alpha, beta, ply):
        if depth <= 0:
            return self.qsearch(alpha, beta, ply)
        self.nodes += 1
        p = self.pos
        # check extension
        in_chk = p.in_check(p.c)
        if in_chk:
            depth += 1
        moves = p.gen()
        mover = p.c
        legal = []
        for m in moves:
            u = p.make(m)
            if not p.in_check(mover):
                legal.append(m)
            p.unmake(m, u)
        if not legal:
            return -MATE + ply if in_chk else 0
        # move ordering: captures first (mvv), then killers
        k0, k1 = self.killers.get(ply, (None, None))
        def order(m):
            is_cap = p.b[m & 127] != 0 or (abs(p.b[m >> 7]) == 1 and ((m >> 7) & 7) != (m & 127 & 7) and p.b[m & 127] == 0)
            if is_cap or (abs(p.b[m >> 7]) == 1 and (m & 127) >> 4 in (0, 7)):
                return (2, self.mvv(m))
            if m == k0:
                return (1, 0)
            if m == k1:
                return (1, 0)
            return (0, 0)
        legal.sort(key=order, reverse=True)
        best = -INF
        for m in legal:
            u = p.make(m)
            score = -self.negamax(depth - 1, -beta, -alpha, ply + 1)
            p.unmake(m, u)
            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                if not (p.b[m & 127] != 0):
                    self.killers[ply] = (m, k0)
                break
        return best

    def find_best(self, max_depth):
        p = self.pos
        best_move = None
        legal = []
        mover = p.c
        for m in p.gen():
            u = p.make(m)
            if not p.in_check(mover):
                legal.append(m)
            p.unmake(m, u)
        if not legal:
            return None
        # order root moves
        for depth in range(1, max_depth + 1):
            alpha = -INF
            local_best = None
            scored = []
            for m in legal:
                u = p.make(m)
                score = -self.negamax(depth - 1, -INF, -alpha, 1)
                p.unmake(m, u)
                scored.append((score, m))
                if score > alpha:
                    alpha = score
                    local_best = m
            scored.sort(reverse=True)
            legal = [m for _, m in scored]
            if local_best is not None:
                best_move = local_best
        return best_move


def sq_name(s):
    return "abcdefgh"[s & 7] + str((s >> 4) + 1)


def move_uci(pos, m):
    f = m >> 7
    to = m & 127
    promo = ""
    if abs(pos.b[f]) == 1 and (to >> 4 == 7 or to >> 4 == 0):
        promo = "q"
    return sq_name(f) + sq_name(to) + promo


if __name__ == "__main__":
    # quick self-test: play a few moves from start via python-chess to ensure legality
    import chess
    fen = chess.STARTING_FEN
    board = chess.Board()
    for i in range(6):
        pos = Pos(board.fen())
        s = Search(pos)
        bm = s.find_best(3)
        u = move_uci(pos, bm)
        print(f"move {i}: {u}  nodes={s.nodes}  eval={pos.evaluate()}")
        m = chess.Move.from_uci(u)
        assert m in board.legal_moves, f"engine produced illegal move {u}"
        board.push(m)
    print("self-play legal OK; final FEN:", board.fen())