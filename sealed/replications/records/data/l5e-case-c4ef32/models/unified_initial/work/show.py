import json,sys
sys.path.insert(0,'.')
tr=[json.loads(l) for l in open('transitions.jsonl',encoding='utf-8') if l.strip()]
H='0123456789abcdef'
def pr(f):
    for r,row in enumerate(f): print('%2d '%r+''.join(H[v] for v in row))
i=int(sys.argv[1]) if len(sys.argv)>1 else -1
t=tr[i]
print(t['action'],t['ctx'])
d=[(r,c,t['prev'][r][c],t['nxt'][r][c]) for r in range(64) for c in range(64) if t['prev'][r][c]!=t['nxt'][r][c]]
print('ndiff',len(d))
if d:
    rs=[x[0] for x in d]; cs=[x[1] for x in d]
    print('bbox rows',min(rs),max(rs),'cols',min(cs),max(cs))
    from collections import Counter
    print(Counter((a,b) for _,_,a,b in d))
if '-f' in sys.argv: pr(t['nxt'])
