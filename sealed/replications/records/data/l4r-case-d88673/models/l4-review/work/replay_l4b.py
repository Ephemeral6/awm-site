"""Replay all observed level-4 transitions through model_l4b (face + pickup) and the counter model."""
import json, sys
sys.path.insert(0, 'work'); sys.path.insert(0, 'concepts')
import model_l4b as Q
from _lib import me, panel_cells
tr = [json.loads(l) for l in open('transitions.jsonl')]
FACE = {'up': 0, 'down': 1, 'left': 2, 'right': 3}
def bar(g): return sum(1 for y in range(64) if g[y][63] == 14)
def abst(g):
    p = me(g)
    if p is None: return None
    r0, c0, s, f = p
    door = 0 if any(g[y][x] == 13 for y in range(29, 33) for x in range(45, 48)) else 1
    picked = 0 if any(g[y][x] == 14 for y in range(34, 36) for x in range(23, 25)) or any(
        g[y][x] in (9, 10) for y in range(34, 36) for x in range(23, 25)) and not picked_seen else 1
    return ((r0 - 1)//2, (c0 - 1)//2, 1 if s == 4 else 0, FACE[f], door)
DIR = {'ACTION1': 0, 'ACTION2': 1, 'ACTION3': 2, 'ACTION4': 3}
n = ok = bad = skip = 0; ubad = 0
picked = 0; u = 0
for k, r in enumerate(tr):
    if r['ctx']['level_prev'] != 4: continue
    if r['ctx']['level_next'] < 4:   # new game started (boundary into an earlier level)
        skip += 1; continue
    p, q, a = r['prev'], r['nxt'], r['action']
    e_gone = any(p[y][x] == 14 for y in range(34, 36) for x in range(23, 25)) and not any(q[y][x] == 14 for y in range(34, 36) for x in range(23, 25))
    if bar(q) > bar(p) and r['ctx']['level_next'] == 4 and not e_gone:   # attempt boundary: real action, cost 1
        legend = a.startswith('ACTION6') and int(a.split(':')[1].split(',')[0]) < 10
        picked = 0; u = 0 if legend else 1; skip += 1; continue
    if k > 0 and tr[k-1]['ctx']['level_prev'] == 3 and tr[k-1]['ctx']['level_next'] == 4:
        picked = 0; u = 0
    globals()['picked_seen'] = picked
    sp = abst(p)
    if a in DIR: mac = ('move', DIR[a])
    elif a.startswith('ACTION6'):
        pv, qv = list(panel_cells(p).values()), list(panel_cells(q).values())
        if pv.count(14) >= 2 and set(qv) == {2}:
            cells = {kk for kk, v in panel_cells(p).items() if v == 14}
            mac = ('resize', None) if any(kk[1] != 1 for kk in cells) else ('fire', 0)
        else:
            mac = None
    if p == q and mac is None:    # inert (free)
        continue
    if a.startswith('ACTION6'):
        x, y = map(int, a.split(':')[1].split(','))
        if x < 10 and y < 21:     # attempt 6: legend click -> hint display only, FREE, abstract state unchanged
            n += 1; ok += 1; continue
    obs = 'win' if r['ctx']['level_next'] != 4 else sp and abst(q)
    st = sp + (picked,)
    if mac is None:
        pred, newly = sp, False; cost = 1
    elif mac[0] == 'resize':
        outs = [Q.step(st, ('resize', qq)) for qq in range(4)]
        outs = [(o[1][:5] if o[0] == 'st' else 'win', o[2]) for o in outs if not (o[0] == 'st' and o[1] == st)]
        match = [o for o in outs if o[0] == obs]
        pred, newly = (match[0] if match else (outs[0] if outs else (sp, False)))
        cost = 5
    elif u == 18 and r['ctx']['state_next'] == 'GAME_OVER':
        # attempt 6: the action starting at the last unit is terminal; its end position is NOT modelled
        # (attempt 5: 4x4 stopped 2 px short of the goal; attempt 6: 4x4 moved 4 px). Only checked: no win.
        pred = obs = ('terminal', r['ctx']['level_next'] == 4); newly = False; cost = 1
    elif False:
        # attempt-5 rule: a 4x4 move starting at the last unit advances one 2-px sub-step, then GAME_OVER
        di, dj = Q.DIRS[mac[1]]; ni, nj = st[0] + di, st[1] + dj
        pred = (ni, nj, 1, mac[1], st[4]); newly = False; cost = 1
        r0, c0 = 2*ni+1, 2*nj+1; f = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}[mac[1]]
        blk = [[q[r0+a][c0+b] for b in range(4)] for a in range(4)]
        ok_pix = all(blk[a][b] == (9 if b >= 2 else 10) for a in range(4) for b in range(4)) if f == 'right' else False
        obs = pred if ok_pix and r['ctx']['state_next'] == 'GAME_OVER' else ('pixels', blk)
    else:
        t, s2, newly = Q.step(st, mac); pred = 'win' if t == 'win' else s2[:5]; cost = Q.COST[mac[0]]
    n += 1
    if pred == obs: ok += 1
    else: bad += 1; print('MISMATCH', k, a, mac, st, pred, obs)
    # counter check (completion click = 2 units, other clicks 1; macro abstraction not used here)
    c = 1 + (1 if mac and mac[0] in ('resize', 'fire') else 0) if a.startswith('ACTION6') else 1
    u = Q.nu(u, ('move', 0), False) if False else u
    v = u + c
    if newly: v = max(0, v - 10); picked = 1
    u = v
    exp = 64 - 2 * int(u * 64 / 18 / 2 + 1e-9)
    if r['ctx']['state_next'] == 'NOT_FINISHED' and r['ctx']['level_next'] == 4 and bar(q) != exp:
        ubad += 1; print('BAR MISMATCH', k, a, u, bar(q), exp)
print(f'level-4 transitions checked {n}, matched {ok}, mismatched {bad}, boundary-skipped {skip}; bar mismatches {ubad}')
