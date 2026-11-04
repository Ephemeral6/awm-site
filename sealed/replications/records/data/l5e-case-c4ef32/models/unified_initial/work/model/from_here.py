import heapq, itertools, sys
import fast
def run(s0, acts, coll='full'):
    dist={s0:0}; par={s0:None}; pq=[(0,s0)]; best=None
    while pq:
        d,t=heapq.heappop(pq)
        if d>dist[t]: continue
        if best and d>best[0]: break
        for a in acts:
            n,cost,cr,win=fast.step(t,a,coll)
            if win:
                v=d+(10 if t[6] else 0)
                if best is None or v<best[0]: best=(v,t,a)
                continue
            if not (0<=n[0]<=60 and 10<=n[1]<=60): continue
            nd=d+cost
            if nd<dist.get(n,10**9): dist[n]=nd; par[n]=(t,a); heapq.heappush(pq,(nd,n))
    if not best: return None,[]
    v,t,a=best; path=[(a,None)]
    while par[t]: p,pa=par[t]; path.append((pa,t)); t=p
    return v,path[::-1]
s0=(25,45,4,'U',True,False,False)
REM=24
for gw,tb,place in itertools.product([True,False],[True],['obs','all']):
    fast.GROW_WALLCHECK=gw; fast.TURN_ONLY_IF_BLOCKED=tb
    acts=[a for a in fast.ACTS if place=='all' or not ((a[0]=='shrink' and a[1]!=(0,0)) or (a[0]=='grow' and a[1]!=(2,2)))]
    v,p=run(s0,acts)
    print('growcheck',gw,'blockedturn',tb,place,'prefix',v,'affordable' if v is not None and v<=REM else 'NO')
    if v is not None and v<=REM:
        for a,t in p: print('   ',a,t)
