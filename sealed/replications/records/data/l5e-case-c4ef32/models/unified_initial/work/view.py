import json
H='0123456789abcdef'
tr=[json.loads(l) for l in open('transitions.jsonl',encoding='utf-8') if l.strip()]
f=tr[-1]['nxt']; p=tr[-1]['prev']
bar=sum(1 for r in range(64) if f[r][62]==14)
print('bar rows e:',bar)
for r in range(5,40): print('%2d '%r+''.join(H[v] for v in f[r][30:56]))
