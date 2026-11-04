"""Replay every observed L4 transition (attempts 1-3) through M4 v3 (work/l4mirror.py == lean/L4Model.lean,
qD = 0) and compare block position/size/facing/box/item. Prints matched / mismatched / abstained."""
import json, sys
sys.path.insert(0,'work'); sys.path.insert(0,'concepts')
import l4mirror as M
from _lib import piece, counter_used
def facing(g,p):
    t,l,k=p; h=k//2
    rows=[[g[t+i][l+j] for j in range(k)] for i in range(k)]
    if all(rows[i][j]==9 for i in range(h) for j in range(k)): return 'U'
    if all(rows[i][j]==9 for i in range(h,k) for j in range(k)): return 'D'
    if all(rows[i][j]==9 for i in range(k) for j in range(h)): return 'L'
    return 'R'
def boxalive(g): return g[6][31]==13
EATEN=[False]
def itemalive(g):
    if EATEN[0]: return False
    p=piece(g); cov=set()
    if p: cov={(p[0]+i,p[1]+j) for i in range(p[2]) for j in range(p[2])}
    alive=any(g[r][c]==14 or ((r,c) in cov and p[2]==4) for r in (34,35) for c in (23,24))
    if not alive: EATEN[0]=True
    return alive
def blk(g):
    p=piece(g)
    if p is None: return None
    t,l,k=p
    return (t,l,k==4,facing(g,p),not boxalive(g),itemalive(g))
CELL={(26,50):1,(31,50):1,(36,50):2,(26,55):3,(31,55):4,(36,55):5,(26,60):6,(31,60):7,(36,60):8}
F={1,3,5,7}; S={1,4,7}
tr=[json.loads(l) for l in open('transitions.jsonl')]
L4=[r for r in tr if r['ctx'].get('level_prev')==4 and r['ctx'].get('level_next')==4]
mask=0; ok=bad=na=0
for r in L4:
    a=r['action']
    pp,pn=piece(r['prev']),piece(r['nxt'])
    if pp and pn and pp[:2]!=pn[:2] and a.startswith('ACTION6') and counter_used(r['nxt'])<counter_used(r['prev']) and pn==(25,37,4):
        EATEN[0]=False; mask=0; na+=1; continue     # attempt boundary (level reset between frames)
    b=blk(r['prev'])
    if counter_used(r['nxt'])<counter_used(r['prev']): EATEN[0]=True   # a refund means the item was eaten
    b2=blk(r['nxt'])
    if r['ctx'].get('state_next')=='GAME_OVER': na+=1; continue
    if a.startswith('ACTION6'):
        x,y=map(int,a.split(':')[1].split(',')); c=CELL.get((x,y))
        if c is None: pred=b
        else:
            m2=mask^(1<<c)
            if m2==sum(1<<i for i in F): ba=('sz',True,0); mask=0
            elif m2==sum(1<<i for i in S): ba=('beam',True); mask=0
            else: ba=None; mask=m2
            if ba is None: pred=b
            else:
                res=M.bstep(b,ba) if b else None
                pred=res[1] if res and res[0]=='go' else None
    else:
        d={'ACTION1':'U','ACTION2':'D','ACTION3':'L','ACTION4':'R'}[a]
        res=M.bstep(b,('mv',d,True,True,True)) if b else None
        pred=res[1] if res and res[0]=='go' else None
    if b is None or b2 is None or pred is None: na+=1; continue
    if pred==b2: ok+=1
    else: bad+=1; print('MISMATCH',r['tid'],a,'pred',pred,'obs',b2)
print('replayed',ok+bad+na,'matched',ok,'mismatched',bad,'abstained',na)
