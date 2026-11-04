import json,sys
from collections import Counter
d=json.load(open(sys.argv[1] if len(sys.argv)>1 else '.last_frame.json'))
g=d['frame']
print('level',d.get('level'))
hexs='0123456789abcdef'
print('   '+''.join(str(i%10) for i in range(64)))
for r,row in enumerate(g):
    print('%2d '%r+''.join(hexs[v] for v in row))
print(Counter(v for row in g for v in row))
