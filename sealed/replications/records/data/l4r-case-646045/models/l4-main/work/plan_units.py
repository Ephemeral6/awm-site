"""Exact budget model (attempt 6 fit): bar = 18 units, plain action 1, commit click 2 (PLUS = 3+2 = 5, LINE = 2+2 = 4),
e pickup +10, GAME_OVER iff remaining < 0 after an action. Pickup rule chosen by PICK."""
import heapq, sys
exec(open('work/gen_cert.py').read().split("def step(st, a)")[0])
D = [(-1,0),(1,0),(0,-1),(0,1)]; NAMES = ['U','D','L','R','PLUS','LINE']
def ov(y, x, h, w): return any(34 <= r <= 35 and 23 <= c <= 24 for r in range(y, y+h) for c in range(x, x+w))
def run(PICK, WIN_AT_NEG=False):
    def nexts(st):
        sm, o, y, x, f, e = st; s = 2 if sm else 4
        for a in range(4):
            dr, dc = D[a]
            if hit(y+dr*s, x+dc*s, s): yield a, 1, 'WIN'; continue
            d = 0
            for k in range(1, s+1):
                if valid(y+dr*k, x+dc*k, s, o): d = k
                else: break
            ny, nx = y+dr*d, x+dc*d; h = s // 2
            front = ov(*((ny, nx, h, s) if a == 0 else (ny+h, nx, h, s) if a == 1 else (ny, nx, s, h) if a == 2 else (ny, nx+h, s, h)))
            pick = (sm and ov(ny, nx, 2, 2)) if PICK == 'small' else (front or (sm and ov(ny, nx, 2, 2))) if PICK == 'front' else ov(ny, nx, s, s)
            yield a, 1, (sm, o, ny, nx, a, e or pick)
        if not sm: yield 4, 5, (1, o, y, x, f, e)
        elif y >= 2 and x >= 2: yield 4, 5, (0, o, y-2, x-2, f, e)
        yield 5, 4, (sm, o | (1 if (x == 31 and f == 0) else 0), y, x, f, e)
    s0 = (0, 0, 25, 37, 1, False); dist = {s0: 0}; par = {}; pq = [(0, s0)]; best = None
    while pq:
        d, st = heapq.heappop(pq)
        if d > dist[st]: continue
        cap = 18 + (10 if st[5] else 0)
        for a, c, n in nexts(st):
            lim = cap + (1 if WIN_AT_NEG and n == 'WIN' else 0)
            if d + c > lim: continue
            if n == 'WIN':
                if best is None or d + c < best[0]: best = (d + c, st, a)
                continue
            if d + c < dist.get(n, 999): dist[n] = d + c; par[n] = (st, a); heapq.heappush(pq, (d + c, n))
    if not best: return None
    st = best[1]; path = [NAMES[best[2]]]
    while st in par: st, a = par[st]; path.append(NAMES[a])
    return best[0], list(reversed(path))
for pick in ('small', 'front', 'any'):
    for wn in (False, True):
        print(pick, 'win-at-minus-1' if wn else '', run(pick, wn))
