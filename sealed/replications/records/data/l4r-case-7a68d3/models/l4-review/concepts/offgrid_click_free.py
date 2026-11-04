"""ACTION6 点在网格 9 格块以外且点中背景色 5 的格子：最终帧与前一帧逐格相同(不收计数条，不动任何物体)。"""
LEVEL = "L1"
SCOPE = "点中的格子不是背景 5(例如图样面板)时 NA——那一支归 panel_hint；前后帧动块位置不同(两帧间世界被重置/跨 attempt)时 NA；只看 ACTION6 且点不在网格格块上；其余 NA。多帧里网格闪 8 色不算终帧差"
NOTE = "v3: tid 23f3ac38570477c8 点在 f 面板(4,1)上，网格出现 f 图样的 0 提示——面板点击不是无效点击，缩 scope 到背景格；L4 观测一次 (50,10)；v2: tid f41d202720b96ae0 的 prev 是上一 attempt 结束时的帧，nxt 是本关重置后的帧，不是点击的效果，加跨 attempt NA"
EVIDENCE = ["1254229a9dc005ab", "f41d202720b96ae0", "23f3ac38570477c8"]
from grid_toggle import _cell


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:"):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    if _cell(x, y) is not None:
        return "NA"
    if prev[y][x] != 5:
        return "NA"
    from _lib import piece
    if piece(prev) != piece(nxt):
        return "NA"
    return "TRUE" if prev == nxt else "FALSE"
