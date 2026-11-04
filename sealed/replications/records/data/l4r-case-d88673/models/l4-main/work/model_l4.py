"""Abstract model of level 4 (lattice of 2x2-pixel cells, macro panel actions).
Same semantics as lean/L4Model.lean. Run: python work/model_l4.py"""
import json, sys
from pathlib import Path
H = Path(__file__).resolve().parent
F = json.load(open(H / "l4_start.json"))
PLAYER = {(y, x) for y in range(25, 29) for x in range(37, 41)}

def pix(y, x, door_open):
    if not (0 <= y < 64 and 0 <= x < 64): return "B"
    if (y, x) in PLAYER: return "F"
    c = F[y][x]
    if c == 13 and 29 <= y <= 32 and 45 <= x <= 47:
        return "F" if door_open else "B"
    if c in (9, 10): return "G"
    if c in (2, 14) and 10 <= x <= 61 and y <= 46: return "F"
    return "B"

def cell(i, j, door):
    if not (0 <= i < 32 and 0 <= j < 32): return "B"
    ps = {pix(2*i+1+a, 2*j+1+b, door) for a in (0, 1) for b in (0, 1)}
    return "B" if "B" in ps else ("G" if "G" in ps else "F")

def box_pix(y, x): return 5 <= y <= 8 and 30 <= x <= 33
def cell_box(i, j): return any(box_pix(2*i+1+a, 2*j+1+b) for a in (0, 1) for b in (0, 1))
def shot_hits(jp, i):
    for k in range(i - 1, -1, -1):
        if cell_box(k, jp): return True
        if C(k, jp, 0) == "B": return False
    return False

CELL = {(i, j, d): cell(i, j, d) for i in range(-2, 34) for j in range(-2, 34) for d in (0, 1)}
def C(i, j, d): return CELL.get((i, j, d), "B")

def rect(i, j, sz, d):
    cs = [(i, j)] if sz == 0 else [(i, j), (i+1, j), (i, j+1), (i+1, j+1)]
    ks = {C(a, b, d) for a, b in cs}
    return "B" if "B" in ks else ("G" if "G" in ks else "F")

DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}  # up down left right
ACTIONS = [("move", k) for k in range(4)] + [("resize", q) for q in range(4)] + [("fire", 0)]
COST = {"move": 1, "resize": 5, "fire": 4}  # attempt 2: unit model, completion +1

def step(s, a):
    """returns ('win', None) or ('st', s')"""
    i, j, sz, up, door = s
    kind, p = a
    if kind == "move":
        di, dj = DIRS[p]; k = 1 if sz == 0 else 2
        ni, nj = i + di*k, j + dj*k
        r = rect(ni, nj, sz, door)
        nup = 1 if p == 0 else 0
        if r == "G": return ("win", None)
        if r == "F" and 0 <= ni < 32 and 0 <= nj < 32: return ("st", (ni, nj, sz, nup, door))
        return ("st", (i, j, sz, nup, door))
    if kind == "resize":
        qi, qj = p // 2, p % 2
        if sz == 1:
            return ("st", (i+qi, j+qj, 0, up, door)) if (i+qi < 32 and j+qj < 32) else ("st", s)
        ni, nj = i - qi, j - qj
        if ni < 0 or nj < 0: return ("st", s)
        r = rect(ni, nj, 1, door)
        if r == "G": return ("win", None)
        if r == "F": return ("st", (ni, nj, 1, up, door))
        return ("st", s)
    # fire (attempt 2): projectile in lattice column j (2x2: its column; 4x4: its LEFT column),
    # moves up from row i-1; hits box -> door opens; hits any other blocked cell -> destroyed.
    if up == 1 and door == 0 and shot_hits(j, i):
        return ("st", (i, j, sz, up, 1))
    return ("st", s)

STATES = [(i, j, sz, up, d) for i in range(32) for j in range(32) for sz in (0, 1) for up in (0, 1) for d in (0, 1)]
def key(s):
    i, j, sz, up, d = s
    return (((i*32 + j)*2 + sz)*2 + up)*2 + d

CAP = 63
def dist():
    d = {s: CAP for s in STATES}
    changed = True
    while changed:
        changed = False
        for s in STATES:
            best = d[s]
            for a in ACTIONS:
                t, s2 = step(s, a)
                v = COST[a[0]] + (0 if t == "win" else d[s2])
                if v < best: best = v
            if best < d[s]:
                d[s] = best; changed = True
    return d

START = (12, 18, 1, 0, 0)
if __name__ == "__main__":
    for i in range(0, 20):
        print("".join(C(i, j, 0) for j in range(32)))
    d = dist()
    print("d(start) =", d[START])
    print("d(start, door already open) =", d[(12, 18, 1, 0, 1)])
    print("d(start as 2x2 at same spot) =", d[(12, 18, 0, 0, 0)])
    # encode table: 6 bits per key
    H_ = 0
    for s in STATES: H_ |= d[s] << (6*key(s))
    (H / "l4_dist.txt").write_text(str(H_))
    print("table bits", H_.bit_length())
