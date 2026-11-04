"""Fast tuple version of rules.step for the search (same semantics; cross-checked against rules.step
on a random sample of explored edges, see selfcheck())."""
import random
import rules as R
from l5map import inrect, BARRIER, SWITCH, EPAD, GOAL, RETICLE4, FPAD

DIRV = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
W = {}
for oc in (False, True):
    for od in (False, True):
        st = dict(open_c=oc, open_d=od)
        W[(oc, od)] = [[R.walkable(st, r, c) for c in range(64)] for r in range(64)]

def wk(oc, od, r, c):
    return 0 <= r < 64 and 0 <= c < 64 and W[(oc, od)][r][c]

ACTS = list(R.actions())
GROW_WALLCHECK = False
SUBSTEP = lambda s: 2      # attempt 5: 2-px sub-steps (4x4 partial move observed)
TURN_ONLY_IF_BLOCKED = False
_shot_cache = {}

def tostate(t):
    r, c, s, f, oc, od, ep = t
    return dict(r=r, c=c, size=s, facing=f, open_c=oc, open_d=od, box_c=not oc, box_d=not od, epad=ep)

def totuple(d):
    return (d['r'], d['c'], d['size'], d['facing'], d['open_c'], d['open_d'], d['epad'])

def ovl(r, c, s, Rc):
    return not (r + s - 1 < Rc[0] or r > Rc[1] or c + s - 1 < Rc[2] or c > Rc[3])

def step(t, a, collision='full'):
    r, c, s, f, oc, od, ep = t
    kind, arg = a
    if kind == 'move':
        dr, dc = DIRV[arg]
        nr, nc = r + dr * s, c + dc * s
        if collision == 'full':
            ok = all(wk(oc, od, nr + i, nc + j) for i in range(s) for j in range(s))
        else:
            ok = wk(oc, od, nr, nc)
        if ok:
            r, c = nr, nc
        elif SUBSTEP:
            # attempt 5: a move advances in sub-steps of SUBSTEP(s) px and stops at the last free one
            k = SUBSTEP(s); best = None
            for m in range(k, s, k):
                pr, pc = r + dr * m, c + dc * m
                if all(wk(oc, od, pr + i, pc + j) for i in range(s) for j in range(s)):
                    best = (pr, pc)
                else:
                    break
            if best:
                r, c = best
        f = arg                     # attempt 2: blocked moves turn too
    elif kind == 'turn':
        if TURN_ONLY_IF_BLOCKED:
            dr, dc = DIRV[arg]; nr, nc = r + dr * s, c + dc * s
            if collision == 'full':
                blocked = not all(wk(oc, od, nr + i, nc + j) for i in range(s) for j in range(s))
            else:
                blocked = not wk(oc, od, nr, nc)
            if blocked:
                f = arg
        else:
            f = arg
    elif kind == 'shrink':
        if s == 4:
            s, r, c = 2, r + arg[0], c + arg[1]
    elif kind == 'grow':
        if s == 2:
            gr, gc = r - arg[0], c - arg[1]
            if not GROW_WALLCHECK or all(wk(oc, od, gr + i, gc + j) for i in range(4) for j in range(4)):
                s, r, c = 4, gr, gc
    elif kind == 'shot':
        k = (r, c, s, f, oc, od)
        if k not in _shot_cache:
            _shot_cache[k] = R.rule_shot(tostate(t))
        n = _shot_cache[k]
        oc, od = n['open_c'], n['open_d']
    else:
        if s == 4:
            r, c = RETICLE4
        else:
            r, c = FPAD[0], FPAD[2]
    credit = 0
    if ep and ovl(r, c, s, EPAD):
        ep = False
        credit = R.REFILL
    n = (r, c, s, f, oc, od, ep)
    return n, R.COST[kind], credit, ovl(r, c, s, GOAL)

def selfcheck(states, collision, k=3000):
    bad = 0
    for t in random.sample(states, min(k, len(states))):
        for a in ACTS:
            n, cost, credit, win = step(t, a, collision)
            m, cost2, credit2 = R.step(tostate(t), a, collision)
            if totuple(m) != n or cost != cost2 or credit != credit2 or R.is_win(m) != win:
                bad += 1
    return bad
