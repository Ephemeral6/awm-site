"""方向动作的目标 4x4 里含 d 色(13)格时，动块不动(动作仍被受理：计数条可走)。"""
LEVEL = "L2"
SCOPE = "只看 ACTION1-4 且动块可定位、目标区含 13 色的转移；其余 NA"
NOTE = ""
EVIDENCE = ["97fdc9241012011e"]
from _lib import DIRS, piece


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS:
        return "NA"
    p = piece(prev)
    if p is None:
        return "NA"
    t0, l0, k = p
    dr, dc = DIRS[action]
    t, l = t0 + dr * k, l0 + dc * k
    cells = [(t + i, l + j) for i in range(k) for j in range(k)]
    if not all(0 <= r < 64 and 0 <= c < 64 for r, c in cells):
        return "NA"
    if not any(prev[r][c] == 13 for r, c in cells):
        return "NA"
    return "TRUE" if piece(nxt) == p else "FALSE"
