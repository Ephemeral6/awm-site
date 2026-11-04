"""凑齐事件(点击使网格 e 集合==左面板图样)且图样色为 b(11) 时：动块(边长、朝向不变)被移到房间里 b 角标围成的 6x6 框的内 4x4 处，原位置变地板 2，网格全复位 2。"""
LEVEL = "L1"
SCOPE = "只看 ACTION6 落在网格格块上、点完 e 集合==左面板非地板格集合、且左面板图样色==11 的转移；其余 NA"
NOTE = "L2 观测一次"
EVIDENCE = ["d3f8d3aa32dd67db"]
from _lib import piece
from grid_toggle import _cell, _state

PR = [(51, 52), (54, 55), (57, 58)]
PC = [(12, 13), (15, 16), (18, 19)]


def panel(g):
    out, col = set(), None
    for i, (r, _) in enumerate(PR):
        for j, (c, _) in enumerate(PC):
            if g[r][c] != 2:
                out.add((i, j)); col = g[r][c]
    return out, col


def markers(g, col=11):
    cs = [(r, c) for r in range(0, 47) for c in range(0, 62) if g[r][c] == col]
    return cs


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:"):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    c = _cell(x, y)
    if c is None:
        return "NA"
    a = _state(prev)
    on = {(i, j) for i in range(3) for j in range(3) if a[i][j] == 14} ^ {c}
    pat, col = panel(prev)
    if on != pat or col != 11:
        return "NA"
    m = markers(prev)
    p = piece(prev)
    if not m or p is None:
        return "NA"
    t = min(r for r, _ in m) + 1; l = min(c2 for _, c2 in m) + 1
    q = piece(nxt)
    if q != (t, l, p[2]):
        return "FALSE"
    if any(v != 2 for row in _state(nxt) for v in row):
        return "FALSE"
    return "TRUE"
