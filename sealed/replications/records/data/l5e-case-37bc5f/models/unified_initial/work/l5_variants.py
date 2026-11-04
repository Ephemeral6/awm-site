"""Which single unverified rule variant would bring the cheapest level-5 win to <= 35 units?
Each variant patches one rule of work/l5_search.py and reruns the Dijkstra (unbounded budget)."""
import sys
sys.path.insert(0, 'work')
import l5_search as S

base_move, base_macros, base_ocv, base_och = S.move, S.macros, S.oc_vert, S.oc_horiz
start = (29, 17, 4, 'D', False, False, False)


def run(name):
    r = S.search(start, B=10 ** 6)
    print('%-55s %s  %s' % (name, r[0] if r else None, ' '.join(r[1]) if r else ''))
    S.move, S.macros, S.oc_vert, S.oc_horiz = base_move, base_macros, base_ocv, base_och


run('baseline')

# V1: open condition ignores facing
S.oc_vert = lambda st, row, col: st[1] == col and st[0] == row + 1
S.oc_horiz = lambda st, row, col: st[0] == row and st[1] + st[2] == col
run('V1 open ignores facing')

# V2: open from anywhere in line with the stalk mouth (vertical: same col, below; horizontal: same row, left)
S.oc_vert = lambda st, row, col: st[3] == 'U' and st[1] == col and st[0] > row
S.oc_horiz = lambda st, row, col: st[3] == 'R' and st[0] == row and st[1] + st[2] <= col
run('V2 open from a distance in line (facing)')


# V3: grow keeps top-left (no shift)
def mac3(st):
    out = []
    for m in base_macros(st):
        if m[0] == 'grow':
            r, c, s, f, g0, g1, pad = st
            if S.fits(g0, g1, r, c, 4):
                out.append(('grow', 5, (r, c, 4, f, g0, g1, pad)))
        else:
            out.append(m)
    if st[2] == 2 and not any(m[0] == 'grow' for m in out):
        r, c, s, f, g0, g1, pad = st
        if S.fits(g0, g1, r, c, 4):
            out.append(('grow', 5, (r, c, 4, f, g0, g1, pad)))
    return out
S.macros = mac3
run('V3 grow keeps top-left')


# V4: grow keeps bottom-left (top = r-2, col = c)
def mac4(st):
    out = [m for m in base_macros(st) if m[0] != 'grow']
    r, c, s, f, g0, g1, pad = st
    if s == 2 and r >= 2 and S.fits(g0, g1, r - 2, c, 4):
        out.append(('grow', 5, (r - 2, c, 4, f, g0, g1, pad)))
    return out
S.macros = mac4
run('V4 grow keeps bottom-left')


# V5: teleport of a 2x2 lands in the pocket too
def mac5(st):
    out = [m for m in base_macros(st) if m[0] != 'tp']
    r, c, s, f, g0, g1, pad = st
    out.append(('tp', 4, (17, 33, s, f, g0, g1, pad)))
    return out
S.macros = mac5
run('V5 2x2 teleport lands in the pocket (17,33)')


# V6: the plus ring costs 4 (if one cell were preset by the hint) -> model as 4
def mac6(st):
    return [(n, (4 if n in ('shrink', 'grow') else c), s2) for n, c, s2 in base_macros(st)]
S.macros = mac6
run('V6 shrink/grow cost 4 instead of 5')


# V7: fires cost 1 extra less (firing click 1 unit)
def mac7(st):
    return [(n, c - 1, s2) for n, c, s2 in base_macros(st)]
S.macros = mac7
run('V7 firing click costs 1 (not 2)')
