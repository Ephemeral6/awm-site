import heapq, fast
from rules import initial
fast.GROW_WALLCHECK=True
orig=fast.step
def mk(rule):
    def step(t,a,coll='full'):
        if a[0]=='tele' and t[2]==2:
            dest=rule(t)
            if dest:
                r,c=dest; s=2; f=t[3]; oc,od,ep=t[4],t[5],t[6]
                return (r,c,s,f,oc,od,ep), 4, 0, fast.ovl(r,c,s,fast.GOAL)
        return orig(t,a,coll)
    return step
def run(stepf):
    s0=fast.totuple(initial()); dist={s0:0}; pq=[(0,s0)]; best=None
    acts=[a for a in fast.ACTS if a[0]!='turn']
    while pq:
        d,t=heapq.heappop(pq)
        if d>dist[t]: continue
        if best is not None and d>best: break
        for a in acts:
            n,cost,cr,win=stepf(t,a)
            if win:
                v=d+(10 if t[6] else 0); best=v if best is None else min(best,v); continue
            if not (0<=n[0]<=60 and 10<=n[1]<=60): continue
            if d+cost<dist.get(n,1e9): dist[n]=d+cost; heapq.heappush(pq,(d+cost,n))
    return best
V={'2x2 always to reticle (18,34)':lambda t:(18-1,34-1) if False else (17,33),
   '2x2 facing U -> reticle (17,33)':lambda t:(17,33) if t[3]=='U' else None,
   '2x2 facing U -> reticle (18,34) [even]':lambda t:(17,33) if t[3]=='U' else None}
for k,v in V.items():
    fast.step=mk(v); print(k,'H0',run(fast.step),'(affordable iff <=45)')
fast.step=orig; print('baseline H0',run(orig))
