"""On level 4, a direction move consumes the e square (its cells turn to floor) iff the piece's top-left after the move is (33,23)."""
LEVEL = "L4"
SCOPE = "same level 4, ACTION1-4, e square present before the move, piece located after; attempt boundary NA"
NOTE = "v2: v1 read consumption from the e cells, wrong when the piece covers them (c423846f0d7a3990, f7278f241e330e97, b8acc8d0bb010655); now read from the bar rising. audit A1: replaces H_front (refuted by the 4x4 at (31,23) facing D, front over e row 34, no pickup)"
EVIDENCE = ["c423846f0d7a3990", "f7278f241e330e97", "b8acc8d0bb010655", "b1995192540e8069"]
from _lib import same_level, piece, is_boundary, DIRS, bar_e


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or not same_level(ctx) or ctx.get("level_prev") != 4 or is_boundary(prev, action, nxt):
        return "NA"
    cells = [(r, c) for r in range(45) for c in range(62) if prev[r][c] == 14]
    if not cells:
        return "NA"
    p = piece(nxt)
    if p is None:
        return "NA"
    consumed = bar_e(nxt) > bar_e(prev)   # the bar only rises on a pickup
    pred = (p["top"], p["left"]) == (33, 23)
    return "TRUE" if consumed == pred else "FALSE"
