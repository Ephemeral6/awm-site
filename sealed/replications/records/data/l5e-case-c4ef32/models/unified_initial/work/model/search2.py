"""Forward Dijkstra on the L5 macro model, memory-light (no edge storage, state cap).
best = min over states s with a winning action of dist(s) + 10*[refill still available at s].
Affordable iff best <= 45 (net budget 35 + 10 credit, last action may start at net 35)."""
import heapq, sys
import fast
from rules import initial

def run(coll, acts, cap=400000, bounded=True):
    s0 = fast.totuple(initial())
    dist = {s0: 0}; pq = [(0, s0)]; best = None; bests = None
    while pq:
        d, t = heapq.heappop(pq)
        if d > dist[t]: continue
        if best is not None and d + 0 > best: break
        for a in acts:
            n, cost, credit, win = fast.step(t, a, coll)
            if win:
                v = d + (10 if t[6] else 0)
                if best is None or v < best: best, bests = v, (t, a)
                continue
            if bounded and not (0 <= n[0] <= 60 and 10 <= n[1] <= 60): continue
            nd = d + cost
            if nd < dist.get(n, 10**9):
                dist[n] = nd; heapq.heappush(pq, (nd, n))
                if len(dist) > cap: return None, len(dist), None
    return best, len(dist), bests

if __name__ == '__main__':
    ACT_ALL = fast.ACTS
    ACT_OBS = [a for a in ACT_ALL if not (a[0]=='shrink' and a[1]!=(0,0)) and not (a[0]=='grow' and a[1]!=(2,2))]
    for name, acts in (('observed-placements', ACT_OBS), ('all-quadrant placements', ACT_ALL)):
        for coll in ('full', 'probe'):
            b, n, w = run(coll, acts)
            print(name, coll, 'states', n, 'best H(start)', b, '=> net', None if b is None else b-10,
                  'AFFORDABLE' if b is not None and b <= 45 else 'not affordable', w)
