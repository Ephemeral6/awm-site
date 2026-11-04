"""Exact Python mirror of lean/L4Model.lean (model M4). Used to compute the PHI table and witnesses."""
import heapq, collections
def inR(a,x,b): return a<=x<=b
def passable(box,r,c):
    return ((inR(21,r,36) and inR(21,c,44)) or (inR(9,r,20) and inR(31,c,32)) or
            (box and inR(29,r,32) and inR(45,c,47)) or (inR(29,r,32) and inR(48,c,56)) or
            (inR(28,r,33) and inR(57,c,61)) or (box and inR(3,r,8) and inR(30,c,33)))
def isCore(r,c): return inR(29,r,32) and inR(57,c,60)
def isItem(r,c): return inR(34,r,35) and inR(23,c,24)
def kk(b): return 4 if b[2] else 2
def cellsOk(box,t,l,k): return all(passable(box,t+i,l+j) for i in range(k) for j in range(k))
def hitsCore(t,l,k): return any(isCore(t+i,l+j) for i in range(k) for j in range(k))
def eatsAt(b): return (not b[2]) and any(isItem(b[0]+i,b[1]+j) for i in range(2) for j in range(2))
def fitsB(b): return cellsOk(b[4],b[0],b[1],kk(b)) and not hitsCore(b[0],b[1],kk(b))
def eatOpt(eat,b):
    t,l,big,up,box,item=b
    return (t,l,big,up,box,False) if (eat and item and eatsAt(b)) else b
def target(b,d):
    k=kk(b); t,l=b[0],b[1]
    if d=='U': return (t-k,l) if k<=t else None
    if d=='D': return (t+k,l)
    if d=='L': return (t,l-k) if k<=l else None
    return (t,l+k)
def bstep(b,a):
    t,l,big,up,box,item=b
    if a[0]=='mv':
        _,d,turn,eat=a; up2=(d=='U'); tg=target(b,d)
        if tg and cellsOk(box,tg[0],tg[1],kk(b)):
            if hitsCore(tg[0],tg[1],kk(b)): return ('win',item)
            return ('go',eatOpt(eat,(tg[0],tg[1],big,up2,box,item)))
        return ('go',eatOpt(eat,(t,l,big,up2,box,item) if turn else b))
    if a[0]=='sz':
        eat=a[1]
        if big: return ('go',eatOpt(eat,(t,l,False,up,box,item)))
        if 2<=t and 2<=l and cellsOk(box,t-2,l-2,4):
            if hitsCore(t-2,l-2,4): return ('win',item)
            return ('go',eatOpt(eat,(t-2,l-2,True,up,box,item)))
        return ('go',eatOpt(eat,b))
    eat=a[1]
    return ('go',eatOpt(eat,(t,l,big,up,box or (up and l==31),item)))
def cost(a): return {'mv':1,'sz':5,'beam':4}[a[0]]
ACTS=[('mv',d,tu,e) for d in 'UDLR' for tu in (False,True) for e in (False,True)]+[('sz',False),('sz',True),('beam',False),('beam',True)]
def idx(b):
    t,l,big,up,box,item=b
    return ((((t*64+l)*2+int(big))*2+int(up))*2+int(box))*2+int(item)
def domain():
    return [(t,l,big,up,box,item) for t in range(40) for l in range(64) for big in (False,True)
            for up in (False,True) for box in (False,True) for item in (False,True) if fitsB((t,l,big,up,box,item))]
def compute_phi(cap=127):
    D=domain(); pred=collections.defaultdict(list); phi={b:10**9 for b in D}; pq=[]
    for b in D:
        for a in ACTS:
            r=bstep(b,a)
            if r[0]=='win':
                v=cost(a)+(10 if r[1] else 0)
                if v<phi[b]: phi[b]=v
            else:
                pred[r[1]].append((cost(a),b))
    for b in D:
        if phi[b]<10**9: heapq.heappush(pq,(phi[b],b))
    while pq:
        d,b=heapq.heappop(pq)
        if d>phi[b]: continue
        for c,p in pred[b]:
            if d+c<phi[p]: phi[p]=d+c; heapq.heappush(pq,(phi[p],p))
    return {b:min(v,cap) for b,v in phi.items()}
START=(25,37,True,False,False,True)
# ---- full-model search (exact click semantics collapsed: macros with pre-check costs) ----
def full_win(B):
    """min-used label search over (blk, item already in blk); macros: sz costs 1,1,1 then 2; beam 1,1 then 2.
    Refund rule as in Lean applyR: if item lost in this step, used := used+c-10 (truncated)."""
    best={START:0}; par={START:None}; q=collections.deque([START])
    def apply(b,u,r,c):
        if r[0]=='win': return 'win',u+c
        b2=r[1]; u2=u+c
        if b[5] and not b2[5]: u2=max(0,u2-10)
        return b2,u2
    while q:
        b=q.popleft(); u=best[b]
        for a in ACTS:
            # macro: pre-clicks one at a time must each start with used<=B
            pre = 0 if a[0]=='mv' else (3 if a[0]=='sz' else 2)
            uu=u; ok=True
            for _ in range(pre):
                if uu>B: ok=False; break
                uu+=1
            if not ok or uu>B: continue
            c = 1 if a[0]=='mv' else 2
            res,u2=apply(b,uu,bstep(b,a),c)
            if res=='win': return (B,u2,b,a,par)
            if res not in best or u2<best[res]:
                best[res]=u2; par[res]=(b,a); q.append(res)
    return None
if __name__=='__main__':
    phi=compute_phi(); print('domain',len(phi),'phi(start)',phi[START])
    for B in range(18,30):
        r=full_win(B)
        if r:
            B,u2,b,a,par=r; path=[a]; s=b
            while par[s]: s,a2=par[s]; path.append(a2)
            print('min budget B =',B,'final used',u2); print(path[::-1]); break
