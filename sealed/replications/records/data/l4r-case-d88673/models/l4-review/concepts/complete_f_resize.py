"""左图例为 15(f) 图案时：一次 ACTION6 让面板 14 格从有变无（完成），玩家边长在 4 与 2 之间切换。"""
LEVEL = "L1"
SCOPE = "条变长的转移（关/尝试边界）返回 NA；只看点中面板格的 ACTION6、同关、图例颜色含 15、前帧面板至少 2 格为 14、后帧面板全为 2（完成）；定位不到玩家 NA"
NOTE = "v2: 单格 14 被点回底色(f82e1e1122b06968, 873aee922d1d07ce)也让 14 消失，但那不是完成，收窄完成判据。缩小时保左上角（两次）；放大时锚点只见过一次（左下保持），不写进主张"
EVIDENCE = ["f82e1e1122b06968", "873aee922d1d07ce", "d95690ccfecf1c7c", "2cb5ee799203a0ce"]

from _lib import panel_cells, click_cell, same_level, legend_colors, me


def assert_(prev, action, nxt, ctx=None):
    from _lib import boundary
    if boundary(prev, nxt):
        return "NA"
    if click_cell(action) is None or not same_level(ctx):
        return "NA"
    if 15 not in legend_colors(prev):
        return "NA"
    pv = list(panel_cells(prev).values()); qv = list(panel_cells(nxt).values())
    if not (pv.count(14) >= 2 and set(qv) == {2}):
        return "NA"
    a, b = me(prev), me(nxt)
    if a is None or b is None:
        return "NA"
    return "TRUE" if {a[2], b[2]} == {2, 4} else "FALSE"
