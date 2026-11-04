"""Attempt-3 generator: append the attempt-3 section to the template (once), compute the g certificate
with the same semantics as the Lean `step3`, then run gen_lean.py-style substitution."""
import sys
from pathlib import Path
sys.set_int_max_str_digits(0)
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H))
import model_l4 as M
import model_l4b as Q

tpl = H / "L4Model.template.lean"
src = tpl.read_text(encoding="utf-8")
if "Attempt 3 amendment" not in src:
    sec = (H / "L4Attempt3.section.lean").read_text(encoding="utf-8")
    src = src.replace("\nend L4\n", sec + "\nend L4\n", 1)
    src = src.replace("#print axioms L4.fire_2x2_col43_fails",
                      "#print axioms L4.l4_unwinnable_with_refill\n#print axioms L4.witness3_wins_cap19\n"
                      "#print axioms L4.pickup_happens\n#print axioms L4.big_cover_no_pickup\n"
                      "#print axioms L4.fire_2x2_col43_fails", 1)
    tpl.write_text(src, encoding="utf-8")

CAP = 17
STATES = [(i, j, b, f, d, p) for i in range(32) for j in range(32) for b in (0, 1) for f in range(4)
          for d in (0, 1) for p in (0, 1)]
def key3(s):
    i, j, b, f, d, p = s
    return ((((i * 32 + j) * 2 + b) * 4 + f) * 2 + d) * 2 + p

# f(s) = max counter from which a win is possible (-1 if none); iterate to fixpoint.
fv = {s: -1 for s in STATES}
changed = True
while changed:
    changed = False
    for s in STATES:
        best = fv[s]
        for a in Q.ACTIONS:
            t, s2, newly = Q.step(s, a)
            c = Q.COST[a[0]]
            if t == "win":
                cand = CAP
            else:
                f2 = fv.get(s2, -1)
                if f2 < 0:
                    continue
                if newly:
                    cand = min(CAP, f2 + 10 - c)   # refill minus 10
                else:
                    cand = min(CAP, f2 - c)
            if cand > best:
                best = cand
        if best > fv[s]:
            fv[s] = best; changed = True
tab = 0
for s in STATES:
    tab |= (fv[s] + 1) << (5 * key3(s))
print("g(start) =", fv[Q.START] + 1)

src = tpl.read_text(encoding="utf-8")
chunks = "\n".join(f"theorem okRows3_{c} : ((List.range 4).map (· + {4*c})).all okRow3 = true := by decide +kernel"
                   for c in range(8))
disp = []
for c in range(7):
    disp.append(f"  by_cases h{c} : k < {4*(c+1)}\n  · exact okRow3_aux {4*c} okRows3_{c} k (by omega) (by omega)")
disp.append("  exact okRow3_aux 28 okRows3_7 k (by omega) (by omega)")
src = src.replace("@CHUNKS@", chunks).replace("@DISPATCH@", "\n".join(disp)).replace("@GT@", hex(tab))
tpl_out = H / "L4Model.template.filled.lean"
tpl_out.write_text(src, encoding="utf-8")
