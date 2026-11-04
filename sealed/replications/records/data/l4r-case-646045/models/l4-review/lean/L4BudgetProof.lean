import Game.BChk.B17_0
import Game.BChk.B19_0
import Game.BChk.B19_1
import Game.BChk.B21_0
import Game.BChk.B21_1
import Game.BChk.B21_2
import Game.BChk.B23_0
import Game.BChk.B23_1
import Game.BChk.B23_2
import Game.BChk.B23_3
import Game.BChk.B25_0
import Game.BChk.B25_1
import Game.BChk.B25_2
import Game.BChk.B25_3
import Game.BChk.B27_0
import Game.BChk.B27_1
import Game.BChk.B27_2
import Game.BChk.B27_3
import Game.BChk.B29_0
import Game.BChk.B29_1
import Game.BChk.B29_2
import Game.BChk.B29_3
import Game.BChk.B29_4
import Game.BChk.B31_0
import Game.BChk.B31_1
import Game.BChk.B31_2
import Game.BChk.B31_3
import Game.BChk.B31_4
import Game.BChk.B31_5
import Game.BChk.B33_0
import Game.BChk.B33_1
import Game.BChk.B33_2
import Game.BChk.B33_3
import Game.BChk.B35_0
import Game.BChk.B35_1
import Game.BChk.B35_2
import Game.BChk.B35_3
import Game.BChk.B37_0
import Game.BChk.B37_1
import Game.BChk.B37_2
import Game.BChk.B37_3
import Game.BChk.B39_0
import Game.BChk.B39_1
import Game.BChk.B39_2
import Game.BChk.B39_3
import Game.BChk.B41_0
import Game.BChk.B41_1
import Game.BChk.B41_2
import Game.BChk.B43_0
import Game.BChk.B43_1
import Game.BChk.B45_0
import Game.BChk.B47_0
import Game.BChk.B49_0
import Game.BChk.B51_0
/-!
# Level 4 is impossible within the exact budget (attempt 6), on the budget model `Game/L4Budget.lean`.

Quantifies over ALL action lists (no length bound): the budget is inside the model (`winsB`).
Pickup rule is looser than established (front-half overlap H_front included); the certificate covers it.
-/
namespace L4M

theorem act_memB (a : MAct) : a ∈ acts := by cases a <;> simp [acts]

theorem all_of_k_chunks {α : Type} (f : α → Bool) : ∀ (k : Nat) (l : List α),
    (∀ i, i < k → ((l.drop (60 * i)).take 60).all f = true) → (l.drop (60 * k)).all f = true →
    l.all f = true := by
  intro k
  induction k with
  | zero => intro l _ h; simpa using h
  | succ k ih =>
    intro l hc ht
    rw [← List.take_append_drop 60 l, List.all_append, Bool.and_eq_true]
    refine ⟨by simpa using hc 0 (by omega), ?_⟩
    apply ih (l.drop 60)
    · intro i hi
      have := hc (i + 1) (by omega)
      rw [List.drop_drop]
      rw [show 60 + 60 * i = 60 * (i + 1) by omega]
      exact this
    · rw [List.drop_drop, show 60 + 60 * k = 60 * (k + 1) by omega]; exact ht

theorem bbucket_ok : ∀ x, x < 64 → (bbucket x).all okB = true := by
  intro x _
  by_cases hx : x ∈ bcols
  · simp only [bcols, List.mem_cons, List.mem_nil_iff, or_false] at hx
    rcases hx with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    · exact all_of_k_chunks okB 1 (bbucket 17) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_17_0
        | _ + 1, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 2 (bbucket 19) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_19_0
        | 1, _ => exact bchk_19_1
        | _ + 2, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 3 (bbucket 21) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_21_0
        | 1, _ => exact bchk_21_1
        | 2, _ => exact bchk_21_2
        | _ + 3, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 23) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_23_0
        | 1, _ => exact bchk_23_1
        | 2, _ => exact bchk_23_2
        | 3, _ => exact bchk_23_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 25) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_25_0
        | 1, _ => exact bchk_25_1
        | 2, _ => exact bchk_25_2
        | 3, _ => exact bchk_25_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 27) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_27_0
        | 1, _ => exact bchk_27_1
        | 2, _ => exact bchk_27_2
        | 3, _ => exact bchk_27_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 5 (bbucket 29) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_29_0
        | 1, _ => exact bchk_29_1
        | 2, _ => exact bchk_29_2
        | 3, _ => exact bchk_29_3
        | 4, _ => exact bchk_29_4
        | _ + 5, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 6 (bbucket 31) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_31_0
        | 1, _ => exact bchk_31_1
        | 2, _ => exact bchk_31_2
        | 3, _ => exact bchk_31_3
        | 4, _ => exact bchk_31_4
        | 5, _ => exact bchk_31_5
        | _ + 6, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 33) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_33_0
        | 1, _ => exact bchk_33_1
        | 2, _ => exact bchk_33_2
        | 3, _ => exact bchk_33_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 35) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_35_0
        | 1, _ => exact bchk_35_1
        | 2, _ => exact bchk_35_2
        | 3, _ => exact bchk_35_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 37) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_37_0
        | 1, _ => exact bchk_37_1
        | 2, _ => exact bchk_37_2
        | 3, _ => exact bchk_37_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 4 (bbucket 39) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_39_0
        | 1, _ => exact bchk_39_1
        | 2, _ => exact bchk_39_2
        | 3, _ => exact bchk_39_3
        | _ + 4, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 3 (bbucket 41) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_41_0
        | 1, _ => exact bchk_41_1
        | 2, _ => exact bchk_41_2
        | _ + 3, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 2 (bbucket 43) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_43_0
        | 1, _ => exact bchk_43_1
        | _ + 2, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 1 (bbucket 45) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_45_0
        | _ + 1, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 1 (bbucket 47) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_47_0
        | _ + 1, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 1 (bbucket 49) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_49_0
        | _ + 1, h => omega) (by decide +kernel)
    · exact all_of_k_chunks okB 1 (bbucket 51) (fun i hi => by
        match i, hi with
        | 0, _ => exact bchk_51_0
        | _ + 1, h => omega) (by decide +kernel)
  · have : bbucket x = [] := by
      unfold bbucket; split <;> simp_all [bcols]
    rw [this]; rfl

theorem blookup_ok {s : BSt} {d : Nat} (h : blookup s = some d) : okB (s, d) = true := by
  unfold blookup at h
  split at h
  · next hx =>
    cases hf : (bbucket s.1.x).find? (fun p => p.1 == s) with
    | none => simp [hf] at h
    | some p =>
      simp only [hf, Option.map_some, Option.some.injEq] at h
      have hm := List.mem_of_find?_eq_some hf
      have he := List.find?_some hf
      simp only [beq_iff_eq] at he
      have hb := bbucket_ok s.1.x hx
      simp only [List.all_eq_true] at hb
      have := hb p hm
      rw [← he, ← h]; exact this
  · simp at h

theorem safeB : ∀ (as : List MAct) (st : BSt) (d spent : Nat),
    blookup st = some d → d ≤ spent → winsB st as spent = false := by
  intro as
  induction as with
  | nil => intro _ _ _ _ _; rfl
  | cons a r ih =>
    intro st d spent hl hd
    have hok := blookup_ok hl
    simp only [okB, List.all_eq_true] at hok
    have h1 := hok a (act_memB a)
    simp only [winsB]
    split at h1
    · next hs =>
      rw [hs]; simp only [decide_eq_true_eq] at h1; simp only [decide_eq_false_iff_not]; omega
    · next s' hs =>
      rw [hs]; dsimp only
      simp only [Bool.or_eq_true, decide_eq_true_eq] at h1
      by_cases hc : spent + bcost a ≤ cap s'.2
      · rw [ite_eq_left_iff.mpr (fun h => absurd hc h)]
        rcases h1 with h1 | h1
        · omega
        · split at h1
          · next d' hl' =>
            simp only [decide_eq_true_eq] at h1
            exact ih s' d' (spent + bcost a) hl' (by omega)
          · exact absurd h1 (by simp)
      · simp only [hc, ite_false]

theorem b0_lookup : blookup b0 = some 0 := by decide +kernel

/-- **MAIN (attempt 6)**: with the exact budget (18 units, +10 for the e pickup), no action list wins level 4,
    even granting the untested front-half pickup rule H_front. -/
theorem L4_budget_no_win : ∀ as : List MAct, winsB b0 as 0 = false :=
  fun as => safeB as b0 0 0 b0_lookup (Nat.le_refl 0)

/-- Non-vacuity 1: with one extra unit of budget (cap 29 after pickup) the planner's 18-action route wins
    (L L L D, shrink, grow, D [front over e], R R D U, LINE, R x6: cost 29). -/
def winsB' (capE : Nat) : BSt → List MAct → Nat → Bool
  | _, [], _ => false
  | st, a :: r, spent =>
    let cp := fun (e : Bool) => if e then capE else 18
    match stepB st a with
    | none => decide (spent + bcost a ≤ cp st.2)
    | some st' => if spent + bcost a ≤ cp st'.2 then winsB' capE st' r (spent + bcost a) else false
def route29 : List MAct := [.left, .left, .left, .down, .plus, .plus, .down, .right, .right, .down, .up,
  .line, .right, .right, .right, .right, .right, .right]
theorem route29_wins_with_cap29 : winsB' 29 b0 route29 0 = true := by decide +kernel
theorem route29_fails_with_cap28 : winsB' 28 b0 route29 0 = false := by decide +kernel

/-- Non-vacuity 2: the budget model agrees with the attempt-6 observation that the 2x2 piece stepping onto e
    from (33,21) picks it up. -/
theorem pickup_observed : pick ⟨true, false, 33, 23, 3⟩ = true := by decide

/-- Attempt 7 as played: L L L D, shrink, D, grow, D (front-half pickup), R R U, LINE, R x6 (cost 29). -/
def played7 : List MAct := [.left, .left, .left, .down, .plus, .down, .plus, .down, .right, .right, .up,
  .line, .right, .right, .right, .right, .right, .right]

def runB : BSt → List MAct → List (Option BSt)
  | _, [] => []
  | st, a :: r => match stepB st a with
    | none => [none]
    | some s' => some s' :: runB s' r

/-- The model reproduces every observed position of attempt 7, including the front-half pickup (flag true after
    the 8th action) and the door opening, and ends with the goal-touch move (`none`). -/
theorem replay_attempt7 : runB b0 played7 =
  [some (⟨false, false, 25, 33, 2⟩, false), some (⟨false, false, 25, 29, 2⟩, false),
   some (⟨false, false, 25, 25, 2⟩, false), some (⟨false, false, 29, 25, 1⟩, false),
   some (⟨true, false, 29, 25, 1⟩, false), some (⟨true, false, 31, 25, 1⟩, false),
   some (⟨false, false, 29, 23, 1⟩, false), some (⟨false, false, 33, 23, 1⟩, true),
   some (⟨false, false, 33, 27, 3⟩, true), some (⟨false, false, 33, 31, 3⟩, true),
   some (⟨false, false, 29, 31, 0⟩, true), some (⟨false, true, 29, 31, 0⟩, true),
   some (⟨false, true, 29, 35, 3⟩, true), some (⟨false, true, 29, 39, 3⟩, true),
   some (⟨false, true, 29, 43, 3⟩, true), some (⟨false, true, 29, 47, 3⟩, true),
   some (⟨false, true, 29, 51, 3⟩, true), none] := by decide +kernel

/-- ...and, as observed (GAME_OVER, no level change), the budget forbids that last move. -/
theorem played7_loses : winsB b0 played7 0 = false := by decide +kernel

/-- Audit A1: every observed pickup is a `pick` (2x2 at (33,23) facing R; 4x4 at (33,23) facing D), and the
    observed non-pickup at (31,23) facing D IS still a `pick` -- i.e. `pick` is looser than the game there (safe). -/
theorem pickup_A1 : pick ⟨true, false, 33, 23, 3⟩ = true ∧ pick ⟨false, false, 33, 23, 1⟩ = true ∧
    pick ⟨false, false, 31, 23, 1⟩ = true ∧ pick ⟨false, false, 33, 23, 3⟩ = true := by decide

#print axioms pickup_A1
#print axioms replay_attempt7
#print axioms played7_loses
#print axioms L4_budget_no_win
#print axioms route29_wins_with_cap29
#print axioms route29_fails_with_cap28
#print axioms pickup_observed
end L4M
