"""计时条读数为 0（第 62 列无 14）时再做一个不换关的动作：state 变成 GAME_OVER。"""
LEVEL = "L5"
SCOPE = "只看 prev 计时条为 0 的转移；换关（赢）的那步 NA"
NOTE = "两次样本：L4 计时条为 0 后那一步直接进终点换关（NA）；L5 计时条 2 格 -> 点击后 GAME_OVER（prev 非 0，不在本条论域）。本条目前只有 0 条可判样本，是登记不是验证。"
EVIDENCE = ["1510a2ddb2d3c0c3"]
from _lib import bar_count


def assert_(prev, action, nxt, ctx=None):
    if bar_count(prev) != 0 or not ctx:
        return "NA"
    if ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    return "TRUE" if ctx.get("state_next") == "GAME_OVER" else "FALSE"
