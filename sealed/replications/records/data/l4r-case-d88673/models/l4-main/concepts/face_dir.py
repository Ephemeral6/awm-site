"""ACTION1-4 之后（无论移没移动），玩家的 9 那一半朝向该动作方向（上/下/左/右）。"""
LEVEL = "L1"
SCOPE = "条变长的转移（关/尝试边界）返回 NA；前后帧逐格完全相同（动作未被受理，如开局第一步）返回 NA；只看 ACTION1-4；换关 NA；动作后定位不到玩家 NA"
NOTE = "v2: 开局第一个 ACTION1(2b3e5ed8fe7b90de) 整帧无差却目标区全是地板——那一步是未被受理而非被挡，缩 scope。依据：被墙挡住的 ACTION1 只把朝向转成向上（b1c8119a84f96fc4）"
EVIDENCE = ["2b3e5ed8fe7b90de", "b1c8119a84f96fc4", "3f5956007e12ca17"]

from _lib import me, same_level

FACE = {"ACTION1": "up", "ACTION2": "down", "ACTION3": "left", "ACTION4": "right"}


def assert_(prev, action, nxt, ctx=None):
    from _lib import boundary
    if boundary(prev, nxt):
        return "NA"
    if prev == nxt:
        return "NA"
    if action not in FACE or not same_level(ctx):
        return "NA"
    b = me(nxt)
    if b is None:
        return "NA"
    return "TRUE" if b[3] == FACE[action] else "FALSE"
