"""目标图样色为 6 时凑成图样，且 agent 朝上、从 agent 最左两列（c, c+1）往上逐行看、碰到的第一个非 2 格是 6 框：该框每格变 2 或 5，框芯色 X 的所有其它格变地板 2，其它 6 框不变；没打中则 6 框与 13 块都不变。"""
LEVEL = "L1"
SCOPE = "只看凑成 6 色图样的点击且 prev 里有 6 框、能定位 agent；不满足该条件时只断言 6 框与 13 块都不变；agent 不朝上 NA（其它朝向的通道是哪两列/行未测）"
NOTE = "v3: v2 写死 13 色，被 360e774a35fcb8ec 打脸（L5 打中的是芯色 12 的框，12 块消失、13 块不动）；改成按框芯色。0fdbe552 上判 FALSE 是读错：6 色格把左上目标图样里的 6 也算进去了，改用 map_cells。v2: v1(朝上且列相交即触发)被 981df856111682d4 打脸（L4 agent (21,29) 朝上，列 29-32 与 6 框 30-33 相交但没触发；其最左两列 29-30 头顶第 20 行就是墙）。改成：从最左两列往上的通道首个非地板格是 6 才触发。v1 note: 两种解释还没分开：(A) 朝向/对准 6 框才触发；(B) 第三次凑成才触发。前两次（朝下@(25,25)，朝右@(25,29)）无效，第三次（朝上@(21,29)）生效。本条按 A 写，可被 B 打脸。"
EVIDENCE = ["4c0c0ca22a14f0b2", "981df856111682d4", "0fdbe552ebe56203", "360e774a35fcb8ec"]
from _lib import parse_click, panel_cell_at, panel, completes, agent, map_cells


def assert_(prev, action, nxt, ctx=None):
    if ctx and ctx.get("level_prev") != ctx.get("level_next"):
        return "NA"
    xy = parse_click(action)
    if not xy or panel_cell_at(*xy) is None:
        return "NA"
    cm = completes(prev, action)
    if not cm or cm[0] != 6:
        return "NA"
    a = agent(prev)
    six = map_cells(prev, 6)
    if a is None or not six:
        return "NA"
    d13 = map_cells(prev, 13)
    c0, c1 = min(c for _, c in six), max(c for _, c in six)
    r0, r1 = min(r for r, _ in six), max(r for r, _ in six)
    inbox = lambda r, c: r0 <= r <= r1 and c0 <= c <= c1
    if a[2] != (-1, 0):
        return "NA"
    hit = None
    for rr in range(a[0] - 1, -1, -1):
        vs = {prev[rr][a[1]], prev[rr][a[1] + 1]}
        if vs == {2}:
            continue
        if vs == {6}:
            hit = (rr, a[1])
        break
    # 被打中的 6 框：包含命中格的 6 色四连通块的外接框
    from geo import components
    comps = components(six)
    if hit:
        box = [cp for cp in comps if hit in cp or (hit[0], hit[1] + 1) in cp][0]
        r0, r1 = min(r for r, _ in box), max(r for r, _ in box)
        c0, c1 = min(c for _, c in box), max(c for _, c in box)
        inner = {prev[r][c] for r in range(r0 + 1, r1) for c in range(c0 + 1, c1)}
        if len(inner) != 1:
            return "NA"
        X = inner.pop()
        inbox = lambda r, c: r0 <= r <= r1 and c0 <= c <= c1
        ok = all(nxt[r][c] == 2 for r, c in map_cells(prev, X) if not inbox(r, c))
        ok = ok and all(nxt[r][c] in (5, 2) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1))
        ok = ok and all(nxt[r][c] == 6 for r, c in six if not inbox(r, c))
    else:
        ok = all(nxt[r][c] == prev[r][c] for r, c in six + d13)
    return "TRUE" if ok else "FALSE"
