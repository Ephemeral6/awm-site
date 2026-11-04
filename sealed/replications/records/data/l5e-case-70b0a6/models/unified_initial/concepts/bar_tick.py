"""右缘计时条（第62列颜色14格数）在不凑成面板图样、且不踩到地图上 14 色道具的动作上，每步要么不变要么恰好少 2。"""
LEVEL = "L4"
SCOPE = "同关内转移；换关 NA；凑成面板图样的那一下点击 NA（a97af443 那一下少了 6，归别处）"
NOTE = "v3: 被 a5b5a3c73550d1d5 打脸（agent 踩上 14 色 2x2 道具，计时条 +16）；缩 scope：踩 14 道具那步 NA，归 pickup_14。tid 981df856 是读错（目标图样位置写死在左下），修 _lib.targets 后判对。v2: 原版断言所有动作变化∈{0,-2}，被 a97af4438459243d（L2 凑成 11 色图样传送那一下 -6）打脸；缩 scope 排除凑图样点击"
EVIDENCE = ["3c367435761b27cf", "44fc0c79a605c5b4", "a97af4438459243d", "981df856111682d4", "a5b5a3c73550d1d5"]
from _lib import bar_count, completes, map_cells


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    if completes(prev, action):
        return "NA"
    if set(map_cells(prev, 14)) - set(map_cells(nxt, 14)):
        return "NA"
    d = bar_count(nxt) - bar_count(prev)
    return "TRUE" if d in (0, -2) else "FALSE"
