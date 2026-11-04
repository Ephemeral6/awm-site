"""A commit that turns the 2x2 piece into a 4x4 puts the 4x4's top-left at (top-2, left-2) of the old 2x2."""
LEVEL = "L1"
SCOPE = "attempt boundary NA; same level, ACTION6, piece located before and after, size 2 -> 4; otherwise NA"
NOTE = "attempt 4 (L4): PLUS on a 2x2 grows it (refutes the earlier no-grow hypothesis H2)"
EVIDENCE = ["f24f3579c4d9a836", "0eac4d3115c02cba"]
from _lib import same_level, piece, is_boundary


def assert_(prev, action, nxt, ctx=None):
    if not action.startswith("ACTION6:") or not same_level(ctx) or is_boundary(prev, action, nxt):
        return "NA"
    a, b = piece(prev), piece(nxt)
    if a is None or b is None or not (a["size"] == 2 and b["size"] == 4):
        return "NA"
    return "TRUE" if (b["top"], b["left"]) == (a["top"] - 2, a["left"] - 2) else "FALSE"
