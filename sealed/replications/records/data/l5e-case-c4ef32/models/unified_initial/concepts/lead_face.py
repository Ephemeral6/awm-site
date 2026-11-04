"""方块移动后，9 色占据它朝移动方向的那一半，10 色占另一半。"""
LEVEL = "L1"
SCOPE = "只看 ACTION1-4 且方块确实移动了、尺寸未变；其余 NA"
NOTE = ""
EVIDENCE = ['3f5956007e12ca17', '827b6b560fc0b5bb']
from _lib import me, level
D={"ACTION1":(-1,0),"ACTION2":(1,0),"ACTION3":(0,-1),"ACTION4":(0,1)}
def assert_(prev, action, nxt, ctx=None):
    if action not in D: return "NA"
    p=me(prev); n=me(nxt)
    if not p or not n or p[:2]==n[:2] or p[2:]!=n[2:]: return "NA"
    r,c,h,w=n; dr,dc=D[action]
    for i in range(h):
        for j in range(w):
            if dr: lead = (i < h//2) if dr<0 else (i >= h//2)
            else: lead = (j < w//2) if dc<0 else (j >= w//2)
            if nxt[r+i][c+j] != (9 if lead else 10): return "FALSE"
    return "TRUE"
