"""When a click makes the set of colour-14 cells in the right 3x3 panel equal to the set of colour-15 cells in the left 3x3 panel, the whole right panel turns to colour 2 in that same transition."""
LEVEL = "L1"
SCOPE = "ACTION6 transitions within a level; NA if panels cannot be read (layout as in level 1: right cells at rows 49/54/59, cols 24/29/34; left cells at rows 51/54/57, cols 12/15/18)"
NOTE = ""
EVIDENCE = ["b800820412efd08b"]
RR = (49, 54, 59); RC = (24, 29, 34)
LR = (51, 54, 57); LC = (12, 15, 18)


def right_set(g, col):
    return {(i, j) for i, r in enumerate(RR) for j, c in enumerate(RC)
            if all(g[r + a][c + b] == col for a in range(3) for b in range(3))}


def left_set(g):
    return {(i, j) for i, r in enumerate(LR) for j, c in enumerate(LC)
            if all(g[r + a][c + b] == 15 for a in range(2) for b in range(2))}


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:") or (ctx and ctx.get("level_prev") != ctx.get("level_next")):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    target = left_set(prev)
    if not target:
        return "NA"
    # the cell clicked, toggled
    hit = None
    for i, r in enumerate(RR):
        for j, c in enumerate(RC):
            if r <= y < r + 3 and c <= x < c + 3:
                hit = (i, j)
    if hit is None:
        return "NA"
    e = right_set(prev, 14)
    e = e ^ {hit}
    fired = len(right_set(nxt, 2)) == 9
    return "TRUE" if fired == (e == target) else "FALSE"
