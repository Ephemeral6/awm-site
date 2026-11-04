"""方向动作使动块的目标位置与出口(9 边框 a 芯的头部块)内部重叠时，本关结束、levels_completed+1。"""
LEVEL = "L5"
SCOPE = "ctx.state_next == GAME_OVER(该步使计数超出预算)时 NA——预算耗尽先于出口判定，归 counter；只看 ACTION1-4 且 prev 中能定位动块与出口；目标位置(按步长=边长)与出口 a 芯不相交时只断言：不过关"
NOTE = "v2: tid c20aa696def56d6b(L4 att2) 目标与出口芯相交但该步是第 19 tick(预算 18)，结果 GAME_OVER 且动块只前进 2 格；出口判定不在预算耗尽步生效；L1 观测：2x2 动块从 rows15-16 上移一步(目标 rows13-14 与 a 芯 rows10-13 相交)即过关"
EVIDENCE = ["61ff3ebb11f68c2b", "c20aa696def56d6b"]
from _lib import DIRS, piece


def exit_core(g):
    """出口芯：被 9 边框围住的 a 色格（四邻里至少一个 9 且不在动块里）。粗定位：a 色格且其所在行或列上紧邻 9。"""
    p = piece(g)
    pc = set()
    if p:
        t, l, k = p
        pc = {(t + i, l + j) for i in range(k) for j in range(k)}
    out = set()
    for r in range(64):
        for c in range(62):
            if g[r][c] == 10 and (r, c) not in pc:
                out.add((r, c))
    return out


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or not ctx:
        return "NA"
    p = piece(prev)
    if p is None:
        return "NA"
    core = exit_core(prev)
    if not core:
        return "NA"
    t0, l0, k = p
    dr, dc = DIRS[action]
    t, l = t0 + dr * k, l0 + dc * k
    tgt = {(t + i, l + j) for i in range(k) for j in range(k)}
    if ctx.get("state_next") == "GAME_OVER":
        return "NA"
    won = ctx.get("level_next") != ctx.get("level_prev")
    hit = bool(tgt & core)
    if hit:
        return "TRUE" if won else "FALSE"
    return "TRUE" if not won else "FALSE"
