import json,sys
sys.path.insert(0,'.')
from geo import diff, diff_sum
tr=[json.loads(l) for l in open('transitions.jsonl') if l.strip()]
n=int(sys.argv[1]) if len(sys.argv)>1 else 1
for r in tr[-n:]:
    d=diff(r['prev'],r['nxt'])
    print(r['action'], r['ctx'], 'ndiff',len(d))
    print(' sum', diff_sum(r['prev'],r['nxt']))
    if len(d)<=80:
        print(' ', d)
