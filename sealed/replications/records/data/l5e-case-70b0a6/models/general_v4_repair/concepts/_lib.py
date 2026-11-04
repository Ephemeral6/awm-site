"""本局词汇：两条以上概念共用的判据写在这里。

**它们是假设，不是事实。**
"""
STEP = 4
DIRS = {"ACTION1": (-1, 0), "ACTION2": (1, 0), "ACTION3": (0, -1), "ACTION4": (0, 1)}
HEAD, TAIL = 9, 10


def agent(g, sizes=(4, 2)):
    """返回 (top,left,dir,size)：size x size 块，头所在一半全 9、另一半全 10；dir 是头所在方向。
    每种尺寸先找；恰好一个命中才返回，否则 None。（L1 里 4x4 被缩成 2x2，所以两种尺寸都认。）"""
    found = []
    for n in sizes:
        h2 = n // 2
        for r in range(0, 65 - n):
            for c in range(0, 65 - n):
                for d in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    ok = True
                    for i in range(n):
                        for j in range(n):
                            if d == (0, -1): head = j < h2
                            elif d == (0, 1): head = j >= h2
                            elif d == (-1, 0): head = i < h2
                            else: head = i >= h2
                            if g[r + i][c + j] != (HEAD if head else TAIL):
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        # 尾半边外侧四邻不许有 10 —— 排除终点框（10 芯更大）里被误认的窗口
                        # v2: 原写法禁止整圈有 9/10，agent 贴着终点框时会认不出（tid 87597ca9，读错不是规则错）
                        for i in range(-1, n + 1):
                            for j in range(-1, n + 1):
                                if (0 <= i < n and 0 <= j < n) or not (0 <= r + i < 64 and 0 <= c + j < 64):
                                    continue
                                if (i in (-1, n)) and (j in (-1, n)):
                                    continue
                                ii, jj = min(max(i, 0), n - 1), min(max(j, 0), n - 1)
                                if g[r + ii][c + jj] == TAIL and g[r + i][c + j] == TAIL:
                                    ok = False
                    if ok:
                        # 排除 4x4 里被误认成 2x2 的情形：只在 4x4 没命中时收 2x2
                        found.append((r, c, d, n))
        if found:
            break
    return found[0] if len(found) == 1 else None


def bar_count(g):
    """右缘第 62 列里颜色 14 的格数（计时条读数）。"""
    return sum(1 for r in range(64) if g[r][62] == 14)


import json as _json, hashlib as _hl, os as _os
_INIT = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "work", "initial_frames.json")


def is_initial(g):
    """g 是否某关开局帧（开局帧哈希登记在 work/initial_frames.json，由 reset/换关时记录）。"""
    try:
        hs = set(_json.load(open(_INIT)).values())
    except Exception:
        return False
    return _hl.md5(_json.dumps(g, separators=(",", ":")).encode()).hexdigest() in hs


PANEL_R = (49, 54, 59)   # 右下 3x3 面板每格 3x3 的左上角行
PANEL_C = (24, 29, 34)   # 列
TGT_R = (51, 54, 57)     # 左下目标图样 3x3（每格 2x2）的左上角行
TGT_C = (12, 15, 18)


def panel_cell_at(x, y):
    """点击坐标 (x=列, y=行) 落在哪个面板格 -> (i,j)，否则 None。
    v3 (attempt 8): 点击区是把整个面板（行 47-63、列 22-38，含外框和格间缝）切成 3x3：
    (27,50)、(23,50)、(23,48) 都切换了 (0,0)。切分线按画出来的格子中点取：列 22-27/28-32/33-38，行同理。"""
    if not (47 <= y <= 63 and 22 <= x <= 38):
        return None
    def band(v, lo):
        return 0 if v <= lo + 5 else (1 if v <= lo + 10 else 2)
    return (band(y, 47), band(x, 22))


def panel(g):
    return [[g[PANEL_R[i]][PANEL_C[j]] for j in range(3)] for i in range(3)]


def target_frame_cells(g):
    """所有 10x10 目标图样框占的格子（含框）。"""
    out = set()
    for r in range(0, 55):
        for c in range(0, 55):
            if all(g[r][c + j] == 3 and g[r + 9][c + j] == 3 for j in range(10)) and                all(g[r + i][c] == 3 and g[r + i][c + 9] == 3 for i in range(10)) and                not any(g[r + i][c + j] == 3 for i in range(1, 9) for j in range(1, 9)):
                out |= {(r + i, c + j) for i in range(10) for j in range(10)}
    return out


def map_cells(g, color):
    """地图上（不含目标图样框、不含面板区 47 行以下、不含计时条 62-63 列）某色的格子。"""
    tf = target_frame_cells(g)
    return [(r, c) for r in range(47) for c in range(62) if g[r][c] == color and (r, c) not in tf]


def targets(g):
    """所有目标图样：10x10 的 3 色方框（内 8x8 无 3），标记格在框内偏移 (1,4,7)。
    返回 [(色, 标记集合)]。v2：L4 起目标图样搬到左上、而且有两个，原先写死左下读错了（tid 981df856）。"""
    out = []
    for r in range(0, 55):
        for c in range(0, 55):
            if any(g[r][c + j] != 3 or g[r + 9][c + j] != 3 for j in range(10)):
                continue
            if any(g[r + i][c] != 3 or g[r + i][c + 9] != 3 for i in range(10)):
                continue
            if any(g[r + i][c + j] == 3 for i in range(1, 9) for j in range(1, 9)):
                continue
            marks = {}
            for i in range(3):
                for j in range(3):
                    v = g[r + 1 + 3 * i][c + 1 + 3 * j]
                    if v != 2:
                        marks[(i, j)] = v
            cols = set(marks.values())
            out.append((cols.pop() if len(cols) == 1 else None, set(marks)))
    return out


def target(g):
    """兼容旧接口：只有一个目标图样时返回它，否则 (None, None)。"""
    t = targets(g)
    return t[0] if len(t) == 1 else (None, None)


def completes(prev, action):
    """这一下点击凑成了哪个目标图样：返回 (色, 集合) 或 None。"""
    xy = parse_click(action)
    if not xy:
        return None
    cell = panel_cell_at(*xy)
    if cell is None:
        return None
    P = panel(prev)
    sel = {(i, j) for i in range(3) for j in range(3) if P[i][j] == 14} ^ {cell}
    for col, T in targets(prev):
        if sel == T:
            return (col, T)
    return None


def parse_click(action):
    if not str(action).startswith("ACTION6:"):
        return None
    x, y = action.split(":")[1].split(",")
    return int(x), int(y)
