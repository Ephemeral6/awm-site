"""本局词汇：两条以上概念共用的判据写在这里。

**它们是假设，不是事实。**
"""
from geo import components, cells_of, bbox

DIRS = {"ACTION1": (-1, 0), "ACTION2": (1, 0), "ACTION3": (0, -1), "ACTION4": (0, 1)}
STEP = 4


def block3(g):
    """The mover: a solid square connected blob of colours {9,10} (side 2 or 4). Returns (top,left,side) or None."""
    found = []
    for comp in components(cells_of(g, (9, 10))):
        t, b, l, r = bbox(comp)
        s = b - t + 1
        if s in (2, 4) and r - l + 1 == s and len(comp) == s * s:
            found.append((t, l, s))
    return found[0] if len(found) == 1 else None


def block(g):
    k = block3(g)
    return None if k is None else (k[0], k[1])


def bar(g):
    """number of colour-14 cells in columns 62-63"""
    return sum(1 for row in g for v in row[62:64] if v == 14)
