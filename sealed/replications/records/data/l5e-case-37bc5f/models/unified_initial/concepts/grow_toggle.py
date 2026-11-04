"""When the plus-ring (shrink) recipe fires while the block is 2x2, the block becomes a 4x4 with the same facing whose square contains the old 2x2 square (anywhere, not only on the 15-pad)."""
LEVEL = "L1"
SCOPE = "ACTION6 transitions within a level, prev block 2x2, and the click fires the plus ring (right panel all 2 in nxt; the prev 14-cells plus the clicked cell equal cells 1,3,5,7); NA otherwise"
NOTE = "v2: tid 2d6344b3 (attempt 6) - 2x2 at r15 c45 grew to r15 c43 (top row kept, because rows 13-14 are not floor); v1 claimed the bottom row is always kept. v1 attempt 3, L5: on the pad (37,15)->(35,13) and off the pad in the pocket (17,33)->(15,33). The horizontal placement differs (it seems to shift to fit the floor); only row/containment is claimed."
EVIDENCE = ["2d6344b3b63cb07b", "6736b8d0fd861a8a", "abeb00ead6627903"]
from _lib import block3
from pattern_fire import right_set, RR, RC


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:") or (ctx and ctx.get("level_prev") != ctx.get("level_next")):
        return "NA"
    a = block3(prev)
    if a is None or a[2] != 2:
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    hit = None
    for i, r in enumerate(RR):
        for j, c in enumerate(RC):
            if r <= y < r + 3 and c <= x < c + 3:
                hit = (i, j)
    if hit is None or len(right_set(nxt, 2)) != 9:
        return "NA"
    if (right_set(prev, 14) ^ {hit}) != {(0, 1), (1, 0), (1, 2), (2, 1)}:
        return "NA"
    b = block3(nxt)
    if b is None or b[2] != 4:
        return "FALSE"
    t, l, _ = a
    ok = b[0] <= t and t + 1 <= b[0] + 3 and b[1] <= l and l + 1 <= b[1] + 3
    return "TRUE" if ok else "FALSE"
