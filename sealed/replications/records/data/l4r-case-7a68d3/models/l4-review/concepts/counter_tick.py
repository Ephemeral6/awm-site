"""同关内右侧计数条已用行数单调不减，且每个转移的增量是偶数(2 行一档)。"""
LEVEL = "L4"
SCOPE = "前后帧动块位置不同且动作不是方向/凑齐(跨 attempt 重置)时 NA；同关内所有动作；换关 NA；读不出返回 NA；房间里 e 色道具格数减少(被吃)的转移 NA——那一支归 e_refill"
NOTE = ("v2: tid d3f8d3aa32dd67db(L2 teleport 一步 +6 行)打掉 {0,2}；"
        "v3: L4 单步 +4 行(d05e58c373a65ef2, b57b75a8d72380aa, c1eaa9a748158026)打掉『普通步 ∈{0,2}』——"
        "每关速率是关卡数据(L1-3 约 2/3 档/步，L4 约 1.6 档/步)，只留偶数且不减；v4: tid 60ebbfc6a613172b 2x2 吃 e 道具，used 64->32，作用域排除吃道具步")
EVIDENCE = ["827b6b560fc0b5bb", "3f5956007e12ca17", "d3f8d3aa32dd67db",
            "d05e58c373a65ef2", "b57b75a8d72380aa", "c1eaa9a748158026", "60ebbfc6a613172b", "f41d202720b96ae0"]
from _lib import counter_used


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") not in (None, ctx.get("level_next")):
        return "NA"
    from _lib import piece
    if str(action).startswith("ACTION6") and piece(prev) != piece(nxt) and prev[63][62] == 0:
        return "NA"   # attempt boundary: prev is the dead game's final frame
    it = lambda g: sum(1 for r in range(47) for c in range(62) if g[r][c] == 14)
    if it(nxt) < it(prev):
        return "NA"
    d = counter_used(nxt) - counter_used(prev)
    return "TRUE" if d >= 0 and d % 2 == 0 else "FALSE"
