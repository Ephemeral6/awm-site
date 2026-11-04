import json,sys
L=[json.loads(l) for l in open('transitions.jsonl')]
i=int(sys.argv[1]) if len(sys.argv)>1 else -1
t=L[i]
p,n=t['prev'],t['nxt']
print(t['action'],t['ctx'])
ch=[(r,c,p[r][c],n[r][c]) for r in range(64) for c in range(64) if p[r][c]!=n[r][c]]
print(len(ch),'changed')
from collections import Counter
print(Counter((a,b) for _,_,a,b in ch))
if ch:
    rs=[x[0] for x in ch]; cs=[x[1] for x in ch]
    print('bbox rows',min(rs),max(rs),'cols',min(cs),max(cs))
if len(ch)<80:
    for x in ch: print(x)
