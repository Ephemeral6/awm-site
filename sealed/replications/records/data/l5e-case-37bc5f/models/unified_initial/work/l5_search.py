"""Cheapest-win search for level 5 under the rules established through attempt 4.

Rules simulated (all from observation; see concepts/ and work/objects.md):
  move: up to `size` cells in the direction, as far as the target square stays on floor (granularity G);
        0 cells -> blocked, but the block still turns to face the direction (blocked_turn). Cost 1.
        a target square touching the socket interior wins.
  refill: a 4x4 or 2x2 whose square contains the unused 14-pad aligned to its 2x2 sub-grid consumes it: -10 units.
  macros (panel starts empty after every fire; clicks needed = recipe cells, firing click costs 2):
        shrink/grow (plus ring) 5 units; vline 4; teleport 4.
  grow: top = t-2, first col of l-2, l-1, l whose 4x4 fits the floor; else nothing.
  open: vertical box: facing up, col == stalk col, row == stalk bottom + 1;
        horizontal box: facing right, row == stalk top, col + size == stalk left col.
  teleport: 2x2 -> (37,15), 4x4 -> (17,33).
  budget: B = 35 units; an action may be sent only while used < 35 (display > 0).
Usage: python work/l5_search.py [G]
"""
import heapq
import sys

G = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def inR(lo, x, hi):
    return lo <= x <= hi


def floor(g0, g1, r, c):
    return ((inR(25, r, 40) and inR(13, c, 28)) or (inR(13, r, 24) and inR(21, c, 22))
            or (g0 and inR(33, r, 36) and inR(29, c, 31)) or (inR(33, r, 36) and inR(32, c, 36))
            or (inR(25, r, 40) and inR(37, c, 52)) or (inR(21, r, 24) and inR(45, c, 46))
            or (inR(15, r, 20) and inR(41, c, 48)) or (inR(15, r, 16) and inR(49, c, 54))
            or (inR(14, r, 20) and inR(33, c, 36)) or (g1 and inR(11, r, 13) and inR(33, c, 36))
            or (inR(5, r, 10) and inR(33, c, 36))
            # opened box areas become floor (observed on L4/L5)
            or (g0 and inR(9, r, 12) and inR(20, c, 23)) or (g1 and inR(14, r, 17) and inR(55, c, 58)))


def goal(r, c):
    return inR(1, r, 4) and inR(33, c, 36)


def sq(r, c, s):
    return [(r + i, c + j) for i in range(s) for j in range(s)]


def fits(g0, g1, r, c, s):
    return r >= 0 and c >= 0 and all(floor(g0, g1, a, b) for a, b in sq(r, c, s))


DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
PAD = (37, 49)


def move(st, d):
    r, c, s, f, g0, g1, pad = st
    dr, dc = DIRS[d]
    best = None
    for k in range(G, s + 1, G):
        nr, nc = r + dr * k, c + dc * k
        if nr < 0 or nc < 0:
            break
        if any(goal(a, b) for a, b in sq(nr, nc, s)):
            return (nr, nc, s, d, g0, g1, pad), True
        if fits(g0, g1, nr, nc, s):
            best = (nr, nc)
        else:
            break
    if best is None:
        return (r, c, s, d, g0, g1, pad), False
    nr, nc = best
    gain = 0
    if not pad and (PAD[0] - nr) % 2 == 0 and (PAD[1] - nc) % 2 == 0 \
            and nr <= PAD[0] <= nr + s - 2 and nc <= PAD[1] <= nc + s - 2:
        pad = True
        gain = 10
    return (nr, nc, s, d, g0, g1, pad), gain


def oc_vert(st, row, col):
    r, c, s, f = st[:4]
    return f == 'U' and c == col and r == row + 1


def oc_horiz(st, row, col):
    r, c, s, f = st[:4]
    return f == 'R' and r == row and c + s == col


def macros(st):
    r, c, s, f, g0, g1, pad = st
    out = []
    if s == 4:
        out.append(('shrink', 5, (r, c, 2, f, g0, g1, pad)))
    else:
        for cc in (c - 2, c - 1, c):
            if r >= 2 and cc >= 0 and fits(g0, g1, r - 2, cc, 4):
                out.append(('grow', 5, (r - 2, cc, 4, f, g0, g1, pad)))
                break
    ng0 = g0 or oc_vert(st, 24, 21)
    ng1 = g1 or oc_horiz(st, 15, 49)
    if (ng0, ng1) != (g0, g1):
        out.append(('vline', 4, (r, c, s, f, ng0, ng1, pad)))
    tr, tc = (37, 15) if s == 2 else (17, 33)
    out.append(('tp', 4, (tr, tc, s, f, g0, g1, pad)))
    return out


def search(start, B=35):
    # Dijkstra on net units used; actions only while used < B
    pq = [(0, 0, start, ())]
    seen = {}
    while pq:
        u, _, st, path = heapq.heappop(pq)
        if seen.get(st, 99) <= u:
            continue
        seen[st] = u
        for d in 'UDLR':
            if u >= B:
                break
            nst, res = move(st, d)
            if res is True:
                return u + 1, path + (d,)
            nu = u + 1 - (res if res else 0)
            heapq.heappush(pq, (nu, len(path) + 1, nst, path + (d,)))
        for name, cost, nst in macros(st):
            # a macro is several clicks; each must be sent while used < B
            if u + cost - 2 >= B:
                continue
            heapq.heappush(pq, (u + cost, len(path) + 1, nst, path + (name,)))
    return None


if __name__ == '__main__':
    start = (29, 17, 4, 'D', False, False, False)
    res = search(start, B=10 ** 6)
    print('G =', G, 'cheapest win (units, unbounded budget):', res[0] if res else None)
    if res:
        print(' '.join(res[1]))
