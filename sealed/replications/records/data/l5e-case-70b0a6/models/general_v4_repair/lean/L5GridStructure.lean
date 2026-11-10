/-
# L5GridStructure — universal property of the established grow placement

Attempt 3 presented the (then) facing-based placement `growEst` as a copairing over facing classes
(`facingIsColimit`). Attempt 9 retired that rule (facing down observed (-2,-2), not the rotated guess;
facing left observed (-2,0)) and replaced it with `growFit`: the first fitting placement.

T6 specialisation (attempt 9): `growFit` is the copairing, over the coproduct of states split by which
placement fits first ({8 fits} ⊔ {8 no, 6 fits} ⊔ {8,6 no, 7 fits} ⊔ {none of 8,6,7}), of the four
placement rules `step · 8`, `step · 6`, `step · 7`, `step · 5` of the permissive grid model.
-/
import Limits.Basic
import L5Grid

open AWM L5G

def p8 (s : S) : Prop := (step s 8).1.big = true ∧ s.big = false
def p6 (s : S) : Prop := (step s 6).1.big = true ∧ s.big = false
def p7 (s : S) : Prop := (step s 7).1.big = true ∧ s.big = false

inductive FitIx | c8 | c6 | c7 | rest

def fitType : FitIx → Type
  | .c8 => {s : S // p8 s}
  | .c6 => {s : S // ¬ p8 s ∧ p6 s}
  | .c7 => {s : S // ¬ p8 s ∧ ¬ p6 s ∧ p7 s}
  | .rest => {s : S // ¬ p8 s ∧ ¬ p6 s ∧ ¬ p7 s}

def fitDiagram : Diagram := discrete FitIx fitType

def fitCocone : Cocone fitDiagram where
  pt := S
  ι
    | .c8 => fun x => x.val
    | .c6 => fun x => x.val
    | .c7 => fun x => x.val
    | .rest => fun x => x.val
  w f := nomatch f

instance (s : S) : Decidable (p8 s) := by unfold p8; infer_instance
instance (s : S) : Decidable (p6 s) := by unfold p6; infer_instance
instance (s : S) : Decidable (p7 s) := by unfold p7; infer_instance

def fitDesc (c : Cocone fitDiagram) (x : S) : c.pt :=
  if h8 : p8 x then c.ι .c8 ⟨x, h8⟩
  else if h6 : p6 x then c.ι .c6 ⟨x, h8, h6⟩
  else if h7 : p7 x then c.ι .c7 ⟨x, h8, h6, h7⟩
  else c.ι .rest ⟨x, h8, h6, h7⟩

def fitIsColimit : IsColimit fitCocone where
  desc := fitDesc
  fac c j x := by
    cases j
    · show fitDesc c x.val = _
      unfold fitDesc
      rw [dif_pos x.property]
      cases x; rfl
    · show fitDesc c x.val = _
      unfold fitDesc
      rw [dif_neg x.property.1, dif_pos x.property.2]
      cases x; rfl
    · show fitDesc c x.val = _
      unfold fitDesc
      rw [dif_neg x.property.1, dif_neg x.property.2.1, dif_pos x.property.2.2]
      cases x; rfl
    · show fitDesc c x.val = _
      unfold fitDesc
      rw [dif_neg x.property.1, dif_neg x.property.2.1, dif_neg x.property.2.2]
      cases x; rfl
  uniq c m h y := by
    show m y = fitDesc c y
    unfold fitDesc
    by_cases h8 : p8 y
    · rw [dif_pos h8]; exact h .c8 ⟨y, h8⟩
    · rw [dif_neg h8]
      by_cases h6 : p6 y
      · rw [dif_pos h6]; exact h .c6 ⟨y, h8, h6⟩
      · rw [dif_neg h6]
        by_cases h7 : p7 y
        · rw [dif_pos h7]; exact h .c7 ⟨y, h8, h6, h7⟩
        · rw [dif_neg h7]; exact h .rest ⟨y, h8, h6, h7⟩

/-- the four placement rules of the permissive model, one per fit class -/
def growBranches : Cocone fitDiagram where
  pt := S × Int
  ι
    | .c8 => fun x => step x.val 8
    | .c6 => fun x => step x.val 6
    | .c7 => fun x => step x.val 7
    | .rest => fun x => step x.val 5
  w f := nomatch f

theorem growFit_is_desc : growFit = fitIsColimit.desc growBranches := by
  funext s
  show growFit s = fitDesc growBranches s
  unfold fitDesc growFit
  by_cases h8 : p8 s
  · have h8' : (step s 8).1.big = true ∧ s.big = false := h8
    rw [dif_pos h8, if_pos h8']; rfl
  · have h8' : ¬ ((step s 8).1.big = true ∧ s.big = false) := h8
    rw [dif_neg h8, if_neg h8']
    by_cases h6 : p6 s
    · have h6' : (step s 6).1.big = true ∧ s.big = false := h6
      rw [dif_pos h6, if_pos h6']; rfl
    · have h6' : ¬ ((step s 6).1.big = true ∧ s.big = false) := h6
      rw [dif_neg h6, if_neg h6']
      by_cases h7 : p7 s
      · have h7' : (step s 7).1.big = true ∧ s.big = false := h7
        rw [dif_pos h7, if_pos h7']; rfl
      · have h7' : ¬ ((step s 7).1.big = true ∧ s.big = false) := h7
        rw [dif_neg h7, if_neg h7']; rfl

/-- non-vacuity: two fit classes give different placements for the same small agent
    (pixel (37,15): class c8 lands at (35,13); placement 7 would land at (35,15)) -/
theorem grow_branches_differ :
    (step ⟨18, 7, false, false, false, false, true, 1⟩ 8).1 ≠ (step ⟨18, 7, false, false, false, false, true, 1⟩ 7).1 := by
  decide

#print axioms fitIsColimit
#print axioms growFit_is_desc
#print axioms grow_branches_differ
