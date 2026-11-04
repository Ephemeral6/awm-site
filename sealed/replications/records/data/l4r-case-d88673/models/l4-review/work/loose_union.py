"""Loosest union of every uncertain L4 rule, to see which relaxation (if any) admits a plan within 18."""
import sys, heapq, itertools
sys.path.insert(0, 'work')
import model_l4 as M, model_l4b as Q, model_l4d as D
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
E = Q.E
def trig(i, j, big, face, mode):
    allc, fr = Q.pcells(i, j, big, face)
    return bool(allc & E) if mode == 'any' else bool((not big and allc & E) or (big and fr & E))
def step(s, a, u, opt):
    i, j, big, face, door, picked = s
    if a[0] == 'move':
        d = a[1]; di, dj = DIRS[d]; n = 2 if big else 1
        ci, cj = i, j
        for _ in range(n):
            ni, nj = ci + di, cj + dj
            if ni < 0 or nj < 0: break
            r = M.rect(ni, nj, big, door)
            if r == 'B': break
            if r == 'G':
                ok = False
                if opt['touch'] and (u < 18 or opt['win18']): ok = True
                fi, fj = i + di*n, j + dj*n
                if opt['contain'] and D.contained(fi, fj, big) and M.rect(fi, fj, big, door) != 'B': ok = True
                if ok: return ('win', None, False)
                break
            ci, cj = ni, nj
        np_ = picked or trig(ci, cj, big, d, opt['pick'])
        return ('st', (ci, cj, big, d, door, int(np_)), bool(np_ and not picked))
    if a[0] == 'resize':
        qi, qj = a[1] // 2, a[1] % 2
        if big:
            ni, nj = i + qi, j + qj
            if not opt['looseResize'] and a[1] != 0: return ('st', s, False)
            nb = 0
        else:
            ni, nj = i - qi, j - qj
            if ni < 0 or nj < 0: return ('st', s, False)
            if not opt['looseResize']:
                c = None
                for cc in [(i-1, j-1), (i-1, j), (i, j-1), (i, j)]:
                    if cc[0] >= 0 and cc[1] >= 0 and M.rect(cc[0], cc[1], 1, door) != 'B': c = cc; break
                if c != (ni, nj): return ('st', s, False)
            if M.rect(ni, nj, 1, door) == 'B': return ('st', s, False)
            nb = 1
        np_ = picked or trig(ni, nj, nb, face, opt['pick'])
        return ('st', (ni, nj, nb, face, door, int(np_)), bool(np_ and not picked))
    t, s2, newly = Q.step(s, a)
    return ('st', s2, False) if t == 'st' else ('st', s, False)
def search(opt, B=18):
    best = {Q.START: 0}; pq = [(0, Q.START, [])]
    while pq:
        u, s, path = heapq.heappop(pq)
        if best.get(s, 99) < u or u > B: continue
        for a in Q.ACTIONS:
            t, s2, newly = step(s, a, u, opt)
            if t == 'win': return u, path + [a]
            v = u + Q.COST[a[0]]
            if newly: v = max(0, v - opt['refill'])
            if v < best.get(s2, 99):
                best[s2] = v; heapq.heappush(pq, (v, s2, path + [a]))
    return None
base = dict(touch=True, win18=False, contain=False, pick='front', looseResize=False, refill=10)
print('established (touch, no win at 18):', search(base))
for k, vals in [('win18', [True]), ('contain', [True]), ('pick', ['any']), ('looseResize', [True]), ('refill', [11, 12])]:
    for v in vals:
        o = dict(base); o[k] = v
        print(k, v, '->', search(o))
o = dict(base, contain=True, pick='any', looseResize=True)
print('all loose except win18:', search(o))
