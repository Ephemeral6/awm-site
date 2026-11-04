"""Attempt-3 route search on L5 (my rules + permissive over-approximations).
Rules: move slides by largest even k<=n that fits (k=0 -> turn only); shrink keeps top-left, creates 15 frame;
grow (15 completion while small): PERMISSIVE - any 4x4 placement containing the 2x2 that fits; removes frame;
fire: PERMISSIVE - any facing, any 2-wide lane inside the agent's span on the facing side;
teleport: frame present -> 15 item centre (37,15) as current size; else pad (17,33) big / (18,34) small.
Costs (fit): every action 0.9, completion +1 (clicks: pattern size), refill -9 on covering (37,49)/(38,50).
Feasible iff cost of all non-final actions minus the last one < 32 (bar>0 before every non-winning action)."""
import json, heapq, sys
STRICT = len(sys.argv) > 1
L=[json.loads(l) for l in open('transitions.jsonl')]
g0=[t for t in L if t['ctx']['level_prev']==5][0]['prev']
A,EX,REF=0.9,1.0,9.0
GOAL={(r,c) for r in range(0,5) for c in range(32,38)}
def floor_ok(r,c,n,cg,dg):
    for i in range(n):
        for j in range(n):
            rr,cc=r+i,c+j
            if not(0<=rr<47 and 0<=cc<62): return False
            v=g0[rr][cc]
            if v in (2,9,10,14,11,15): continue
            if v==12 and cg: continue
            if v==13 and dg: continue
            if v==6 and ((cg and 9<=rr<=12 and 20<=cc<=23) or (dg and 14<=rr<=17 and 55<=cc<=58)): continue
            return False
    return True
D={1:(-1,0),2:(1,0),3:(0,-1),4:(0,1)}
def eff(x,y,cg,dg):
    v=g0[x][y]
    if v in (9,10,14,11,15): return 2
    if v==12 and cg: return 2
    if v==13 and dg: return 2
    if v==6 and ((cg and 9<=x<=12 and 20<=y<=23) or (dg and 14<=x<=17 and 55<=y<=58)): return 2
    return v
def fires(r,c,n,f,cg,dg):
    out=set()
    dr,dc=D[f]
    for o in range(0,n-1):
        if dr: lane=[(None,c+o),(None,c+o+1)]
        else: lane=[(r+o,None),(r+o+1,None)]
        for k in range(1,64):
            if dr: cs=[(r-k if dr<0 else r+n-1+k, y) for _,y in lane]
            else: cs=[(x, c-k if dc<0 else c+n-1+k) for x,_ in lane]
            if not all(0<=x<47 and 0<=y<62 for x,y in cs): break
            vs={eff(x,y,cg,dg) for x,y in cs}
            if vs=={2}: continue
            if vs=={6}: out.add('c' if cs[0][0]<=12 and cs[0][1]<=23 else 'd')
            break
    return out
def overlaps(r,c,n): return any((r+i,c+j) in GOAL for i in range(n) for j in range(n))
start=(29,17,4,2,False,False,False,False)
dist={start:0.0};prev={};pq=[(0.0,start)];best=None
while pq:
    d,s=heapq.heappop(pq)
    if d>dist.get(s,1e9)+1e-9: continue
    if best and d>=best[0]: break
    r,c,n,f,cg,dg,ee,fr=s
    succ=[]
    for a,(dr,dc) in D.items():
        if overlaps(r+dr*n,c+dc*n,n):
            if best is None or d<best[0]: best=(d,s,a)
            continue
        k=0
        for kk in range(2,n+1,2):
            if floor_ok(r+dr*kk,c+dc*kk,n,cg,dg): k=kk
            else: break
        nr,nc=r+dr*k,c+dc*k
        cost=A; ee2=ee
        if not ee and any((nr+i,nc+j) in ((37,49),(38,50)) for i in range(n) for j in range(n)): ee2=True; cost-=REF
        succ.append(((nr,nc,n,a,cg,dg,ee2,fr),cost,'M%d'%a))
    if n==4: succ.append(((r,c,2,f,cg,dg,ee,True),4*A+EX,'SHRINK'))
    else:
        for rr in ((r,) if STRICT else (r-2,r)):
            for cc in ((c-2,) if STRICT else (c-2,c)):
                if floor_ok(rr,cc,4,cg,dg): succ.append(((rr,cc,4,f,cg,dg,ee,False),4*A+EX,'GROW@%d,%d'%(rr,cc)))
    for h in fires(r,c,n,f,cg,dg):
        if h=='c' and not cg: succ.append(((r,c,n,f,True,dg,ee,fr),3*A+EX,'FIREc'))
        if h=='d' and not dg: succ.append(((r,c,n,f,cg,True,ee,fr),3*A+EX,'FIREd'))
    tgt=((37,15) if n==2 else (36,14)) if fr else ((17,33) if n==4 else (18,34))
    if tgt!=(r,c): succ.append(((tgt[0],tgt[1],n,f,cg,dg,ee,fr),3*A+EX,'TELE'))
    for s2,cst,lab in succ:
        nd=d+cst
        if nd<dist.get(s2,1e9)-1e-9:
            dist[s2]=nd;prev[s2]=(s,lab);heapq.heappush(pq,(nd,s2))
d,s,a=best
path=[]
while s in prev: s,lab=prev[s]; path.append(lab)
path.reverse()
print('min cost of non-final actions',round(d,2),'; last non-final starts at',round(d-A,2),'(need <32)')
print(len(path)+1,'actions:',' '.join(path),'WIN%d'%a)
