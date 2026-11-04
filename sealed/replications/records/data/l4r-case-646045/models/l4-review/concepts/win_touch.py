"""方向键过关当且仅当：块整步平移（步长=边长）后的外框会碰到场上非块的 9/10 格（目标框）。"""
LEVEL = "L5"
SCOPE = "GAME_OVER steps NA (attempt 7: c20aa696def56d6b, touch move at budget -1 ended the game with no win; cannot tell whether touch or budget decided); ACTION1-4、点前能定位到块；点前帧必须是同一关（level_prev 有值）；否则 NA"
NOTE = "L1 是块完全进入框内一格，L2 是块与框错位重叠也过——所以只要求碰到"
EVIDENCE = ["c20aa696def56d6b", "0ba05691632adb10"]
from _lib import piece, DIRS


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or not ctx or ctx.get("level_prev") is None or ctx.get("state_next") == "GAME_OVER":
        return "NA"
    p = piece(prev)
    if p is None:
        return "NA"
    s = p["size"]
    dr, dc = DIRS[action]
    t, l = p["top"] + dr * s, p["left"] + dc * s
    own = {(r, c) for r in range(p["top"], p["top"] + s) for c in range(p["left"], p["left"] + s)}
    hit = False
    for r in range(t, t + s):
        for c in range(l, l + s):
            if 0 <= r < 64 and 0 <= c < 62 and (r, c) not in own and prev[r][c] in (9, 10):
                hit = True
    won = ctx.get("level_next") != ctx.get("level_prev")
    return "TRUE" if hit == won else "FALSE"
