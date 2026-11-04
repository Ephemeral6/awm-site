"""Reconciliation of the L5 macro model against every observed level-5 transition.

read(frame) -> abstract state (block pos/size/facing, gates, refill pad).
Each observed transition is mapped to a macro action:
  ACTION1-4                         -> move U/D/L/R
  ACTION6 that fires (panel resets)  -> the power whose pattern was completed
  ACTION6 that does not fire          -> no change of the abstract state
Prediction = rules.step (both flag versions: separate box/open flags in rules.py, merged flags in fast.py).
"""
import json, os, sys
import rules as R
import fast
fast.GROW_WALLCHECK = True
from l5map import inrect

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
PAN = {(49, 24): 'TL', (49, 29): 'TM', (49, 34): 'TR', (54, 24): 'ML', (54, 29): 'C', (54, 34): 'MR',
       (59, 24): 'BL', (59, 29): 'BM', (59, 34): 'BR'}
PATTERNS = {frozenset(['TM', 'ML', 'MR', 'BM']): 'size', frozenset(['TM', 'C', 'BM']): 'shot',
            frozenset(['TL', 'TM', 'C']): 'tele'}


def read(f):
    cells = [(r, c) for r in range(47) for c in range(10, 60)
             if f[r][c] in (9, 10) and not inrect(r, c, (0, 4, 32, 37))]
    rs = [r for r, _ in cells]; cs = [c for _, c in cells]
    r0, c0 = min(rs), min(cs); n = max(rs) - r0 + 1
    h = n // 2
    if all(f[r0 + i][c0 + j] == 9 for i in range(h) for j in range(n)): fc = 'U'
    elif all(f[r0 + h + i][c0 + j] == 9 for i in range(h) for j in range(n)): fc = 'D'
    elif all(f[r0 + i][c0 + j] == 9 for i in range(n) for j in range(h)): fc = 'L'
    else: fc = 'R'
    oc = not any(f[r][c] == 12 for r in range(33, 37) for c in range(29, 32))
    od = not any(f[r][c] == 13 for r in range(11, 14) for c in range(33, 37))
    ep = any(f[r][c] == 14 for r in range(37, 39) for c in range(49, 51))
    under = R.overlaps(r0, c0, n, (37, 38, 49, 50))
    return dict(r=r0, c=c0, size=n, facing=fc, open_c=oc, open_d=od, box_c=not oc, box_d=not od,
                epad=ep), under


def panel(f):
    return frozenset(v for (r, c), v in PAN.items() if f[r][c] == 14)


def macro(t):
    a = t['action']
    if a in ('ACTION1', 'ACTION2', 'ACTION3', 'ACTION4'):
        return ('move', 'UDLR'['1234'.index(a[-1]) if False else {'1': 0, '2': 1, '3': 2, '4': 3}[a[-1]]])
    p0, p1 = panel(t['prev']), panel(t['nxt'])
    x, y = map(int, a.split(':')[1].split(','))
    hit = [v for (r, c), v in PAN.items() if r <= y < r + 3 and c <= x < c + 3]
    if hit and p1 == frozenset() and (p0 ^ {hit[0]}) in PATTERNS:
        return PATTERNS[p0 ^ {hit[0]}]
    return None


def main():
    tr = [json.loads(l) for l in open(os.path.join(ROOT, 'transitions.jsonl'), encoding='utf-8') if l.strip()]
    # drop transitions taken right after a GAME_OVER (their prev frame belongs to the previous attempt)
    after_over = {i for i in range(1, len(tr)) if tr[i - 1]['ctx'].get('state_next') == 'GAME_OVER'}
    L5 = [t for i, t in enumerate(tr) if i not in after_over and t['ctx']['level_prev'] == 5 and t['ctx']['level_next'] == 5]
    # drop the transition whose prev frame is the game-over frame of attempt 1 (world reset in between)
    L5 = [t for t in L5 if not any((t['prev'][r][c] in (6, 12, 13)) != (t['nxt'][r][c] in (6, 12, 13))
                                   and (t['nxt'][r][c] in (6, 12, 13)) for r in range(47) for c in range(10, 60))]
    ok = bad = 0; fails = []
    for i, t in enumerate(L5):
        s, under = read(t['prev'])
        if under: s['epad'] = prev_ep          # pad hidden under the block: carry the last reading
        m = macro(t)
        if m is None:
            pred = dict(s)
        elif m == 'size':
            pred = (R.step(s, ('shrink', (0, 0)))[0] if s['size'] == 4 else R.post(R.rule_grow_engine(s))[0])
        elif m == 'shot':
            pred = R.step(s, ('shot', None))[0]
        elif m == 'tele':
            pred = R.step(s, ('tele', None))[0]
        else:
            pred = R.step(s, m)[0]
        nx, under_n = read(t['nxt'])
        if under_n: nx['epad'] = pred['epad']
        fpred = fast.tostate(fast.step(fast.totuple(s), ('shrink', (0, 0)) if m == 'size' and s['size'] == 4 else
                                       ('grow', next((q for q in [(2,2),(0,2),(2,0),(0,0)] if R.rule_grow(s, q)['size'] == 4), (2,2))) if m == 'size' else (m if isinstance(m, tuple) else (m, None)) if m else ('turn', s['facing']))[0])
        keys = ['r', 'c', 'size', 'facing', 'open_c', 'open_d', 'epad']
        same = all(pred[k] == nx[k] for k in keys)
        merged_same = all(fpred[k] == pred[k] for k in keys)
        if same and merged_same: ok += 1
        else:
            bad += 1; fails.append((i, t['action'], m, {k: (pred[k], nx[k], fpred[k]) for k in keys if pred[k] != nx[k] or fpred[k] != pred[k]}))
        prev_ep = nx['epad']
    print('L5 transitions reconciled:', len(L5), 'matched:', ok, 'mismatched:', bad)
    for f in fails: print('  ', f)
    return ok, bad


prev_ep = True
if __name__ == '__main__':
    main()
