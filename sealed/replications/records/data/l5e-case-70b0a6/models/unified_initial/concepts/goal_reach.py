"""agent 的移动目标块与终点框（9 边 10 芯的那个框）有重叠时，这一步换关（level_next = level_prev + 1）。"""
LEVEL = "L5"
SCOPE = "只看 ACTION1-4 且能在 prev 里定位 agent 且目标块与终点框重叠；否则 NA"
NOTE = "依据只有 L1 一次：2x2 从 (15,35) 上移，目标 (13,35) 压在框芯上"
EVIDENCE = ["d03e3189bcf9a3f2"]
from _lib import agent, DIRS


def goal_cells(g, a):
    r, c, _, n = a
    out = set()
    for rr in range(64):
        for cc in range(64):
            if g[rr][cc] in (9, 10) and not (r <= rr < r + n and c <= cc < c + n):
                out.add((rr, cc))
    return out


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or not ctx:
        return "NA"
    a = agent(prev)
    if a is None:
        return "NA"
    r, c, _, n = a
    dr, dc = DIRS[action]
    tgt = {(r + dr * n + i, c + dc * n + j) for i in range(n) for j in range(n)}
    if not (tgt & goal_cells(prev, a)):
        return "NA"
    return "TRUE" if ctx.get("level_next") == (ctx.get("level_prev") or 0) + 1 else "FALSE"
