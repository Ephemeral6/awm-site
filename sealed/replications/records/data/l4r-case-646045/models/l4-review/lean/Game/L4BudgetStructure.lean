import Limits.Basic
import Game.L4Budget
/-! Attempt 6 composition: the budget model's state `BSt = MSt × Bool` is the product of the macro board
    state and the e-pickup flag (limit of a two-object discrete diagram). -/
namespace L4BS
open AWM L4M

inductive Part | board | taken
def partTy : Part → Type
  | .board => MSt | .taken => Bool
def bDiagram : Diagram := discrete Part partTy
def bCone : Cone bDiagram where
  pt := BSt
  π | .board => Prod.fst | .taken => Prod.snd
  w f := nomatch f
def bstIsLimit : IsLimit bCone where
  lift s p := (s.π .board p, s.π .taken p)
  fac _ j _ := by cases j <;> rfl
  uniq s m h p := by
    have e1 := h .board p; have e2 := h .taken p
    cases hm : m p
    simp only [bCone, hm] at e1 e2
    subst e1 e2; rfl

/-- `stepB` factors through the product: its board component is `stepM`, its flag component is `pick`. -/
theorem stepB_components (st : BSt) (a : MAct) (s' : MSt) (h : stepM st.1 a = some s') :
    stepB st a = some (s', st.2 || pick s') := by
  simp [stepB, h]

#print axioms bstIsLimit
#print axioms stepB_components
end L4BS
