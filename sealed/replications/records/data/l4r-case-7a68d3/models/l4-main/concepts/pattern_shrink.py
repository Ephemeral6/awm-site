"""点击使右网格 e 格集合恰好等于左面板 f 图样(上中/左中/右中/下中)的那一步：网格 9 格全部复位为 2，且动块边长 4 -> 2(位置保留左上角，朝向保留)。"""
LEVEL = "L1"
SCOPE = "只看 ACTION6 落在网格格块上、且点击后(按 toggle 推算)e 集合 == 左面板图样 的转移；其余 NA。只在动块边长 4 时断言边长变 2"
NOTE = ""
EVIDENCE = ["86ce47eb0c2a3681"]
from _lib import piece
from grid_toggle import _cell, _state

PAT = {(0, 1), (1, 0), (1, 2), (2, 1)}


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:"):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    c = _cell(x, y)
    if c is None:
        return "NA"
    a = _state(prev)
    on = {(i, j) for i in range(3) for j in range(3) if a[i][j] == 14}
    on ^= {c}
    if on != PAT:
        return "NA"
    b = _state(nxt)
    if any(v != 2 for row in b for v in row):
        return "FALSE"
    p, q = piece(prev), piece(nxt)
    if p is None or p[2] != 4:
        return "NA"
    if q is None or q[2] != 2 or (q[0], q[1]) != (p[0], p[1]):
        return "FALSE"
    return "TRUE"
