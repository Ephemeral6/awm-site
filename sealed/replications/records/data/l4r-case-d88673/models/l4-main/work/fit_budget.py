"""Fit the bar model: lost_rows(u) = 2*floor(u*64/B/2), u = cumulative units.
Variants: whether fully-inert actions (prev==nxt apart from nothing) count; completion extra units."""
import json, sys
sys.path.insert(0, 'concepts')
from _lib import panel_cells
tr = [json.loads(l) for l in open('transitions.jsonl')]
def bar(g): return sum(1 for y in range(64) if g[y][63] == 14)
def is_completion(p, q):
    return list(panel_cells(p).values()).count(14) >= 2 and set(panel_cells(q).values()) == {2} and str(1)
levels = {}
for r in tr:
    lv = r['ctx']['level_prev']
    if r['ctx']['level_next'] != lv or r['ctx']['state_next'] != 'NOT_FINISHED':
        continue
    levels.setdefault(lv, []).append(r)
for count_inert in (False, True):
  for extra in (0, 1, 2):
    res = []
    for lv, rs in sorted(levels.items()):
        start = bar(rs[0]['prev'])
        seq = []; u = 0
        for r in rs:
            p, q = r['prev'], r['nxt']
            inert = (p == q)
            if inert and not count_inert:
                pass
            else:
                u += 1
                ap = str(r['action'])
                if ap.startswith('ACTION6') and list(panel_cells(p).values()).count(14) >= 2 and set(panel_cells(q).values()) == {2}:
                    u += extra
            seq.append((u, start - bar(q)))
        ok = []
        for B in range(10, 80):
            rr = 64 / B
            if all(lost == 2 * int(uu * rr / 2 + 1e-9) for uu, lost in seq):
                ok.append(B)
        res.append((lv, ok))
    print('inert counted' if count_inert else 'inert free', 'extra', extra, res)
