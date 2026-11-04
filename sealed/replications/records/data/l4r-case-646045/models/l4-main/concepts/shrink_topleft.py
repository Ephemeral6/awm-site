"""块由 4x4 变成 2x2 的那一步（缩小提交），新块的左上角与旧块左上角重合（保留左上象限）。"""
LEVEL = "L1"
SCOPE = "同关内 ACTION6、前后都能定位到块、且边长 4->2；否则 NA"
NOTE = "L1、L4 朝上，L4 朝左（attempt 3）—— 与朝向无关"
EVIDENCE = ["21c59e8375e50989"]
from _lib import same_level, piece


def assert_(prev, action, nxt, ctx=None):
    if not action.startswith("ACTION6:") or not same_level(ctx):
        return "NA"
    a, b = piece(prev), piece(nxt)
    if a is None or b is None or not (a["size"] == 4 and b["size"] == 2):
        return "NA"
    return "TRUE" if (a["top"], a["left"]) == (b["top"], b["left"]) else "FALSE"
