/-
# L5Structure — universal properties of the L5 model's objects and rules

T1 decomposition : `St` is the limit (product) of its five slots.
T2 generalisation: the three ability rules shrink_f / teleport_b / switch_6 are one rule
                   `completeRule s : Completion → St`, the copairing over the colour-indexed
                   coproduct `Completion` (= 15 ⊔ 11 ⊔ 6×Core).
T3 specialisation: `step s : Act → St` is the copairing of walk / complete / climb over the
                   coproduct `Act`.
-/
import Limits.Basic
import L5Model

open AWM L5

/-! ## T1: St is a product (limit of a discrete diagram) -/

inductive SlotIx | loc | big | cGone | dGone | fFrame

def slotType : SlotIx → Type
  | .loc => Loc
  | .big => Bool
  | .cGone => Bool
  | .dGone => Bool
  | .fFrame => Bool

def stDiagram : Diagram := discrete SlotIx slotType

def stCone : Cone stDiagram where
  pt := St
  π
    | .loc => St.loc
    | .big => St.big
    | .cGone => St.cGone
    | .dGone => St.dGone
    | .fFrame => St.fFrame
  w f := nomatch f

def stIsLimit : IsLimit stCone where
  lift s x := ⟨s.π .loc x, s.π .big x, s.π .cGone x, s.π .dGone x, s.π .fFrame x⟩
  fac s j x := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .loc x; have h2 := h .big x; have h3 := h .cGone x
    have h4 := h .dGone x; have h5 := h .fFrame x
    cases hm : m x with
    | mk l b c d f =>
      simp only [stCone, hm] at h1 h2 h3 h4 h5
      subst h1; subst h2; subst h3; subst h4; subst h5; rfl

#print axioms stIsLimit

/-! ## T2: the ability rules are one rule over the colour coproduct -/

inductive ColourIx | c15 | c11 | c6

def colourType : ColourIx → Type
  | .c15 => Unit
  | .c11 => Unit
  | .c6 => Core

def colourDiagram : Diagram := discrete ColourIx colourType

def completionCocone : Cocone colourDiagram where
  pt := Completion
  ι
    | .c15 => fun _ => .shrink15
    | .c11 => fun _ => .teleport11
    | .c6 => fun k => .switch6 k
  w f := nomatch f

def completionIsColimit : IsColimit completionCocone where
  desc s
    | .shrink15 => s.ι .c15 ()
    | .teleport11 => s.ι .c11 ()
    | .switch6 k => s.ι .c6 k
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | shrink15 => exact h .c15 ()
    | teleport11 => exact h .c11 ()
    | switch6 k => exact h .c6 k

/-- the three separate ability rules, as a cocone with vertex St -/
def abilityRules (s : St) : Cocone colourDiagram where
  pt := St
  ι
    | .c15 => fun _ => sizeRule s
    | .c11 => fun _ => teleportRule s
    | .c6 => fun k => switchRule s k
  w f := nomatch f

theorem completeRule_is_desc (s : St) :
    completeRule s = completionIsColimit.desc (abilityRules s) := by
  funext k; cases k <;> rfl

#print axioms completionIsColimit
#print axioms completeRule_is_desc

/-! ## T3: step is the copairing over the action coproduct -/

inductive ActIx | walk | complete | climb

def actType : ActIx → Type
  | .walk => Walk
  | .complete => Completion
  | .climb => Unit

def actDiagram : Diagram := discrete ActIx actType

def actCocone : Cocone actDiagram where
  pt := Act
  ι
    | .walk => fun w => .walk w
    | .complete => fun k => .complete k
    | .climb => fun _ => .climb
  w f := nomatch f

def actIsColimit : IsColimit actCocone where
  desc s
    | .walk w => s.ι .walk w
    | .complete k => s.ι .complete k
    | .climb => s.ι .climb ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | walk w => exact h .walk w
    | complete k => exact h .complete k
    | climb => exact h .climb ()

def branchRules (s : St) : Cocone actDiagram where
  pt := St
  ι
    | .walk => walkRule s
    | .complete => completeRule s
    | .climb => fun _ => climbRule s
  w f := nomatch f

theorem step_is_desc (s : St) : step s = actIsColimit.desc (branchRules s) := by
  funext a; cases a <;> rfl

#print axioms actIsColimit
#print axioms step_is_desc

/-! ## T4 (attempt 2): specialisation of the size rule — St = big states ⊔ small states,
    and `sizeRule` (the 15-completion) is the copairing of shrink (on big) and grow (on small) -/

inductive SizeIx | big | small

def sizeType : SizeIx → Type
  | .big => {s : St // s.big = true}
  | .small => {s : St // s.big = false}

def sizeDiagram : Diagram := discrete SizeIx sizeType

def sizeCocone : Cocone sizeDiagram where
  pt := St
  ι
    | .big => fun x => x.val
    | .small => fun x => x.val
  w f := nomatch f

def sizeIsColimit : IsColimit sizeCocone where
  desc c x := if h : x.big = true then c.ι .big ⟨x, h⟩ else c.ι .small ⟨x, by simpa using h⟩
  fac c j x := by
    cases j
    · have hx : x.val.big = true := x.property
      show (if h : x.val.big = true then _ else _) = _
      rw [dif_pos hx]
      cases x; rfl
    · have hx : x.val.big = false := x.property
      show (if h : x.val.big = true then _ else _) = _
      rw [dif_neg (by simp [hx])]
      cases x; rfl
  uniq c m h y := by
    by_cases hb : y.big = true
    · rw [dif_pos hb]; exact h .big ⟨y, hb⟩
    · rw [dif_neg hb]; exact h .small ⟨y, by simpa using hb⟩

def sizeBranches : Cocone sizeDiagram where
  pt := St
  ι
    | .big => fun x => shrinkRule x.val
    | .small => fun x => growRule x.val
  w f := nomatch f

theorem sizeRule_is_desc : sizeRule = sizeIsColimit.desc sizeBranches := by
  funext s
  by_cases hb : s.big = true
  · simp [sizeRule, sizeIsColimit, sizeBranches, hb]
  · simp [sizeRule, sizeIsColimit, sizeBranches, hb]

#print axioms sizeIsColimit
#print axioms sizeRule_is_desc

/-! ## non-vacuity: the decompositions really constrain -/

theorem st_ext (a b : St) (h1 : a.loc = b.loc) (h2 : a.big = b.big) (h3 : a.cGone = b.cGone)
    (h4 : a.dGone = b.dGone) (h5 : a.fFrame = b.fFrame) : a = b := by
  have := stIsLimit.hom_ext (X := Unit) (fun _ => a) (fun _ => b) (by
    intro j _; cases j
    · exact h1
    · exact h2
    · exact h3
    · exact h4
    · exact h5)
  exact congrFun this ()

/-- the colour branches really differ (the copairing is not constant) -/
theorem ability_branches_differ :
    completeRule start .shrink15 ≠ completeRule start .teleport11 := by decide

#print axioms st_ext
#print axioms ability_branches_differ
