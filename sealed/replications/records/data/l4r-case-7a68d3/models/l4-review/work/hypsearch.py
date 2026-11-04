"""Row-accurate L4 search over hypothesis combinations. Rules fixed by observation: moves, d-block, costs
(move 1, click 1, completing click 2), shrink keeps top-left, grow facing-left -> (t-2,l-2), beam iff faces up & l==31.
Varied: grow anchor for facing U/D/R, eat rule, refund rule, whether a win may land at used 19."""
import collections, itertools, json, sys
sys.path.insert(0,'work')
from l4mirror import passable, isCore, isItem
def cells(t,l,k): return [(t+i,l+j) for i in range(k) for j in range(k)]
def fits(t,l,k,box): return t>=0 and l>=0 and all(passable(box,r,c) for r,c in cells(t,l,k))
def core(t,l,k): return any(isCore(r,c) for r,c in cells(t,l,k))
def front(t,l,k,f):
    h=k//2
    return [(t+i,l+j) for i in range(k) for j in range(k) if {'U':i<h,'D':i>=h,'L':j<h,'R':j>=h}[f]]
D={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}
def search(anch, eat, refund, win19, B=18, start=((25,37,4,'D',False,True),0)):
    s0,u0=start
    best={s0:u0}; par={s0:None}; q=collections.deque([s0]); wins=[]
    def eats(t,l,k,f):
        it=any(isItem(r,c) for r,c in cells(t,l,k))
        if not it: return False
        if eat=='two': return k==2
        if eat=='front': return k==2 or any(isItem(r,c) for r,c in front(t,l,k,f))
        if eat=='any': return True
    def push(s,u,p,a):
        t,l,k,f,box,item=s
        if item and eats(t,l,k,f):
            s=(t,l,k,f,box,False); u = max(0,u-10) if refund=='m10' else min(u,9) if refund=='set9' else u
        if u>B: return
        if s not in best or u<best[s]: best[s]=u; par[s]=(p,a); q.append(s)
    while q:
        s=q.popleft(); u=best[s]; t,l,k,f,box,item=s
        lim = B+1 if win19 else B
        for d,(dr,dc) in D.items():
            t2,l2=t+dr*k,l+dc*k
            if fits(t2,l2,k,box):
                if core(t2,l2,k):
                    if u+1<=lim: wins.append((u+1,s,d))
                    continue
                push((t2,l2,k,d,box,item),u+1,s,d)
            else:
                push((t,l,k,d,box,item),u+1,s,d+'*')
        if k==4 and u+3<=B: push((t,l,2,f,box,item),u+5,s,'F')
        elif k==2 and u+3<=B:
            dt,dl=anch[f]; t2,l2=t+dt,l+dl
            if fits(t2,l2,4,box):
                if core(t2,l2,4):
                    if u+5<=lim+1: wins.append((u+5,s,'F'))
                else: push((t2,l2,4,f,box,item),u+5,s,'F')
        if f=='U' and l==31 and u+2<=B: push((t,l,k,f,True,item),u+4,s,'B')
    if not wins: return None
    w=min(wins); path=[w[2]]; s=w[1]
    while par[s]: s,a=par[s]; path.append(a)
    return w[0], path[::-1]
OPT=[(0,0),(0,-2),(-2,0),(-2,-2)]
if __name__=='__main__':
    res=collections.Counter(); plans=collections.defaultdict(list)
    for au,ad,ar in itertools.product(OPT,OPT,OPT):
        anch={'L':(-2,-2),'U':au,'D':ad,'R':ar}
        for eat in ('two','front','any'):
            for refund in ('m10','set9'):
                for win19 in (False,True):
                    r=search(anch,eat,refund,win19)
                    key=(eat,refund,win19)
                    res[key+(r is not None,)]+=1
                    if r: plans[key].append((anch,r))
    for k in sorted(res): print(k,res[k])
    json.dump({str(k):[(str(a),r) for a,r in v[:3]] for k,v in plans.items()},open('work/hypsearch_out.json','w'),indent=0)
