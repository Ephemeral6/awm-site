"""ACTION1-4 之后，玩家沿该方向平移 0、2、…、s 格（2 格一个子步，能走几个子步走几个；s 不变）。"""
LEVEL = "L1"
SCOPE = "条变长的转移（关/尝试边界）返回 NA；只看 ACTION1-4；换关返回 NA；前后帧任一定位不到玩家返回 NA"
NOTE = "v2(attempt 8): ece0a2f5605e3199 — 4x4 左移只走 2 格（整步目标是墙、半步是地板），旧版「0 或 s」被打脸，改为 2 格子步。v2: 04b75d4f6f442b83 是尝试边界（prev 为上一局 GAME_OVER 帧），缩 scope。"
EVIDENCE = ["ece0a2f5605e3199", "04b75d4f6f442b83", "3f5956007e12ca17", "827b6b560fc0b5bb", "6290c46c1baefeb2"]

from _lib import me, DIRS, same_level


def assert_(prev, action, nxt, ctx=None):
    from _lib import boundary
    if boundary(prev, nxt):
        return "NA"
    if action not in DIRS or not same_level(ctx):
        return "NA"
    a, b = me(prev), me(nxt)
    if a is None or b is None:
        return "NA"
    if a[2] != b[2]:
        return "FALSE"
    dr, dc = DIRS[action]
    d = (b[0] - a[0], b[1] - a[1])
    for k in range(0, a[2] + 1, 2):
        if d == (dr * k, dc * k):
            return "TRUE"
    return "FALSE"
