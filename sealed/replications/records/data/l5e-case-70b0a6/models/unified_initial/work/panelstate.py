import json,sys
sys.path.insert(0,'concepts')
from _lib import panel
L=[json.loads(l) for l in open('transitions.jsonl')]
for t in L[-int(sys.argv[1]):]:
    print(t['action'], panel(t['nxt']), t['ctx'].get('nframes'))
