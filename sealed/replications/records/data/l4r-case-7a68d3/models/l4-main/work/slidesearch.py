"""Row-accurate L4 search with the SLIDE rule (attempt 3): a move that cannot go its full k slides the largest
free multiple of 2 (k=4: 2), else stays. Other rules as M4 v2: shrink TL (all facings), grow (t-2,l-2) facings L/D
(U/R: option), eat 2x2 overlap or 4x4 front overlap (moves) / grow overlap, refund -10, costs, budget 18, no win past 18."""
import collections, sys
sys.path.insert(0,'work')
from l4mirror import passable, isCore, isItem
def cells(t,l,k): return [(t+i,l+j) for i in range(k) for j in range(k)]
def fits(t,l,k,box): return t>=0 and l>=0 and all(passable(box,r,c) for r,c in cells(t,l,k))
def core(t,l,k): return any(isCore(r,c) for r,c in cells(t,l,k))
def front(t,l,k,f):
    h=k//2; return [(t+i,l+j) for i in range(k) for j in range(k) if {'U':i<h,'D':i>=h,'L':j<h,'R':j>=h}[f]]
D={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}
def eats(t,l,k,f,grown=False):
    if k==2: return any(isItem(r,c) for r,c in cells(t,l,2))
    if grown: return any(isItem(r,c) for r,c in cells(t,l,4))
    return any(isItem(r,c) for r,c in front(t,l,4,f))
def search(start,u0,B=18,growUR=((-2,-2),),coreBlocks=False):
    best={start:u0}; par={start:None}; q=collections.deque([start]); wins=[]
    def push(s,u,p,a,grown=False):
        t,l,k,f,box,item=s
        if item and eats(t,l,k,f,grown): s=(t,l,k,f,box,False); u=max(0,u-10)
        if u>B: return
        if s not in best or u<best[s]: best[s]=u; par[s]=(p,a); q.append(s)
    while q:
        s=q.popleft(); u=best[s]; t,l,k,f,box,item=s
        for d,(dr,dc) in D.items():
            moved=False
            for step in ([k,k-2] if k==4 else [k]):
                t2,l2=t+dr*step,l+dc*step
                if t2>=0 and l2>=0 and all(passable(box,r,c) or (False) for r,c in cells(t2,l2,k)):
                    if core(t2,l2,k) and not coreBlocks:
                        if u+1<=B: wins.append((u+1,s,d+str(step)))
                        moved=True; break
                    if core(t2,l2,k) and coreBlocks: continue
                    push((t2,l2,k,d,box,item),u+1,s,d+str(step)); moved=True; break
            if not moved: push((t,l,k,d,box,item),u+1,s,d+'*')
        if k==4 and u+3<=B: push((t,l,2,f,box,item),u+5,s,'F')
        if k==2 and u+3<=B:
            for dt,dl in ([(-2,-2)] if f in 'LD' else growUR):
                t2,l2=t+dt,l+dl
                if fits(t2,l2,4,box):
                    if core(t2,l2,4):
                        if u+5<=B: wins.append((u+5,s,'F'))
                    else: push((t2,l2,4,f,box,item),u+5,s,'F',grown=True)
        if f=='U' and l==31 and u+2<=B: push((t,l,k,f,True,item),u+4,s,'B')
    if not wins: return None
    w=min(wins); path=[w[2]]; s=w[1]
    while par[s]: s,a=par[s]; path.append(a)
    return w[0],path[::-1]
if __name__=='__main__':
    print('from now:',search((33,35,4,'D',False,True),13))
    print('from reset:',search((25,37,4,'D',False,True),0))
    print('from reset, core blocks moves:',search((25,37,4,'D',False,True),0,coreBlocks=True))
