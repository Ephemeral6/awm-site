"""动块(2x2 任意部分，或 4x4 的 9 色前半)与 e 色道具格相交的那一步：道具消失，计数条减少 10 tick(=该步后 used = 之前 used + 本步花费 - 10)。"""
LEVEL = "L4"
SCOPE = "v2: 4x4 情形只认前半(9 色)相交；只看 ACTION1-4、prev 中房间里(行<47、列<62)有 e 色道具、nxt 动块边长 2 的转移；其余 NA。4x4 盖住道具不触发(tid 9a86d908fa99d97e)——本条不主张 4x4 情形"
NOTE = "v2 (attempt 2): tid 7e0ae8a49d1be806 4x4 长大落在道具上、前半覆盖 -> 吃掉，16->6 tick；旧版只主张 2x2；L4 观测一次：计数条 64/64 时 2x2 左移压到道具上半，used 64->32"
EVIDENCE = ["60ebbfc6a613172b"]
from _lib import piece, counter_used


def item(g):
    return {(r, c) for r in range(47) for c in range(62) if g[r][c] == 14}


def assert_(prev, action, nxt, ctx=None):
    if action not in ("ACTION1", "ACTION2", "ACTION3", "ACTION4"):
        return "NA"
    it = item(prev)
    q = piece(nxt)
    if not it or q is None or q[2] != 2:
        return "NA"
    t, l, k = q
    cov = {(t + i, l + j) for i in range(k) for j in range(k)}
    if not (cov & it):
        return "NA"
    gone = not (item(nxt) - cov)
    d = counter_used(prev) - counter_used(nxt)
    return "TRUE" if gone and d == 32 else "FALSE"
