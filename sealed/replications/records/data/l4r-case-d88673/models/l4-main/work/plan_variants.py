import sys, heapq, itertools
sys.path.insert(0, 'work')
import model_l4 as M
import model_l4b as Q
E = Q.E
def grow_cands(i, j, face, door, hyp):
    free = lambda a, b: a >= 0 and b >= 0 and M.rect(a, b, 1, door) != "B"
    if hyp == 'bottom':
        order = [(i-1, j), (i-1, j-1)]
    else:
        # vertical: toward front if facing up/down, else default up; horizontal: toward front if left/right, else default
        vpref = {0: [i-1, i], 1: [i, i-1]}.get(face, [i-1, i])
        hdef = [j, j-1] if hyp == 'front_R' else [j-1, j]
        hpref = {2: [j-1, j], 3: [j, j-1]}.get(face, hdef)
        order = [(a, b) for a in vpref for b in hpref] if face in (0, 1) else [(a, b) for b in hpref for a in vpref]
    for c in order:
        if free(*c): return c
    return None
def step(s, a, hyp, trig):
    i, j, big, face, door, picked = s
    if a[0] == 'resize' and not big:
        if a[1] != 0: return ('st', s, False)
        c = grow_cands(i, j, face, door, hyp)
        if c is None: return ('st', s, False)
        ni, nj = c
        if M.rect(ni, nj, 1, door) == 'G': return ('win', None, False)
        t = trig_f(ni, nj, 1, face, trig)
        np_ = picked or t
        return ('st', (ni, nj, 1, face, door, int(np_)), bool(np_ and not picked))
    r = Q.step(s, a)
    if r[0] == 'st' and r[2]:
        # recompute trigger under this hypothesis
        ni, nj, nb, nf, nd, _ = r[1]
        t = trig_f(ni, nj, nb, nf, trig)
        if not t: return ('st', (ni, nj, nb, nf, nd, picked), False)
    elif r[0] == 'st' and not r[2] and not picked:
        ni, nj, nb, nf, nd, _ = r[1]
        t = trig_f(ni, nj, nb, nf, trig)
        if t: return ('st', (ni, nj, nb, nf, nd, 1), True)
    return r
def trig_f(i, j, big, face, trig):
    allc, fr = Q.pcells(i, j, big, face)
    small = (not big) and bool(allc & E); front = bool(fr & E)
    return {'small': small, 'front': front, 'union': small or front}[trig]
def nu(u, a, newly, refill):
    v = u + Q.COST[a[0]]
    if not newly: return v
    return 7 if refill == 'set7' else max(0, v - 10)
def plan(hyp, trig, refill, B=18):
    st0 = Q.START; best = {st0: 0}; pq = [(0, st0, [])]
    while pq:
        u, s, path = heapq.heappop(pq)
        if best.get(s, 99) < u or u > B: continue
        for a in Q.ACTIONS:
            t, s2, newly = step(s, a, hyp, trig)
            if t == 'win': return u, path + [a]
            v = nu(u, a, newly, refill)
            if v < best.get(s2, 99):
                best[s2] = v; heapq.heappush(pq, (v, s2, path + [a]))
    return None
if __name__ == '__main__':
    for hyp, trig, refill in itertools.product(('bottom', 'front_R', 'front_L'), ('small', 'front', 'union'), ('set7', 'minus10')):
        r = plan(hyp, trig, refill)
        print(hyp, trig, refill, '->', r)
