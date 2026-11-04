import json,sys
tr=[json.loads(l) for l in open('transitions.jsonl')]
i=int(sys.argv[1]); r0,r1,c0,c1=map(int,sys.argv[2:6])
r=tr[i]
H='0123456789abcdef'
print(r['action'])
for y in range(r0,r1+1):
    print('%2d '%y+''.join(H[v] for v in r['prev'][y][c0:c1+1])+'   '+''.join(H[v] for v in r['nxt'][y][c0:c1+1]))
