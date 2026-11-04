"""Objects and rules of the game, as executable functions (attempt 1 knowledge).

OBJECTS (abstract state of a level)                       slot kept because ...
  Block   : r, c (top-left), size in {2,4}, facing in UDLR   pos/size: win & collision; facing: shot direction
  Barrier : key k, rect, open flag                           open flag: collision
  Switch  : key k, rect (6-bordered box), present flag       present flag: whether a shot still opens k
  Pad e   : rect, available flag                             available: refill once
  Pad f   : rect (2x2 teleport target)                       target of a 2x2 teleport
  Reticle : 4x4 teleport target top-left                     target of a 4x4 teleport
  Goal    : rect                                             win test
  Budget  : B, spent, credit                                 game over test
  Panel   : set of e-cells (frame level only)                which power fires
The macro model used for search / Lean folds the Panel into fire macros (see transforms.json T1).

RULES (each is a function state, action -> state; domain stated in the docstring)
"""
from l5map import (base_walkable, inrect, BARRIER, SWITCH, EPAD, FPAD, RETICLE4, GOAL, START)

DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
COST = {'move': 1, 'turn': 1, 'shrink': 5, 'grow': 5, 'shot': 4, 'tele': 4}
REFILL = 10
BUDGET = 35


def walkable(st, r, c):
    if base_walkable(r, c):
        return True
    for k, R in BARRIER.items():
        if inrect(r, c, R) and st['open_' + k]:
            return True
    return False


def footprint(r, c, s):
    return [(r + i, c + j) for i in range(s) for j in range(s)]


def overlaps(r, c, s, R):
    return any(inrect(y, x, R) for y, x in footprint(r, c, s))


# ---- R1 move ---------------------------------------------------------------
def rule_move(st, d, collision='full'):
    """Domain: any state, d in UDLR.  Target = pos + size*dir.  collision='full': every target cell
    walkable (ASSUMPTION, not tested on a partial overlap); 'probe': only target top-left cell (the
    alternative hypothesis).  Success: pos := target, facing := d.  Blocked: position unchanged, facing := d (attempt 2)."""
    dr, dc = DIRS[d]
    s = st['size']
    r, c = st['r'] + dr * s, st['c'] + dc * s
    cells = footprint(r, c, s) if collision == 'full' else [(r, c)]
    if all(walkable(st, y, x) for y, x in cells):
        return dict(st, r=r, c=c, facing=d)
    # attempt 5: the move advances in 2-px sub-steps and stops at the last free one
    # (4x4 from (17,33) up against the d barrier ended at (15,33); a 2x2 has no partial step)
    best = None
    for m in range(2, s, 2):
        pr, pc = st['r'] + dr * m, st['c'] + dc * m
        if all(walkable(st, y, x) for y, x in footprint(pr, pc, s)):
            best = (pr, pc)
        else:
            break
    if best:
        return dict(st, r=best[0], c=best[1], facing=d)
    return dict(st, facing=d)      # attempt 2: a blocked move still turns the block (observed at (25,45))


# ---- R1' turn (lenient superset: a blocked move that might still update facing) ----
def rule_turn(st, d):
    return dict(st, facing=d)


# ---- R2 size toggle ----------------------------------------------------------
QUADS = [(0, 0), (0, 2), (2, 0), (2, 2)]


def rule_shrink(st, q):
    """Domain: size 4.  Observed (3x, facing up): q=(0,0).  Model allows every quadrant (superset)."""
    if st['size'] != 4:
        return dict(st)
    return dict(st, size=2, r=st['r'] + q[0], c=st['c'] + q[1])


def rule_grow(st, q):
    """Domain: size 2.  Observed once (facing right): 2x2 at (r,c) -> 4x4 at (r-2,c-2), i.e. q=(2,2).
    Model allows every quadrant; fails unless the 4x4 footprint is walkable (established attempt 2)."""
    if st['size'] != 2:
        return dict(st)
    r, c = st['r'] - q[0], st['c'] - q[1]
    if not all(walkable(st, y, x) for y, x in footprint(r, c, 4)):
        return dict(st)            # attempt 2: grow into a non-walkable footprint fails (power still paid)
    return dict(st, size=4, r=r, c=c)


# ---- R3 shot -----------------------------------------------------------------
def shot_passable(st, r, c):
    if base_walkable(r, c):
        return True
    return any(inrect(r, c, R) for R in BARRIER.values())     # lenient: barriers transparent


def probe_lines(st):
    r, c, s, f = st['r'], st['c'], st['size'], st['facing']
    if f == 'U':
        return [[(y, c) for y in range(r - 1, -1, -1)]]          # established: left column only
    if f == 'D':
        return [[(y, x) for y in range(r + s, 47)] for x in range(c, c + s)]
    if f == 'L':
        return [[(y, x) for x in range(c - 1, 9, -1)] for y in range(r, r + s)]
    return [[(y, x) for x in range(c + s, 60)] for y in range(r, r + s)]


def rule_shot(st):
    """Domain: any state.  Projectile along a probe line in the facing direction; the first
    non-passable cell decides: if it is in a present switch box k, box removed and barrier k opens.
    Up uses the left column (L3 hit / L4 miss); other directions: any line (superset)."""
    out = dict(st)
    for line in probe_lines(st):
        for (y, x) in line:
            if shot_passable(st, y, x):
                continue
            for k, R in SWITCH.items():
                if inrect(y, x, R) and st['box_' + k]:
                    out['box_' + k] = False
                    out['open_' + k] = True
            break
    return out


# ---- R4 teleport -------------------------------------------------------------
def rule_tele(st):
    """4x4 -> reticle interior (L2, L5 reticle); 2x2 -> f pad (observed once on L5)."""
    if st['size'] == 4:
        return dict(st, r=RETICLE4[0], c=RETICLE4[1])
    return dict(st, r=FPAD[0], c=FPAD[2])


# ---- R5 refill / R6 win (post-conditions of every action) --------------------
def post(st):
    st = dict(st)
    credit = 0
    if st['epad'] and overlaps(st['r'], st['c'], st['size'], EPAD):
        st['epad'] = False
        credit = REFILL
    return st, credit


def is_win(st):
    return overlaps(st['r'], st['c'], st['size'], GOAL)


def actions():
    for d in 'UDLR':
        yield ('move', d)
    for d in 'UDLR':
        yield ('turn', d)
    for q in QUADS:
        yield ('shrink', q)
        yield ('grow', q)
    yield ('shot', None)
    yield ('tele', None)


def step(st, a, collision='full'):
    kind, arg = a
    if kind == 'move':
        n = rule_move(st, arg, collision)
    elif kind == 'turn':
        n = rule_turn(st, arg)
    elif kind == 'shrink':
        n = rule_shrink(st, arg)
    elif kind == 'grow':
        n = rule_grow(st, arg)
    elif kind == 'shot':
        n = rule_shot(st)
    else:
        n = rule_tele(st)
    n, credit = post(n)
    return n, COST[kind], credit


def initial():
    return dict(r=START['r'], c=START['c'], size=4, facing='D',
                open_c=False, open_d=False, box_c=True, box_d=True, epad=True)


def rule_grow_engine(st):
    """Deterministic grow as observed: try the up-left placement (r-2,c-2) first; if its footprint is
    not walkable, try (r, c-2) (attempt 6: 2x2 at (15,43) -> 4x4 at (15,41)), then the remaining
    quadrants (order of these two unobserved).  The Lean model allows every walkable quadrant."""
    for q in [(2, 2), (0, 2), (2, 0), (0, 0)]:
        n = rule_grow(st, q)
        if n['size'] == 4:
            return n
    return dict(st)
