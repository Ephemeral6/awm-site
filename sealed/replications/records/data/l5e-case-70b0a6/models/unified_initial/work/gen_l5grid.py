"""Generate lean/L5GridData.lean: masks of the L5 map at 2-pixel resolution and a cost-to-go table f
for the certificate in lean/L5Grid.lean. Every function here mirrors a Lean definition of the same name;
Lean re-checks the table, so a mismatch makes the proof fail, never pass wrongly."""
import json, sys
sys.set_int_max_str_digits(0)
L=[json.loads(l) for l in open('transitions.jsonl')]
g0=[t for t in L if t['ctx']['level_prev']==5][0]['prev']
NI,NJ=23,31
def pix_ok(v,r,c,cg,dg):
    if v in (2,9,10,14,15,11): return True
    if v==12 and cg: return True
    if v==13 and dg: return True
    if v==6 and cg and 9<=r<=12 and 20<=c<=23: return True
    if v==6 and dg and 14<=r<=17 and 55<=c<=58: return True
    return False
W0=WC=WD=BC=BD=0
for i in range(NI):
    for j in range(NJ):
        px=[(2*i+1+a,2*j+1+b) for a in (0,1) for b in (0,1)]
        k=i*NJ+j
        a0=all(pix_ok(g0[r][c],r,c,False,False) for r,c in px)
        ac=all(pix_ok(g0[r][c],r,c,True,False) for r,c in px)
        ad=all(pix_ok(g0[r][c],r,c,False,True) for r,c in px)
        if a0: W0|=1<<k
        elif ac: WC|=1<<k
        elif ad: WD|=1<<k
        if any(9<=r<=12 and 20<=c<=23 and g0[r][c] in (6,12) for r,c in px): BC|=1<<k
        if any(14<=r<=17 and 55<=c<=58 and g0[r][c] in (6,13) for r,c in px): BD|=1<<k
bit=lambda m,k:(m>>k)&1==1
def walk(cg,dg,i,j): return i<NI and j<NJ and (bit(W0,i*NJ+j) or (cg and bit(WC,i*NJ+j)) or (dg and bit(WD,i*NJ+j)))
def fits(cg,dg,i,j,big):
    if big: return walk(cg,dg,i,j) and walk(cg,dg,i,j+1) and walk(cg,dg,i+1,j) and walk(cg,dg,i+1,j+1)
    return walk(cg,dg,i,j)
# state = (i,j,big,cg,dg,ee,fr)
def sz(s): return 2 if s[2] else 1
def tgt(s,d,n):
    i,j=s[0],s[1]
    if d==0: return (i-n,j) if i>=n else None
    if d==1: return (i+n,j)
    if d==2: return (i,j-n) if j>=n else None
    return (i,j+n)
def goalHit(ti,tj,n): return 2*ti+1<=4 and 2*tj+2*n>=32 and 2*tj+1<=37
def wins(s,a):
    if a>=4: return False
    t=tgt(s,a,sz(s))
    return t is not None and goalHit(t[0],t[1],sz(s))
def winReady(s): return any(wins(s,d) for d in range(4))
def covers(i,j,big,a,b):
    n=2 if big else 1
    return i<=a<i+n and j<=b<j+n
def mc(s): return 90 if s[2] else 89
def place(s,i,j,d):
    if (not s[5]) and covers(i,j,s[2],18,24): return ((i,j,s[2],s[3],s[4],True,s[6],d),mc(s)-900)
    return ((i,j)+s[2:7]+(d,),mc(s))
def move(s,d):
    t=tgt(s,d,sz(s))
    if t is None: return (s[:7]+(d,),mc(s))
    if fits(s[3],s[4],t[0],t[1],s[2]): return place(s,t[0],t[1],d)
    if s[2]:
        h=tgt(s,d,1)
        if h is not None and fits(s[3],s[4],h[0],h[1],True): return place(s,h[0],h[1],d)
    return (s[:7]+(d,),mc(s))
def rayHit(cg,dg,box,fuel,i,j,d):
    while True:
        if fuel==0: return False
        fuel-=1
        if walk(cg,dg,i,j):
            if d==0:
                if i==0: return False
                i-=1
            elif d==1: i+=1
            elif d==2:
                if j==0: return False
                j-=1
            else: j+=1
        else:
            return i<NI and j<NJ and bit(box,i*NJ+j)
def laneHit(s,box):
    i,j,n=s[0],s[1],sz(s);cg,dg=s[3],s[4]
    d=s[7]
    for k in range(n):
        if d==0 and i>=1 and rayHit(cg,dg,box,40,i-1,j+k,0): return True
        if d==1 and rayHit(cg,dg,box,40,i+n,j+k,1): return True
        if d==2 and j>=1 and rayHit(cg,dg,box,40,i+k,j-1,2): return True
        if d==3 and rayHit(cg,dg,box,40,i+k,j+n,3): return True
    return False
OFF=[(0,0),(0,1),(1,0),(1,1)]
def step(s,a):
    i,j,big,cg,dg,ee,fr,fc=s
    if a<4: return move(s,a)
    if a==4: return ((i,j,False,cg,dg,ee,True,fc),468) if big else (s,468)
    if 5<=a<=8:
        if big: return (s,468)
        di,dj=OFF[a-5]
        if i>=di and j>=dj and fits(cg,dg,i-di,j-dj,True): return ((i-di,j-dj,True,cg,dg,ee,False,fc),468)
        return (s,468)
    if a==9: return ((i,j,big,True,dg,ee,fr,fc),376) if (not cg and laneHit(s,BC)) else (s,376)
    if a==10: return ((i,j,big,cg,True,ee,fr,fc),376) if (not dg and laneHit(s,BD)) else (s,376)
    if a==11: return (((18,7) if fr else (8,16))+s[2:],376)
    return (s,0)
start=(14,8,True,False,False,False,False,1)
# reachable
R={start};st=[start]
while st:
    s=st.pop()
    for a in range(12):
        if wins(s,a): continue
        t,_=step(s,a)
        if t not in R: R.add(t);st.append(t)
print('reachable',len(R))
T2={s for s in R if any((not wins(s,a)) and winReady(step(s,a)[0]) for a in range(12))}
print('T2',len(T2))
INF=10**9
f={s:(0 if s in T2 else INF) for s in R}
changed=True
while changed:
    changed=False
    for s in R:
        for a in range(12):
            if wins(s,a): continue
            t,w=step(s,a)
            if f[t]<INF and w+f[t]<f[s]: f[s]=w+f[t];changed=True
for s in R:
    if f[s]>=INF: f[s]=30000 if s[5] else 29190
print('f(start)=',f[start],' min f', min(f.values()), 'max f', max(f.values()))
def code(s): return s[0]*3968+s[1]*128+s[7]*32+(16 if s[2] else 0)+(8 if s[3] else 0)+(4 if s[4] else 0)+(2 if s[5] else 0)+(1 if s[6] else 0)
rows=[0]*NI
for s,v in f.items():
    x=v+2000
    assert 1<=x<65536
    c=code(s); rows[c//3968]|=x<<(16*(c%3968))
with open('lean/L5GridData.lean','w',encoding='utf-8') as o:
    o.write('/- generated by work/gen_l5grid.py from the L5 initial frame (do not edit) -/\nnamespace L5G\n')
    for n,v in (('W0',W0),('WC',WC),('WD',WD),('BC',BC),('BD',BD)): o.write('def %s : Nat := %d\n'%(n,v))
    o.write('def ftab : Nat → Nat\n')
    for i,v in enumerate(rows): o.write('  | %d => %d\n'%(i,v))
    o.write('  | _ => 0\nend L5G\n')
print('written')

# extract an optimal path start -> T2 -> win
names={0:'U',1:'D',2:'L',3:'R',4:'SHRINK',5:'GROW00',6:'GROW0-1',7:'GROW-10',8:'GROW-1-1',9:'FIREc',10:'FIREd',11:'TELE'}
s=start;path=[];run=0
while s not in T2:
    for a in range(12):
        if wins(s,a): continue
        t,w=step(s,a)
        if f[t]+w==f[s]:
            path.append((names[a],t[:2],'big' if t[2] else 'small',run+w));run+=w;s=t;break
for a in range(12):
    if not wins(s,a) and winReady(step(s,a)[0]):
        t,w=step(s,a);path.append((names[a],t[:2],run+w,'->winReady'));break
for p in path: print(p)
