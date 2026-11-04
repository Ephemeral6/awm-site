import heapq
exec(open('work/gen_cert.py').read().split("def step(st, a)")[0])
D = [(-1,0),(1,0),(0,-1),(0,1)]
NAMES = ['U','D','L','R','PLUS','LINE']
REFILL = 64
def overlaps_e(y, x, s): return any(34 <= r <= 35 and 23 <= c <= 24 for r in range(y, y+s) for c in range(x, x+s))
def nexts(st):
    sm, o, y, x, f, e = st; s = 2 if sm else 4
    for a in range(4):
        dr, dc = D[a]
        if hit(y+dr*s, x+dc*s, s): yield a, 7, 'WIN'; continue
        d = 0
        for k in range(1, s+1):
            if valid(y+dr*k, x+dc*k, s, o): d = k
            else: break
        ny, nx = y+dr*d, x+dc*d
        ne = e or (sm and overlaps_e(ny, nx, 2))
        yield a, 7, (sm, o, ny, nx, a, ne)
    if not sm: yield 4, 35, (1, o, y, x, f, e)
    elif y >= 2 and x >= 2: yield 4, 35, (0, o, y-2, x-2, f, e)
    yield 5, 28, (sm, o | (1 if (x == 31 and f == 0) else 0), y, x, f, e)
s0 = (0, 0, 25, 37, 1, False)
dist = {s0: 0}; par = {}; pq = [(0, s0)]; best = None
while pq:
    d, st = heapq.heappop(pq)
    if d > dist[st]: continue
    cap = 128 + (REFILL if st[5] else 0)
    if d >= cap: continue
    for a, c, n in nexts(st):
        if n == 'WIN':
            if best is None or d + c < best[0]: best = (d + c, st, a)
            continue
        if d + c < dist.get(n, 10**9):
            dist[n] = d + c; par[n] = (st, a); heapq.heappush(pq, (d + c, n))
print('states', len(dist), 'best', best and best[0])
if best:
    st = best[1]; path = [NAMES[best[2]]]
    while st in par: st, a = par[st]; path.append(NAMES[a])
    path.reverse(); print(len(path), path)
