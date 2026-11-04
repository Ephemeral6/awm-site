"""Generate the reachable-set certificate for lean/L4Macro.lean (loose grow: grown 4x4 only needs to stay on the 64x64 board)."""
import heapq
def walk(r, c, o):
    if 21 <= r <= 36 and 21 <= c <= 44: return True
    if 9 <= r <= 20 and 31 <= c <= 32: return True
    if o and 5 <= r <= 8 and 30 <= c <= 33: return True
    if 29 <= r <= 32 and 45 <= c <= 47: return o
    if 29 <= r <= 32 and 48 <= c <= 56: return True
    return False
def valid(y, x, s, o): return all(walk(r, c, o) for r in range(y, y+s) for c in range(x, x+s))
def hit(y, x, s): return any(28 <= r <= 33 and 57 <= c <= 62 for r in range(y, y+s) for c in range(x, x+s))
D = [(-1,0),(1,0),(0,-1),(0,1)]   # face 0=U 1=D 2=L 3=R ; actions 0..3 moves, 4 PLUS, 5 LINE
COST = [1,1,1,1,4,3]
def step(st, a):
    sm, o, y, x, f = st; s = 2 if sm else 4
    if a < 4:
        dr, dc = D[a]
        if hit(y+dr*s, x+dc*s, s): return 'WIN'
        d = 0
        for k in range(1, s+1):
            if valid(y+dr*k, x+dc*k, s, o): d = k
            else: break
        return (sm, o, y+dr*d, x+dc*d, a)
    if a == 4:
        if not sm: return (1, o, y, x, f)
        if y >= 2 and x >= 2 and y <= 62 and x <= 62: return (0, o, y-2, x-2, f)
        return st
    fire = 1 if (x == 31 and f == 0) else 0
    return (sm, o | fire, y, x, f)
def key(st): sm, o, y, x, f = st; return (((sm*2+o)*64+y)*64+x)*4+f
B = 19
s0 = (0, 0, 25, 37, 1)
dist = {s0: 0}; pq = [(0, s0)]
while pq:
    d, st = heapq.heappop(pq)
    if d > dist[st]: continue
    for a in range(6):
        n = step(st, a)
        if n == 'WIN':
            assert d + COST[a] > B, ('win within budget', d, st, a)
            continue
        nd = d + COST[a]
        if nd <= B and nd < dist.get(n, 99):
            dist[n] = nd; heapq.heappush(pq, (nd, n))
print('states within budget', len(dist))
keys = sorted(key(s) for s in dist)
packed = 0
for s, d in dist.items(): packed |= d << (5 * key(s))
mask = 0
for k in keys: mask |= 1 << k
open('work/cert_keys.txt','w').write(','.join(map(str, keys)))
open('work/cert_packed.txt','w').write(str(packed))
open('work/cert_mask.txt','w').write(str(mask))
print('packed digits', len(str(packed)), 'mask digits', len(str(mask)))
