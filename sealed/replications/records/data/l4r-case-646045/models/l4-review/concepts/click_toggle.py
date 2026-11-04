"""点面板某格且未触发提交时：只有那一格变色，0 或 2 变 14，14 变回 2（0 格再点未测）。"""
LEVEL = "L1"
SCOPE = "同关内 ACTION6 点在 3x3 面板格内、且之后面板仍含 0 或 14（未提交）；否则 NA"
NOTE = ""
EVIDENCE = ["eded344d6029c02b", "916c2813ff2ba332", "c6791d78458309a6"]
from _lib import same_level, panel, panel_cell_at


def _xy(action):
    if not action.startswith("ACTION6:"):
        return None
    x, y = action.split(":")[1].split(",")
    return int(x), int(y)


def assert_(prev, action, nxt, ctx=None):
    xy = _xy(action)
    if xy is None or not same_level(ctx):
        return "NA"
    cell = panel_cell_at(*xy)
    if cell is None:
        return "NA"
    p, q = panel(prev), panel(nxt)
    if any(v is None for row in p + q for v in row):
        return "NA"
    if all(v not in (0, 14) for row in q for v in row):
        return "NA"   # 提交了，归 commit 管
    i, j = cell
    for a in range(3):
        for b in range(3):
            if (a, b) != (i, j) and p[a][b] != q[a][b]:
                return "FALSE"
    old, new = p[i][j], q[i][j]
    if old in (0, 2):
        return "TRUE" if new == 14 else "FALSE"
    if old == 14:
        return "TRUE" if new == 2 else "FALSE"
    return "NA"


def apply(prev, action, ctx=None):
    xy = _xy(action)
    if xy is None or not same_level(ctx) or panel_cell_at(*xy) is None:
        return None
    return None
