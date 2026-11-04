"""本局词汇（假设）。"""
DIRS = {"ACTION1": (-1, 0), "ACTION2": (1, 0), "ACTION3": (0, -1), "ACTION4": (0, 1)}
FLOOR = 2


def _pat(k, d):
    h = k // 2
    out = {}
    for i in range(k):
        for j in range(k):
            lead = {"U": i < h, "D": i >= h, "L": j < h, "R": j >= h}[d]
            out[(i, j)] = 9 if lead else 10
    return out


def piece(g):
    """动块 -> (top,left,k) 或 None。
    v3 读法：先找 4x4 窗口恰好等于四种朝向图样之一(一半 9 一半 a)且唯一；没有则找 2x2 图样窗口，
    v4: 与出口芯(4x4 全 a 窗口)相交的窗口一律不算——出口 9 环+a 芯能拼出假图样；且要求该 2x2 的四邻外圈没有别的 9/a 格(排除出口 9 环+a 芯的假匹配)，唯一才返回。
    v1(rows15-46 计数)在 L4 把出口 a 芯误计；v2(连通块)在动块贴着出口时与出口并块。"""
    H, W = len(g), 62
    core = set()
    for t in range(H - 3):
        for l in range(W - 3):
            if all(g[t + i][l + j] == 10 for i in range(4) for j in range(4)):
                core |= {(t + i, l + j) for i in range(4) for j in range(4)}
    for k in (4, 2):
        hits = []
        pats = [_pat(k, d) for d in "UDLR"]
        for t in range(H - k + 1):
            for l in range(W - k + 1):
                if g[t][l] not in (9, 10):
                    continue
                if any((t + i, l + j) in core for i in range(k) for j in range(k)):
                    continue
                for P in pats:
                    if all(g[t + i][l + j] == v for (i, j), v in P.items()):
                        hits.append((t, l))
                        break
        if k == 2:
            iso = []
            for t, l in hits:
                ring = [(t - 1, l), (t - 1, l + 1), (t + 2, l), (t + 2, l + 1),
                        (t, l - 1), (t + 1, l - 1), (t, l + 2), (t + 1, l + 2)]
                if all(not (0 <= r < H and 0 <= c < W) or g[r][c] not in (9, 10) for r, c in ring):
                    iso.append((t, l))
            hits = iso
        if len(hits) == 1:
            return (hits[0][0], hits[0][1], k)
        if len(hits) > 1:
            return None
    return None


def counter_used(g):
    """右侧 2 列计数条：从顶往下已变 0 的行数。"""
    n = 0
    for r in range(64):
        if g[r][62] == 0 and g[r][63] == 0:
            n += 1
        else:
            break
    return n
