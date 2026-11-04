import json,sys,math,itertools
sys.path.insert(0,'concepts')
from _lib import bar_count, completes, map_cells, agent
L=[json.loads(l) for l in open('transitions.jsonl')]
# split level-5 transitions into attempts (start = prev equals L5 initial frame after a GAME_OVER or level entry)
g0=[t for t in L if t['ctx']['level_prev']==5][0]['prev']
runs=[];cur=None
for t in L:
    if t['ctx']['level_prev']!=5 or t['ctx']['level_next']!=5: continue
    if t['prev']==g0: cur=[];runs.append(cur)
    if cur is not None: cur.append(t)
def kind(t):
    if not t['action'].startswith('ACTION6'):
        if set(map_cells(t['prev'],14))-set(map_cells(t['nxt'],14)): return 'R'
        a=agent(t['prev']); return 'MB' if (a and a[3]==4) else 'MS'
    if completes(t['prev'],t['action']): return 'C'
    if t['ctx'].get('nframes')==13 and t['prev']==t['nxt']: return 'X'   # off-panel blink
    x,y=map(int,t['action'].split(':')[1].split(','))
    if x<10 and y<32: return 'X'  # thumbnail
    return 'K'
data=[]
for run in runs:
    used=[];ks=[];prevbar=None
    for t in run:
        if t['ctx']['state_next']=='GAME_OVER': break
        used.append((64-bar_count(t['nxt']))//2); ks.append(kind(t))
    data.append((ks,used))
print([len(k) for k,_ in data])
sols=[]
for mb in range(85,96):
  for ms in range(85,101):
    for kc in range(85,96):
      for ex in range(5,16):
        ok=True
        for ks,used in data:
          tot=0
          for k,u in zip(ks,used):
            tot+={'MB':mb,'MS':ms,'K':kc,'C':kc+ex*10,'R':mb-900,'X':0}[k]
            if tot//100!=u: ok=False;break
          if not ok: break
        if ok: sols.append((mb,ms,kc,ex*10))
print(len(sols)); print(sols[:30])
