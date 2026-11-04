import heapq, sys
import fast
from rules import initial
from search2 import *
def runp(coll, acts):
    s0 = fast.totuple(initial())
    dist = {s0: 0}; par = {s0: None}; pq = [(0, s0)]; best = None
    while pq:
        d, t = heapq.heappop(pq)
        if d > dist[t]: continue
        if best is not None and d > best[0]: break
        for a in acts:
            n, cost, credit, win = fast.step(t, a, coll)
            if win:
                v = d + (10 if t[6] else 0)
                if best is None or v < best[0]: best = (v, t, a)
                continue
            if not (0 <= n[0] <= 60 and 10 <= n[1] <= 60): continue
            nd = d + cost
            if nd < dist.get(n, 10**9):
                dist[n] = nd; par[n] = (t, a); heapq.heappush(pq, (nd, n))
    v, t, a = best; path = [(a, None)]
    while par[t]: p, pa = par[t]; path.append((pa, t)); t = p
    return v, path[::-1]
if __name__=='__main__':
  ACT_OBS = [a for a in fast.ACTS if not (a[0]=='shrink' and a[1]!=(0,0)) and not (a[0]=='grow' and a[1]!=(2,2))]
  v, p = runp(sys.argv[1], ACT_OBS if sys.argv[2]=='obs' else fast.ACTS)
  print(v)
  for a, t in p: print(a, t)
