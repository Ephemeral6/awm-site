"""Exact BFS on the level-4 macro model (attempt 4 knowledge). Pixel geometry read off the L4 frame."""
from collections import deque
import itertools, sys
LOOSE_GROW = len(sys.argv) > 1 and sys.argv[1] == 'loose'

def walk(r, c, opened):
    if 21 <= r <= 36 and 21 <= c <= 44: return True          # region
    if 9 <= r <= 20 and 31 <= c <= 32: return True           # stem
    if opened and 5 <= r <= 8 and 30 <= c <= 33: return True # former 6-box
    if 29 <= r <= 32 and 45 <= c <= 47: return opened        # door
    if 29 <= r <= 32 and 48 <= c <= 56: return True          # corridor
    return False

def valid(y, x, s, opened):
    return all(walk(r, c, opened) for r in range(y, y+s) for c in range(x, x+s))

def goalhit(y, x, s):
    return any(28 <= r <= 33 and 57 <= c <= 62 for r in range(y, y+s) for c in range(x, x+s))

D = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
def step(st, a):
    small, opened, y, x, face = st
    s = 2 if small else 4
    if a in D:
        dr, dc = D[a]
        if goalhit(y+dr*s, x+dc*s, s): return 'WIN'
        d = 0
        for k in range(1, s+1):
            if valid(y+dr*k, x+dc*k, s, opened): d = k
            else: break
        return (small, opened, y+dr*d, x+dc*d, a)
    if a == 'PLUS':
        if not small: return (True, opened, y, x, face)
        ny, nx = y-2, x-2
        if not LOOSE_GROW and not valid(ny, nx, 4, opened): return st   # grow blocked (assumption)
        return (False, opened, ny, nx, face)
    if a == 'LINE':
        fire = (x == 31 and face == 'U')
        return (small, opened or fire, y, x, face)
COST = {'U':1,'D':1,'L':1,'R':1,'PLUS':4,'LINE':3}
s0 = (False, False, 25, 37, 'D')
import heapq
dist = {s0: 0}; pq = [(0, s0)]; best = None; par = {}
while pq:
    d, st = heapq.heappop(pq)
    if d > dist.get(st, 1e9): continue
    for a, c in COST.items():
        nx = step(st, a)
        if nx == 'WIN':
            if best is None or d + c < best[0]: best = (d + c, st, a)
            continue
        if d + c < dist.get(nx, 1e9):
            dist[nx] = d + c; par[nx] = (st, a); heapq.heappush(pq, (d + c, nx))
print('states', len(dist), 'min actions to win', best[0])
st = best[1]; path = [best[2]]
while st in par: st, a = par[st]; path.append(a)
print(list(reversed(path)))
