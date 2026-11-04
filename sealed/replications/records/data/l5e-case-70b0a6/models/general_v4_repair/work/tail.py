import json,sys
sys.path.insert(0,'concepts')
from _lib import bar_count, agent
L=[json.loads(l) for l in open('transitions.jsonl')]
n=int(sys.argv[1]) if len(sys.argv)>1 else 5
for t in L[-n:]:
    print(t['action'], 'bar', bar_count(t['prev']),'->',bar_count(t['nxt']), 'nf', t['ctx'].get('nframes'), 'agent', agent(t['nxt']), t['ctx']['state_next'], t['ctx']['level_next'])
