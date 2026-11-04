"""ACTION1-4 的目标块（平移一个边长 n）里含墙 5 或 13 块、且不碰终点框时：agent 朝该方向平移 k 格，k 是 {0,2,..,n-2} 中使整块落在地板上的最大值，并转向该方向；除此与计时条（列 62-63）外整帧不变。"""
LEVEL = "L2"
SCOPE = "只看 ACTION1-4，prev 能定位 agent，目标块含 5 或 13 且不含 9/10；否则 NA；出界 NA"
NOTE = "v4.2: 腾空格露出身下的 11 标记 (20,33)/(20,36)，期望帧当成地板而判错；改为不断言腾空格。v4.1: 滑动判据的地板集漏了 11/15（落点标记、15 道具都在地板上，可走），在 718146ddcc560be2（4x4 在 11 标记框里向上滑 2 格）上判 FALSE；读错不是规则错，补进地板集。v4: v3 断言 agent 原地不动，被 6ea85a34ed9606cb 打脸（L5 4x4 在 (15,43) 向右，满步目标含墙，实际滑了 2 格到 (15,45)）；扩成『滑到能去的最远偶数格』。之前 3 次被挡都是紧邻障碍，k=0，仍判对。v3: v2 断言 agent 整块不变，被 a53f1c315582045e 打脸（撞墙时原地转向朝下）；之前两次撞 13 块时本就朝下所以看不出。v2: 原版断言整帧不变，被 009c5a47ecee1578 打脸（被挡那步计时条少了 2，地图不变）；改为不看计时条列。只断言 5/13 两种色；其余色（6、11 等）未测，不担保"
EVIDENCE = ["9205e9c66e42cf63", "009c5a47ecee1578", "a53f1c315582045e", "6ea85a34ed9606cb", "718146ddcc560be2"]
from _lib import agent, DIRS


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS:
        return "NA"
    a = agent(prev)
    if a is None:
        return "NA"
    r, c, _, n = a
    dr, dc = DIRS[action]
    nr, nc = r + dr * n, c + dc * n
    if not (0 <= nr <= 64 - n and 0 <= nc <= 64 - n):
        return "NA"
    cells = [(nr + i, nc + j) for i in range(n) for j in range(n) if not (r <= nr + i < r + n and c <= nc + j < c + n)]
    vals = {prev[x][y] for x, y in cells}
    if vals & {9, 10} or not (vals & {5, 13}):
        return "NA"
    k = 0
    for kk in range(2, n, 2):
        tr, tc = r + dr * kk, c + dc * kk
        if all(prev[tr + i][tc + j] in (2, 9, 10, 14, 11, 15) for i in range(n) for j in range(n)):
            k = kk
        else:
            break
    exp = expected(prev, (r, c, None, n), (dr, dc), k)
    nr2, nc2 = r + dr * k, c + dc * k
    vacated = {(r + i, c + j) for i in range(n) for j in range(n)} -               {(nr2 + i, nc2 + j) for i in range(n) for j in range(n)}
    # 腾空的格子露出的是 agent 身下原来的东西（地板或 11 标记），不在帧上，不断言
    same = all(exp[x][y] == nxt[x][y] for x in range(64) for y in range(62) if (x, y) not in vacated)
    return "TRUE" if same else "FALSE"


def expected(prev, a, d, k=0):
    r, c, _, n = a
    h2 = n // 2
    g = [row[:] for row in prev]
    for i in range(n):
        for j in range(n):
            g[r + i][c + j] = 2
    r, c = r + d[0] * k, c + d[1] * k
    for i in range(n):
        for j in range(n):
            if d == (-1, 0): head = i < h2
            elif d == (1, 0): head = i >= h2
            elif d == (0, -1): head = j < h2
            else: head = j >= h2
            g[r + i][c + j] = 9 if head else 10
    return g


def apply(prev, action, ctx=None):
    if action not in DIRS:
        return None
    a = agent(prev)
    if a is None:
        return None
    exp = expected(prev, a, DIRS[action], 0)
    if assert_(prev, action, exp) != "TRUE":
        return None
    return {(r, c): exp[r][c] for r in range(64) for c in range(62)}
