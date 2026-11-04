"""方向键（ACTION1上/2下/3左/4右）被受理时：块沿该方向平移 0..边长 格、不发生横向位移、边长不变，且之后 9 那一半朝向该方向。"""
LEVEL = "L1"
SCOPE = "attempt 交界转移（_lib.ATTEMPT_BOUNDARY）返回 NA；同关内 ACTION1-4、整帧有变化、前后都能定位到块；否则 NA"
NOTE = "被墙挡时位移被截短（L1 见到 4 截成 2、以及 0）；截短规律另立"
EVIDENCE = ["51e0835791ca0303", "3f5956007e12ca17", "827b6b560fc0b5bb", "5580ee1a82842888"]
from _lib import is_boundary, same_level, piece, DIRS

FACE = {"ACTION1": "U", "ACTION2": "D", "ACTION3": "L", "ACTION4": "R"}


def assert_(prev, action, nxt, ctx=None):
    if is_boundary(prev, action, nxt):
        return "NA"
    if action not in DIRS or not same_level(ctx) or prev == nxt:
        return "NA"
    a, b = piece(prev), piece(nxt)
    if a is None or b is None:
        return "NA"
    dr, dc = DIRS[action]
    mr, mc = b["top"] - a["top"], b["left"] - a["left"]
    s = a["size"]
    if b["size"] != s:
        return "FALSE"
    if dr == 0 and mr != 0 or dc == 0 and mc != 0:
        return "FALSE"
    m = mr * dr + mc * dc
    if not (0 <= m <= s):
        return "FALSE"
    return "TRUE" if b["face"] == FACE[action] else "FALSE"


def apply(prev, action, ctx=None):
    return None
