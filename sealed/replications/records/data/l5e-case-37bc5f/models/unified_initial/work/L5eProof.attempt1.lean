/-
# L5eProof — level 4 is winnable in the model, given one explicit hypothesis on the 6-recipe

MAIN-THEOREM: lean/L5eProof.lean : L5e.l4_winnable

Quantifies over: every open-condition `oc : Blk → Bool` and every cost profile `C`.
Assumes (explicit hypotheses, none of them computed outside Lean):
  hoc : oc ⟨21, 31, 2, .up⟩ = true      -- NOT established in play; the open question
  hm  : C.move ≤ 4, hc : C.click ≤ 4, hf : C.fire ≤ 8, hb : C.budget = 128
        (bar cells; upper bounds of every cost observed on level 4, bar = 128 cells)
-/
import L5eModel

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace L5e

/-! ## 0. conformance: the model replays the observed level-4 trajectory -/

def mv (d : Dir) : Act := .move d
def ck (i : Nat) : Act := .click i

/-- the level-4 actions actually sent (all were accepted; none swallowed) -/
def l4observed : List Act :=
  [mv .left, mv .left, mv .up,
   ck 1, ck 4, ck 7,  ck 1, ck 7, ck 4,  ck 1, ck 4, ck 7,
   mv .down, mv .down, mv .down, mv .left, mv .left,
   mv .right, mv .right, mv .up, mv .up, mv .up,
   ck 1, ck 3, ck 5, ck 7,
   mv .right, ck 1, ck 4, ck 7,
   mv .up]

/-- observed end state: 2x2 block at r19-20 c31-32 facing up, barrier closed, box present,
    panel all colour 2. (Read off the final frame, tid 48b2f90905c5eecf.) -/
theorem l4_replay_matches :
    run L4 (ocCand 31 20) l4init l4observed =
      { blk := ⟨19, 31, 2, .up⟩, panel := 0, gate := ⟨false, true⟩, status := .playing } := by
  decide +kernel

/-- the cost kinds of the observed trajectory: fires exactly at the 5 observed firing clicks -/
theorem l4_replay_kinds :
    (trace L4 (ocCand 31 20) l4init l4observed).2 =
      [.mv, .mv, .mv, .ck, .ck, .fire, .ck, .ck, .fire, .ck, .ck, .fire,
       .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv,
       .ck, .ck, .ck, .fire, .mv, .ck, .ck, .fire, .mv] := by
  decide +kernel

/-- ocCand agrees with all 7 observed 6-fires (L3: stalk col 29, bottom row 12; L4: col 31, row 20). -/
theorem ocCand_fits_observed_fires :
    ocCand 29 12 ⟨17, 37, 4, .down⟩ = false ∧ ocCand 29 12 ⟨25, 25, 4, .down⟩ = false ∧
    ocCand 29 12 ⟨13, 29, 4, .up⟩ = true ∧
    ocCand 31 20 ⟨21, 29, 4, .up⟩ = false ∧ ocCand 31 20 ⟨21, 31, 2, .right⟩ = false := by
  decide

/-! ## 1. the witness plan -/

def planPre : List Act :=
  [ck 1, ck 3, ck 5, ck 7,                 -- plus ring -> shrink to 2x2 at r25 c37
   mv .left, mv .left, mv .left,           -- c35, c33, c31
   mv .up, mv .up,                         -- r23, r21 : under the stalk, facing up
   ck 1, ck 4]
def planFire : Act := ck 7                 -- completes the vertical line -> 6-recipe
def planPost : List Act :=
  [mv .down, mv .down, mv .down, mv .down,  -- r29
   mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   mv .right, mv .right, mv .right, mv .right, mv .right, mv .right]  -- c57: touches socket
def plan : List Act := planPre ++ planFire :: planPost

/-! ### oc-irrelevance: a run depends on `oc` only at the states where the 6-recipe fires -/

/-- does this action evaluate `oc`? (it is a click that completes the open6 recipe while playing) -/
def queried (L : Level) (s : St) : Act → Bool
  | .move _ => false
  | .click i =>
    s.status != .won && i < 9 &&
      (match L.recipes.find? (fun rc => rc.mask == (s.panel ^^^ (1 <<< i))) with
       | some rc => rc.eff == .open6
       | none => false)

theorem step_irrel (L : Level) (oc oc' : Blk → Bool) (s : St) (a : Act)
    (h : queried L s a = true → oc s.blk = oc' s.blk) : step L oc s a = step L oc' s a := by
  unfold step
  cases hs : (s.status == Status.won)
  · simp only [Bool.false_eq_true, if_false]
    cases a with
    | move d => rfl
    | click i =>
      simp only [stepCore, clickRule]
      by_cases hi : i < 9
      · simp only [hi, if_true]
        cases hf : L.recipes.find? (fun rc => rc.mask == (s.panel ^^^ (1 <<< i))) with
        | none => rfl
        | some rc =>
          simp only
          cases he : rc.eff with
          | shrink => rfl
          | teleport r c => rfl
          | open6 =>
            have hq : queried L s (.click i) = true := by
              have hw : s.status ≠ Status.won := by
                intro e; rw [e] at hs; exact absurd hs (by decide)
              simp only [queried, hf, he, hi]
              cases hst : s.status with
              | won => exact absurd hst hw
              | playing => decide
            have := h hq
            simp only [applyEffect, this]
      · simp only [hi, if_false]
  · rfl

/-- blocks at which `oc` is consulted along the run driven by `oc'` -/
def queries (L : Level) (oc' : Blk → Bool) : St → List Act → List Blk
  | _, [] => []
  | s, a :: as =>
    (if queried L s a then [s.blk] else []) ++ queries L oc' (step L oc' s a) as

theorem trace_irrel (L : Level) (oc oc' : Blk → Bool) :
    ∀ (s : St) (as : List Act), (∀ b ∈ queries L oc' s as, oc b = oc' b) →
      trace L oc s as = trace L oc' s as
  | _, [] , _ => rfl
  | s, a :: as, h => by
    have hstep : step L oc s a = step L oc' s a := by
      apply step_irrel
      intro hq
      apply h
      simp [queries, hq]
    have hrest : trace L oc (step L oc' s a) as = trace L oc' (step L oc' s a) as := by
      apply trace_irrel L oc oc' _ as
      intro b hb
      apply h
      simp only [queries, List.mem_append]
      exact Or.inr hb
    simp only [trace, hstep, hrest]

def ocTrue : Blk → Bool := fun _ => true

/-- along the plan (driven by `ocTrue`) `oc` is consulted exactly once, at the planned firing state -/
theorem plan_queries : queries L4 ocTrue l4init plan = [⟨21, 31, 2, .up⟩] := by decide +kernel

theorem plan_trace_true :
    trace L4 ocTrue l4init plan =
      ({ blk := ⟨29, 57, 2, .right⟩, panel := 0, gate := ⟨true, false⟩, status := .won },
       [.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 .mv) := by
  decide +kernel

theorem plan_trace (oc : Blk → Bool) (hoc : oc ⟨21, 31, 2, .up⟩ = true) :
    trace L4 oc l4init plan =
      ({ blk := ⟨29, 57, 2, .right⟩, panel := 0, gate := ⟨true, false⟩, status := .won },
       [.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 .mv) := by
  rw [trace_irrel L4 oc ocTrue l4init plan, plan_trace_true]
  intro b hb
  rw [plan_queries] at hb
  simp only [List.mem_singleton] at hb
  subst hb
  exact hoc

/-! ## 2. budget: game over iff an action is sent when spent ≥ budget -/

theorem costSum_take_le (C : Costs) : ∀ (l : List Kind) (k : Nat), costSum C (l.take k) ≤ costSum C l
  | [], _ => by simp [costSum]
  | _ :: _, 0 => by simp [costSum]
  | x :: xs, k + 1 => by
      simp only [List.take_succ_cons, costSum]
      have := costSum_take_le C xs k
      omega

def cnt (k : Kind) : List Kind → Nat
  | [] => 0
  | x :: xs => (if x == k then 1 else 0) + cnt k xs

theorem costSum_cnt (C : Costs) : ∀ l : List Kind,
    costSum C l = cnt .mv l * C.move + cnt .ck l * C.click + cnt .fire l * C.fire
  | [] => by simp [costSum, cnt]
  | x :: xs => by
    have ih := costSum_cnt C xs
    cases x <;> simp [costSum, costOf, cnt, ih, Nat.add_mul] <;> omega

/-- every action of the plan is sent while spent < budget: the cost of the actions before
    action k is below the budget, for every k < 29 (the plan length). -/
def alive (C : Costs) (ks : List Kind) : Prop := ∀ k, k < ks.length → costSum C (ks.take k) < C.budget

theorem plan_kinds_alive (C : Costs) (hm : C.move ≤ 4) (hc : C.click ≤ 4) (hf : C.fire ≤ 8)
    (hb : C.budget = 128) :
    alive C ([.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 .mv) := by
  intro k hk
  have hlen : ([Kind.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 Kind.mv).length = 29 := rfl
  rw [hlen] at hk
  -- the prefix before action k is a prefix of the first 28 actions
  have htk : ∀ l : List Kind, l.take k = (l.take 28).take k := by
    intro l; rw [List.take_take]; congr 1; omega
  rw [htk]
  have hle := costSum_take_le C (([Kind.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 Kind.mv).take 28) k
  have h28 : costSum C (([Kind.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 Kind.mv).take 28)
      = 5 * C.click + 2 * C.fire + 21 * C.move := by
    rw [costSum_cnt]
    have e1 : cnt .mv (([Kind.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 Kind.mv).take 28) = 21 := by decide
    have e2 : cnt .ck (([Kind.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 Kind.mv).take 28) = 5 := by decide
    have e3 : cnt .fire (([Kind.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 Kind.mv).take 28) = 2 := by decide
    rw [e1, e2, e3]; omega
  omega

/-! ## 3. main theorem -/

/-- **Level 4 is won by `plan`** in the model, for every open-condition that holds at the planned
    firing state and every cost profile within the observed level-4 bounds. -/
theorem l4_winnable (oc : Blk → Bool) (hoc : oc ⟨21, 31, 2, .up⟩ = true)
    (C : Costs) (hm : C.move ≤ 4) (hc : C.click ≤ 4) (hf : C.fire ≤ 8) (hb : C.budget = 128) :
    (trace L4 oc l4init plan).1.status = .won ∧ alive C (trace L4 oc l4init plan).2 := by
  rw [plan_trace oc hoc]
  exact ⟨rfl, plan_kinds_alive C hm hc hf hb⟩

/-! ## 4. non-vacuity -/

/-- the hypothesis on `oc` is a real constraint: if the 6-recipe never opens, the same plan
    does not win (the block stops at the closed barrier). -/
theorem plan_fails_without_open :
    (trace L4 (fun _ => false) l4init plan).1.status = .playing := by decide +kernel

/-- and with the barrier never opened, no plan wins at all is NOT claimed here; this only shows
    the hypothesis is used. The budget hypothesis is also a real constraint: -/
theorem plan_dies_on_small_budget :
    ¬ alive ⟨4, 4, 8, 119⟩ ([.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 .mv) := by
  intro h
  have := h 28 (by decide)
  revert this; decide +kernel

/-- the exact budget threshold for this plan with worst-case costs is 121 cells (spent before
    the last action = 120). -/
theorem plan_alive_at_121 :
    alive ⟨4, 4, 8, 121⟩ ([.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 .mv) := by
  intro k hk
  revert k hk; decide +kernel

/-- the hypothesis `hoc` is satisfiable by the one candidate that fits all 7 observed fires -/
theorem ocCand_meets_hoc : ocCand 31 20 ⟨21, 31, 2, .up⟩ = true := by decide

end L5e

#print axioms L5e.l4_winnable
#print axioms L5e.l4_replay_matches
#print axioms L5e.l4_replay_kinds
#print axioms L5e.ocCand_fits_observed_fires
#print axioms L5e.plan_fails_without_open
#print axioms L5e.plan_dies_on_small_budget
#print axioms L5e.plan_alive_at_121
#print axioms L5e.ocCand_meets_hoc
#print axioms L5e.plan_trace
#print axioms L5e.trace_irrel
