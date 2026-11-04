"""Clicking inside a right-panel cell whose 3x3 colour is 2 turns it to 14, and one that is 14 turns it to 2; nothing else on screen except the bar changes."""
LEVEL = "L1"
SCOPE = "NA when the click fires a recipe (nxt right panel all colour 2 with the clicked cell 2->2; that case belongs to pattern_fire); ACTION6 whose (x,y) lies in a 3x3 cell of colour 2 or 14 inside rows 47-63 cols 22-38; NA otherwise"
NOTE = "v3: NA when prev bar is empty - tid ab8295ee is the attempt boundary (recorded prev = stale GAME_OVER frame, level re-set by the harness). v2: tid 46e925253c9ae170 - the clicked 2-cell completed the recipe, so the panel reset and the cell stayed 2. Firing clicks carved out to pattern_fire."
EVIDENCE = ["ab8295eead0f7bb9", "46e925253c9ae170", "001cde5b0ff5bef3", "0464fe6650e3b1a7"]


def _cell(prev, action):
    if not str(action).startswith("ACTION6:"):
        return None
    x, y = map(int, action.split(":")[1].split(","))
    if not (47 <= y <= 63 and 22 <= x <= 38):
        return None
    # find maximal uniform 3x3 containing (y,x)
    v = prev[y][x]
    if v not in (2, 14):
        return None
    for t in range(y - 2, y + 1):
        for l in range(x - 2, x + 1):
            if all(prev[r][c] == v for r in range(t, t + 3) for c in range(l, l + 3)):
                return t, l, v
    return None


def assert_(prev, action, nxt, ctx=None):
    from _lib import bar
    if bar(prev) == 0:
        return "NA"
    k = _cell(prev, action)
    if k is None:
        return "NA"
    t, l, v = k
    w = 14 if v == 2 else 2
    from pattern_fire import right_set
    if len(right_set(nxt, 2)) == 9 and w == 14:
        return "NA"
    for r in range(64):
        for c in range(62):
            inside = t <= r < t + 3 and l <= c < l + 3
            exp = w if inside else prev[r][c]
            if nxt[r][c] != exp:
                return "FALSE"
    return "TRUE"


def apply(prev, action, ctx=None):
    k = _cell(prev, action)
    if k is None:
        return None
    t, l, v = k
    return {(r, c): (14 if v == 2 else 2) for r in range(t, t + 3) for c in range(l, l + 3)}
