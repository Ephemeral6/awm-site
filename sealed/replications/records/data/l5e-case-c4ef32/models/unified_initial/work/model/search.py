"""Exact search on the L5 macro model (uses fast.step == rules.step, cross-checked).

H(s) = min over winning continuations of (gross prefix cost) + 10*[refill still available at the
state from which the winning action is taken].  Net-budget rule (35, +10 refill credit, last action
may start at net 35): affordable from START iff H(START) <= 45.
"""
import heapq, json, sys
import fast
from rules import initial

def explore(coll):
    s0 = fast.totuple(initial())
    seen = {s0: 0}; order = [s0]; edges = {}
    i = 0
    while i < len(order):
        t = order[i]; i += 1
        out = []
        for a in fast.ACTS:
            n, cost, credit, win = fast.step(t, a, coll)
            out.append((a, n, cost, win))
            if not win and n not in seen:
                seen[n] = len(order); order.append(n)
        edges[t] = out
    return order, edges

def potential(order, edges):
    INF = 10**9
    H = {t: INF for t in order}; rev = {t: [] for t in order}
    for t, out in edges.items():
        for a, n, cost, win in out:
            if win:
                H[t] = min(H[t], 10 if t[6] else 0)
            else:
                rev[n].append((t, cost))
    pq = [(v, t) for t, v in H.items() if v < INF]; heapq.heapify(pq)
    while pq:
        v, t = heapq.heappop(pq)
        if v > H[t]: continue
        for p, cost in rev[t]:
            if v + cost < H[p]:
                H[p] = v + cost; heapq.heappush(pq, (H[p], p))
    return H

def best_path(edges, H, t):
    path = []
    while True:
        out = edges[t]
        if any(w for a, n, c, w in out) and H[t] == (10 if t[6] else 0):
            path.append([a for a, n, c, w in out if w][0]); return path
        for a, n, c, w in out:
            if not w and H[n] + c == H[t]:
                path.append(a); t = n; break
        else:
            return path + ['??']

if __name__ == '__main__':
    res = {}
    for coll in sys.argv[1:] or ['full', 'probe']:
        order, edges = explore(coll)
        H = potential(order, edges)
        h0 = H[order[0]]
        bad = fast.selfcheck(order, coll)
        p = best_path(edges, H, order[0])
        print(coll, 'states', len(order), 'selfcheck mismatches', bad, 'H(start)', h0,
              '=> min net prefix spend', h0 - 10, 'affordable' if h0 <= 45 else 'NOT affordable')
        print('  optimal path', len(p), p)
        res[coll] = dict(states=len(order), H0=h0, path=[list(map(str, a)) for a in p])
    json.dump(res, open('search_result.json', 'w'), indent=1)
