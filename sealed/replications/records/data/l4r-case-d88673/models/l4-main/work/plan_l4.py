"""Plan level 4 with the exact unit budget and the e-marker refill. Variants for unknowns:
REFILL: 'set7' (counter set to 7 after the pickup move) | 'minus10' (counter -= 10)
TRIGGER: 'small' (any 2x2 overlap) | 'front' (overlap by the player's 9 half, any size)"""
import sys, heapq
sys.path.insert(0, 'work')
import model_l4 as M
B = 18
E = {(34, 23), (34, 24), (35, 23), (35, 24)}
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
def cells(i, j, sz, face):
    s = 2 if sz == 0 else 4; r0, c0 = 2*i+1, 2*j+1
    allc = {(r0+a, c0+b) for a in range(s) for b in range(s)}
    h = s // 2
    front = {"up": {(r0+a, c0+b) for a in range(h) for b in range(s)},
             "down": {(r0+h+a, c0+b) for a in range(h) for b in range(s)},
             "left": {(r0+a, c0+b) for a in range(s) for b in range(h)},
             "right": {(r0+a, c0+h+b) for a in range(s) for b in range(h)}}[face]
    return allc, front
FN = {0: "up", 1: "down", 2: "left", 3: "right"}
def plan(refill, trigger, anchored):
    # state: (i,j,sz,face,door,picked,u)
    st0 = (12, 18, 1, 1, 0, 0, 0)
    pq = [(0, st0, [])]; seen = {}
    while pq:
        u, s, path = heapq.heappop(pq)
        i, j, sz, face, door, picked, _ = s
        key = s[:6]
        if seen.get(key, 99) <= u: continue
        seen[key] = u
        for a in M.ACTIONS:
            if anchored and a[0] == 'resize':
                if sz == 1 and a[1] != 0: continue
                if sz == 0 and a[1] not in (2, 3): continue  # grow keeps bottom row (left or right ext)
            c = M.COST[a[0]] if a[0] != 'resize' else 5
            nu = u + c
            if nu > B: continue
            t, s2 = M.step((i, j, sz, 1 if face == 0 else 0, door), a)
            if t == 'win': return nu, path + [a]
            ni, nj, nsz, nup, ndoor = s2
            nface = a[1] if a[0] == 'move' else face
            npicked = picked
            if not picked:
                allc, front = cells(ni, nj, nsz, FN[nface])
                hit = (nsz == 0 and allc & E) if trigger == 'small' else (front & E)
                if hit:
                    npicked = 1
                    nu = 7 if refill == 'set7' else max(0, nu - 10)
            ns = (ni, nj, nsz, nface, ndoor, npicked, 0)
            heapq.heappush(pq, (nu, ns, path + [a]))
    return None
for refill in ('set7', 'minus10'):
    for trigger in ('small', 'front'):
        for anchored in (False, True):
            print(refill, trigger, 'anchored' if anchored else 'loose', plan(refill, trigger, anchored))
