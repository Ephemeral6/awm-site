"""计量条已空（右缘 14 色格为 0）时，下一个动作的结果是 GAME_OVER；条未空时不会 GAME_OVER。"""
LEVEL = "L5"
SCOPE = "attempt 交界那条转移（_lib.ATTEMPT_BOUNDARY）返回 NA；同关内转移；看 ctx.state_next；换关返回 NA"
NOTE = "v2 (attempt 5): v1 claimed GAME_OVER iff the bar was empty before the action; 5d74c42bb8aba168 (a commit that took the bar 4 rows -> 0) ended the game in the same action, while in attempt 1 a move that emptied the bar did not. The emptying action is now NA. v1: 只有一例条空；条空那一步本身（把条清零的动作）仍是 NOT_FINISHED"
EVIDENCE = ["fce373ad12535a61", "5d74c42bb8aba168", "f24f3579c4d9a836", "fe3e730a0e76484d"]
from _lib import is_boundary, same_level, bar_e


def assert_(prev, action, nxt, ctx=None):
    if is_boundary(prev, action, nxt):
        return "NA"
    if not same_level(ctx):
        return "NA"
    empty = bar_e(prev) == 0
    over = ctx.get("state_next") == "GAME_OVER"
    if empty:
        return "TRUE" if over else "FALSE"
    if bar_e(nxt) == 0:
        return "NA"   # the action that empties the bar: GAME_OVER on a commit (attempt 5), not on a move (attempt 1)
    return "FALSE" if over else "TRUE"
