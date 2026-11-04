"""Alternative bar model: each action = 1 tick; a completing click = 1+e ticks; refill = -R ticks;
display rows = 2*f(32*(B-n)/B) with f in {floor, ceil, round}. Fit integers B,e,R per level."""
import json,sys,math
sys.path.insert(0,'concepts')
from _lib import bar_count, completes, map_cells, agent
L=[json.loads(l) for l in open('transitions.jsonl')]
def runs_for(lv):
    out=[];cur=None
    for t in L:
        if t['ctx']['level_prev']!=lv or t['ctx']['level_next']!=lv:
            if t['ctx']['level_prev']==lv-1 and t['ctx']['level_next']==lv: cur=[];out.append(cur)
            continue
        if bar_count(t['prev'])==64 and (cur is None or (cur and cur[-1]['ctx']['state_next']=='GAME_OVER')):
            cur=[];out.append(cur)
        if cur is not None: cur.append(t)
    return out
def kind(t):
    if t['action'].startswith('ACTION6'):
        if completes(t['prev'],t['action']): return 'C'
        if t['ctx'].get('nframes')==13 and all(t['prev'][r][c]==t['nxt'][r][c] for r in range(64) for c in range(62)): return 'X'
        x,y=map(int,t['action'].split(':')[1].split(','))
        if x<10: return 'X'
        return 'K'
    if set(map_cells(t['prev'],14))-set(map_cells(t['nxt'],14)): return 'R'
    return 'M'
for lv in (1,2,3,4,5):
    runs=[r for r in runs_for(lv) if len(r)>3]
    data=[]
    for run in runs:
        seq=[]
        for t in run:
            if t['ctx']['state_next']=='GAME_OVER' or t['ctx']['level_next']!=lv: break
            seq.append((kind(t),bar_count(t['nxt'])))
        data.append(seq)
    sols=[]
    for B in range(20,80):
        for e in range(0,4):
            for R in range(0,20):
                for fn in ('floor','ceil','round'):
                    f={'floor':math.floor,'ceil':math.ceil,'round':round}[fn]
                    ok=True
                    for seq in data:
                        n=0
                        for k,bc in seq:
                            n+={'M':1,'K':1,'C':1+e,'R':1-R,'X':0}[k]
                            if 2*max(0,f(32*(B-n)/B))!=bc: ok=False;break
                        if not ok: break
                    if ok: sols.append((B,e,R,fn))
    used_R = any(k=='R' for s in data for k,_ in s)
    sols2=sorted(set((B,e,(R if used_R else None),fn) for B,e,R,fn in sols))
    print('L%d runs=%d'%(lv,len(data)), sols2[:12], '...' if len(sols2)>12 else '')
