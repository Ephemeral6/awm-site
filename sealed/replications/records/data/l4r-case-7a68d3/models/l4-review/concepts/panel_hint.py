"""ACTION6 on a pattern panel: the grid shows that panel's pattern as 0-hints (cells of the pattern are 0, every other non-e cell is 2 - a new hint replaces an old one); the block does not move; 0 ticks. A repeat click on the panel whose hint is already shown plays a demo and leaves the grid unchanged."""
LEVEL = "L1"
SCOPE = "只看 ACTION6 且点中的格子位于 L4 左上两个面板之一(rows0-9 或 rows11-20, cols0-9)；其余 NA。只在点击前网格无 e 格时断言"
NOTE = "v2: clicking the 6 panel while the f hint was shown replaced the f hint (old claim: other cells unchanged - wrong). L4 attempt 2 观测一次：点 f 面板 (4,1) -> 网格 1,3,5,7 号格 2->0，计数条不变"
EVIDENCE = ["23f3ac38570477c8", "ec77e56274ad21f9"]
from grid_toggle import _state
from _lib import piece, counter_used

PATS = {"f": {(0, 1), (1, 0), (1, 2), (2, 1)}, "six": {(0, 1), (1, 1), (2, 1)}}


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:"):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    if not (0 <= x <= 9 and (0 <= y <= 9 or 11 <= y <= 20)):
        return "NA"
    a = _state(prev)
    if any(v == 14 for row in a for v in row):
        return "NA"
    pat = PATS["f"] if y <= 9 else PATS["six"]
    b = _state(nxt)
    for i in range(3):
        for j in range(3):
            want = 0 if (i, j) in pat else 2
            if b[i][j] != want:
                return "FALSE"
    if piece(prev) != piece(nxt) or counter_used(prev) != counter_used(nxt):
        return "FALSE"
    return "TRUE"
