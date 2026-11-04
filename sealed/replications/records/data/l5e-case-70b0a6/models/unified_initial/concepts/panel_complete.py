"""点面板格使 14 格集合恰好等于目标图样标记集合时：面板 9 格全部变成 2（清空）。"""
LEVEL = "L1"
SCOPE = "只看落在面板格上的 ACTION6 且点完后 14 集合 == 目标标记集合；否则 NA；换关 NA"
NOTE = "依据只有 L1 一次（目标色 15）"
EVIDENCE = ["4a6a19253b1c9168"]
from _lib import parse_click, panel_cell_at, panel, completes


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    xy = parse_click(action)
    if not xy:
        return "NA"
    cell = panel_cell_at(*xy)
    if cell is None:
        return "NA"
    Q = panel(nxt)
    if not completes(prev, action):
        return "NA"
    return "TRUE" if all(Q[i][j] == 2 for i in range(3) for j in range(3)) else "FALSE"
