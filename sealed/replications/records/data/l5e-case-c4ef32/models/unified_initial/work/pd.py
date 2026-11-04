import json
H='0123456789abcdef'
tr=[json.loads(l) for l in open('transitions.jsonl',encoding='utf-8') if l.strip()]
t=tr[-1]
d=[(r,c,a,b) for r in range(64) for c in range(64) if (a:=t['prev'][r][c])!=(b:=t['nxt'][r][c])]
print(len(d), d[:40])
print('bar', sum(1 for r in range(64) if t['nxt'][r][62]==14), t['ctx'])
import sys
if len(sys.argv)>1:
    r0,r1,c0,c1=map(int,sys.argv[1:5])
    for r in range(r0,r1): print('%2d '%r+''.join(H[v] for v in t['nxt'][r][c0:c1]))
