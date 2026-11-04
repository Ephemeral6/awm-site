"""目标图样色为 11 时凑成图样：agent（尺寸、朝向不变）落到某一组四角标记框（11 色或 15 色，四个同色标记围成的方框）的正中。"""
LEVEL = "L1"
SCOPE = "只看凑成 11 色图样的点击且 prev/nxt 都能定位 agent；否则 NA。**不断言**有多组标记框时挑哪一组。"
NOTE = ("v2: v1 断言落点 = 11 色标记最小行列 +1，被 690233a241103e36 打脸：L5 agent 缩成 2x2 后地图上出现 15 色四角标记"
        "(围着 15 色 2x2 道具)，传送落到了那里 (37,15)，而不是 11 色标记框。改为只断言『落在某组标记框正中』。")
EVIDENCE = ["a97af4438459243d", "690233a241103e36"]
from _lib import parse_click, panel_cell_at, panel, completes, agent


def frames(g, col):
    """同色四角标记：四个格子恰好是一个正方形的四角（行列各两值、边长相等）。"""
    cells = [(r, c) for r in range(47) for c in range(62) if g[r][c] == col]
    S = set(cells)
    out = []
    for (r0, c0) in cells:
        for (r1, c1) in cells:
            if r1 > r0 and c1 > c0 and r1 - r0 == c1 - c0 and (r0, c1) in S and (r1, c0) in S:
                out.append((r0, c0, r1, c1))
    return out


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    cm = completes(prev, action)
    if not cm or cm[0] != 11:
        return "NA"
    a, b = agent(prev), agent(nxt)
    if a is None or b is None:
        return "NA"
    if b[2] != a[2] or b[3] != a[3]:
        return "FALSE"
    n = a[3]
    for col in (11, 15):
        for (r0, c0, r1, c1) in frames(prev, col):
            if (r0 + r1 + 1) // 2 - n // 2 == b[0] and (c0 + c1 + 1) // 2 - n // 2 == b[1]:
                return "TRUE"
    # 15 色道具本身也算落点标记（L5 那次落在 15 道具上，四角是 15）
    return "FALSE"
