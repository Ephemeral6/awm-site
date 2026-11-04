"""ACTION6 点在右下 3x3 网格的某一格(3x3 像素块)上，那一格在 e 和原色之间切换；网格其余格不变（图样未凑齐时）。"""
LEVEL = "L1"
SCOPE = "只看 ACTION6 且点落在网格 9 个格块之一；凑齐事件(点完后网格无 e 且被点格原本不是 e)时 NA——那一支归 pattern_* 概念"
NOTE = "v3: tid 81a76158dafd4548 completed the 6 pattern by toggling a cell OFF ({0,1,4,7} -> {1,4,7}); completion exemption widened. v2: tid d3f8d3aa32dd67db 是 L2 凑齐事件(prev 只有 2 个 e，旧判据要求>=3 漏掉)；改成结构判据"
EVIDENCE = ["a5a33aff38ce1384", "52194cf4a7592f7a", "b0d49325f305875f", "d3f8d3aa32dd67db", "81a76158dafd4548"]
ROWS = [(49, 51), (54, 56), (59, 61)]
COLS = [(25, 27), (30, 32), (35, 37)]


def _cell(x, y):
    for i, (r0, r1) in enumerate(ROWS):
        for j, (c0, c1) in enumerate(COLS):
            if r0 <= y <= r1 and c0 <= x <= c1:
                return i, j
    return None


def _state(g):
    return [[g[ROWS[i][0]][COLS[j][0]] for j in range(3)] for i in range(3)]


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:"):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    c = _cell(x, y)
    if c is None:
        return "NA"
    a, b = _state(prev), _state(nxt)
    i, j = c
    if all(v != 14 for row in b for v in row) and sum(v == 14 for row in a for v in row) >= 2:
        return "NA"   # completion event (by toggling on OR off) - belongs to pattern_* concepts
    for u in range(3):
        for v in range(3):
            if (u, v) == (i, j):
                ok = (b[u][v] == 14) if a[u][v] != 14 else (b[u][v] != 14)
            else:
                ok = b[u][v] == a[u][v]
            if not ok:
                return "FALSE"
    return "TRUE"
