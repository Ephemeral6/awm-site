import Limits.Basic
import Game.L4Model
/-! Universal properties of the L4 model's object type (`St`, a product) and rule (`step`, a copairing). -/
namespace L4S
open AWM L4 Skeleton2

/-! ## Decomposition: St = product of its six slots (limit of a discrete diagram) -/
inductive Slot | small | opened | won | x | dP | dL | y | face

def slotTy : Slot → Type
  | .small => Bool | .opened => Bool | .won => Bool | .x => Nat | .dP => Nat | .dL => Nat
  | .y => Nat | .face => Dir

def stDiagram : Diagram := discrete Slot slotTy

def stCone : Cone stDiagram where
  pt := St
  π | .small => St.small | .opened => St.opened | .won => St.won | .x => St.x | .dP => St.dP | .dL => St.dL
    | .y => St.y | .face => St.face
  w f := nomatch f

def stIsLimit : IsLimit stCone where
  lift s p := ⟨s.π .small p, s.π .opened p, s.π .won p, s.π .x p, s.π .dP p, s.π .dL p, s.π .y p, s.π .face p⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h p := by
    have e1 := h .small p; have e2 := h .opened p; have e3 := h .won p
    have e4 := h .x p; have e5 := h .dP p; have e6 := h .dL p
    have e7 := h .y p; have e8 := h .face p
    cases hm : m p
    simp only [stCone, hm] at e1 e2 e3 e4 e5 e6 e7 e8
    subst e1 e2 e3 e4 e5 e6 e7 e8; rfl

/-! ## Generalization: the four action rules are one rule = copairing over the action coproduct -/
inductive ActIx | left | right | up | down | noop | click

def actTy : ActIx → Type
  | .left => Unit | .right => Unit | .up => Unit | .down => Unit | .noop => Unit | .click => Bool × Bool

def actDiagram : Diagram := discrete ActIx actTy

def actCocone : Cocone actDiagram where
  pt := Act
  ι | .left => fun _ => .left | .right => fun _ => .right | .up => fun _ => .up | .down => fun _ => .down
    | .noop => fun _ => .noop
    | .click => fun uv => .click uv.1 uv.2
  w f := nomatch f

def actIsColimit : IsColimit actCocone where
  desc s
    | .left => s.ι .left () | .right => s.ι .right () | .up => s.ι .up () | .down => s.ι .down ()
    | .noop => s.ι .noop ()
    | .click u v => s.ι .click (u, v)
  fac _ j x := by cases j <;> rfl
  uniq s m h a := by
    cases a with
    | left => exact h .left ()
    | right => exact h .right ()
    | up => exact h .up ()
    | down => exact h .down ()
    | noop => exact h .noop ()
    | click u v => exact h .click (u, v)

/-- The per-case rules R_left, R_right, R_noop, R_click as a cocone. -/
def ruleCocone (fires : St → Bool) (grow : Bool) (s : St) : Cocone actDiagram where
  pt := Res St
  ι | .left => fun _ => step fires grow s .left
    | .right => fun _ => step fires grow s .right
    | .up => fun _ => step fires grow s .up
    | .down => fun _ => step fires grow s .down
    | .noop => fun _ => step fires grow s .noop
    | .click => fun uv => step fires grow s (.click uv.1 uv.2)
  w f := nomatch f

/-- `step` is exactly the copairing (`desc`) of the per-case rules. -/
theorem step_is_desc (fires : St → Bool) (grow : Bool) (s : St) :
    step fires grow s = actIsColimit.desc (ruleCocone fires grow s) := by
  funext a; cases a <;> rfl

/-- Non-vacuity: branches differ (left vs noop from the start). -/
theorem branches_differ : step (fun _ => false) false s0 .left ≠ step (fun _ => false) false s0 .noop := by
  intro h
  simp only [step, rLeft, size, s0, Bool.false_eq_true, ite_false, Res.ok.injEq] at h
  have := congrArg St.x h
  simp at this

#print axioms stIsLimit
#print axioms actIsColimit
#print axioms step_is_desc
#print axioms branches_differ
end L4S
