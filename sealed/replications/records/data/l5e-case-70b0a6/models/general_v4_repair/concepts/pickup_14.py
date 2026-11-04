"""agent 移动后盖住地图上 14 色道具的那一步：计时条格数增加（道具被吃掉）。"""
LEVEL = "L4"
SCOPE = "只看同关内、prev 地图上的 14 色格在 nxt 里少了的转移；否则 NA"
NOTE = "依据只有 L5 一次（38 -> 54）；增加量是否固定未知，只断言『增加』"
EVIDENCE = ["a5b5a3c73550d1d5"]
from _lib import bar_count, map_cells


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    if not (set(map_cells(prev, 14)) - set(map_cells(nxt, 14))):
        return "NA"
    return "TRUE" if bar_count(nxt) > bar_count(prev) else "FALSE"
