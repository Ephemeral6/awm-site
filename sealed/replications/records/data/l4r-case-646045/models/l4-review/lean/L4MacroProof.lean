import Game.Chk.C19_0
import Game.Chk.C19_1
import Game.Chk.C21_0
import Game.Chk.C21_1
import Game.Chk.C23_0
import Game.Chk.C23_1
import Game.Chk.C25_0
import Game.Chk.C25_1
import Game.Chk.C25_2
import Game.Chk.C27_0
import Game.Chk.C27_1
import Game.Chk.C27_2
import Game.Chk.C29_0
import Game.Chk.C29_1
import Game.Chk.C29_2
import Game.Chk.C29_3
import Game.Chk.C30_0
import Game.Chk.C31_0
import Game.Chk.C31_1
import Game.Chk.C31_2
import Game.Chk.C32_0
import Game.Chk.C33_0
import Game.Chk.C33_1
import Game.Chk.C33_2
import Game.Chk.C35_0
import Game.Chk.C35_1
import Game.Chk.C35_2
import Game.Chk.C37_0
import Game.Chk.C37_1
import Game.Chk.C37_2
import Game.Chk.C39_0
import Game.Chk.C39_1
import Game.Chk.C41_0
import Game.Chk.C41_1
import Game.Chk.C43_0
import Game.Chk.C45_0
import Game.Chk.C47_0
/-!
# Level 4 is impossible within the budget (attempt 4), on the macro model `Game/L4Macro.lean`.

Budget premise (measured on L4 in all four attempts): every action costs at least 7 of the bar's
128 units and an action only executes while fewer than 128 units are spent, so at most 19 actions
execute (7*18 = 126 < 128 <= 7*19 = 133).  `totalCost` counts actions (plus = 4 clicks, line = 3).
The certificate `bucket` (generated in Python) is re-checked chunk by chunk in `Game/Chk/*.lean`.
-/
namespace L4M

theorem all_of_chunks {α : Type} (l : List α) (f : α → Bool)
    (h0 : (l.take 60).all f = true) (h1 : ((l.drop 60).take 60).all f = true)
    (h2 : ((l.drop 120).take 60).all f = true) (h3 : (l.drop 180).all f = true) : l.all f = true := by
  rw [← List.take_append_drop 60 l, List.all_append, h0, Bool.true_and,
      ← List.take_append_drop 60 (l.drop 60), List.all_append, h1, Bool.true_and, List.drop_drop,
      ← List.take_append_drop 60 (l.drop (60 + 60)), List.all_append, Bool.and_eq_true]
  refine ⟨h2, ?_⟩
  rw [List.drop_drop]; exact h3

theorem bucket_ok : ∀ x, x < 64 → (bucket x).all okEntry = true := by
  intro x _
  by_cases hx : x ∈ cols
  · simp only [cols, List.mem_cons, List.mem_nil_iff, or_false] at hx
    rcases hx with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    · exact all_of_chunks _ _ chk_19_0 chk_19_1 (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_21_0 chk_21_1 (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_23_0 chk_23_1 (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_25_0 chk_25_1 chk_25_2 (by decide +kernel)
    · exact all_of_chunks _ _ chk_27_0 chk_27_1 chk_27_2 (by decide +kernel)
    · exact all_of_chunks _ _ chk_29_0 chk_29_1 chk_29_2 chk_29_3
    · exact all_of_chunks _ _ chk_30_0 (by decide +kernel) (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_31_0 chk_31_1 chk_31_2 (by decide +kernel)
    · exact all_of_chunks _ _ chk_32_0 (by decide +kernel) (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_33_0 chk_33_1 chk_33_2 (by decide +kernel)
    · exact all_of_chunks _ _ chk_35_0 chk_35_1 chk_35_2 (by decide +kernel)
    · exact all_of_chunks _ _ chk_37_0 chk_37_1 chk_37_2 (by decide +kernel)
    · exact all_of_chunks _ _ chk_39_0 chk_39_1 (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_41_0 chk_41_1 (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_43_0 (by decide +kernel) (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_45_0 (by decide +kernel) (by decide +kernel) (by decide +kernel)
    · exact all_of_chunks _ _ chk_47_0 (by decide +kernel) (by decide +kernel) (by decide +kernel)
  · have : bucket x = [] := by
      unfold bucket; split <;> simp_all [cols]
    rw [this]; rfl

theorem lookup_ok {s : MSt} {d : Nat} (h : lookup s = some d) : okEntry (s, d) = true := by
  unfold lookup at h
  split at h
  · next hx =>
    cases hf : (bucket s.x).find? (fun p => p.1 == s) with
    | none => simp [hf] at h
    | some p =>
      simp only [hf, Option.map_some, Option.some.injEq] at h
      have hm := List.mem_of_find?_eq_some hf
      have he := List.find?_some hf
      simp only [beq_iff_eq] at he
      have hb := bucket_ok s.x hx
      simp only [List.all_eq_true] at hb
      have := hb p hm
      rw [← he, ← h]; exact this
  · simp at h

theorem act_mem (a : MAct) : a ∈ acts := by cases a <;> simp [acts]

theorem safe : ∀ (as : List MAct) (st : MSt) (d spent : Nat),
    lookup st = some d → d ≤ spent → spent + totalCost as ≤ 19 → wins st as = false := by
  intro as
  induction as with
  | nil => intro _ _ _ _ _ _; rfl
  | cons a r ih =>
    intro st d spent hl hd hb
    have hok := lookup_ok hl
    simp only [okEntry, List.all_eq_true] at hok
    have h1 := hok a (act_mem a)
    simp only [totalCost] at hb
    have hnot : ¬ (19 < d + cost a) := by omega
    simp only [Bool.or_eq_true, decide_eq_true_eq, hnot, false_or] at h1
    simp only [wins]
    split at h1
    · exact absurd h1 (by simp)
    · next s' hs =>
      rw [hs]
      split at h1
      · next d' hl' =>
        simp only [decide_eq_true_eq] at h1
        exact ih s' d' (spent + cost a) hl' (by omega) (by omega)
      · exact absurd h1 (by simp)

theorem s0_lookup : lookup s0 = some 0 := by decide +kernel

/-- **MAIN (attempt 4)**: in the macro model, no play of at most 19 actions wins level 4. -/
theorem L4_macro_no_win_within_19 :
    ∀ as : List MAct, totalCost as ≤ 19 → wins s0 as = false :=
  fun as h => safe as s0 0 0 s0_lookup (Nat.le_refl 0) (by omega)

/-- Non-vacuity: the 21-action plan found by search wins (L; shrink; U; grow -> 4x4 at x31; LINE opens
    the door; R R D D R R R R-touch).  So the model can be won, and the budget is what forbids it. -/
def win21 : List MAct := [.left, .plus, .up, .plus, .line, .right, .right, .down, .down,
  .right, .right, .right, .right]
theorem win21_cost : totalCost win21 = 21 := by decide
theorem win21_wins : wins s0 win21 = true := by decide +kernel

/-- Non-vacuity of H1'' (the premise is a real constraint): if the shot opened the door from the start
    position, `line` then 6 moves would win in 9 actions. -/
def s0open : MSt := { s0 with opened := true }
theorem open_door_short : wins s0open [.down, .right, .right, .right, .right, .right] = true := by decide +kernel

/-- Replay of observed L4 play (attempt 4): left, shrink, left, up, LINE (door opened), grow.
    Observed frames: 4x4 (25,33); 2x2 (25,33); 2x2 (25,31); 2x2 (23,31) facing up; door open; 4x4 (21,29). -/
def run : MSt → List MAct → List (Option MSt)
  | _, [] => []
  | st, a :: r => match stepM st a with
    | none => [none]
    | some s' => some s' :: run s' r
theorem replay_attempt4 : run s0 [.left, .plus, .left, .up, .line, .plus] =
    [some ⟨false, false, 25, 33, 2⟩, some ⟨true, false, 25, 33, 2⟩, some ⟨true, false, 25, 31, 2⟩,
     some ⟨true, false, 23, 31, 0⟩, some ⟨true, true, 23, 31, 0⟩, some ⟨false, true, 21, 29, 0⟩] := by decide

/-- Replay of attempt 3: down, right, LINE (door stayed shut), down, left, LINE (no effect), shrink.
    Observed: 4x4 (29,37); (29,41) facing R; shut; (33,41); (33,37) facing L; shut; 2x2 (33,37). -/
theorem replay_attempt3 : run s0 [.down, .right, .line, .down, .left, .line, .plus] =
    [some ⟨false, false, 29, 37, 1⟩, some ⟨false, false, 29, 41, 3⟩, some ⟨false, false, 29, 41, 3⟩,
     some ⟨false, false, 33, 41, 1⟩, some ⟨false, false, 33, 37, 2⟩, some ⟨false, false, 33, 37, 2⟩,
     some ⟨true, false, 33, 37, 2⟩] := by decide

/-- Replay of attempt 5: D, L, shrink, D, L, U, LINE (door opened), R, LINE (shot ran down the corridor,
    no level change).  Observed: 4x4 (29,37) (29,33); 2x2 (29,33) (31,33) (31,31) (29,31)U; door open;
    (29,33)R; no win. -/
theorem replay_attempt5 : run s0 [.down, .left, .plus, .down, .left, .up, .line, .right, .line] =
    [some ⟨false, false, 29, 37, 1⟩, some ⟨false, false, 29, 33, 2⟩, some ⟨true, false, 29, 33, 2⟩,
     some ⟨true, false, 31, 33, 1⟩, some ⟨true, false, 31, 31, 2⟩, some ⟨true, false, 29, 31, 0⟩,
     some ⟨true, true, 29, 31, 0⟩, some ⟨true, true, 29, 33, 3⟩, some ⟨true, true, 29, 33, 3⟩] := by decide

#print axioms replay_attempt5
#print axioms replay_attempt4
#print axioms replay_attempt3
#print axioms L4_macro_no_win_within_19
#print axioms win21_wins
#print axioms open_door_short
end L4M
