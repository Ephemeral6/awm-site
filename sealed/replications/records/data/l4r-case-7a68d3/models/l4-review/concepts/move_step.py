"""ACTION1/2/3/4 使动块平移 k 格（k=动块边长；上/下/左/右），当目标 kxk 新占格全是地板色 2 且边长不变时。"""
LEVEL = "L1"
SCOPE = "只看 ACTION1-4；前后帧逐格相同(未受理)返回 NA；动块定位不到返回 NA；目标新占格不全是地板 2 返回 NA；换关 NA"
NOTE = "v4: tid 87597ca9e44bde43/78c690ae04bae54f 判 FALSE 是读错(_lib.piece v2 把贴着出口的动块与出口并块)，修 _lib.piece 后判 TRUE；v2: tid 2b3e5ed8fe7b90de(开局首个 ACTION1)整帧无差，属未受理；v3: 动块边长从 4 变 2 后泛化成步长=边长（待验）"
EVIDENCE = ["3f5956007e12ca17", "827b6b560fc0b5bb", "2b3e5ed8fe7b90de", "87597ca9e44bde43", "78c690ae04bae54f"]
from _lib import DIRS, piece


def target(prev, action):
    p = piece(prev)
    if p is None:
        return None
    t0, l0, k = p
    dr, dc = DIRS[action]
    t, l = t0 + dr * k, l0 + dc * k
    if not (0 <= t and t + k <= 64 and 0 <= l and l + k <= 62):
        return None
    old = {(t0 + a, l0 + b) for a in range(k) for b in range(k)}
    for i in range(k):
        for j in range(k):
            if (t + i, l + j) not in old and prev[t + i][l + j] != 2:
                return None
    return (t, l, k)


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or prev == nxt:
        return "NA"
    if ctx and ctx.get("level_prev") not in (None, ctx.get("level_next")):
        return "NA"
    tg = target(prev, action)
    if tg is None:
        return "NA"
    return "TRUE" if piece(nxt) == tg else "FALSE"
