"""A direction action that would put the block onto the socket's colour-10 interior (the 9-framed 10 box not part of the block) ends the level: level counter increases in that transition."""
LEVEL = "L5"
SCOPE = "ACTION1-4 where block and socket are both located in prev; NA otherwise. Claims only the 'ends level' direction, plus: if the target square does not touch the socket interior, level does not change."
NOTE = ""
EVIDENCE = ["97aa9084e4b51928"]
from _lib import block3, DIRS
from geo import components, cells_of, bbox


def socket_interior(g, blk):
    t, l, s = blk
    own = {(t + r, l + c) for r in range(s) for c in range(s)}
    out = set()
    for comp in components(cells_of(g, 10)):
        if not (set(comp) & own):
            out |= set(comp)
    return out


def assert_(prev, action, nxt, ctx=None):
    if action not in DIRS or not ctx:
        return "NA"
    b = block3(prev)
    if b is None:
        return "NA"
    si = socket_interior(prev, b)
    if not si:
        return "NA"
    t, l, s = b
    dr, dc = DIRS[action]
    tgt = {(t + dr * s + r, l + dc * s + c) for r in range(s) for c in range(s)}
    adv = ctx.get("level_next") != ctx.get("level_prev")
    if tgt & si:
        return "TRUE" if adv else "FALSE"
    return "TRUE" if not adv else "FALSE"
