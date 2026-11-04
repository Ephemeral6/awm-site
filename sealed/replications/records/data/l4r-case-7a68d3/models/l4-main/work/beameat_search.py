"""Hypothesis H_beamEat: a beam passing over the item eats it (refund -10). Loose beam path = full block width."""
import sys, collections; sys.path.insert(0,'work')
import slidesearch as S
from l4mirror import passable, isItem
D=S.D
def beam_path(t,l,k,f,box,mode='full'):
    dr,dc=D[f]; cells=[]
    for step in range(1,40):
        tt,ll=t+dr*step,l+dc*step
        cs=S.cells(tt,ll,k)
        if mode=='lefthalf':   # beam lane = 2 cells of the block (left half for U, analogous for others)
            h=k//2
            if f in 'UD': cs=[(r,c) for r,c in cs if c<ll+h]
            else: cs=[(r,c) for r,c in cs if r<tt+h]
        if not all(passable(box,r,c) for r,c in cs): break
        cells+=cs
    return cells
def search(start,u0,B=18,mode='full'):
    best={start:u0}; par={start:None}; q=collections.deque([start]); wins=[]
    def push(s,u,p,a):
        t,l,k,f,box,item=s
        if item and S.eats(t,l,k,f): s=(t,l,k,f,box,False); u=max(0,u-10)
        if u>B: return
        if s not in best or u<best[s]: best[s]=u; par[s]=(p,a); q.append(s)
    while q:
        s=q.popleft(); u=best[s]; t,l,k,f,box,item=s
        for d,(dr,dc) in D.items():
            moved=False
            for step in ([k,k-2] if k==4 else [k]):
                t2,l2=t+dr*step,l+dc*step
                if t2>=0 and l2>=0 and all(passable(box,r,c) for r,c in S.cells(t2,l2,k)):
                    if S.core(t2,l2,k):
                        if u+1<=B: wins.append((u+1,s,d))
                    else: push((t2,l2,k,d,box,item),u+1,s,d)
                    moved=True; break
            if not moved: push((t,l,k,d,box,item),u+1,s,d+'*')
        if k==4 and u+3<=B: push((t,l,2,f,box,item),u+5,s,'F')
        if k==2 and u+3<=B and S.fits(t-2,l-2,4,box): push((t-2,l-2,4,f,box,item),u+5,s,'F')
        if u+2<=B:
            nbox = box or (f=='U' and l==31); nitem=item; uu=u+4
            if item and any(isItem(r,c) for r,c in beam_path(t,l,k,f,box,mode)): nitem=False; uu=max(0,uu-10)
            if uu<=B:
                s2=(t,l,k,f,nbox,nitem)
                if s2 not in best or uu<best[s2]: best[s2]=uu; par[s2]=(s,'B'); q.append(s2)
    if not wins: return None
    w=min(wins); path=[w[2]]; s=w[1]; states=[s]
    while par[s]: s,a=par[s]; path.append(a); states.append(s)
    return w[0], list(zip(path[::-1][1:]+[path[0]], states[::-1]))
for mode in ('full','lefthalf'):
    r=search((25,37,4,'D',False,True),0,mode=mode)
    print(mode, r if r is None else r[0])
    if r:
        for a,s in r[1]: print('   ',s,'->',a)
