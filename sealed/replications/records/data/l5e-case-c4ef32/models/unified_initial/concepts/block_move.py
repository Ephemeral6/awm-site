"""ACTION1/2/3/4 把方块沿 上/下/左/右 平移恰好一个边长 s（尺寸不变），前提是落点在帧上原本全是地板色 2。"""
LEVEL = "L1"
SCOPE = "只看 ACTION1-4；换关、方块定位不到、或尺寸变化时 NA；落点不全是 2 时 NA（阻挡另说）"
NOTE = "v1.4: tid c1aa91c8a7d96c79 is the first action of attempt 6, prev = attempt-5 game-over frame (2x2 block); size change => not a move => NA. v1.3: tid 58acca6a42c339e0 (4x4 climbing to row 13 in the L5 goal corridor) was a reading error: _lib.me only scanned rows 15-44; widened to rows 0-44, cols 10-59 minus the L5 goal box. v1.2: tid f1af602a8ba8e5e2 is the first action of attempt 2; its prev frame is the game-over frame of attempt 1 (level reset between them), so it is not a single move: when barrier/switch cells (colours 12,13,6) differ between prev and nxt, the world was reset -> NA. v1.1: 开局第一步 ACTION1(tid 2b3e5ed8fe7b90de) 整帧无差而落点是地板，按 METHOD 2.1 归为未受理，整帧无差时 NA"
EVIDENCE = ['3f5956007e12ca17', '827b6b560fc0b5bb', 'f1af602a8ba8e5e2', '58acca6a42c339e0', 'c1aa91c8a7d96c79']
from _lib import me, level
D={"ACTION1":(-1,0),"ACTION2":(1,0),"ACTION3":(0,-1),"ACTION4":(0,1)}
def assert_(prev, action, nxt, ctx=None):
    if action not in D: return "NA"
    a,b=level(ctx)
    if a!=b: return "NA"
    if any((prev[r][c] in (6,12,13)) != (nxt[r][c] in (6,12,13)) for r in range(47) for c in range(10,60)): return "NA"  # world reset, not a move
    if prev==nxt: return "NA"  # 整帧无差 = 未受理（开局第一步被吞），不是阻挡
    p=me(prev); n=me(nxt)
    if not p or not n or p[2]!=p[3]: return "NA"
    if n[2:]!=p[2:]: return "NA"  # size changed: not a plain move (e.g. level reset between attempts)
    s=p[2]; dr,dc=D[action]; r,c=p[0]+dr*s,p[1]+dc*s
    if not all(0<=r+i<64 and 0<=c+j<64 and (prev[r+i][c+j]==2 or (p[0]<=r+i<p[0]+s and p[1]<=c+j<p[1]+s)) for i in range(s) for j in range(s)): return "NA"
    return "TRUE" if (n[0],n[1],n[2],n[3])==(r,c,s,s) else "FALSE"
