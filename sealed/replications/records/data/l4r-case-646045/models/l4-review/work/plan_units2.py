import heapq
exec(open('work/gen_cert.py').read().split("def step(st, a)")[0])
D = [(-1,0),(1,0),(0,-1),(0,1)]; NAMES = ['U','D','L','R','PLUS','LINE']
def ov(y, x, h, w): return any(34 <= r <= 35 and 23 <= c <= 24 for r in range(y, y+h) for c in range(x, x+w))
def run(PICK, MODE, WINNEG=False):
    # state: (sm,o,y,x,f,capTotal) capTotal=18 until pickup
    s0 = (0, 0, 25, 37, 1, 18); dist = {s0: 0}; par = {}; pq = [(0, s0)]; best = None
    while pq:
        d, st = heapq.heappop(pq)
        if d > dist[st]: continue
        sm, o, y, x, f, cap = st; s = 2 if sm else 4
        cand = []
        for a in range(4):
            dr, dc = D[a]
            if hit(y+dr*s, x+dc*s, s): cand.append((a, 1, 'WIN')); continue
            k0 = 0
            for k in range(1, s+1):
                if valid(y+dr*k, x+dc*k, s, o): k0 = k
                else: break
            ny, nx = y+dr*k0, x+dc*k0; h = s // 2
            fr = ov(*((ny, nx, h, s) if a == 0 else (ny+h, nx, h, s) if a == 1 else (ny, nx, s, h) if a == 2 else (ny, nx+h, s, h)))
            pk = (sm and ov(ny, nx, 2, 2)) or (PICK == 'front' and fr)
            ncap = cap
            if pk and cap == 18:
                ncap = 28 if MODE == 'add' else (d + 1 + 12)
            cand.append((a, 1, (sm, o, ny, nx, a, ncap)))
        if not sm: cand.append((4, 5, (1, o, y, x, f, cap)))
        elif y >= 2 and x >= 2: cand.append((4, 5, (0, o, y-2, x-2, f, cap)))
        cand.append((5, 4, (sm, o | (1 if (x == 31 and f == 0) else 0), y, x, f, cap)))
        for a, c, n in cand:
            if n == 'WIN':
                if d + c <= cap + (1 if WINNEG else 0) and (best is None or d + c < best[0]): best = (d + c, st, a)
                continue
            if d + c > n[5]: continue
            if d + c < dist.get(n, 999): dist[n] = d + c; par[n] = (st, a); heapq.heappush(pq, (d + c, n))
    if not best: return None
    st = best[1]; path = [NAMES[best[2]]]
    while st in par: st, a = par[st]; path.append(NAMES[a])
    return best[0], list(reversed(path))
for pick in ('small', 'front'):
    for mode in ('add', 'set12'):
        for wn in (False, True):
            print(pick, mode, 'winneg' if wn else '', run(pick, mode, wn))
