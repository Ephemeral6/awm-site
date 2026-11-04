"""本局词汇（假设，不是事实）。

FLOOR=2, WALL/背景=5, 玩家由 9(前) 和 10/a(后) 两半组成的正方形，边长 2 或 4。
面板：右侧 3x3 面板，格子中心列 25/30/35，中心行 50/55/60，每格 3x3 像素。
"""
PANEL_COLS = (25, 30, 35)
PANEL_ROWS = (50, 55, 60)
DIRS = {"ACTION1": (-1, 0), "ACTION2": (1, 0), "ACTION3": (0, -1), "ACTION4": (0, 1)}


def _comps(g, colors, rmax=45):
    seen = set(); out = []
    for y in range(min(rmax, len(g))):
        for x in range(len(g[0])):
            if g[y][x] in colors and (y, x) not in seen:
                st = [(y, x)]; seen.add((y, x)); cs = []
                while st:
                    a, b = st.pop(); cs.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        p, q = a + da, b + db
                        if 0 <= p < rmax and 0 <= q < len(g[0]) and (p, q) not in seen and g[p][q] in colors:
                            seen.add((p, q)); st.append((p, q))
                out.append(cs)
    return out


def me(g):
    """玩家：{9,10} 连通块，bbox 为边长 s∈{2,4} 的满正方形，9 恰占一半且成一侧。返回 (r0,c0,s,facing) 或 None。"""
    found = []
    for cs in _comps(g, (9, 10)):
        ys = [a for a, _ in cs]; xs = [b for _, b in cs]
        r0, c0 = min(ys), min(xs); h = max(ys) - r0 + 1; w = max(xs) - c0 + 1
        if h != w or h not in (2, 4) or len(cs) != h * w:
            continue
        s = h; half = s // 2
        nine = {(a, b) for a, b in cs if g[a][b] == 9}
        if len(nine) != s * s // 2:
            continue
        sides = {
            "up": {(r0 + i, c0 + j) for i in range(half) for j in range(s)},
            "down": {(r0 + half + i, c0 + j) for i in range(half) for j in range(s)},
            "left": {(r0 + i, c0 + j) for i in range(s) for j in range(half)},
            "right": {(r0 + i, c0 + half + j) for i in range(s) for j in range(half)},
        }
        f = [k for k, v in sides.items() if v == nine]
        if len(f) == 1:
            found.append((r0, c0, s, f[0]))
    return found[0] if len(found) == 1 else None


def same_level(ctx):
    return ctx is not None and ctx.get("level_prev") == ctx.get("level_next")


def panel_cells(g):
    """右面板 3x3：返回 {(i,j): 主色}（取每格 3x3 的中心像素）。"""
    return {(i, j): g[r][c] for i, r in enumerate(PANEL_ROWS) for j, c in enumerate(PANEL_COLS)}


def click_cell(action):
    """ACTION6:x,y → 命中的面板格 (i,j)，否则 None。格子像素为中心 ±1。"""
    if not str(action).startswith("ACTION6:"):
        return None
    x, y = map(int, action.split(":", 1)[1].split(","))
    for i, r in enumerate(PANEL_ROWS):
        for j, c in enumerate(PANEL_COLS):
            if abs(x - c) <= 1 and abs(y - r) <= 1:
                return (i, j)
    return None


def legend_colors(g):
    """左面板（行 51-58，列 12-19）内除 2 以外的颜色集合。"""
    return {g[y][x] for y in range(51, 59) for x in range(12, 20)} - {2}


def bar(g):
    """右缘 e 条剩余行数。"""
    return sum(1 for y in range(64) if g[y][63] == 14)


def boundary(prev, nxt):
    """条变长 = 关卡/尝试边界：prev 不是这一局 nxt 的真前驱。"""
    return bar(nxt) > bar(prev)
