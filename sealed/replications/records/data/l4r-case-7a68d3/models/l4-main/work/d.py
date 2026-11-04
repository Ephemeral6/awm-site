import json
from collections import Counter
tr=[json.loads(l) for l in open('transitions.jsonl')]
import sys
n=int(sys.argv[1]) if len(sys.argv)>1 else 1
for r in tr[-n:]:
    d=[(y,x,r['prev'][y][x],r['nxt'][y][x]) for y in range(64) for x in range(64) if r['prev'][y][x]!=r['nxt'][y][x]]
    print(r['action'],r['tid'],len(d),dict(Counter((a,b) for _,_,a,b in d)), r['ctx'])
    if d:
        ys=[y for y,_,_,_ in d]; xs=[x for _,x,_,_ in d]
        print('  bbox rows',min(ys),max(ys),'cols',min(xs),max(xs))
