"""本局词汇（假设）：方块 = 9/10 两色块，位于 15<=行<45（排除顶部 9/10 目标框）。"""
def me(g):
    cells=[(r,c) for r in range(0,45) for c in range(10,60) if g[r][c] in (9,10) and not (r<=4 and 32<=c<=37)]
    if not cells: return None
    rs=[r for r,_ in cells]; cs=[c for _,c in cells]
    return (min(rs),min(cs),max(rs)-min(rs)+1,max(cs)-min(cs)+1)
def level(ctx):
    return (ctx or {}).get('level_prev'), (ctx or {}).get('level_next')
