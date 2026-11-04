"""目标图样色为 15 时凑成图样：4x4 agent 变成 2x2，左上角落在原块左上角 (r,c)，朝向保持。"""
LEVEL = "L1"
SCOPE = "只看凑成图样的那一下点击（同 panel_complete 的条件）且目标色 15 且 prev 有 4x4 agent；否则 NA"
NOTE = "依据只有一次"
EVIDENCE = ["4a6a19253b1c9168"]
from _lib import parse_click, panel_cell_at, panel, completes, agent


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    xy = parse_click(action)
    if not xy or panel_cell_at(*xy) is None:
        return "NA"
    cell = panel_cell_at(*xy)
    cm = completes(prev, action)
    if not cm or cm[0] != 15:
        return "NA"
    a = agent(prev)
    if a is None or a[3] != 4:
        return "NA"
    b = agent(nxt)
    return "TRUE" if b == (a[0], a[1], a[2], 2) else "FALSE"
