"""Exact Python mirror of lean/L4Model.lean, model M4 v2 (attempt-2 amendments).
v2 changes vs v1 (kept in work/l4mirror_v1.py):
  * Blk.up:Bool -> Blk.face in 'UDLR' (the eat rule now reads the front half).
  * eat: 2x2 overlapping item, OR 4x4 whose front half overlaps item, OR a grow whose 4x4 placement
    overlaps item (looser union; observed: grow-with-front ate, back-half cover did not).
  * sz carries an anchor choice q used only by grow facing U/R (untested -> any of 4 placements, looser);
    grow facing L/D -> (t-2,l-2) (observed); shrink keeps top-left facing U/L/R (observed) and facing D uses
    the model parameter QD (hypothesis H_shrinkD: QD = 0, top-left).
  * budget: a winning action that would make used > 18 is game over (stepB, Lean side)."""
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
def anyItem(t,l,k): return any(isItem(t+i,l+j) for i in range(k) for j in range(k))
def frontItem(t,l,k,f):
    h=k//2
    return any(isItem(t+i,l+j) for i in range(k) for j in range(k)
               if {'U':i<h,'D':i>=h,'L':j<h,'R':j>=h}[f])
def eatsAt(b):
    t,l,big,f,box,item=b
    return anyItem(t,l,2) if not big else frontItem(t,l,4,f)
def fitsB(b): return cellsOk(b[4],b[0],b[1],kk(b)) and not hitsCore(b[0],b[1],kk(b))
def eatOpt(eat,b,grown=False):
    t,l,big,f,box,item=b
    if eat and item and (eatsAt(b) or (grown and anyItem(t,l,4))): return (t,l,big,f,box,False)
    return b
QS=[(0,0),(0,2),(2,0),(2,2)]
def target(b,d):
    k=kk(b); t,l=b[0],b[1]
    if d=='U': return (t-k,l) if k<=t else None
    if d=='D': return (t+k,l)
    if d=='L': return (t,l-k) if k<=l else None
    return (t,l+k)
QD=[0]   # shrink-facing-down quadrant parameter (hypothesis H_shrinkD: 0 = top-left)
def bstep(b,a):
    t,l,big,f,box,item=b
    if a[0]=='mv':
        _,d,turn,eat=a; tg=target(b,d)
        if tg and cellsOk(box,tg[0],tg[1],kk(b)):
            if hitsCore(tg[0],tg[1],kk(b)): return ('win',item)
            return ('go',eatOpt(eat,(tg[0],tg[1],big,d,box,item)))
        return ('go',eatOpt(eat,(t,l,big,d,box,item) if turn else b))
    if a[0]=='sz':
        _,eat,q=a
        if big:
            dt,dl = QS[QD[0]] if f=='D' else (0,0)
            return ('go',eatOpt(eat,(t+dt,l+dl,False,f,box,item)))
        dt,dl = (-2,-2) if f in 'LD' else (QS[q][0]-2,QS[q][1]-2)
        t2,l2=t+dt,l+dl
        if t2>=0 and l2>=0 and cellsOk(box,t2,l2,4):
            if hitsCore(t2,l2,4): return ('win',item)
            return ('go',eatOpt(eat,(t2,l2,True,f,box,item),grown=True))
        return ('go',eatOpt(eat,b))
    eat=a[1]
    return ('go',eatOpt(eat,(t,l,big,f,box or (f=='U' and l==31),item)))
def cost(a): return {'mv':1,'sz':5,'beam':4}[a[0]]
ACTS=[('mv',d,tu,e) for d in 'UDLR' for tu in (False,True) for e in (False,True)]+\
     [('sz',e,q) for e in (False,True) for q in range(4)]+[('beam',False),('beam',True)]
FI={'U':0,'D':1,'L':2,'R':3}
def idx(b):
    t,l,big,f,box,item=b
    return ((((t*64+l)*2+int(big))*4+FI[f])*2+int(box))*2+int(item)
ROW=64*2*4*2*2
def domain():
    return [(t,l,big,f,box,item) for t in range(40) for l in range(64) for big in (False,True)
            for f in 'UDLR' for box in (False,True) for item in (False,True) if fitsB((t,l,big,f,box,item))]
def compute_phi(cap=127):
    D=domain(); pred=collections.defaultdict(list); phi={b:10**9 for b in D}; pq=[]
    for b in D:
        for a in ACTS:
            r=bstep(b,a)
            if r[0]=='win':
                v=cost(a)+(10 if r[1] else 0)
                if v<phi[b]: phi[b]=v
            else: pred[r[1]].append((cost(a),b))
    for b in D:
        if phi[b]<10**9: heapq.heappush(pq,(phi[b],b))
    while pq:
        d,b=heapq.heappop(pq)
        if d>phi[b]: continue
        for c,p in pred[b]:
            if d+c<phi[p]: phi[p]=d+c; heapq.heappush(pq,(phi[p],p))
    return {b:min(v,cap) for b,v in phi.items()}
START=(25,37,True,'D',False,True)
def full_win(B):
    """exact click-level budget semantics (pre-clicks must each start with used<=B; a win must end <= B)."""
    best={START:0}; par={START:None}; q=collections.deque([START])
    while q:
        b=q.popleft(); u=best[b]
        for a in ACTS:
            pre = 0 if a[0]=='mv' else (3 if a[0]=='sz' else 2)
            if u+pre>B: continue
            c = 1 if a[0]=='mv' else 2
            r=bstep(b,a); u2=u+pre+c
            if r[0]=='win':
                if u2<=B: return B,u2,b,a,par
                continue
            b2=r[1]
            if b[5] and not b2[5]: u2=max(0,u2-10)
            if u2>B: continue
            if b2 not in best or u2<best[b2]: best[b2]=u2; par[b2]=(b,a); q.append(b2)
    return None
if __name__=='__main__':
    import sys
    QD[0]=int(sys.argv[1]) if len(sys.argv)>1 else 0
    phi=compute_phi(); print('domain',len(phi),'phi(start)',phi[START])
    for B in range(18,26):
        r=full_win(B)
        if r:
            B,u2,b,a,par=r; path=[a]; s=b
            while par[s]: s,a2=par[s]; path.append(a2)
            print('min budget B =',B,'final used',u2); print(path[::-1]); break
