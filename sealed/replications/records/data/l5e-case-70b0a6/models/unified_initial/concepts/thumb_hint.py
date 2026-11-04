"""点击某个目标图样缩略图（10x10 的 3 色框内）：面板上非 14 的格子里，该图样的标记格变 0、其余变 2；agent 不动。"""
LEVEL = "L1"
SCOPE = "只看落在某个目标图样框内的 ACTION6；否则 NA"
NOTE = "attempt 2 新增；依据一次（点 11 图样缩略图，面板出现 0 色提示，与 L1-L3 开局面板的 0 色提示同形）。计时条那一步没少，是否免费未定。"
EVIDENCE = ["c921e7404a1429b1"]
from _lib import parse_click, targets, panel, agent


def _frames(g):
    out = []
    for r in range(0, 55):
        for c in range(0, 55):
            if all(g[r][c + j] == 3 and g[r + 9][c + j] == 3 for j in range(10)) and \
               all(g[r + i][c] == 3 and g[r + i][c + 9] == 3 for i in range(10)) and \
               not any(g[r + i][c + j] == 3 for i in range(1, 9) for j in range(1, 9)):
                marks = {(i, j) for i in range(3) for j in range(3) if g[r + 1 + 3 * i][c + 1 + 3 * j] != 2}
                out.append((r, c, marks))
    return out


def assert_(prev, action, nxt, ctx=None):
    xy = parse_click(action)
    if not xy:
        return "NA"
    x, y = xy
    hit = [m for (r, c, m) in _frames(prev) if r <= y <= r + 9 and c <= x <= c + 9]
    if len(hit) != 1:
        return "NA"
    P, Q = panel(prev), panel(nxt)
    for i in range(3):
        for j in range(3):
            if P[i][j] == 14:
                continue
            want = 0 if (i, j) in hit[0] else 2
            if Q[i][j] != want:
                return "FALSE"
    return "TRUE" if agent(prev) == agent(nxt) else "FALSE"
