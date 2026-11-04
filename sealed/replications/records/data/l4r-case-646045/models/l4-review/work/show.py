import json,sys
sys.path.insert(0,'.')
d=json.load(open('.last_frame.json'))
g=d['frame']
H='0123456789abcdef'
print('level',d['level'])
print('   '+''.join(str(i%10) for i in range(64)))
for y,row in enumerate(g):
    print('%2d '%y+''.join(H[v] for v in row))
