/-
# L5GridStructure — universal property of the established grow placement (attempt 3)

T5 specialisation: `growEst` (grow_place) is the copairing, over the coproduct of states split by
facing (up | down | left | other = right), of the four placement rules `step · 6`, `step · 7`,
`step · 5`, `step · 8` of the permissive grid model.
-/
import Limits.Basic
import L5Grid

open AWM L5G

inductive FacingIx | up | down | left | other

def facingType : FacingIx → Type
  | .up => {s : S // s.fc = 0}
  | .down => {s : S // s.fc = 1}
  | .left => {s : S // s.fc = 2}
  | .other => {s : S // s.fc ≠ 0 ∧ s.fc ≠ 1 ∧ s.fc ≠ 2}

def facingDiagram : Diagram := discrete FacingIx facingType

def facingCocone : Cocone facingDiagram where
  pt := S
  ι
    | .up => fun x => x.val
    | .down => fun x => x.val
    | .left => fun x => x.val
    | .other => fun x => x.val
  w f := nomatch f

def facingDesc (c : Cocone facingDiagram) (x : S) : c.pt :=
  if h0 : x.fc = 0 then c.ι .up ⟨x, h0⟩
  else if h1 : x.fc = 1 then c.ι .down ⟨x, h1⟩
  else if h2 : x.fc = 2 then c.ι .left ⟨x, h2⟩
  else c.ι .other ⟨x, h0, h1, h2⟩

def facingIsColimit : IsColimit facingCocone where
  desc := facingDesc
  fac c j x := by
    cases j
    · have h : x.val.fc = 0 := x.property
      show facingDesc c x.val = _
      simp only [facingDesc, h, dite_true]
      cases x; rfl
    · have h : x.val.fc = 1 := x.property
      show facingDesc c x.val = _
      simp only [facingDesc, h]; rfl
    · have h : x.val.fc = 2 := x.property
      show facingDesc c x.val = _
      simp only [facingDesc, h]; rfl
    · obtain ⟨h0, h1, h2⟩ := x.property
      show facingDesc c x.val = _
      simp only [facingDesc, h0, h1, h2, dite_false]
      cases x; rfl
  uniq c m h y := by
    show m y = facingDesc c y
    unfold facingDesc
    by_cases h0 : y.fc = 0
    · rw [dif_pos h0]; exact h .up ⟨y, h0⟩
    · rw [dif_neg h0]
      by_cases h1 : y.fc = 1
      · rw [dif_pos h1]; exact h .down ⟨y, h1⟩
      · rw [dif_neg h1]
        by_cases h2 : y.fc = 2
        · rw [dif_pos h2]; exact h .left ⟨y, h2⟩
        · rw [dif_neg h2]; exact h .other ⟨y, h0, h1, h2⟩

/-- the four placement rules of the permissive model, one per facing class -/
def growBranches : Cocone facingDiagram where
  pt := S × Int
  ι
    | .up => fun x => step x.val 6
    | .down => fun x => step x.val 7
    | .left => fun x => step x.val 5
    | .other => fun x => step x.val 8
  w f := nomatch f

theorem growEst_is_desc : growEst = facingIsColimit.desc growBranches := by
  funext s
  show step s (growIdx s.fc) = facingDesc growBranches s
  unfold facingDesc growIdx
  by_cases h0 : s.fc = 0
  · simp [h0, growBranches]
  · by_cases h1 : s.fc = 1
    · simp [h1, growBranches]
    · by_cases h2 : s.fc = 2
      · simp [h2, growBranches]
      · simp [h0, h1, h2, growBranches]

/-- non-vacuity: the facing branches really differ on the same small agent -/
theorem grow_branches_differ :
    (step ⟨8, 23, false, true, false, true, true, 0⟩ 6).1 ≠ (step ⟨8, 23, false, true, false, true, true, 0⟩ 8).1 := by
  decide

#print axioms facingIsColimit
#print axioms growEst_is_desc
#print axioms grow_branches_differ
