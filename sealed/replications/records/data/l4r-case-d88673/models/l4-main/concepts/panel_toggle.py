"""ACTION6 点中右面板某格：要么该格在底色(0/2)与 14 之间翻转、其余格不变；要么（完成）面板里 14 全部消失。"""
LEVEL = "L1"
SCOPE = "条变长的转移（关/尝试边界）返回 NA；只看点中面板格的 ACTION6；换关 NA"
NOTE = ""
EVIDENCE = ["98933de0dbc1a78d", "f82e1e1122b06968", "c07136eaa0425d7c"]

from _lib import panel_cells, click_cell, same_level


def assert_(prev, action, nxt, ctx=None):
    from _lib import boundary
    if boundary(prev, nxt):
        return "NA"
    ij = click_cell(action)
    if ij is None or not same_level(ctx):
        return "NA"
    p, q = panel_cells(prev), panel_cells(nxt)
    if 14 not in q.values():
        return "TRUE"  # 完成分支（另有概念管它的后果）
    for k in p:
        if k == ij:
            ok = (p[k] == 14 and q[k] != 14) or (p[k] != 14 and q[k] == 14)
        else:
            ok = p[k] == q[k]
        if not ok:
            return "FALSE"
    return "TRUE"
