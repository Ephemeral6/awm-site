"""After a direction action that moves the block, its colour-9 half is the half on the side of the movement direction (colour-10 the opposite half)."""
LEVEL = "L1"
SCOPE = "ACTION1-4 where block moved, same level; NA otherwise"
NOTE = "v3: NA when prev bar is empty - tid 6ea51469 is an attempt boundary (recorded prev = stale GAME_OVER frame). v2: added NA on level change - tid 97aa9084e4b51928 was the level-1->2 switch where a new level's block was read as the moved one"
EVIDENCE = ["97aa9084e4b51928", "3f5956007e12ca17", "827b6b560fc0b5bb", "5580ee1a82842888", "e3b6a995fbd25760"]
from _lib import block3, DIRS


def _expect(t, l, d, s=4):
    out = {}
    h = s // 2
    for r in range(s):
        for c in range(s):
            if d == (-1, 0): front = r < h
            elif d == (1, 0): front = r >= h
            elif d == (0, -1): front = c < h
            else: front = c >= h
            out[(t + r, l + c)] = 9 if front else 10
    return out


def assert_(prev, action, nxt, ctx=None):
    from _lib import bar
    if bar(prev) == 0:
        return "NA"
    if action not in DIRS or (ctx and ctx.get("level_prev") != ctx.get("level_next")):
        return "NA"
    a, b = block3(prev), block3(nxt)
    if a is None or b is None or a[:2] == b[:2]:
        return "NA"
    e = _expect(b[0], b[1], DIRS[action], b[2])
    return "TRUE" if all(nxt[r][c] == v for (r, c), v in e.items()) else "FALSE"


def apply(prev, action, ctx=None):
    if action not in DIRS:
        return None
    a = block3(prev)
    if a is None:
        return None
    d = DIRS[action]
    return _expect(a[0] + a[2] * d[0], a[1] + a[2] * d[1], d, a[2])
