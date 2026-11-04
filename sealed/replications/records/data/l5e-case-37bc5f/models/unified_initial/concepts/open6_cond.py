"""When a recipe fires while 6-framed boxes are on the board, a box disappears iff the block sits at the mouth of that box's 2-wide stalk, flush with the stalk's first row/column (vertical stalk: block left col = stalk left col, block top = row below the stalk; horizontal stalk: block top row = stalk top row, block right edge = column before the stalk), and faces along the stalk toward the box."""
LEVEL = "L1"
SCOPE = "ACTION6 transitions within a level where nxt's right panel (rows 49/54/59, cols 24/29/34) is all colour 2 and prev had some colour-14 panel cell (a fire), and prev contains the 6-box; NA otherwise"
NOTE = "v3: tid d40d4c50 (L5 box2 fire) - box2 has a HORIZONTAL stalk (rows 15-16 c49-54) and opened with the 2x2 at r15 c47 facing right; v2 only knew vertical stalks. v2: tid bc372a75 (L5) - box interior was colour 12, and two boxes were present; v1 looked only at the first box and counted colour-13 cells. Now: any box whose vertical stalk matches; opened = a 6-box disappeared. v1 after attempt 2; fits all 8 observed fires (L3 x3, L4 x5 in attempt 1 incl. the shrink fire which is NA-or-FALSE-consistent, plus this attempt's success)"
EVIDENCE = ["d40d4c508896f1b4", "bc372a75ace8feb4", "a4766650260eb2a3", "92fdc7d68d5a2a2b"]
from _lib import block3
from geo import cells_of, components, bbox

RR = (49, 54, 59); RC = (24, 29, 34)


def _panel(g, col):
    return [all(g[r + a][c + b] == col for a in range(3) for b in range(3)) for r in RR for c in RC]


def _boxes(g):
    return [c for c in components(cells_of(g, 6)) if (lambda t, b, l, r: b - t == 3 and r - l == 3)(*bbox(c))]


def _hstalks(g):
    """(stalk_top_row, stalk_left_col) for every 6-framed box with a horizontal stalk to its left"""
    out = []
    for comp in _boxes(g):
        t, b, l, r = bbox(comp)
        col = l - 1
        if col >= 0 and g[t + 1][col] == 2 and g[t + 2][col] == 2:
            while col - 1 >= 0 and g[t + 1][col - 1] == 2 and g[t][col - 1] != 2:
                col -= 1
            out.append((t + 1, col))
    return out


def _stalks(g):
    """(stalk_left_col, stalk_bottom_row) for every 6-framed box with a vertical stalk below it"""
    out = []
    for comp in _boxes(g):
        t, b, l, r = bbox(comp)
        if b - t == 3 and r - l == 3:
            # stalk: colour-2 cells straight below the box, cols l+1..l+2
            row = b + 1
            if g[row][l + 1] == 2 and g[row][l + 2] == 2:
                while row + 1 < 64 and g[row + 1][l + 1] == 2 and g[row + 1][l] != 2:
                    row += 1
                out.append((l + 1, row))
    return out


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6") or (ctx and ctx.get("level_prev") != ctx.get("level_next")):
        return "NA"
    if not all(_panel(nxt, 2)) or not any(_panel(prev, 14)):
        return "NA"
    if not _boxes(prev):
        return "NA"
    st = _stalks(prev)
    k = block3(prev)
    if k is None:
        return "NA"
    t, l, s = k
    facing_up = prev[t][l] == 9 and prev[t + s - 1][l] == 10
    facing_right = prev[t][l + s - 1] == 9 and prev[t][l] == 10
    predict_open = (facing_up and any(l == c and t == r + 1 for c, r in st)) or         (facing_right and any(t == r and l + s == c for r, c in _hstalks(prev)))
    opened = len(_boxes(nxt)) < len(_boxes(prev))
    return "TRUE" if predict_open == opened else "FALSE"
