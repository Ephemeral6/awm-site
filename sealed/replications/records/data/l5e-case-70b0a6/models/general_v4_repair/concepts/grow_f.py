"""目标图样色为 15 时凑成图样、且 agent 是 2x2：agent 变成 4x4（朝向不变），地图上 15 色格变少（四角标记消失；15 色 2x2 道具本身还在）。"""
LEVEL = "L1"
SCOPE = "只看凑成 15 色图样的点击且 prev 里 agent 是 2x2、且按 grow_place 的 4x4 落位全在地板上；落位不够地方时 NA（见 NOTE）。不断言 4x4 落在哪（一次样本：2x2@(15,45) 朝上 -> 4x4@(15,43)）"
NOTE = "v2 (attempt 5): 被 821d9d4677ca0bb8 打脸——2x2 在 2 宽竖井 (13,21) 朝上，grow_place 落位 (13,19) 是墙：agent 不变、15 标记不变、面板照样清空、计时条照样多扣（与 L5Grid 的 grow 失败分支一致）。缩 scope 到落位能放下的情形。attempt 2 新增；初稿断言地图上无 15 色格，在自己的依据上判 FALSE（读错：15 色道具本身还在），改成『15 色格变少』。依据一次。shrink_f 的另一半：15 图样是大小切换。"
EVIDENCE = ["2d6344b3b63cb07b", "821d9d4677ca0bb8"]
from _lib import completes, agent, map_cells


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    cm = completes(prev, action)
    if not cm or cm[0] != 15:
        return "NA"
    a = agent(prev)
    if a is None or a[3] != 2:
        return "NA"
    off = {(-1, 0): (0, -2), (0, 1): (-2, -2), (1, 0): (-2, 0), (0, -1): (0, 0)}[a[2]]
    r0, c0 = a[0] + off[0], a[1] + off[1]
    if not all(0 <= r0 + i < 64 and 0 <= c0 + j < 64 and prev[r0 + i][c0 + j] in (2, 9, 10) for i in range(4) for j in range(4)):
        return "NA"
    b = agent(nxt)
    ok = b is not None and b[3] == 4 and b[2] == a[2] and len(map_cells(nxt, 15)) < len(map_cells(prev, 15))
    return "TRUE" if ok else "FALSE"
