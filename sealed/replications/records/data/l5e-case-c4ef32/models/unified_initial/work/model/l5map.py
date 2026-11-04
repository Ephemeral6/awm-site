"""Level-5 map data read off the initial L5 frame (work/model/l5_init.json).

Everything here is *level data* (positions/colours), not rules.  Rules live in rules.py.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
F0 = json.load(open(os.path.join(HERE, 'l5_init.json')))

# rectangles (r0, r1, c0, c1) inclusive
GOAL = (0, 4, 32, 37)            # 9-bordered box, interior a = rows 1-4 cols 33-36
BARRIER = {'c': (33, 36, 29, 31), 'd': (11, 13, 33, 36)}
SWITCH = {'c': (9, 12, 20, 23), 'd': (14, 17, 55, 58)}   # 6-bordered boxes; interior colour = key
EPAD = (37, 38, 49, 50)          # colour 14 refill pad
FPAD = (37, 38, 15, 16)          # colour 15 pad: 2x2 teleport target (observed)
RETICLE4 = (17, 33)              # top-left of the 4x4 teleport target (b-corner reticle interior)
START = dict(r=29, c=17, size=4, facing='D')

PLAY_ROWS = 47                   # rows >= 47 are the panel / icons, not board
PLAY_COLS = 60                   # cols >= 60 hold the budget bar
ICON_COLS = 10                   # cols < 10 hold the power icons, not board


def inrect(r, c, R):
    return R[0] <= r <= R[1] and R[2] <= c <= R[3]


def base_walkable(r, c):
    """Walkable for the block regardless of barrier state (strict reading of the frame)."""
    if not (0 <= r < PLAY_ROWS and ICON_COLS <= c < PLAY_COLS):
        return False
    for R in SWITCH.values():
        if inrect(r, c, R):
            return False
    for R in BARRIER.values():
        if inrect(r, c, R):
            return False
    v = F0[r][c]
    if v in (2, 11, 14, 15):
        return True
    if v in (9, 10):              # goal box or the block's own start cells
        return True
    return False


def check_map():
    """Every non-background board cell is classified exactly once."""
    bad = []
    for r in range(PLAY_ROWS):
        for c in range(ICON_COLS, PLAY_COLS):
            v = F0[r][c]
            cls = [base_walkable(r, c)] + [inrect(r, c, R) for R in BARRIER.values()] + \
                  [inrect(r, c, R) for R in SWITCH.values()]
            if v == 5:
                if any(cls):
                    bad.append((r, c, v))
            elif sum(cls) != 1:
                bad.append((r, c, v))
    return bad


if __name__ == '__main__':
    print('map classification problems:', check_map())
