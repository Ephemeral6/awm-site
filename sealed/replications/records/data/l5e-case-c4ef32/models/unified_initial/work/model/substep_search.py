import heapq, fast, sys
from rules import initial
fast.GROW_WALLCHECK=True
def run(s0, acts, limit_pos=True):
    dist={s0:0}; par={s0:None}; pq=[(0,s0)]; best=None
    while pq:
        d,t=heapq.heappop(pq)
        if d>dist[t]: continue
        if best and d>best[0]: break
        for a in acts:
            n,cost,cr,win=fast.step(t,a)
            if win:
                v=d+(10 if t[6] else 0)
                if best is None or v<best[0]: best=(v,t,a)
                continue
            if not (0<=n[0]<=60 and 10<=n[1]<=60): continue
            if d+cost<dist.get(n,1e9): dist[n]=d+cost; par[n]=(t,a); heapq.heappush(pq,(d+cost,n))
    if not best: return None,[],len(dist)
    v,t,a=best; path=[(a,None)]
    while par[t]: p,pa=par[t]; path.append((pa,t)); t=p
    return v,path[::-1],len(dist)
acts=[a for a in fast.ACTS if a[0]!='turn']
for name,sub in (('none',None),('4x4:2, 2x2:1',lambda s: s//2),('2px for both',lambda s: 2)):
    fast.SUBSTEP=sub
    v,p,n=run(fast.totuple(initial()),acts)
    print(name,'H0',v,'states',n,'affordable' if v is not None and v<=45 else 'NO')
    if v is not None and v<=45:
        for a,t in p: print('   ',a,t)
