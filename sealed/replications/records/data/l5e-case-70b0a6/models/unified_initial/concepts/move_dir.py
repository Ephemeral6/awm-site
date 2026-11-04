"""ACTION1-4 把 agent（n x n 头9尾10块，n∈{4,2}）沿 上/下/左/右 平移 n 格，且头朝向移动方向；目标 4x4 全是红地板(2)时一定发生。"""
LEVEL = "L1"
SCOPE = "只看 ACTION1-4；prev 是开局帧且动作为 ACTION1 时 NA（tid 2b3e5ed8 那一步 ACTION1 未生效，原因未明，待实验）；目标 4x4 不全是 2 返回 NA；定位不到 agent 返回 NA；换关返回 NA"
NOTE = "v2: 原版只认 4x4、步长写死 4；L1 缩小后 2x2 每步走 2（tid 见 EVIDENCE 之外的 L1 尾段），扩成步长=边长"
EVIDENCE = ["3f5956007e12ca17", "3c367435761b27cf", "87597ca9e44bde43"]

from _lib import agent, DIRS, STEP, is_initial


def _pred(prev, action):
    if action not in DIRS or (is_initial(prev) and action == 'ACTION1'):
        return None
    a = agent(prev)
    if a is None:
        return None
    r, c, _, n = a
    dr, dc = DIRS[action]
    nr, nc = r + dr * n, c + dc * n
    if not (0 <= nr <= 64 - n and 0 <= nc <= 64 - n):
        return None
    for i in range(n):
        for j in range(n):
            rr, cc = nr + i, nc + j
            if r <= rr < r + n and c <= cc < c + n:
                continue
            if prev[rr][cc] != 2:
                return None
    return (nr, nc, (dr, dc), n)


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    p = _pred(prev, action)
    if p is None:
        return "NA"
    return "TRUE" if agent(nxt) == p else "FALSE"


def apply(prev, action, ctx=None):
    p = _pred(prev, action)
    if p is None:
        return None
    a = agent(prev)
    out = {}
    nr, nc, (dr, dc), n = p
    h2 = n // 2
    for i in range(n):
        for j in range(n):
            out[(a[0] + i, a[1] + j)] = 2
    for i in range(n):
        for j in range(n):
            if dr == -1: head = i < h2
            elif dr == 1: head = i >= h2
            elif dc == -1: head = j < h2
            else: head = j >= h2
            out[(nr + i, nc + j)] = 9 if head else 10
    return out
