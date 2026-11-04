"""Attempt-5 amendment: the action that starts at counter u = B (=18, the last affordable unit).
Observed: a 4x4 move starting at 18 advanced only 2 px (one sub-step) and the game ended (tid c20aa696def56d6b);
2x2 moves starting at 18 advanced their full 2 px (attempts 1, 3, 4). Unknown, taken GENEROUSLY:
  * the half-step of a 4x4 at u = 18 wins if its (half-advanced) rectangle reaches the goal;
  * any panel click / completion starting at u <= 18 resolves (macros: generous, may START at <= 18).
Everything else as model_l4b (rules of attempts 1-4)."""
import sys, heapq, os
sys.path.insert(0, os.path.dirname(__file__))
import model_l4 as M
import model_l4b as Q
B = 18
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}

def half_move_wins(s, d):
    i, j, big, face, door, picked = s
    di, dj = DIRS[d]
    ni, nj = i + di, j + dj          # one lattice cell = 2 px
    if ni < 0 or nj < 0: return False
    return M.rect(ni, nj, 1, door) == "G"

def search(B=B, half_rule=True):
    best = {Q.START: 0}; pq = [(0, Q.START, [])]
    while pq:
        u, s, path = heapq.heappop(pq)
        if best.get(s, 99) < u or u > B: continue
        for a in Q.ACTIONS:
            if u == B and half_rule and a[0] == 'move' and s[2] == 1:
                if half_move_wins(s, a[1]): return u, path + [a]
                continue                      # game ends after it anyway
            t, s2, newly = Q.step(s, a)
            if t == 'win': return u, path + [a]
            if u == B: continue               # game over after this action
            v = Q.nu(u, a, newly)
            if v < best.get(s2, 99):
                best[s2] = v; heapq.heappush(pq, (v, s2, path + [a]))
    return None
if __name__ == '__main__':
    print('attempt-5 rule, cap 18:', search())
    print('no half rule (attempt-4 model), cap 18:', search(half_rule=False))
