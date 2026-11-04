import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent.parent
tr=[json.loads(l) for l in open(H/"transitions.jsonl") if l.strip()]
n=int(sys.argv[1]) if len(sys.argv)>1 else 1
for r in tr[-n:]:
    p,q=r["prev"],r["nxt"]
    d=[(y,x,p[y][x],q[y][x]) for y in range(64) for x in range(64) if p[y][x]!=q[y][x]]
    print(r["action"],r["tid"],r["ctx"],"ndiff",len(d))
    from collections import Counter
    print(Counter((a,b) for _,_,a,b in d))
    if d:
        ys=[t[0] for t in d]; xs=[t[1] for t in d]
        print("bbox rows",min(ys),max(ys),"cols",min(xs),max(xs))
    if len(d)<=40: print(d)
