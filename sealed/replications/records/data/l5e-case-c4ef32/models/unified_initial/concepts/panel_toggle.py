"""ACTION6 点在右下 3x3 面板的某格（未凑齐完成条件时）：那一格 3x3 像素在 原色(0/2) 与 14 之间翻转，面板别的格不变。"""
LEVEL = "L1"
SCOPE = "只看 ACTION6 点在面板格内（行49-61, 列24-36 的格心区域）；面板出现 >1 格变化时（完成事件）NA；换关 NA"
NOTE = ""
EVIDENCE = ['001cde5b0ff5bef3', '53cb8f5a1f8355f2']
from _lib import level
def assert_(prev, action, nxt, ctx=None):
    if not action.startswith("ACTION6:"): return "NA"
    a,b=level(ctx)
    if a!=b or a!=1: return "NA"
    x,y=map(int,action.split(":")[1].split(","))
    cells=[(r0,c0) for r0 in (49,54,59) for c0 in (24,29,34)]
    hit=[rc for rc in cells if rc[0]<=y<rc[0]+3 and rc[1]<=x<rc[1]+3]
    if not hit: return "NA"
    changed=[rc for rc in cells if prev[rc[0]][rc[1]]!=nxt[rc[0]][rc[1]]]
    if len(changed)>1: return "NA"
    r0,c0=hit[0]; pv=prev[r0][c0]; nv=nxt[r0][c0]
    if changed!=[hit[0]]: return "FALSE"
    ok = (pv==14 and nv in (0,2)) or (pv in (0,2) and nv==14)
    return "TRUE" if ok else "FALSE"
