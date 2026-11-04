"""Loosest-consistent row-accurate L4 search: union of hypotheses that fit all observations."""
import json, collections
exec(open('work/realsearch.py').read().split('def run(')[0])
def front(t,l,k,f):
    h=k//2
    return {(t+i,l+j) for i in range(k) for j in range(k)
            if {'U':i<h,'D':i>=h,'L':j<h,'R':j>=h}[f]}
def run2(B=18, eatrule='union', anchors='all', quads='all', beamcols=(31,)):
    D={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}
    start=(25,37,4,'D',False,True)
    best={start:0}; q=collections.deque([start]); wins=[]; par={start:None}
    def after(t,l,k,f,box,item,u,s,a):
        if item and cells(t,l,k)&ITEM:
            ok = (k==2) or (u>B) or bool(front(t,l,k,f)&ITEM) if eatrule=='union' else (k==2)
            if ok:
                item=False; u=min(max(0,u-10),9)
        if u>B: return
        s2=(t,l,k,f,box,item)
        if s2 not in best or u<best[s2]:
            best[s2]=u; par[s2]=(s,a); q.append(s2)
    while q:
        s=q.popleft(); u=best[s]
        t,l,k,f,box,item=s
        for d,(dr,dc) in D.items():
            t2,l2=t+dr*k,l+dc*k
            new=cells(t2,l2,k)-cells(t,l,k)
            if all(floor(r,c,box) for r,c in new):
                if cells(t2,l2,k)&CORE: wins.append((u+1,s,d)); continue
                after(t2,l2,k,d,box,item,u+1,s,d)
            else:
                after(t,l,k,d,box,item,u+1,s,d+'blk'); after(t,l,k,f,box,item,u+1,s,'blk-keep')
        if k==4:
            for dt,dl in ([(0,0),(0,2),(2,0),(2,2)] if quads=='all' else [(0,0)]):
                after(t+dt,l+dl,2,f,box,item,u+5,s,'shrink')
        else:
            for dt,dl in ([(0,0),(0,-2),(-2,0),(-2,-2)] if anchors=='all' else [(-2,-2)]):
                t2,l2=t+dt,l+dl
                if cells(t2,l2,4)&CORE: wins.append((u+5,s,'grow-into-exit')); continue
                if all(floor(r,c,box) for r,c in cells(t2,l2,4)):
                    after(t2,l2,4,f,box,item,u+5,s,'grow')
        if f=='U' and l in beamcols and all(floor(r,c,box) for r in range(9,t) for c in (31,32)):
            after(t,l,k,f,True,item,u+4,s,'beam')
    if not wins: return None, len(best)
    w=min(wins,key=lambda x:x[0]); path=[w[2]]; s=w[1]
    while par[s]: s,a=par[s]; path.append(a)
    return w[0], path[::-1]
print('union, all anchors/quads:', run2())
print('2x2-only, observed anchors:', run2(eatrule='two',anchors='obs',quads='obs'))
print('union, B=19:', run2(B=19))
print('union, B=20:', run2(B=20))
print('union, beam at 29 or 31 (4x4 at 29 allowed):', run2(beamcols=(29,31)))
