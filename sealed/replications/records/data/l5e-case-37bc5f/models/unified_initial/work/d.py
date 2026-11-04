# show diff of last transition
import json,sys
sys.path.insert(0,'.')
from geo import diff, diff_sum, diff_groups
L=[json.loads(l) for l in open('transitions.jsonl') if l.strip()]
n=int(sys.argv[1]) if len(sys.argv)>1 else 1
for r in L[-n:]:
    print(r['action'], r['ctx'], 'tid', r['tid'])
    print(' sum', diff_sum(r['prev'],r['nxt']))
    for k,v in diff_groups(r['prev'],r['nxt']).items():
        print('  ',k,len(v),v[:12])
