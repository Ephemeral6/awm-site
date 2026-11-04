import fast, itertools, json
from search2 import run
res=[]
for gw, turn, place, coll in itertools.product([True, False],[False, True],['obs','all'],['full','probe']):
    fast.GROW_WALLCHECK = gw
    acts=[a for a in fast.ACTS if (turn or a[0]!='turn') and (place=='all' or not ((a[0]=='shrink' and a[1]!=(0,0)) or (a[0]=='grow' and a[1]!=(2,2)))) ]
    b,n,w=run(coll,acts)
    res.append(dict(grow_wallcheck=gw, turn=turn, placements=place, collision=coll, H0=b, net=b-10, affordable=b<=45, states=n))
    print(res[-1])
json.dump(res,open('variants.json','w'),indent=1)
