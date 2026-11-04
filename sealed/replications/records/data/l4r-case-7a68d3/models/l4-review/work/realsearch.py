"""Row-accurate L4 search under established rules + named hypothesis variants. Min 'used' label-correcting."""
import json, collections, sys
F=json.load(open('work/L4_initial.json'))
ITEM={(r,c) for r in range(47) for c in range(62) if F[r][c]==14}
DBAR={(r,c) for r in range(21,40) for c in range(45,48) if F[r][c]==13}
CORE={(r,c) for r in range(26,36) for c in range(55,62) if F[r][c]==10}
RING={(r,c) for r in range(26,36) for c in range(55,62) if F[r][c]==9}
START=(25,37,4,'D')
def floor(r,c,box):
    if not(0<=r<64 and 0<=c<62): return False
    if (r,c) in ITEM or (r,c) in CORE or (r,c) in RING: return True
    if (r,c) in DBAR: return box
    v=F[r][c]
    if 25<=r<=28 and 37<=c<=40: return True  # start block cells are floor underneath
    return v==2
def cells(t,l,k): return {(t+i,l+j) for i in range(k) for j in range(k)}
def run(refund='minus10', eat='two', B=18, blockedturn=True):
    D={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}
    start=(START[0],START[1],START[2],START[3],False,True)
    best={start:0}; par={start:None}
    q=collections.deque([start]); wins=[]
    def push(s2,u2,s,a):
        if u2>B and True: return
        if s2 not in best or u2<best[s2]:
            best[s2]=u2; par[s2]=(s,a); q.append(s2)
    def after(t,l,k,f,box,item,u,s,a):
        if item and (eat=='any' or k==2) and cells(t,l,k)&ITEM:
            item=False
            u = max(0,u-10) if refund=='minus10' else 9
        if u>B: return
        push((t,l,k,f,box,item),u,s,a)
    while q:
        s=q.popleft(); u=best[s]
        if u>B: continue
        t,l,k,f,box,item=s
        for d,(dr,dc) in D.items():
            t2,l2=t+dr*k,l+dc*k
            new=cells(t2,l2,k)-cells(t,l,k)
            if all(floor(r,c,box) for r,c in new):
                if cells(t2,l2,k)&CORE:
                    wins.append((u+1,s,d)); continue
                after(t2,l2,k,d,box,item,u+1,s,d)
            else:
                if blockedturn: after(t,l,k,d,box,item,u+1,s,d+'blk')
        if k==4:
            after(t,l,2,f,box,item,u+5,s,'shrink')
        else:
            t2,l2=t-2,l-2
            if all(floor(r,c,box) for r,c in cells(t2,l2,4)):
                after(t2,l2,4,f,box,item,u+5,s,'grow')
        if f=='U' and l==31 and all(floor(r,c,box) for r in range(9,t) for c in (31,32)):
            after(t,l,k,f,True,item,u+4,s,'beam')
    if not wins: return None
    w=min(wins,key=lambda x:x[0])
    path=[w[2]]; s=w[1]
    while par[s]: s,a=par[s]; path.append(a)
    return w[0], path[::-1]
for refund in ('minus10','set9'):
    for eat in ('two','any'):
        print(refund,eat,run(refund,eat))
