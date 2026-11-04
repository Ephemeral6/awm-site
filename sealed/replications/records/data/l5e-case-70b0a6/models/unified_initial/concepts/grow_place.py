"""15 色图样在 agent 为 2x2 时凑成：4x4 的位置使原 2x2 成为新 4x4 头部那半边里『面朝方向的右手边』那一块：
朝上 -> (r, c-2)；朝右 -> (r-2, c-2)；朝下 -> (r-2, c)；朝左 -> (r, c)。"""
LEVEL = "L1"
SCOPE = "只看凑成 15 色图样、prev agent 为 2x2、nxt agent 为 4x4 的点击；否则 NA"
NOTE = "attempt 3 新增。依据：attempt 2 朝上 (15,45)->(15,43)；attempt 3 朝右 (17,47)->(15,45)。朝下/朝左两支是按旋转外推，未测。"
EVIDENCE = ["2d6344b3b63cb07b", "75955b9510aed3c6"]
from _lib import completes, agent

OFF = {(-1, 0): (0, -2), (0, 1): (-2, -2), (1, 0): (-2, 0), (0, -1): (0, 0)}


def assert_(prev, action, nxt, ctx=None):
    cm = completes(prev, action)
    if not cm or cm[0] != 15:
        return "NA"
    a, b = agent(prev), agent(nxt)
    if a is None or b is None or a[3] != 2 or b[3] != 4:
        return "NA"
    dr, dc = OFF[a[2]]
    return "TRUE" if (b[0], b[1]) == (a[0] + dr, a[1] + dc) else "FALSE"
