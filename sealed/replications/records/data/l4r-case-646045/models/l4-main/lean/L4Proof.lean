import Game.L4Model
namespace L4
open Skeleton2

set_option maxHeartbeats 4000000

theorem inv_step (fires : St → Bool) (s s' : St) (a : Act)
    (hi : Inv s) (h : step fires false s a = .ok s') : Inv s' := by
  rcases s with ⟨sm, op, wn, x, p, l, y, fc⟩
  unfold Inv at hi
  cases wn
  · cases a with
    | noop => cases h; exact hi
    | left =>
      simp only [step, rLeft, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> (simp only [Inv, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all <;> omega
    | right =>
      simp only [step, rRight, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> cases op <;> (simp only [Inv, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all <;> omega
    | up =>
      simp only [step, rUp, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> (simp only [Inv, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all
    | down =>
      simp only [step, rDown, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> (simp only [Inv, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all
    | click u v =>
      simp only [step, rClick, Bool.false_eq_true, ite_false] at h
      cases sm <;> cases u <;> cases v <;> simp only [Bool.false_eq_true, ite_false, ite_true] at h <;>
        (repeat' split at h) <;> (try cases h) <;> simp_all [Inv] <;> omega
  · simp only [step, ite_true] at h; cases h; exact hi


theorem hstep (fires : St → Bool) (hfire : ∀ s, fires s = true → s.x = 31)
    (s s' : St) (a : Act) (hi : Inv s) (h : step fires false s a = .ok s') : Φ s ≤ Φ s' + 1 := by
  rcases s with ⟨sm, op, wn, x, p, l, y, fc⟩
  unfold Inv at hi
  cases wn
  · cases a with
    | noop => cases h; omega
    | left =>
      simp only [step, rLeft, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> cases op <;> (simp only [Φ, dist31, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all <;> omega
    | right =>
      simp only [step, rRight, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> cases op <;> (simp only [Φ, dist31, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all <;> omega
    | up =>
      simp only [step, rUp, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> cases op <;> (simp only [Φ, dist31, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all
    | down =>
      simp only [step, rDown, size, Bool.false_eq_true, ite_false] at h
      cases h; cases sm <;> cases op <;> (simp only [Φ, dist31, Bool.false_eq_true, ite_false, ite_true] at hi ⊢; repeat' split) <;> simp_all
    | click u v =>
      have hf := hfire ⟨sm, op, false, x, p, l, y, fc⟩
      simp only [step, rClick, Bool.false_eq_true, ite_false] at h
      cases hfv : fires ⟨sm, op, false, x, p, l, y, fc⟩ <;> simp only [hfv] at h hf <;>
      cases sm <;> cases op <;> cases u <;> cases v <;> simp only [Bool.false_eq_true, ite_false, ite_true] at h <;>
        (repeat' split at h) <;> (try cases h) <;> simp_all [Φ, dist31] <;> omega
  · simp only [step, ite_true] at h; cases h; omega

theorem hgoal : ∀ s, goal s = true → Φ s = 0 := by
  intro s h; simp only [goal] at h; simp [Φ, h]

/-- Potential lemma with the reachability invariant (Skeleton2.potential_le_length + `Inv`). -/
theorem pot (fires : St → Bool) (hfire : ∀ s, fires s = true → s.x = 31) :
    ∀ (as : List Act) (s : St), Inv s → everGoal (step fires false) goal s as = true → Φ s ≤ as.length := by
  intro as
  induction as with
  | nil => intro s _ hw; simp only [everGoal] at hw; simp [hgoal s hw]
  | cons a rest ih =>
    intro s hi hw
    simp only [everGoal, Bool.or_eq_true] at hw
    rcases hw with hg | hr
    · simp [hgoal s hg]
    · split at hr
      · next s' hok =>
        have h1 := ih s' (inv_step fires s s' a hi hok) hr
        have h2 := hstep fires hfire s s' a hi hok
        simp only [List.length_cons]; omega
      · exact absurd hr (by simp)

theorem s0_inv : Inv s0 := by simp [Inv, s0]
theorem s0_phi : Φ s0 = 22 := by decide

/-- **MAIN**: in the L4 model, under H1' (`hfire`) and H2 (`grow = false`, built into `step _ false`),
    no action sequence of length ≤ 21 reaches `won` from the level-4 start. -/
theorem L4_no_win_within_21 (fires : St → Bool) (hfire : ∀ s, fires s = true → s.x = 31) :
    ∀ as : List Act, as.length ≤ 21 → everGoal (step fires false) goal s0 as = false := by
  intro as hlen
  cases hq : everGoal (step fires false) goal s0 as
  · rfl
  · have := pot fires hfire as s0 s0_inv hq
    rw [s0_phi] at this; omega

/-! ## Non-vacuity -/

/-- H1' with the fewest assumptions: fires exactly when a 2x2 piece is under the stem. -/
def firesAligned (s : St) : Bool := s.small && s.x == 31

theorem firesAligned_ok : ∀ s, firesAligned s = true → s.x = 31 := by
  intro s h; simp [firesAligned] at h; exact h.2

/-- Bound is tight: 22 actions win (left; PLUS×4; left; LINE×3; right×13). -/
def win22 : List Act :=
  [.left, .click false false, .click false true, .click false true, .click false false, .left,
   .click false false, .click true false, .click false false] ++ List.replicate 13 .right

theorem win22_len : win22.length = 22 := by decide
theorem win22_wins : everGoal (step firesAligned false) goal s0 win22 = true := by decide

/-- Relaxing H1' (door opens on any LINE commit): 8 actions win (LINE×3; right×5). -/
def win8 : List Act := [.click false false, .click true false, .click false false] ++ List.replicate 5 .right
theorem win8_wins : everGoal (step (fun _ => true) false) goal s0 win8 = true := by decide

/-! ## Attempt 2: the shot route (winnable under H_shot) -/

/-- State just before the third LINE click on the shot route: 4x4 at top 29, left 41, facing right. -/
def sShot : St := { small := false, opened := false, won := false, x := 41, dP := 4, dL := 1, y := 29, face := .R }

/-- down; right; LINE×3 (fires a shot right along rows 29-32 into the d door); right×4 (45,49,53,touch). -/
def win9 : List Act := [.down, .right, .click false false, .click true false, .click false false,
  .right, .right, .right, .right]

theorem win9_len : win9.length = 9 := by decide

/-- **MAIN (attempt 2)**: for EVERY 6-effect condition `fires` under which the shot fired from `sShot`
    opens the door (hypothesis H_shot), the 9-action sequence `win9` wins level 4 in the model. -/
theorem L4_win9 (fires : St → Bool) (hshot : fires sShot = true) :
    everGoal (step fires false) goal s0 win9 = true := by
  have e : fires ⟨false, false, false, 41, 4, 1, 29, Dir.R⟩ = true := hshot
  simp [win9, everGoal, step, rDown, rRight, rClick, size, s0, goal, e]

/-- Non-vacuity of H_shot: if the shot never opens the door, the same 9 actions do not win. -/
theorem win9_needs_shot : everGoal (step (fun _ => false) false) goal s0 win9 = false := by decide

/-- H_shot is consistent with every observed failed L4 commit (attempt 1: facing up at top 21 left 29;
    attempt 2: facing right at top 21 left 29): those states differ from `sShot`. -/
theorem failed_commits_not_sShot :
    ({ sShot with x := 29, y := 21, face := .U, dP := 4, dL := 1 } : St) ≠ sShot ∧
    ({ sShot with x := 29, y := 21, dP := 4, dL := 1 } : St) ≠ sShot := by decide

/-! ## Attempt 3: H_shot refuted; the shot mechanism as the 6-effect condition -/

/-- Observed shot mechanism (attempts 2-3): a LINE commit fires a shot from the piece front in the facing
    direction; it stops at wall cells, passes over d and e without changing them; d opens only when the
    shot hits the 6-box, which is reachable only straight up the stem (cols 31-32), and an upward shot is
    stopped when its LEFT column meets wall (L3 success: left col in stem; L4 failures: left col 29 = wall).
    Hence: the door opens iff the piece faces up with left column 31. (Hypothesis H1''.) -/
def firesShot (s : St) : Bool := s.x == 31 && s.face == .U

theorem firesShot_hfire : ∀ s, firesShot s = true → s.x = 31 := by
  intro s h; simp [firesShot] at h; exact h.1

/-- H1'' agrees with all five observed L4 commits that did NOT open the door. -/
theorem firesShot_matches_failures :
    firesShot { sShot with x := 29, y := 21, face := .U } = false ∧      -- attempt 1 (twice)
    firesShot { sShot with x := 29, y := 21, face := .R } = false ∧      -- attempt 2
    firesShot sShot = false ∧                                            -- attempt 3, shot into the door
    firesShot { sShot with x := 37, y := 33, face := .L } = false := by   -- attempt 3, shot over e
  decide

/-- **MAIN (attempt 3)**: with the observed shot mechanism, no sequence of ≤ 21 actions wins level 4. -/
theorem L4_shot_no_win_within_21 :
    ∀ as : List Act, as.length ≤ 21 → everGoal (step firesShot false) goal s0 as = false :=
  L4_no_win_within_21 firesShot firesShot_hfire

/-- Non-vacuity / tightness: 23 actions win (left; PLUS×4; left; up; LINE×3; right×13). -/
def win23 : List Act :=
  [.left, .click false false, .click false true, .click false true, .click false false, .left, .up,
   .click false false, .click true false, .click false false] ++ List.replicate 13 .right
theorem win23_len : win23.length = 23 := by decide
theorem win23_wins : everGoal (step firesShot false) goal s0 win23 = true := by decide

#print axioms L4_shot_no_win_within_21
#print axioms firesShot_matches_failures
#print axioms win23_wins
#print axioms L4_win9
#print axioms win9_needs_shot
#print axioms failed_commits_not_sShot
#print axioms inv_step
#print axioms hstep
#print axioms pot
#print axioms L4_no_win_within_21
#print axioms win22_wins
#print axioms win8_wins

end L4
