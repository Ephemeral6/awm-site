"""Attempt-8 hypothesis H_contain (alternative to the budget reading of attempts 5/7):
 * a move WINS iff its target rectangle lies entirely inside the goal object (cap incl. 9 frame:
   rows 28-33, cols 57-61) -- consistent with all three past wins;
 * a 4x4 move whose target overlaps the goal object only partly is truncated: it advances one 2-px
   sub-step if that is free (attempts 5 and 7: cols 51-54 -> 53-56);
 * every action that STARTS at counter <= 18 resolves (attempt 6: full 4-px move at 18).
Everything else as model_l4b."""
import sys, heapq, os
sys.path.insert(0, os.path.dirname(__file__))
import model_l4 as M
import model_l4b as Q
B = 18
CAP = (28, 33, 57, 61)
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
def pix_rect(i, j, big):
    s = 4 if big else 2; r0, c0 = 2*i+1, 2*j+1
    return r0, r0+s-1, c0, c0+s-1
def contained(i, j, big):
    r0, r1, c0, c1 = pix_rect(i, j, big)
    return CAP[0] <= r0 and r1 <= CAP[1] and CAP[2] <= c0 and c1 <= CAP[3]
def overlaps(i, j, big):
    r0, r1, c0, c1 = pix_rect(i, j, big)
    return not (r1 < CAP[0] or r0 > CAP[1] or c1 < CAP[2] or c0 > CAP[3])
def step(s, a):
    i, j, big, face, door, picked = s
    if a[0] == 'move':
        d = a[1]; di, dj = DIRS[d]; k = 2 if big else 1
        ni, nj = i + di*k, j + dj*k
        if ni >= 0 and nj >= 0 and contained(ni, nj, big) and M.rect(ni, nj, 1 if big else 0, door) != 'B':
            return ('win', None, False)
        if ni >= 0 and nj >= 0 and overlaps(ni, nj, big):
            if big:   # truncated: one 2-px sub-step if free and not touching the goal
                hi, hj = i + di, j + dj
                if hi >= 0 and hj >= 0 and not overlaps(hi, hj, 1) and M.rect(hi, hj, 1, door) == 'F':
                    np_ = picked or Q.triggers(hi, hj, 1, d)
                    return ('st', (hi, hj, 1, d, door, int(np_)), bool(np_ and not picked))
            return ('st', (i, j, big, d, door, picked), False)
    t, s2, newly = Q.step(s, a)
    if t == 'win': return ('st', s, False) if a[0] != 'move' else (t, s2, newly)
    return (t, s2, newly)
def search(B=B):
    best = {Q.START: 0}; pq = [(0, Q.START, [])]
    while pq:
        u, s, path = heapq.heappop(pq)
        if best.get(s, 99) < u or u > B: continue
        for a in Q.ACTIONS:
            t, s2, newly = step(s, a)
            if t == 'win': return u, path + [a]
            v = Q.nu(u, a, newly)
            if v < best.get(s2, 99):
                best[s2] = v; heapq.heappush(pq, (v, s2, path + [a]))
    return None
if __name__ == '__main__':
    for Bv in (17, 18, 19, 20):
        print(Bv, search(Bv))
