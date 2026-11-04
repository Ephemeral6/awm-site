"""Hypothesis H_sub (untested against walls): a move advances as many 2-px sub-steps (max 2 for 4x4,
1 for 2x2) as are free; it stops before a blocked sub-step (consistent with every observed move:
the only half-free cases, attempts 5/7, advanced 2 px). Goal variants:
  'touch18'  : touching the goal wins, except an action starting at counter 18 cannot win
  'contain'  : a sub-step into the goal object counts only if fully inside it (else blocked)."""
import sys, heapq, os
sys.path.insert(0, os.path.dirname(__file__))
import model_l4 as M, model_l4b as Q, model_l4d as D
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
def move(s, d, goal, u):
    i, j, big, face, door, picked = s
    di, dj = DIRS[d]; n = 2 if big else 1
    ci, cj = i, j; win = False
    for _ in range(n):
        ni, nj = ci + di, cj + dj
        if ni < 0 or nj < 0: break
        r = M.rect(ni, nj, big, door)
        if r == 'B': break
        if D.overlaps(ni, nj, big):
            if goal == 'contain':
                if D.contained(ni, nj, big): win = True
                break
            else:
                if u < 18: win = True
                break
        ci, cj = ni, nj
    if win: return ('win', None, False)
    np_ = picked or Q.triggers(ci, cj, big, d)
    return ('st', (ci, cj, big, d, door, int(np_)), bool(np_ and not picked))
def search(goal, B=18):
    best = {Q.START: 0}; pq = [(0, Q.START, [])]
    while pq:
        u, s, path = heapq.heappop(pq)
        if best.get(s, 99) < u or u > B: continue
        for a in Q.ACTIONS:
            if a[0] == 'move': t, s2, newly = move(s, a[1], goal, u)
            else:
                t, s2, newly = Q.step(s, a)
                if t == 'win': continue
            if t == 'win': return u, path + [a]
            v = Q.nu(u, a, newly)
            if v < best.get(s2, 99):
                best[s2] = v; heapq.heappush(pq, (v, s2, path + [a]))
    return None
if __name__ == '__main__':
    for goal in ('touch18', 'contain'):
        print(goal, search(goal))
