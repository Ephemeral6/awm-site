"""ACTION1..4: if the block moves at all, it moves 1..side cells in the action's direction (straight, keeping its size): a full side when the whole target square is floor, otherwise only as far as the floor allows."""
LEVEL = "L1"
SCOPE = "ACTION1-4 only; NA if block not located in either frame, if it did not move, or on level change"
NOTE = "v4: tid 891d9c73 (L5) - 4x4 at r15 c43, ACTION4: full target c47 blocked at rows 17-18, block moved 2 to c45. Claim weakened to 0 < distance <= side in the action direction. v3: NA when prev bar is empty - tid 6ea51469 is an attempt boundary (recorded prev = stale GAME_OVER frame). v2: was 'exactly 4 cells'; generalised to side length after the block shrank to 2x2 (untested at side 2 when written)"
EVIDENCE = ["891d9c7343ca7295", "6ea5146914c97dba", "3f5956007e12ca17", "827b6b560fc0b5bb", "5580ee1a82842888", "e3b6a995fbd25760"]
from _lib import block3, DIRS


def assert_(prev, action, nxt, ctx=None):
    from _lib import bar
    if bar(prev) == 0:
        return "NA"
    if action not in DIRS or (ctx and ctx.get("level_prev") != ctx.get("level_next")):
        return "NA"
    a, b = block3(prev), block3(nxt)
    if a is None or b is None or a[:2] == b[:2]:
        return "NA"
    dr, dc = DIRS[action]
    s = a[2]
    if b[2] != s:
        return "FALSE"
    for k in range(1, s + 1):
        if (b[0] - a[0], b[1] - a[1]) == (dr * k, dc * k):
            return "TRUE"
    return "FALSE"
