"""本局词汇（假设，不是事实）。坐标 (row, col)。"""
from geo import components, bbox

BAR_COLS = (62, 63)          # 右缘计量条
BAR_FULL, BAR_EMPTY = 14, 0
PANEL_ROWS = (49, 54, 59)    # 右下 3x3 面板，每格 3x3
PANEL_COLS = (24, 29, 34)
SEL = 14                     # 点选高亮色
PLAY_MAX_ROW = 45            # 场地在这一行之上
DIRS = {"ACTION1": (-1, 0), "ACTION2": (1, 0), "ACTION3": (0, -1), "ACTION4": (0, 1)}


def same_level(ctx):
    return bool(ctx) and ctx.get("level_prev") == ctx.get("level_next") and ctx.get("level_prev") is not None


def bar_e(g):
    return sum(1 for r in range(64) for c in BAR_COLS if g[r][c] == BAR_FULL)


def panel(g):
    """3x3 面板每格颜色（取格子左上角）；格内不纯色返回 None。"""
    out = []
    for r0 in PANEL_ROWS:
        row = []
        for c0 in PANEL_COLS:
            cs = {g[r][c] for r in range(r0, r0 + 3) for c in range(c0, c0 + 3)}
            row.append(cs.pop() if len(cs) == 1 else None)
        out.append(row)
    return out


def panel_cell_at(x, y):
    for i, r0 in enumerate(PANEL_ROWS):
        for j, c0 in enumerate(PANEL_COLS):
            if r0 <= y < r0 + 3 and c0 <= x < c0 + 3:
                return (i, j)
    return None


def piece(g):
    """可动块：场地里 9∪10 的连通块，外框为正方形、边长 2 或 4、两色各占一半。
    返回 dict(top,left,size,face) ；face = 9 那一半所在方向 'U','D','L','R'。找不到/不唯一返回 None。"""
    cells = [(r, c) for r in range(PLAY_MAX_ROW) for c in range(62) if g[r][c] in (9, 10)]
    found = []
    for comp in components(cells):
        t, b, l, rr = bbox(comp)
        s = b - t + 1
        if s != rr - l + 1 or s not in (2, 4) or len(comp) != s * s:
            continue
        h = s // 2
        nine = {(r, c) for r, c in comp if g[r][c] == 9}
        if len(nine) != s * h:
            continue
        sides = {
            'U': {(r, c) for r, c in comp if r < t + h},
            'D': {(r, c) for r, c in comp if r >= t + h},
            'L': {(r, c) for r, c in comp if c < l + h},
            'R': {(r, c) for r, c in comp if c >= l + h},
        }
        f = [k for k, v in sides.items() if v == nine]
        if len(f) != 1:
            continue
        found.append({"top": t, "left": l, "size": s, "face": f[0]})
    if len(found) == 1:
        return found[0]
    if found:
        return None
    # 后备：块贴着目标框时连通块会粘在一起 —— 改用 4x4 窗口找「一半全 9、一半全 10」的正方形
    win = []
    for t in range(PLAY_MAX_ROW - 3):
        for l in range(59):
            cs = [(r, c) for r in range(t, t + 4) for c in range(l, l + 4)]
            if any(g[r][c] not in (9, 10) for r, c in cs):
                continue
            nine = {(r, c) for r, c in cs if g[r][c] == 9}
            if len(nine) != 8:
                continue
            sides = {'U': {(r, c) for r, c in cs if r < t + 2}, 'D': {(r, c) for r, c in cs if r >= t + 2},
                     'L': {(r, c) for r, c in cs if c < l + 2}, 'R': {(r, c) for r, c in cs if c >= l + 2}}
            f = [k for k, v in sides.items() if v == nine]
            if len(f) == 1:
                win.append({"top": t, "left": l, "size": 4, "face": f[0]})
    return win[0] if len(win) == 1 else None


# 换 attempt 的那一条转移：prev 是上一次 attempt 的 GAME_OVER 帧，nxt 是服务重开的关。不是世界规则的样本。
ATTEMPT_BOUNDARY = {"ecc182fb09e2e348", "fce373ad12535a61", "f34655e345d326f6", "57077599351d5187", "6a48aac6de977a1e", "13c87adadedec9e7", "f24f3579c4d9a836", "51e0835791ca0303"}


def is_boundary(prev, action, nxt):
    import hashlib, json
    h = hashlib.md5()
    h.update(json.dumps(prev, separators=(",", ":")).encode())
    h.update(str(action).encode())
    h.update(json.dumps(nxt, separators=(",", ":")).encode())
    return h.hexdigest()[:16] in ATTEMPT_BOUNDARY


def e_obj(g):
    """Cells of colour 14 on the board (rows < 45, cols < 62): the e-square pickup (attempt 6)."""
    return sum(1 for r in range(45) for c in range(62) if g[r][c] == 14)
