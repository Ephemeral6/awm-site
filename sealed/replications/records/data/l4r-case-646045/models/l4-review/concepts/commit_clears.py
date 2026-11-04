"""v4: a panel click commits (panel all 2) iff the selection after the click equals a pattern ENABLED on this level (its legend patterns) —：提交——面板 9 格全变 2，且块被改变（L1：4x4 缩成 2x2）。"""
LEVEL = "L1"
SCOPE = "same level, ACTION6 on a panel cell; judges only whether the panel becomes all 2"
NOTE = "v4 (attempt 6): v3 (any known pattern commits) failed on 23dd8a56c8839902: the L-tromino did not commit on L4, whose legends show only PLUS and LINE. v3 (attempt 5): v2 (commit iff the clicked cell is the last 0) failed on a7d4b06feafdc043: a LINE hint was left on the panel and the PLUS selection still committed. Hints do not matter; the selection does. v2: v1 用「已选∪本格 == 0 格集」，但 0 格被点后变 14，点前看不出它原来是 0，在 21c59e8375e50989 上误判 FALSE。多选了非 0 格时是否仍提交未测。块怎么变由目标图样颜色决定（f=缩小？）—— 另立"
EVIDENCE = ["23dd8a56c8839902", "a7d4b06feafdc043", "21c59e8375e50989", "eded344d6029c02b", "916c2813ff2ba332", "c6791d78458309a6"]
from _lib import same_level, panel, panel_cell_at


PATTERNS = [
    {(0, 1), (1, 0), (1, 2), (2, 1)},   # PLUS (f legend, L1/L4)
    {(0, 0), (0, 1), (1, 1)},           # L-tromino (b legend, L2)
    {(0, 1), (1, 1), (2, 1)},           # LINE (6 legend, L3/L4)
]


# per-level data: the patterns shown in that level's legend panel(s)
LEVEL_PATTERNS = {1: [0], 2: [1], 3: [2], 4: [0, 2]}


def assert_(prev, action, nxt, ctx=None):
    if not action.startswith("ACTION6:") or not same_level(ctx):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    cell = panel_cell_at(x, y)
    if cell is None:
        return "NA"
    p, q = panel(prev), panel(nxt)
    if any(v is None for row in p + q for v in row):
        return "NA"
    sel = {(a, b) for a in range(3) for b in range(3) if p[a][b] == 14}
    sel2 = sel - {cell} if cell in sel else sel | {cell}
    allsame = all(v == 2 for row in q for v in row)
    enabled = LEVEL_PATTERNS.get(ctx.get("level_prev"))
    if enabled is None:
        return "NA"
    pred = sel2 in [PATTERNS[i] for i in enabled]
    return "TRUE" if pred == allsame else "FALSE"
