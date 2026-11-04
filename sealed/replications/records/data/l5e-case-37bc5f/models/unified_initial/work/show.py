import json,sys
sys.path.insert(0,'.')
from geo import hist, blobs
f=json.load(open('.last_frame.json'))
g=f['frame']; print('level',f['level'])
H='0123456789abcdef'
print('   '+''.join(str(i%10) for i in range(64)))
for i,row in enumerate(g): print('%2d '%i+''.join(H[v] for v in row))
print(hist(g))
