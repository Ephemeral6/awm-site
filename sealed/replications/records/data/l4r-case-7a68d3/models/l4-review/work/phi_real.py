"""Strict row-accurate abstract model of L4 (model M4). Backward Dijkstra Phi(s) = min macro-cost to goal,
goal-arrival adds 10*item. State s=(t,l,big,up,box,item)."""
import json, heapq, itertools
def passable(r,c,box):
    if 21<=r<=36 and 21<=c<=44: return True            # room
    if 9<=r<=20 and 31<=c<=32: return True             # stem
    if 29<=r<=32 and 45<=c<=47: return box             # d barrier
    if 29<=r<=32 and 48<=c<=56: return True            # corridor
    if 28<=r<=33 and 57<=c<=61: return True            # exit ring+core
    return False
def core(r,c): return 29<=r<=32 and 57<=c<=60
def item_cell(r,c): return 34<=r<=35 and 23<=c<=24
def cells(t,l,k): return [(t+i,l+j) for i in range(k) for j in range(k)]
def fits(t,l,k,box): return all(passable(r,c,box) for r,c in cells(t,l,k))
def hits_core(t,l,k): return any(core(r,c) for r,c in cells(t,l,k))
def eats(t,l,k): return k==2 and any(item_cell(r,c) for r,c in cells(t,l,k))
DIRS={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}
def succ(s):
    """yield (cost, kind, s2) ; kind 'win' => goal reached (s2 = state at arrival for item penalty)."""
    t,l,big,up,box,item=s; k=4 if big else 2
    out=[]
    def fin(c,t2,l2,big2,up2,box2):
        k2=4 if big2 else 2
        it=item
        res=[(c,'go',(t2,l2,big2,up2,box2,it))]
        if it and eats(t2,l2,k2): res.append((c,'go',(t2,l2,big2,up2,box2,False)))
        return res
    for d,(dr,dc) in DIRS.items():
        t2,l2=t+dr*k,l+dc*k
        if t2>=0 and l2>=0 and fits(t2,l2,k,box):
            if hits_core(t2,l2,k): out.append((1,'win',(t2,l2,big,d=='U',box,item))); continue
            out+=fin(1,t2,l2,big,d=='U',box)
        else:
            out+=fin(1,t,l,big,d=='U',box); out+=fin(1,t,l,big,up,box)
    if big: out+=fin(5,t,l,False,up,box)
    else:
        t2,l2=t-2,l-2
        if t2>=0 and l2>=0:
            if hits_core(t2,l2,4) and all(passable(r,c,box) or core(r,c) for r,c in cells(t2,l2,4)):
                out.append((5,'win',(t2,l2,True,up,box,item)))
            elif fits(t2,l2,4,box): out+=fin(5,t2,l2,True,up,box)
    beam = up and l==31 and all(passable(r,c,box) for r in range(9,t) for c in (31,32))
    out+=fin(4,t,l,big,up,box or beam)
    return out
def domain():
    D=[]
    for t in range(64):
        for l in range(62):
            for big in (False,True):
                k=4 if big else 2
                for box in (False,True):
                    if t+k<=64 and l+k<=62 and fits(t,l,k,box) and not hits_core(t,l,k):
                        for up in (False,True):
                            for item in (False,True):
                                D.append((t,l,big,up,box,item))
    return D
D=domain(); Dset=set(D)
INF=99
pred={s:[] for s in D}; winc={}
for s in D:
    for c,kind,s2 in succ(s):
        if kind=='win':
            v=c+(10 if s2[5] else 0); winc[s]=min(winc.get(s,INF),v)
        else:
            assert s2 in Dset, (s,s2)
            pred[s2].append((c,s))
phi={s:INF for s in D}; pq=[]
for s,v in winc.items(): phi[s]=v; heapq.heappush(pq,(v,s))
while pq:
    d,s=heapq.heappop(pq)
    if d>phi[s]: continue
    for c,p in pred[s]:
        if d+c<phi[p]: phi[p]=d+c; heapq.heappush(pq,(phi[p],p))
s0=(25,37,True,False,False,True)
print('domain',len(D),'Phi(s0)=',phi[s0],'max',max(phi.values()))
json.dump({'D':D,'phi':[phi[s] for s in D]},open('work/phi_real.json','w'))
