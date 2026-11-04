"""Replay every observed level-4 transition through the abstract model (work/model_l4.py) and compare."""
import json, sys
sys.path.insert(0, 'work'); sys.path.insert(0, 'concepts')
import model_l4 as M
from _lib import me, panel_cells
tr = [json.loads(l) for l in open('transitions.jsonl')]
l4 = [r for r in tr if r['ctx']['level_prev'] == 4]
# attempt boundary: the first attempt-2 transition's prev is attempt-1's final (GAME_OVER) frame, not a real predecessor
BOUNDARY = {tr[k]['tid'] for k in range(1, len(tr)) if tr[k-1]['ctx']['state_next'] == 'GAME_OVER'}
def abst(g):
    p = me(g)
    if p is None: return None
    r0, c0, s, f = p
    door = 0 if any(g[y][x] == 13 for y in range(29, 33) for x in range(45, 48)) else 1
    return ((r0 - 1)//2, (c0 - 1)//2, 1 if s == 4 else 0, 1 if f == 'up' else 0, door)
DIR = {'ACTION1': 0, 'ACTION2': 1, 'ACTION3': 2, 'ACTION4': 3}
n = ok = bad = skipped = 0
for r in l4:
    a = r['action']; p, q = r['prev'], r['nxt']
    sp, sq = abst(p), abst(q)
    if r['tid'] in BOUNDARY:
        skipped += 1; print('skip (attempt boundary, prev is from the previous attempt):', a); continue
    if r['ctx']['state_next'] == 'GAME_OVER' and abst(q) == sp:
        skipped += 1; print('skip (game over, bar not modelled):', a); continue
    if a in DIR: mac = ('move', DIR[a])
    elif a.startswith('ACTION6'):
        pv, qv = list(panel_cells(p).values()), list(panel_cells(q).values())
        if pv.count(14) >= 2 and set(qv) == {2}:
            # decide which pattern completed: f (edge cells) vs 6 (middle column)
            cells = {k for k, v in panel_cells(p).items() if v == 14}
            mac = ('resize', 0) if any(k[1] != 1 for k in cells) or (1, 0) in cells else ('fire', 0)
        else:
            mac = None  # plain click: panel only, abstract state unchanged
    n += 1
    obs = 'win' if r['ctx']['level_next'] != 4 else sq
    if mac is None:
        pred = sp
    elif mac[0] == 'resize':   # loose resize: some quadrant must reproduce the observation
        outs = [M.step(sp, ('resize', k)) for k in range(4)]
        outs = ['win' if t == 'win' else s2 for t, s2 in outs]
        pred = obs if obs in outs else outs[0]
    else:
        t, s2 = M.step(sp, mac); pred = 'win' if t == 'win' else s2
    if pred == obs: ok += 1
    else:
        bad += 1; print('MISMATCH', a, mac, sp, pred, obs)
print(f'level-4 transitions checked {n}, matched {ok}, mismatched {bad}, skipped {skipped}')
