"""Validate 0x88 movegen + make/unmake via perft against python-chess (dev only)."""
import sys
import chess
from engine import Pos

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
POS3 = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
POS4 = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
POS5 = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"


def legal_moves(p):
    """Legal moves from the engine's Pos as (from,to) tuples."""
    res = []
    for m in p.gen():
        u = p.make(m)
        if not p.in_check(-p.c):  # after make, side to move is -c; mover was p.c... 
            # mover is the side that just moved = -p.c (since make flipped). Check that mover's king safe.
            res.append((m >> 7, m & 127))
        p.unmake(m, u)
    return res


def engine_legal(p):
    mover = p.c
    res = []
    for m in p.gen():
        u = p.make(m)
        if not p.in_check(mover):
            res.append(m)
        p.unmake(m, u)
    return res


def perft_engine(p, depth):
    if depth == 0:
        return 1
    mover = p.c
    nodes = 0
    for m in p.gen():
        u = p.make(m)
        if not p.in_check(mover):
            nodes += perft_engine(p, depth - 1)
        p.unmake(m, u)
    return nodes


def move_to_uci(m):
    f, to = m >> 7, m & 127
    sq = lambda s: "abcdefgh"[s & 7] + str((s >> 4) + 1)
    return sq(f) + sq(to)


def engine_uci_set(p):
    mover = p.c
    out = set()
    for m in p.gen():
        u = p.make(m)
        if not p.in_check(mover):
            s = move_to_uci(m)
            out.add(s[:4])  # engine promotes to queen only; compare on from+to
        p.unmake(m, u)
    return out


def ref_uci_set(board):
    out = set()
    for m in board.legal_moves:
        if m.promotion is not None and m.promotion != chess.QUEEN:
            continue
        out.add(m.uci()[:4])
    return out


def ref_perft(board, depth):
    if depth == 0:
        return 1
    nodes = 0
    for m in board.legal_moves:
        # engine only ever promotes to queen; mirror that so counts are comparable
        if m.promotion is not None and m.promotion != chess.QUEEN:
            continue
        board.push(m)
        nodes += ref_perft(board, depth - 1)
        board.pop()
    return nodes


def compare(name, fen, depths=(1, 2, 3)):
    print(f"\n=== {name} ===")
    print("FEN:", fen)
    for d in depths:
        p = Pos(fen)
        eng = perft_engine(p, d)
        board = chess.Board(fen)
        ref = ref_perft(board, d)
        ok = "OK" if eng == ref else "MISMATCH"
        print(f"  depth {d}: engine={eng}  ref={ref}  {ok}")
        if eng != ref:
            return False
    return True


def compare_movegen(name, fen):
    p = Pos(fen)
    eng = engine_uci_set(p)
    ref = ref_uci_set(chess.Board(fen))
    if eng == ref:
        print(f"  movegen {name}: OK ({len(eng)} moves)")
        return True
    else:
        print(f"  movegen {name}: MISMATCH")
        print("    engine-only:", sorted(eng - ref))
        print("    ref-only:   ", sorted(ref - eng))
        return False


if __name__ == "__main__":
    allok = True
    for name, fen in [("start", START), ("kiwipete", KIWIPETE), ("pos3", POS3),
                      ("pos4", POS4), ("pos5", POS5)]:
        allok &= compare(name, fen, (1, 2, 3))
        allok &= compare_movegen(name, fen)
    print("\nALL OK" if allok else "\nFAILURES PRESENT")