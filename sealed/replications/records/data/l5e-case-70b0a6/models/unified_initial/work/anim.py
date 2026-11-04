import json
F=json.load(open('.last_frames.json'))
print(len(F),'frames')
base=F[-1]
for k,g in enumerate(F):
    ch=[(r,c,g[r][c],base[r][c]) for r in range(64) for c in range(64) if g[r][c]!=base[r][c]]
    if ch:
        rs=[x[0] for x in ch]; cs=[x[1] for x in ch]
        from collections import Counter
        print(k,len(ch),'rows',min(rs),max(rs),'cols',min(cs),max(cs),Counter(x[2] for x in ch).most_common(4))
    else: print(k,'== final')
