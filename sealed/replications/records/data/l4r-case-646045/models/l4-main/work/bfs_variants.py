import heapq
exec(open('work/gen_cert.py').read().split("def step(st, a)")[0])
D = [(-1,0),(1,0),(0,-1),(0,1)]
def run(free_shrink, free_grow, B=40):
    def nexts(st):
        sm, o, y, x, f = st; s = 2 if sm else 4
        for a in range(4):
            dr, dc = D[a]
            if hit(y+dr*s, x+dc*s, s): yield 1, 'WIN'; continue
            d = 0
            for k in range(1, s+1):
                if valid(y+dr*k, x+dc*k, s, o): d = k
                else: break
            yield 1, (sm, o, y+dr*d, x+dc*d, a)
        if not sm:
            offs = [(0,0),(0,2),(2,0),(2,2)] if free_shrink else [(0,0)]
            for oy, ox in offs: yield 4, (1, o, y+oy, x+ox, f)
        else:
            offs = [(0,0),(0,-2),(-2,0),(-2,-2)] if free_grow else [(-2,-2)]
            for oy, ox in offs:
                if 0 <= y+oy <= 60 and 0 <= x+ox <= 60: yield 4, (0, o, y+oy, x+ox, f)
        yield 3, (sm, o | (1 if (x == 31 and f == 0) else 0), y, x, f)
    s0 = (0, 0, 25, 37, 1); dist = {s0: 0}; pq = [(0, s0)]
    while pq:
        d, st = heapq.heappop(pq)
        if d > dist[st] or d > B: continue
        for c, n in nexts(st):
            if n == 'WIN': return d + c
            if d + c < dist.get(n, 999): dist[n] = d + c; heapq.heappush(pq, (d + c, n))
for fs in (False, True):
    for fg in (False, True):
        print('free_shrink', fs, 'free_grow', fg, 'min actions', run(fs, fg))
