"""Dijkstra over the L5 grid model (my rules) to find the cheapest win under a hypothesis.
hyp 'grow': 15-completion while small -> big at same top-left if 4x4 fits on floor; clears 15 frame.
hyp 'ffeat': walking big onto the 15 item consumes it; then shrink creates no 15 frame.
Costs (fit on L5): move .89, click .94, completion +1, refill -9. Teleport: 15 frame present -> 15 item centre."""
import json, heapq, sys
L=[json.loads(l) for l in open('transitions.jsonl')]
g0=[t for t in L if t['ctx']['level_prev']==5][0]['prev']
hyp=sys.argv[1]
MOVE,CLICK,EX,REF=0.89,0.94,1.0,9.0
GOAL={(r,c) for r in range(0,5) for c in range(32,38)}
def base(r,c):
    v=g0[r][c]
    return v
def free(r,c,n,st):
    cg,dg,ee,ff=st
    for i in range(n):
        for j in range(n):
            rr,cc=r+i,c+j
            if not(0<=rr<47 and 0<=cc<62): return False
            v=g0[rr][cc]
            if v==2 or v==9 or v==10: continue
            if v==14: continue
            if v==15 and hyp=='ffeat': continue
            if v==12 and cg: continue
            if v==13 and dg: continue
            if v==6:
                # boxes: c-box (rows 9-12 cols 20-23) becomes floor when cg; d-box when dg
                if cg and 9<=rr<=12 and 20<=cc<=23: continue
                if dg and 14<=rr<=17 and 55<=cc<=58: continue
            if v==11: continue  # markers sit on floor
            return False
    return True
def overlaps_goal(r,c,n): return any((r+i,c+j) in GOAL for i in range(n) for j in range(n))
D={1:(-1,0),2:(1,0),3:(0,-1),4:(0,1)}
def lane_hits(r,c,n,f,st):
    cg,dg,ee,ff=st
    if f==1: cells=lambda k:[(r-k,c),(r-k,c+1)]
    elif f==4: cells=lambda k:[(r,c+n-1+k),(r+1,c+n-1+k)]
    else: return None
    for k in range(1,64):
        cs=cells(k)
        if not all(0<=x<64 and 0<=y<62 for x,y in cs): return None
        vs={g0[x][y] for x,y in cs}
        # treat removed things as floor
        vs2=set()
        for (x,y) in cs:
            v=g0[x][y]
            if v==12 and cg: v=2
            if v==13 and dg: v=2
            if v==6 and cg and 9<=x<=12 and 20<=y<=23: v=2
            if v==6 and dg and 14<=x<=17 and 55<=y<=58: v=2
            if v in(9,10,14,11): v=2
            vs2.add(v)
        if vs2=={2}: continue
        if vs2=={6}:
            if 9<=cs[0][0]<=12: return 'c'
            return 'd'
        return None
    return None
start=(29,17,4,2,(False,False,False,False),False)  # r,c,n,facing,(cg,dg,ee,ffeaten),frame
dist={start:0};prev={}
pq=[(0,start)]
best=None
while pq:
    d,s=heapq.heappop(pq)
    if d>dist.get(s,1e9): continue
    r,c,n,f,st,fr=s
    cg,dg,ee,ff=st
    succ=[]
    for a,(dr,dc) in D.items():
        nr,nc=r+dr*n,c+dc*n
        if overlaps_goal(nr,nc,n):
            if best is None or d<best[0]: best=(d,s,a)
            continue
        if free(nr,nc,n,st):
            cost=MOVE; ee2=ee; ff2=ff
            cells={(nr+i,nc+j) for i in range(n) for j in range(n)}
            if not ee and (37,49) in cells: ee2=True; cost-=REF
            if hyp=='ffeat' and not ff and n==4 and (37,15) in cells: ff2=True
            succ.append(((nr,nc,n,a,(cg,dg,ee2,ff2),fr),cost,'M%d'%a))
        else:
            succ.append(((r,c,n,a,st,fr),MOVE,'T%d'%a))
    # completions
    if n==4:
        succ.append(((r,c,2,f,st, not (hyp=='ffeat' and ff)),4*CLICK+EX,'SHRINK'))
    elif hyp=='grow' and free(r,c,4,st):
        succ.append(((r,c,4,f,st,False),4*CLICK+EX,'GROW'))
    h=lane_hits(r,c,n,f,st)
    if h=='c' and not cg: succ.append(((r,c,n,f,(True,dg,ee,ff),fr),3*CLICK+EX,'FIREc'))
    if h=='d' and not dg: succ.append(((r,c,n,f,(cg,True,ee,ff),fr),3*CLICK+EX,'FIREd'))
    if fr: tgt=(37,15) if n==2 else None
    else: tgt=(17,33) if n==4 else (18,34)
    if tgt and (tgt[0],tgt[1])!=(r,c): succ.append(((tgt[0],tgt[1],n,f,st,fr),3*CLICK+EX,'TELE'))
    for s2,cst,lab in succ:
        nd=d+cst
        if nd<dist.get(s2,1e9)-1e-9:
            dist[s2]=nd;prev[s2]=(s,lab);heapq.heappush(pq,(nd,s2))
print(hyp,'best cost before final move',best[0] if best else None)
if best:
    path=[];s=best[1]
    while s in prev: s,lab=prev[s][0],prev[s][1]; path.append(lab)
    path.reverse(); path.append('WIN%d'%best[2])
    print(len(path),' '.join(path))
