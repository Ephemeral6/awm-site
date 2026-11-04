"""L5 计时条是整数刻度：每个动作 1 刻度，凑成图样的那一下点击 2 刻度，吃 14 道具 -10 刻度（该步净 -9），盘外点击 0；显示行数 = 2*ceil(32*(35-n)/35)。"""
LEVEL = "L4"
SCOPE = "只看 L5、能从本关起点重放到这一步的转移（用 transitions 里同一段 L5 的历史累计 n）；否则 NA"
NOTE = "attempt 9 新增，替代 bar_tick 的小数拟合；在 8 段 L5 记录上唯一解 (B=35, e=1, R=10, ceil)。L4 也是 B=35，L3 B=50。"
EVIDENCE = ["8bff09cfd7708cfb"]
import json, math, os
from _lib import bar_count, completes, map_cells

_HERE = os.path.dirname(os.path.abspath(__file__))


def _cost(prev, action, nxt):
    if str(action).startswith("ACTION6"):
        if completes(prev, action):
            return 2
        x, y = map(int, action.split(":")[1].split(","))
        if 22 <= x <= 38 and 47 <= y <= 63:
            return 1
        return 0
    if set(map_cells(prev, 14)) - set(map_cells(nxt, 14)):
        return 1 - 10
    return 1


def assert_(prev, action, nxt, ctx=None):
    if not ctx or ctx.get("level_prev") != 5 or ctx.get("level_next") != 5 or ctx.get("state_next") == "GAME_OVER":
        return "NA"
    if bar_count(prev) % 2 or bar_count(nxt) % 2:
        return "NA"
    # 由 prev 的显示反推 n 的可能区间，再看 nxt 是否落在 n+cost 的显示上
    ns = [n for n in range(0, 36) if 2 * math.ceil(32 * (35 - n) / 35) == bar_count(prev)]
    if not ns:
        return "NA"
    c = _cost(prev, action, nxt)
    ok = any(2 * max(0, math.ceil(32 * (35 - max(0, n + c)) / 35)) == bar_count(nxt) for n in ns)
    return "TRUE" if ok else "FALSE"
