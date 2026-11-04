"""Attempt-3 amendment of model_l4: facing (4 values), e-marker pickup flag, counter u with refill.
Generous on every unknown:
  pickup trigger = player is 2x2 and overlaps e  OR  player's front half overlaps e   (union of hypotheses)
  refill         = u := min(7, max(0, u - 10))                                       (lower of 'set 7' / 'minus 10')
  any action (incl. a whole macro) may START when u <= 18; a win counts even if it overshoots.
Established and enforced: shrink keeps top-left; grow keeps the bottom row and extends right if free,
else left (both observed); only when both are walled may grow pick any free placement (never observed)."""
import sys, heapq
sys.path.insert(0, __import__('os').path.dirname(__file__))
import model_l4 as M
B = 18
E = {(34, 23), (34, 24), (35, 23), (35, 24)}
COST = {"move": 1, "resize": 5, "fire": 4}
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}  # face codes: 0 up 1 down 2 left 3 right

def pcells(i, j, big, face):
    s = 4 if big else 2; r0, c0 = 2*i+1, 2*j+1; h = s // 2
    allc = {(r0+a, c0+b) for a in range(s) for b in range(s)}
    fr = {0: {(r0+a, c0+b) for a in range(h) for b in range(s)},
          1: {(r0+h+a, c0+b) for a in range(h) for b in range(s)},
          2: {(r0+a, c0+b) for a in range(s) for b in range(h)},
          3: {(r0+a, c0+h+b) for a in range(s) for b in range(h)}}[face]
    return allc, fr

def triggers(i, j, big, face):
    # attempt 4: a 4x4 picks up with its FRONT half (observed); a 2x2 with any overlap (observed facing left;
    # its 1-px front vs whole body not separated -> body, the looser reading)
    allc, fr = pcells(i, j, big, face)
    return bool((not big and allc & E) or (big and fr & E))

def free4(i, j, door):
    return i >= 0 and j >= 0 and M.rect(i, j, 1, door) != "B"

def step(s, a):
    """s = (i,j,big,face,door,picked). returns ('win',None) or ('st', s', newly_picked)"""
    i, j, big, face, door, picked = s
    kind, p = a
    if kind == "move":
        # attempt 8: moves advance in 2-px sub-steps as far as free (tid ece0a2f5605e3199)
        di, dj = DIRS[p]; k = 2 if big else 1
        ni, nj = i, j
        fi, fj = i + di*k, j + dj*k
        if fi >= 0 and fj >= 0 and M.rect(fi, fj, big, door) != "B":
            if M.rect(fi, fj, big, door) == "G": return ("win", None, False)
            ni, nj = fi, fj
        elif big:
            hi, hj = i + di, j + dj
            if hi >= 0 and hj >= 0 and M.rect(hi, hj, 1, door) != "B":
                if M.rect(hi, hj, 1, door) == "G": return ("win", None, False)
                ni, nj = hi, hj
        nface = p
    elif kind == "resize":
        if big:
            if p != 0: return ("st", s, False)
            ni, nj, nbig, nface = i, j, 0, face
            nb = False
        else:
            # attempt 4: grow extends UP and LEFT unless walled (3 observations); right only if left walled
            if free4(i-1, j-1, door): cands = [(i-1, j-1)]
            elif free4(i-1, j, door): cands = [(i-1, j)]
            else: cands = [(i-qi, j-qj) for qi in (0, 1) for qj in (0, 1)]
            qi, qj = p // 2, p % 2
            if (i-qi, j-qj) not in cands: return ("st", s, False)
            ni, nj = i-qi, j-qj
            if ni < 0 or nj < 0: return ("st", s, False)
            r = M.rect(ni, nj, 1, door)
            if r == "G": return ("win", None, False)
            if r == "B": return ("st", s, False)
        nbig = 1 - big; nface = face
        np_ = picked or triggers(ni, nj, nbig, nface)
        return ("st", (ni, nj, nbig, nface, door, int(np_)), np_ and not picked)
    else:
        t, s2 = M.step((i, j, big, 1 if face == 0 else 0, door), ("fire", 0))
        return ("st", (i, j, big, face, s2[4], picked), False)
    nbig = big
    np_ = picked or triggers(ni, nj, nbig, nface)
    return ("st", (ni, nj, nbig, nface, door, int(np_)), np_ and not picked)

ACTIONS = M.ACTIONS
def nu(u, a, newly):
    v = u + COST[a[0]]
    return max(0, v - 10) if newly else v   # attempt 4: refill = minus 10 (15 -> 5 observed)

START = (12, 18, 1, 1, 0, 0)

def min_peak():
    """Dijkstra on u: smallest counter with which each state can be reached; win reachable iff some
    winning action starts with u <= B."""
    best = {START: 0}; pq = [(0, START, [])]
    while pq:
        u, s, path = heapq.heappop(pq)
        if best.get(s, 99) < u: continue
        if u > B: continue
        for a in ACTIONS:
            t, s2, newly = step(s, a)
            if t == "win": return path + [a]
            v = nu(u, a, newly)
            if v < best.get(s2, 99):
                best[s2] = v; heapq.heappush(pq, (v, s2, path + [a]))
    return None

if __name__ == "__main__":
    print("win under generous union, cap 18:", min_peak())
    for Bv in range(19, 30):
        B = Bv
        r = min_peak()
        if r: print("smallest cap admitting a win:", Bv, r); break
