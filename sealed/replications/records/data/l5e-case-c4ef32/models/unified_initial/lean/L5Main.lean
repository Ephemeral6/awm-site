import L5Rows0
import L5Rows1
import L5Rows2
import L5Rows3
/-!
# L5Main — level 5 is not winnable within budget under `L5Model`

MAIN-THEOREM: `L5.L5_unwinnable`
  ∀ action lists `as` (macro actions, any length) that end in a win from `start`
  (the run stops at its first win), the run is not affordable:
  prefixCost + 10·[refill unused before the last action] ≥ 46 > 45.
Hypotheses: none beyond the definitions in L5Model (whose ASSUMPTION / SUPERSET notes list
what is established and what is not).
-/
namespace L5

theorem parts_ok (r : Fin 32) : part r 0 = true ∧ part r 1 = true ∧ part r 2 = true ∧ part r 3 = true := by
  match r with
  | ⟨0, _⟩ => exact ⟨part_0_0, part_0_1, part_0_2, part_0_3⟩
  | ⟨1, _⟩ => exact ⟨part_1_0, part_1_1, part_1_2, part_1_3⟩
  | ⟨2, _⟩ => exact ⟨part_2_0, part_2_1, part_2_2, part_2_3⟩
  | ⟨3, _⟩ => exact ⟨part_3_0, part_3_1, part_3_2, part_3_3⟩
  | ⟨4, _⟩ => exact ⟨part_4_0, part_4_1, part_4_2, part_4_3⟩
  | ⟨5, _⟩ => exact ⟨part_5_0, part_5_1, part_5_2, part_5_3⟩
  | ⟨6, _⟩ => exact ⟨part_6_0, part_6_1, part_6_2, part_6_3⟩
  | ⟨7, _⟩ => exact ⟨part_7_0, part_7_1, part_7_2, part_7_3⟩
  | ⟨8, _⟩ => exact ⟨part_8_0, part_8_1, part_8_2, part_8_3⟩
  | ⟨9, _⟩ => exact ⟨part_9_0, part_9_1, part_9_2, part_9_3⟩
  | ⟨10, _⟩ => exact ⟨part_10_0, part_10_1, part_10_2, part_10_3⟩
  | ⟨11, _⟩ => exact ⟨part_11_0, part_11_1, part_11_2, part_11_3⟩
  | ⟨12, _⟩ => exact ⟨part_12_0, part_12_1, part_12_2, part_12_3⟩
  | ⟨13, _⟩ => exact ⟨part_13_0, part_13_1, part_13_2, part_13_3⟩
  | ⟨14, _⟩ => exact ⟨part_14_0, part_14_1, part_14_2, part_14_3⟩
  | ⟨15, _⟩ => exact ⟨part_15_0, part_15_1, part_15_2, part_15_3⟩
  | ⟨16, _⟩ => exact ⟨part_16_0, part_16_1, part_16_2, part_16_3⟩
  | ⟨17, _⟩ => exact ⟨part_17_0, part_17_1, part_17_2, part_17_3⟩
  | ⟨18, _⟩ => exact ⟨part_18_0, part_18_1, part_18_2, part_18_3⟩
  | ⟨19, _⟩ => exact ⟨part_19_0, part_19_1, part_19_2, part_19_3⟩
  | ⟨20, _⟩ => exact ⟨part_20_0, part_20_1, part_20_2, part_20_3⟩
  | ⟨21, _⟩ => exact ⟨part_21_0, part_21_1, part_21_2, part_21_3⟩
  | ⟨22, _⟩ => exact ⟨part_22_0, part_22_1, part_22_2, part_22_3⟩
  | ⟨23, _⟩ => exact ⟨part_23_0, part_23_1, part_23_2, part_23_3⟩
  | ⟨24, _⟩ => exact ⟨part_24_0, part_24_1, part_24_2, part_24_3⟩
  | ⟨25, _⟩ => exact ⟨part_25_0, part_25_1, part_25_2, part_25_3⟩
  | ⟨26, _⟩ => exact ⟨part_26_0, part_26_1, part_26_2, part_26_3⟩
  | ⟨27, _⟩ => exact ⟨part_27_0, part_27_1, part_27_2, part_27_3⟩
  | ⟨28, _⟩ => exact ⟨part_28_0, part_28_1, part_28_2, part_28_3⟩
  | ⟨29, _⟩ => exact ⟨part_29_0, part_29_1, part_29_2, part_29_3⟩
  | ⟨30, _⟩ => exact ⟨part_30_0, part_30_1, part_30_2, part_30_3⟩
  | ⟨31, _⟩ => exact ⟨part_31_0, part_31_1, part_31_2, part_31_3⟩
  | ⟨n + 32, h⟩ => exact absurd h (by omega)

theorem stCheck_all (s : St) : stCheck s = true := by
  obtain ⟨h0, h1, h2, h3⟩ := parts_ok s.r
  exact stCheck_of_col (colCheck_of_parts h0 h1 h2 h3 s.c)

theorem okAct_of_inR {s : St} (hs : inR s = true) (a : Act) : okAct s a = true := by
  have hc := stCheck_all s
  simp only [stCheck, hs, Bool.not_true, Bool.false_or, List.all_eq_true] at hc
  exact hc a (mem_allActs a)

/-- potential argument: along any run that ends in its first win, H bounds the spend -/
theorem bound : ∀ (as : List Act) (s : St), inR s = true → endsInWin s as →
    H s ≤ prefixCost s as + 10 * b2n (lastEp s as) := by
  intro as
  induction as with
  | nil => intro s _ h; exact absurd h (by simp [endsInWin])
  | cons a rest ih =>
    intro s hs h
    have hok := okAct_of_inR hs a
    cases rest with
    | nil =>
      simp only [endsInWin] at h
      simp only [okAct, h, ite_true, decide_eq_true_eq] at hok
      simp only [prefixCost, lastEp]
      omega
    | cons b rest' =>
      simp only [endsInWin] at h
      obtain ⟨hnw, hrest⟩ := h
      simp only [okAct, hnw, Bool.false_eq_true, ite_false, Bool.and_eq_true, decide_eq_true_eq] at hok
      obtain ⟨hin, hle⟩ := hok
      have := ih (step s a) hin hrest
      simp only [prefixCost, lastEp]
      omega

theorem start_inR : inR start = true := by decide +kernel
theorem start_H : H start = 46 := by decide +kernel

/-- **MAIN-THEOREM**: no run from the level-5 start that ends in a win is affordable. -/
theorem L5_unwinnable (as : List Act) (hw : endsInWin start as) : ¬ affordable start as := by
  intro ha
  have hb := bound as start start_inR hw
  rw [start_H] at hb
  unfold affordable at ha
  cases hl : lastEp start as <;> simp only [b2n, hl, ite_true, ite_false, Bool.false_eq_true] at hb ha <;> omega

/-! ## non-vacuity: relaxing the net budget by one unit (35 → 36) makes the level winnable -/

def endsInWinB : St → List Act → Bool
  | _, [] => false
  | s, [a] => win (step s a)
  | s, a :: b :: rest => !win (step s a) && endsInWinB (step s a) (b :: rest)

theorem endsInWin_of_B : ∀ (as : List Act) (s : St), endsInWinB s as = true → endsInWin s as := by
  intro as
  induction as with
  | nil => intro s h; simp [endsInWinB] at h
  | cons a rest ih =>
    intro s h
    cases rest with
    | nil => simpa [endsInWinB, endsInWin] using h
    | cons b rest' =>
      simp only [endsInWinB, Bool.and_eq_true, Bool.not_eq_true'] at h
      exact ⟨h.1, ih _ h.2⟩

/-- the cheapest winning run found by the search (30 macro actions) -/
def witness : List Act :=
  [.move .R, .move .U, .shot, .move .R, .move .D, .move .D,
   .move .R, .move .R, .move .R, .move .R, .move .R, .move .R, .move .D,
   .move .U, .move .U, .move .U, .move .L, .shrink .tl,
   .move .U, .move .U, .move .U, .move .U, .move .R, .grow .br, .shot, .tele,
   .move .U, .move .U, .move .U, .move .U]

theorem witness_wins : endsInWin start witness := endsInWin_of_B _ _ (by decide +kernel)
theorem witness_spend : prefixCost start witness + 10 * b2n (lastEp start witness) = 46 := by decide +kernel

/-- the bound of the main theorem is attained: with one more unit of net budget the level is won -/
theorem relaxed_by_one : ∃ as, endsInWin start as ∧ prefixCost start as + 10 * b2n (lastEp start as) ≤ 46 :=
  ⟨witness, witness_wins, by rw [witness_spend]; exact Nat.le_refl _⟩

/-- the budget premise is a real constraint: the same run is excluded at the real budget -/
theorem witness_not_affordable : ¬ affordable start witness := L5_unwinnable witness witness_wins


/-! ## reconciliation: the macro sequence actually played on attempt 1 (41 transitions, panel clicks
    folded into their firing click) ends, in the model, exactly where the game ended:
    4×4 block at pixel (35,13), facing left, both barriers open, refill used. -/
def attempt1 : List Act :=
  [.move .R, .move .U, .shot, .move .D, .move .D,
   .move .R, .move .R, .move .R, .move .R, .move .R, .move .R, .move .R, .move .D,
   .move .U, .move .L, .move .U, .move .U, .shrink .tl,
   .move .U, .move .U, .move .U, .move .U, .move .U, .move .R, .shot, .tele, .grow .br,
   .move .R, .move .L]

def runAll : St → List Act → St
  | s, [] => s
  | s, a :: as => runAll (step s a) as

theorem attempt1_end : runAll start attempt1 =
    { r := half 35, c := half 13, big := true, f := .L, oc := true, od := true, ep := false } := by decide +kernel

theorem attempt1_tele_to_fpad : runAll start (attempt1.take 26) =
    { r := half 37, c := half 15, big := false, f := .R, oc := true, od := true, ep := false } := by decide +kernel

/-- attempt 5 reconciliation: a 4×4 at pixel (17,33) pressing up against the closed d barrier makes a
    2-pixel partial step to (15,33) and turns up (R1 as revised). -/
theorem attempt5_partial_move :
    step { r := half 17, c := half 33, big := true, f := .D, oc := false, od := false, ep := true } (.move .U) =
      { r := half 15, c := half 33, big := true, f := .U, oc := false, od := false, ep := true } := by decide

/-- attempt 5 reconciliation: a 2×2 at (15,33) pressing up has no partial step; it only turns. -/
theorem attempt5_small_blocked :
    step { r := half 15, c := half 33, big := false, f := .D, oc := false, od := false, ep := true } (.move .U) =
      { r := half 15, c := half 33, big := false, f := .U, oc := false, od := false, ep := true } := by decide

end L5

#print axioms L5.L5_unwinnable
#print axioms L5.relaxed_by_one
#print axioms L5.witness_not_affordable
#print axioms L5.attempt1_end
#print axioms L5.attempt1_tele_to_fpad
#print axioms L5.attempt5_partial_move
#print axioms L5.attempt5_small_blocked
