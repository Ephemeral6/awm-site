"""Each transition the colour-14 bar in columns 62-63 changes by a multiple of 4 cells, and it grows only when a colour-14 cell outside the bar (a board pickup) stops being colour 14 in that transition."""
LEVEL = "L4"
SCOPE = "all actions within a level; NA on level change"
NOTE = "v4: tid 88632a96 (L5) - the 2x2 block stepped exactly onto the 14-square r37-38 c49-50 and the bar grew by 36. Growth now allowed exactly when a board 14-cell is covered. v3: NA when prev bar is empty - tid ab8295ee is the attempt boundary (recorded prev = stale GAME_OVER frame, level re-set by the harness). v2: v1 said loss in {0,4}; tid b800820412efd08b (the pattern-completing click) lost 8. Widened to multiples of 4."
EVIDENCE = ["88632a961ede3ff5", "ab8295eead0f7bb9", "b800820412efd08b", "827b6b560fc0b5bb", "e3b6a995fbd25760", "3f5956007e12ca17"]
from _lib import bar


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    if bar(prev) == 0:
        return "NA"
    d = bar(prev) - bar(nxt)
    if d % 4 != 0:
        return "FALSE"
    if d >= 0:
        return "TRUE"
    covered = any(prev[r][c] == 14 and nxt[r][c] != 14 for r in range(64) for c in range(62))
    return "TRUE" if covered else "FALSE"
