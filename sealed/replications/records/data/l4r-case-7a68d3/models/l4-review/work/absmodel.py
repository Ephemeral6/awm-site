"""Relaxed abstract model of L4 (block level, macro patterns). Dijkstra cost-to-goal."""
import heapq, itertools, json
# state: (i, big, up, box, item); l = 2i+1
def L(i): return 2*i+1
def k_of(big): return 4 if big else 2
def overlap_item(l,k): return l <= 24 and l+k-1 >= 23
def goal(s):
    i,big,up,box,item=s; l=L(i); k=k_of(big)
    return box and l+k-1 >= 57
def eat_opts(s):
    i,big,up,box,item=s
    out=[s]
    if item and overlap_item(L(i),k_of(big)):
        out.append((i,big,up,box,False))
    return out
def succ(s):
    """list of (action_name, cost, s')"""
    i,big,up,box,item=s; l=L(i); k=k_of(big)
    res=[]
    def add(name,c,t):
        for t2 in eat_opts(t): res.append((name,c,t2))
    # moves
    # left
    nl=l-k
    add('L',1,((nl-1)//2,big,False,box,item) if nl>=1 else (i,big,False,box,item))
    add('L',1,s)  # blocked keep-facing variant
    nl=l+k
    ok = nl+k-1 <= 63 and (box or nl+k-1 < 45)
    add('R',1,((nl-1)//2,big,False,box,item) if ok else (i,big,False,box,item))
    add('R',1,s)
    add('U',1,(i,big,True,box,item)); add('U',1,s)
    add('D',1,(i,big,False,box,item)); add('D',1,s)
    # f pattern: size toggle, cost 5 (3 clicks + completing click 2)
    if big:
        for nl in (l, l+2):
            if nl <= 63: add('F',5,((nl-1)//2,False,up,box,item))
    else:
        for nl in (l-2, l):
            if nl >= 1: add('F',5,((nl-1)//2,True,up,box,item))
    # beam: cost 4 (2 clicks + completing 2)
    add('B',4,(i,big,up,box or (up and l==31),item))
    return res
states=list(itertools.product(range(32),[False,True],[False,True],[False,True],[False,True]))
INF=10**6
# backward Dijkstra: Phi(goal)=10*item
pred={s:[] for s in states}
for s in states:
    for a,c,t in succ(s): pred[t].append((c,s))
phi={s:INF for s in states}
pq=[]
for s in states:
    if goal(s):
        phi[s]=10 if s[4] else 0; heapq.heappush(pq,(phi[s],s))
while pq:
    d,s=heapq.heappop(pq)
    if d>phi[s]: continue
    for c,p in pred[s]:
        if goal(p): continue
        if d+c<phi[p]:
            phi[p]=d+c; heapq.heappush(pq,(phi[p],p))
s0=((37-1)//2,True,False,False,True)
print('Phi(s0)=',phi[s0])
s0n=((37-1)//2,True,False,False,False)
print('Phi(s0 no item)=',phi[s0n])
M=max(v for v in phi.values() if v<INF); print('max finite',M, 'inf count', sum(v>=INF for v in phi.values()))
json.dump({str(s):phi[s] for s in states},open('work/phi.json','w'))

def plan(s):
    out=[]
    while not goal(s):
        best=None
        for a,c,t in succ(s):
            if goal(t): v=c+(10 if t[4] else 0)
            else: v=c+phi[t]
            if v==phi[s] and t!=s: best=(a,c,t); break
        a,c,t=best; out.append((a,c,(L(t[0]),k_of(t[1]),t[2],t[3],t[4]))); s=t
    return out
for x in plan(s0): print(x)
