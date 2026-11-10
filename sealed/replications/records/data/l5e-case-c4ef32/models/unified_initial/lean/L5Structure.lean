import Limits.Basic
import L5Model
/-!
# L5Structure — universal properties of the objects and rules of `L5Model`

* `stIsLimit`   : the state `St` is the product (limit of a discrete diagram) of its seven slots.
* `gateIsLimit` : a gate = (switch box present, barrier open) subject to present = ¬open is the
                  equalizer of `fst` and `not ∘ snd`; `Bool` (the single slot kept in `St`) is that limit.
* `actIsColimit`: the macro action type `Act` is the coproduct of its five cases.
* `step_is_desc`: the transition rule `step s` is the copairing of the five per-case rules.
-/
open AWM

namespace L5

/-! ## the state is a product -/

inductive StIx | r | c | big | f | oc | od | ep

def stF : StIx → Type
  | .r => Fin 32 | .c => Fin 32 | .big => Bool | .f => Dir | .oc => Bool | .od => Bool | .ep => Bool

def stDiagram : Diagram := discrete StIx stF

def stCone : Cone stDiagram where
  pt := St
  π
    | .r => St.r | .c => St.c | .big => St.big | .f => St.f | .oc => St.oc | .od => St.od | .ep => St.ep
  w f := nomatch f

def stIsLimit : IsLimit stCone where
  lift s x := ⟨s.π .r x, s.π .c x, s.π .big x, s.π .f x, s.π .oc x, s.π .od x, s.π .ep x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have hr := h .r x; have hc := h .c x; have hb := h .big x; have hf := h .f x
    have ho := h .oc x; have hd := h .od x; have he := h .ep x
    cases hm : m x
    simp only [stCone, hm] at hr hc hb hf ho hd he
    subst hr hc hb hf ho hd he
    rfl

/-! ## a gate is an equalizer (transform T2: Switch.present and Barrier.open merged) -/

def gateDiagram : Diagram := parallelPair (fun p : Bool × Bool => p.1) (fun p : Bool × Bool => !p.2)

/-- the kept slot `open : Bool`, with present := ¬open -/
def gateCone : Cone gateDiagram where
  pt := Bool
  π
    | .src => fun o => (!o, o)
    | .tgt => fun o => !o
  w
    | .fst, _ => rfl
    | .snd, _ => rfl

def gateIsLimit : IsLimit gateCone where
  lift s x := (s.π .src x).2
  fac s j x := by
    have h1 := s.w .fst x
    have h2 := s.w .snd x
    simp only [gateDiagram, parallelPair] at h1 h2
    cases j with
    | src =>
      show (!(s.π .src x).2, (s.π .src x).2) = s.π .src x
      cases hp : s.π .src x with
      | mk a b => rw [hp] at h1 h2; simp only at h1 h2 ⊢; rw [← h2] at h1; rw [h1]
    | tgt =>
      show (!(s.π .src x).2) = s.π .tgt x
      exact h2
  uniq s m h x := by
    have := h .src x
    simp only [gateCone] at this
    show m x = (s.π .src x).2
    rw [← this]

/-! ## actions form a coproduct, and `step` is the copairing of the per-case rules -/

inductive ActIx | move | shrink | grow | shot | tele

def actF : ActIx → Type
  | .move => Dir | .shrink => Quad | .grow => Quad | .shot => Unit | .tele => Unit

def actDiagram : Diagram := discrete ActIx actF

def actCocone : Cocone actDiagram where
  pt := Act
  ι
    | .move => Act.move | .shrink => Act.shrink | .grow => Act.grow
    | .shot => fun _ => Act.shot | .tele => fun _ => Act.tele
  w f := nomatch f

def actIsColimit : IsColimit actCocone where
  desc s
    | .move d => s.ι .move d
    | .shrink q => s.ι .shrink q
    | .grow q => s.ι .grow q
    | .shot => s.ι .shot ()
    | .tele => s.ι .tele ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | move d => exact h .move d
    | shrink q => exact h .shrink q
    | grow q => exact h .grow q
    | shot => exact h .shot ()
    | tele => exact h .tele ()

/-- the per-case rules R1–R4, each followed by the post-conditions R5 -/
def rulesCocone (s : St) : Cocone actDiagram where
  pt := St
  ι
    | .move => fun d => post (ruleMove s d)
    | .shrink => fun q => post (ruleShrink s q)
    | .grow => fun q => post (ruleGrow s q)
    | .shot => fun _ => post (ruleShot s)
    | .tele => fun _ => post (ruleTele s)
  w f := nomatch f

theorem step_is_desc (s : St) : step s = actIsColimit.desc (rulesCocone s) := by
  funext a; cases a <;> rfl

/-! ## non-vacuity of the universal properties -/

/-- two states with equal slots are equal (product determined by projections) -/
theorem St.ext' (a b : St) (h : ∀ j, stCone.π j a = stCone.π j b) : a = b := by
  have := stIsLimit.hom_ext (X := Unit) (fun _ => a) (fun _ => b) (fun j _ => h j)
  exact congrFun this ()

/-- the copairing really branches: a move and a teleport from the start differ -/
theorem step_branches_differ : step start (.move .R) ≠ step start .tele := by decide

end L5

#print axioms L5.stIsLimit
#print axioms L5.gateIsLimit
#print axioms L5.actIsColimit
#print axioms L5.step_is_desc
#print axioms L5.St.ext'
#print axioms L5.step_branches_differ
