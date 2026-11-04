"""动块平移后，9 色那一半在运动方向那一侧，a 色那一半在另一侧。"""
LEVEL = "L1"
SCOPE = "换关转移 NA；只看 ACTION1-4 且动块前后都定位到、确实移动且边长不变的转移；否则 NA"
NOTE = "v2: 泛化到任意边长 k；v3: tid a644c7a41103a3af 是过关换图那一步，nxt 的动块是新关的(朝向是新关初值)，属作用域外，加换关 NA"
EVIDENCE = ["3f5956007e12ca17", "827b6b560fc0b5bb", "a644c7a41103a3af"]
from _lib import DIRS, piece


def _lead(i, j, k, dr, dc):
    h = k // 2
    if dr:
        return (i >= h) if dr > 0 else (i < h)
    return (j >= h) if dc > 0 else (j < h)


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS:
        return "NA"
    if ctx and ctx.get("level_prev") not in (None, ctx.get("level_next")):
        return "NA"
    p, q = piece(prev), piece(nxt)
    if p is None or q is None or p == q or p[2] != q[2]:
        return "NA"
    dr, dc = DIRS[action]
    t, l, k = q
    for i in range(k):
        for j in range(k):
            if nxt[t + i][l + j] != (9 if _lead(i, j, k, dr, dc) else 10):
                return "FALSE"
    return "TRUE"


def apply(prev, action, ctx=None):
    if action not in DIRS:
        return None
    import move_step
    tg = move_step.target(prev, action)
    if tg is None:
        return None
    t0, l0, k = piece(prev)
    t, l, _ = tg
    dr, dc = DIRS[action]
    out = {(t0 + i, l0 + j): 2 for i in range(k) for j in range(k)}
    for i in range(k):
        for j in range(k):
            out[(t + i, l + j)] = 9 if _lead(i, j, k, dr, dc) else 10
    return out
