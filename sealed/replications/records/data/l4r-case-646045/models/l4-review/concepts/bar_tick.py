"""每个被受理的动作（帧有变化）里，计量条只会从上往下由 14 变 0：变的格子是紧接已空段之下的连续若干整节（每节 2 行），可为 0 节。"""
LEVEL = "L4"
SCOPE = "attempt 交界那条转移（_lib.ATTEMPT_BOUNDARY）返回 NA；同关内、帧有变化的转移；换关或整帧不变返回 NA"
NOTE = "v3 (attempt 6): c423846f0d7a3990 - the bar went UP when the 2x2 piece stepped onto the e square; such steps are now NA (rule e_refill). v2：v1 断言每步至多一节，被 L2 的提交步打脸（一步掉 3 节，tid 见 EVIDENCE 首条）。节拍（哪一步掉一节）尚未定：约每 3 步掉 2 节，规律未知，所以只断言掉的形状"
EVIDENCE = ["c423846f0d7a3990", "f24f3579c4d9a836", "a97af4438459243d", "3f5956007e12ca17", "827b6b560fc0b5bb", "5580ee1a82842888"]
from _lib import is_boundary, same_level, e_obj, BAR_COLS


def assert_(prev, action, nxt, ctx=None):
    if is_boundary(prev, action, nxt):
        return "NA"
    if e_obj(prev) != e_obj(nxt):
        return "NA"   # the e pickup refills the bar: see e_refill
    if not same_level(ctx) or prev == nxt:
        return "NA"
    ch = [(r, c) for r in range(64) for c in BAR_COLS if prev[r][c] != nxt[r][c]]
    if not ch:
        return "TRUE"
    tops = [r for r in range(64) if prev[r][62] == 14]
    if not tops:
        return "FALSE"
    t = tops[0]
    rows = sorted({r for r, _ in ch})
    k = len(rows)
    want = {(r, c) for r in range(t, t + k) for c in BAR_COLS}
    ok = k % 2 == 0 and set(ch) == want and all(nxt[r][c] == 0 for r, c in want)
    return "TRUE" if ok else "FALSE"
