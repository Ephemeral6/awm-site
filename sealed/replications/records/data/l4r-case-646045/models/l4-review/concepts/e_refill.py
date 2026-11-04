"""When the e square's cells all turn to floor (colour 2) in a step, the bar gains at least 8 notches (16 rows of 14)."""
LEVEL = "L4"
SCOPE = "same level, steps where the board's colour-14 cell count changes; attempt boundary NA; otherwise NA"
NOTE = "v2: v1 also fired when the 4x4 merely covered the square (64f92cc80404e92e, 0019a4b146a56062); now only cells turning to floor count. attempt 6: a 2x2 piece moving to overlap the e square consumed it; the bar went 12 -> 44 rows of 14 (+16 notches). A 4x4 covering it fully (attempts 2 and 6) did NOT consume it"
EVIDENCE = ["64f92cc80404e92e", "0019a4b146a56062", "c423846f0d7a3990"]
from _lib import same_level, e_obj, bar_e, is_boundary


def assert_(prev, action, nxt, ctx=None):
    if not same_level(ctx) or is_boundary(prev, action, nxt):
        return "NA"
    cells = [(r, c) for r in range(45) for c in range(62) if prev[r][c] == 14]
    if not cells:
        return "NA"
    consumed = all(nxt[r][c] == 2 for r, c in cells)
    if not consumed:
        return "NA"   # still there, or only covered by the piece (colours 9/10)
    return "TRUE" if bar_e(nxt) - bar_e(prev) >= 32 else "FALSE"
