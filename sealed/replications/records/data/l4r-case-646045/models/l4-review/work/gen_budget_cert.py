import heapq, re
exec(open('work/gen_cert.py').read().split("def key(st)")[0])   # walk/valid/hit/step (loose grow)
def onE(y, x, h, w): return any(34 <= r <= 35 and 23 <= c <= 24 for r in range(y, y+h) for c in range(x, x+w))
def front(st):
    sm, o, y, x, f = st; s = 2 if sm else 4; h = s // 2
    return [onE(y, x, h, s), onE(y+h, x, h, s), onE(y, x, s, h), onE(y, x+h, s, h)][f]
def pick(st): return (st[0] and onE(st[2], st[3], 2, 2)) or front(st) or (st[2] == 33 and st[3] == 23)
COSTB = [1,1,1,1,5,4]
def cap(e): return 28 if e else 18
s0 = ((0, 0, 25, 37, 1), False)
dist = {s0: 0}; pq = [(0, s0)]
while pq:
    d, (st, e) = heapq.heappop(pq)
    if d > dist[(st, e)]: continue
    for a in range(6):
        n = step(st, a); c = COSTB[a]
        if n == 'WIN':
            assert d + c > cap(e), ('WIN', d, st, e, a); continue
        ne = e or pick(n)
        if d + c > cap(ne): continue
        if d + c < dist.get((n, ne), 999):
            dist[(n, ne)] = d + c; heapq.heappush(pq, (d + c, (n, ne)))
print('entries', len(dist))
by = {}
for ((sm, o, y, x, f), e), d in dist.items():
    by.setdefault(x, []).append('((⟨%s, %s, %d, %d, %d⟩, %s), %d)' % ('true' if sm else 'false', 'true' if o else 'false', y, x, f, 'true' if e else 'false', d))
L = ['import Game.L4Budget', 'namespace L4M', '',
     '/-- Certificate (work/gen_budget_cert.py): states reachable within the budget, bucketed by column, least spend. -/',
     'def bbucket : Nat → List (BSt × Nat)']
for x in sorted(by): L.append('  | %d => [%s]' % (x, ', '.join(by[x])))
L += ['  | _ => []', '', 'def bcols : List Nat := [%s]' % ', '.join(map(str, sorted(by))), '',
      'def blookup (s : BSt) : Option Nat :=',
      '  if s.1.x < 64 then ((bbucket s.1.x).find? (fun p => p.1 == s)).map (·.2) else none', '',
      'def okB (p : BSt × Nat) : Bool :=',
      '  acts.all fun a =>',
      '    match stepB p.1 a with',
      '    | none => decide (cap p.1.2 < p.2 + bcost a)',
      '    | some s\' => decide (cap s\'.2 < p.2 + bcost a) ||',
      '        (match blookup s\' with',
      '         | some d\' => decide (d\' ≤ p.2 + bcost a)',
      '         | none => false)', '']
nchunks = {}
for x in sorted(by):
    n = len(by[x]); k = (n + 59) // 60; nchunks[x] = k
L.append('def bchunk (x i : Nat) : List (BSt × Nat) := ((bbucket x).drop (60 * i)).take 60')
L.append('end L4M')
open('lean/Game/L4BudgetCert.lean', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
import json; json.dump(nchunks, open('work/bchunks.json', 'w'))
print(nchunks)
