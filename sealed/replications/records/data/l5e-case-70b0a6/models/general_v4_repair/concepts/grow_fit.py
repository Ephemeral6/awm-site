"""15 色图样在 agent 为 2x2 时凑成：4x4 落在第一个能放下的位置，按顺序试 (r-2,c-2)、{(r,c-2),(r-2,c)}、(r,c)；都放不下则 agent 不变。与朝向无关。"""
LEVEL = "L1"
SCOPE = "只看凑成 15 色图样、prev agent 为 2x2 的点击；中间两候选都能放下而 (r-2,c-2) 放不下时次序未定，判 NA"
NOTE = "attempt 9 新增，替换按朝向分支的 grow_place（已撤册）。依据 5 次：上(15,45)->(15,43)、右(17,47)->(15,45)、下(37,15)->(35,13)、左(37,13)->(35,13)、竖井(13,21) 放不下 -> 不变。"
EVIDENCE = ["2d6344b3b63cb07b", "75955b9510aed3c6", "9ce863479d42731a", "821d9d4677ca0bb8", "9ce863479d42731a", "75955b9510aed3c6", "f11a62eaf9e6fcf5", "0d31a36613487e89"]
from _lib import completes, agent


def fits(g, r, c):
    return all(0 <= r + i < 47 and 0 <= c + j < 62 and g[r + i][c + j] in (2, 9, 10, 11, 14, 15)
               for i in range(4) for j in range(4))


def assert_(prev, action, nxt, ctx=None):
    cm = completes(prev, action)
    if not cm or cm[0] != 15:
        return "NA"
    a = agent(prev)
    if a is None or a[3] != 2:
        return "NA"
    r, c = a[0], a[1]
    b = agent(nxt)
    if fits(prev, r - 2, c - 2):
        want = (r - 2, c - 2)
    else:
        mids = [p for p in ((r, c - 2), (r - 2, c)) if fits(prev, *p)]
        if len(mids) == 2:
            return "NA"
        if mids:
            want = mids[0]
        elif fits(prev, r, c):
            want = (r, c)
        else:
            return "TRUE" if b == a else "FALSE"
    return "TRUE" if b is not None and b[3] == 4 and (b[0], b[1]) == want else "FALSE"
