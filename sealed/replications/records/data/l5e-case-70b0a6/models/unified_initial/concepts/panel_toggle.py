"""点面板格：若点完后 14 格集合 ≠ 目标图样标记集合，则只有被点那格变：非 14 → 14，14 → 非 14；其余面板格不变。"""
LEVEL = "L1"
SCOPE = "只看落在面板格上的 ACTION6；点完会凑成目标集合的情形 NA（归 panel_complete）；换关 NA"
NOTE = "tid 981df856 是读错（目标图样位置写死在左下），修 _lib.targets 后判对。"
EVIDENCE = ["8433f7abf0f4996c", "adaa3e1a81d59bf2", "981df856111682d4"]
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
    P, Q = panel(prev), panel(nxt)
    if completes(prev, action):
        return "NA"
    for i in range(3):
        for j in range(3):
            if (i, j) == cell:
                if (P[i][j] == 14) == (Q[i][j] == 14):
                    return "FALSE"
            elif P[i][j] != Q[i][j]:
                return "FALSE"
    return "TRUE"
