"""GAME_OVER 只发生在 prev 计时条 ≤ 2 行时；且计时条为 0 时再做一个不换关的动作必 GAME_OVER。（整数刻度模型：不赢的动作使已用刻度超过本关预算 B 即 GAME_OVER。）"""
LEVEL = "L5"
SCOPE = "同关内转移；换关（赢）的那步 NA"
NOTE = "v2 (attempt 9): 计时条 2 行（n=34）时一个 2 刻度的凑图样点击 -> GAME_OVER（S2：动作后 n>B 即结束，与动作代价有关），扩成两支。v1: 两次样本：L4 计时条为 0 后那一步直接进终点换关（NA）；L5 计时条 2 格 -> 点击后 GAME_OVER（prev 非 0，不在本条论域）。本条目前只有 0 条可判样本，是登记不是验证。"
EVIDENCE = ["1510a2ddb2d3c0c3"]
from _lib import bar_count


def assert_(prev, action, nxt, ctx=None):
    if not ctx or ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    over = ctx.get("state_next") == "GAME_OVER"
    if over and bar_count(prev) > 2:
        return "FALSE"
    if bar_count(prev) == 0 and not over:
        return "FALSE"
    if over or bar_count(prev) == 0:
        return "TRUE"
    return "NA"
