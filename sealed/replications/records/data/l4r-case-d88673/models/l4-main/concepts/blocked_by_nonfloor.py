"""ACTION1-4：若目标矩形（沿方向平移 s 后的 s×s 区域）在前帧里全是地板色 2，玩家就移过去；若含 5（背景），玩家走不满 s（可能走一个 2 格子步）。"""
LEVEL = "L2"
SCOPE = "条变长的转移（关/尝试边界）返回 NA；前后帧逐格完全相同（动作未被受理，如开局第一步）返回 NA；只看 ACTION1-4、同关、前后都能定位玩家；目标区里出现 2/5 以外的颜色时返回 NA（未测）"
NOTE = "v3(attempt 8): ece0a2f5605e3199 — 目标区含墙时仍可能走一个 2 格子步；改为「目标区含墙 ⇒ 没走满 s」。v2: 开局第一个 ACTION1(2b3e5ed8fe7b90de) 整帧无差却目标区全是地板——那一步是未被受理而非被挡，缩 scope。level1 曾误读颈部列号（35-36 读成 37-38），先前「颈部挡人」的结论作废"
EVIDENCE = ["ece0a2f5605e3199", "2b3e5ed8fe7b90de", "3f5956007e12ca17", "b18cd3be04400a73", "5ff7ab20b6e81f1d"]

from _lib import me, DIRS, same_level


def assert_(prev, action, nxt, ctx=None):
    from _lib import boundary
    if boundary(prev, nxt):
        return "NA"
    if prev == nxt:
        return "NA"
    if action not in DIRS or not same_level(ctx):
        return "NA"
    a, b = me(prev), me(nxt)
    if a is None or b is None:
        return "NA"
    r0, c0, s, _ = a
    dr, dc = DIRS[action]
    nr, nc = r0 + dr * s, c0 + dc * s
    cols = set()
    for y in range(nr, nr + s):
        for x in range(nc, nc + s):
            if not (0 <= y < 64 and 0 <= x < 64):
                cols.add(-1)
            else:
                cols.add(prev[y][x])
    moved = (b[0], b[1]) != (r0, c0)
    if cols == {2}:
        return "TRUE" if moved else "FALSE"
    if cols <= {2, 5} and 5 in cols:
        full = (b[0], b[1]) == (nr, nc)
        return "TRUE" if not full else "FALSE"
    return "NA"
