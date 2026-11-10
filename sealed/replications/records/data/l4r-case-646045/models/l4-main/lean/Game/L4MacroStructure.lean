import Limits.Basic
import Game.L4Macro
/-! Universal properties of the attempt-4 macro model: `MSt` is a product, `stepM` a copairing. -/
namespace L4MS
open AWM L4M

inductive Slot | small | opened | y | x | face
def slotTy : Slot → Type
  | .small => Bool | .opened => Bool | .y => Nat | .x => Nat | .face => Nat
def stDiagram : Diagram := discrete Slot slotTy
def stCone : Cone stDiagram where
  pt := MSt
  π | .small => MSt.small | .opened => MSt.opened | .y => MSt.y | .x => MSt.x | .face => MSt.face
  w f := nomatch f
def mstIsLimit : IsLimit stCone where
  lift s p := ⟨s.π .small p, s.π .opened p, s.π .y p, s.π .x p, s.π .face p⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h p := by
    have e1 := h .small p; have e2 := h .opened p; have e3 := h .y p; have e4 := h .x p
    have e5 := h .face p
    cases hm : m p
    simp only [stCone, hm] at e1 e2 e3 e4 e5
    subst e1 e2 e3 e4 e5; rfl

inductive ActIx | up | down | left | right | plus | line
def actDiagram : Diagram := discrete ActIx (fun _ => Unit)
def actCocone : Cocone actDiagram where
  pt := MAct
  ι | .up => fun _ => .up | .down => fun _ => .down | .left => fun _ => .left
    | .right => fun _ => .right | .plus => fun _ => .plus | .line => fun _ => .line
  w f := nomatch f
def mactIsColimit : IsColimit actCocone where
  desc s
    | .up => s.ι .up () | .down => s.ι .down () | .left => s.ι .left ()
    | .right => s.ι .right () | .plus => s.ι .plus () | .line => s.ι .line ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h a := by cases a <;> first
    | exact h .up () | exact h .down () | exact h .left () | exact h .right ()
    | exact h .plus () | exact h .line ()

def ruleCocone (st : MSt) : Cocone actDiagram where
  pt := Option MSt
  ι | .up => fun _ => stepM st .up | .down => fun _ => stepM st .down
    | .left => fun _ => stepM st .left | .right => fun _ => stepM st .right
    | .plus => fun _ => stepM st .plus | .line => fun _ => stepM st .line
  w f := nomatch f

/-- `stepM` (R_move ×4 with clamp + win_touch, R_plus = shrink/grow, R_line = shot) is the copairing. -/
theorem stepM_is_desc (st : MSt) : stepM st = mactIsColimit.desc (ruleCocone st) := by
  funext a; cases a <;> rfl

#print axioms mstIsLimit
#print axioms mactIsColimit
#print axioms stepM_is_desc
end L4MS
