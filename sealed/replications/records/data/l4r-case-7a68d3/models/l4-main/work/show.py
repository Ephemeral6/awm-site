import json,sys
p=sys.argv[1] if len(sys.argv)>1 else '.last_frame.json'
d=json.load(open(p))
f=d['frame'] if 'frame' in d else d
print('level',d.get('level'))
print('   '+''.join(str(i%10) for i in range(64)))
for i,r in enumerate(f):
    print('%2d '%i+''.join('0123456789abcdef'[v] for v in r))
