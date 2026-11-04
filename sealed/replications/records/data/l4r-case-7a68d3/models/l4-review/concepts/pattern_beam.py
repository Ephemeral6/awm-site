"""凑齐事件且左面板图样色为 6 时：动块位置与朝向都不变(发射光束，多帧动画)，网格复位 2；最终帧动块所在 4x4 不变。"""
LEVEL = "L1"
SCOPE = "只看 ACTION6 落在网格格块上、点完 e 集合==左面板非地板集合、图样色==6 的转移；其余 NA。不主张光束对别的物体的效果"
NOTE = "L3 观测两次：一次朝下在房中(无可见残留)、一次朝下贴着 d 阻挡(d 闪 7 后复原)"
EVIDENCE = ["0068a92f1a1cecf0", "3ff7f2eeb67ac1e2"]
from _lib import piece
from grid_toggle import _cell, _state
from pattern_teleport import panel


def assert_(prev, action, nxt, ctx=None):
    if not str(action).startswith("ACTION6:"):
        return "NA"
    x, y = map(int, action.split(":")[1].split(","))
    c = _cell(x, y)
    if c is None:
        return "NA"
    on = {(i, j) for i in range(3) for j in range(3) if _state(prev)[i][j] == 14} ^ {c}
    pat, col = panel(prev)
    if on != pat or col != 6:
        return "NA"
    p = piece(prev)
    if p is None:
        return "NA"
    t, l, k = p
    same = all(prev[t + i][l + j] == nxt[t + i][l + j] for i in range(k) for j in range(k))
    grid_ok = all(v == 2 for row in _state(nxt) for v in row)
    return "TRUE" if same and grid_ok else "FALSE"
