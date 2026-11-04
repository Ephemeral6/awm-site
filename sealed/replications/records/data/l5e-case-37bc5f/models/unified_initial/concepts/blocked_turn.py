"""A direction action that is processed but does not move the block (blocked) still turns it: afterwards the colour-9 half faces the action's direction, and the block keeps its position and size."""
LEVEL = "L2"
SCOPE = "ACTION1-4 within a level, block located in both frames, the action was processed (the frame changed somewhere), and the block did not move; NA otherwise (a whole-frame-identical step, e.g. the swallowed first action after /reset, is NA)"
NOTE = "v1 attempt 4, L5 tid 8e11f274: 4x4 at r37 c49 facing down, ACTION4 blocked -> facing right. L3 tid 97fdc924 (blocked push down while facing down) agrees."
EVIDENCE = ["8e11f274ee90b7ce"]
from _lib import block3, DIRS


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or (ctx and ctx.get("level_prev") != ctx.get("level_next")):
        return "NA"
    if prev == nxt:
        return "NA"
    a, b = block3(prev), block3(nxt)
    if a is None or b is None or a != b:
        return "NA"
    t, l, s = a
    h = s // 2
    d = DIRS[action]
    for r in range(s):
        for c in range(s):
            if d == (-1, 0): front = r < h
            elif d == (1, 0): front = r >= h
            elif d == (0, -1): front = c < h
            else: front = c >= h
            if nxt[t + r][l + c] != (9 if front else 10):
                return "FALSE"
    return "TRUE"
