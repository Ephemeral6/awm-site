"""Attempt-5 amendment of work/L4Model.template.lean + certificate (g for the half-step budget rule)."""
import sys
from pathlib import Path
sys.set_int_max_str_digits(0)
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H))
import model_l4 as M
import model_l4b as Q

tpl = H / "L4Model.template.lean"
s = tpl.read_text(encoding="utf-8")

if "def runB5" not in s:
    a = s.index("def ok3 (s : St3) (a : Act) : Bool :=")
    b = s.index("def dirs : List Dir")
    s = s[:a] + '''/-- Attempt 5: the action that STARTS at the last affordable unit (u = cap) is the last one. A 4x4 move then
    advances only one 2-px sub-step (observed tid c20aa696def56d6b); generously, that half-step wins if its
    rectangle reaches the goal. Every other last action resolves fully (2x2 moves observed; clicks generous). -/
def halfWin (s : St3) (d : Dir) : Bool :=
  let tgt : Option (Nat × Nat) := match d with
    | .up => if s.i < 1 then none else some (s.i - 1, s.j)
    | .down => some (s.i + 1, s.j)
    | .left => if s.j < 1 then none else some (s.i, s.j - 1)
    | .right => some (s.i, s.j + 1)
  match tgt with
  | none => false
  | some (ni, nj) => !rectBlocked s.door true ni nj && rectGoal true ni nj

def isWin : Out3 → Bool | .win => true | _ => false

def lastWins (s : St3) (a : Act) : Bool :=
  match a with
  | .move d => if s.big then halfWin s d else isWin (step3 s a)
  | _ => isWin (step3 s a)

/-- Budgeted run, attempt-5 rule. -/
def runB5 (cap : Nat) (s : St3) (u : Nat) : List Act → Bool
  | [] => false
  | a :: as => if u > cap then false else if u = cap then lastWins s a else match step3 s a with
    | .win => true
    | .st s' n => runB5 cap s' (nu u a n) as

def ok3 (s : St3) (a : Act) : Bool :=
  if g s > 18 then true else
  !lastWins s a &&
  (if g s = 18 then true else
    match step3 s a with
    | .win => false
    | .st s' n => valid3 s' && decide (g s' ≤ nu (g s) a n))

''' + s[b:]
    # replace the invariant proof and the cap-17 theorem
    a = s.index("/-- Invariant: from a valid state whose counter is at least g, no action list wins under cap 17. -/")
    b = s.index("theorem g_start : g start3 = 0 := by decide")
    s = s[:a] + '''/-- Invariant: from a valid state whose counter is at least g, no action list wins (cap 18, attempt-5 rule). -/
theorem no_win_from (as : List Act) : ∀ s u, valid3 s = true → g s ≤ u → runB5 18 s u as = false := by
  induction as with
  | nil => intro s u _ _; rfl
  | cons a as ih =>
    intro s u hv hg
    have hok := ok3_of_valid s hv a
    by_cases hu : u > 18
    · simp [runB5, hu]
    · have hgs : ¬ g s > 18 := by omega
      unfold ok3 at hok
      simp only [hgs, if_false, Bool.and_eq_true, Bool.not_eq_true'] at hok
      by_cases he : u = 18
      · simp only [runB5, hu, he, if_false, if_true]; exact hok.1
      · have hg17 : ¬ g s = 18 := by omega
        simp only [hg17, if_false] at hok
        simp only [runB5, hu, he, if_false]
        cases hs : step3 s a with
        | win => rw [hs] at hok; simp at hok
        | st s' n =>
          rw [hs] at hok
          simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
          exact ih s' (nu u a n) hok.2.1 (Nat.le_trans hok.2.2 (nu_mono _ _ a n hg))

''' + s[b:]
    a = s.index("/- RETIRED (attempt 4):")
    b = s.index("/-- The attempt-4 plan.")
    s = s[:a] + '''/- RETIRED (attempt 4): `l4_unwinnable_with_refill` and `witness3_wins_cap19` (grow right-first and
   refill min 7 refuted by attempt 4).
   RETIRED (attempt 5): `l4_no_win_cap17 : runB 17 start3 0 as = false` -- its certificate is replaced by the
   attempt-5 one below; the question it answered (is there slack?) is subsumed by `l4_unwinnable_half`. -/

/-- MAIN (attempt 5): with the attempt-5 budget rule (cap 18; a 4x4 move starting at 18 only half-steps),
    no list of model actions wins level 4. -/
theorem l4_unwinnable_half (as : List Act) : runB5 18 start3 0 as = false :=
  no_win_from as start3 0 valid_start3 (by rw [g_start]; exact Nat.le_refl 0)

/-- Non-vacuity 1: one more unit (cap 19) and the attempt-4 plan wins under the attempt-5 rule. -/
theorem plan4_wins_cap19 : runB5 19 start3 0 plan4 = true := by decide

/-- Non-vacuity 2: the half-step rule is what blocks: under the attempt-4 rule (full last move) plan4 wins
    at cap 18 (`l4_winnable`), but under the attempt-5 rule it does not. -/
theorem plan4_fails_cap18 : runB5 18 start3 0 plan4 = false := by decide

''' + s[b:]
    # plan4 must be defined before the theorems that use it: move plan4 def above
    p0 = s.index("/-- The attempt-4 plan.")
    p1 = s.index("/-- MAIN (attempt 4)")
    plan_txt = s[p0:p1]
    s = s[:p0] + s[p1:]
    s = s.replace("/-- MAIN (attempt 5):", plan_txt + "/-- MAIN (attempt 5):", 1)
    s = s.replace("theorem l4_winnable : runB 18 start3 0 plan4 = true := by decide",
                  "/-  (kept) attempt-4 budget rule -/\ntheorem l4_winnable : runB 18 start3 0 plan4 = true := by decide")
    s = s.replace("#print axioms L4.l4_no_win_cap17\n",
                  "#print axioms L4.l4_unwinnable_half\n#print axioms L4.plan4_wins_cap19\n#print axioms L4.plan4_fails_cap18\n")
    tpl.write_text(s, encoding="utf-8")

# ---- certificate for the attempt-5 rule (cap 18) ----
CAP = 18
STATES = [(i, j, b, f, d, p) for i in range(32) for j in range(32) for b in (0, 1) for f in range(4)
          for d in (0, 1) for p in (0, 1)]
def key3(st):
    i, j, b, f, d, p = st
    return ((((i * 32 + j) * 2 + b) * 4 + f) * 2 + d) * 2 + p
DIRS = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
def half_win(st, d):
    i, j, big, face, door, picked = st
    di, dj = DIRS[d]; ni, nj = i + di, j + dj
    if ni < 0 or nj < 0: return False
    return M.rect(ni, nj, 1, door) == "G"
def last_wins(st, a):
    if a[0] == "move" and st[2] == 1: return half_win(st, a[1])
    return Q.step(st, a)[0] == "win"
fv = {st: -1 for st in STATES}
lw = {st: any(last_wins(st, a) for a in Q.ACTIONS) for st in STATES}
changed = True
while changed:
    changed = False
    for st in STATES:
        best = 18 if lw[st] else fv[st]
        if best == 18:
            if fv[st] != 18: fv[st] = 18; changed = True
            continue
        for a in Q.ACTIONS:
            t, s2, newly = Q.step(st, a)
            c = Q.COST[a[0]]
            if t == "win":
                cand = 17
            else:
                f2 = fv.get(s2, -1)
                if f2 < 0: continue
                cand = min(17, f2 + 10 - c) if newly else min(17, f2 - c)
            best = max(best, cand)
        if best > fv[st]:
            fv[st] = best; changed = True
tab = 0
for st in STATES:
    tab |= (fv[st] + 1) << (5 * key3(st))
print("g(start) =", fv[Q.START] + 1)
s = tpl.read_text(encoding="utf-8")
chunks = "\n".join(f"theorem okRows3_{c} : ((List.range 4).map (· + {4*c})).all okRow3 = true := by decide +kernel"
                   for c in range(8))
disp = []
for c in range(7):
    disp.append(f"  by_cases h{c} : k < {4*(c+1)}\n  · exact okRow3_aux {4*c} okRows3_{c} k (by omega) (by omega)")
disp.append("  exact okRow3_aux 28 okRows3_7 k (by omega) (by omega)")
s = s.replace("@CHUNKS@", chunks).replace("@DISPATCH@", "\n".join(disp)).replace("@GT@", hex(tab))
(H / "L4Model.template.filled.lean").write_text(s, encoding="utf-8")
