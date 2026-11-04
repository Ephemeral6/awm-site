"""A click outside the 3x3 panel and outside the legend panels (cols 0-9, rows 0-20) leaves the final frame unchanged (no bar cost)."""
LEVEL = "L1"
SCOPE = "same level, ACTION6 whose point is not on a panel cell and not in cols 0-9 rows 0-20; attempt boundary NA"
NOTE = "attempt 4: e square, background, piece clicks; the animation flashes the panel 8 four times"
EVIDENCE = ["20710574338b03e7"]
from _lib import same_level, panel_cell_at, is_boundary


def assert_(prev, action, nxt, ctx=None):
    if not action.startswith("ACTION6:") or not same_level(ctx) or is_boundary(prev, action, nxt):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    if panel_cell_at(x, y) is not None or (x <= 9 and y <= 20):
        return "NA"
    if 47 <= y <= 63 and 22 <= x <= 38:
        return "NA"   # panel frame/border: not tested
    return "TRUE" if prev == nxt else "FALSE"
