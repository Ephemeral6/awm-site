/-
# L4Structure — the objects and rules of L4Model presented as limits / colimits.

* `St` (state) is the PRODUCT (limit of a discrete diagram) of its five slots i, j, big, up, door.
* `Act` (action) is the COPRODUCT (colimit of a discrete diagram) of Dir (move), Fin 4 (resize), Unit (fire).
* `Out` (outcome) is the COPRODUCT of Unit (win) and St (continue).
* `step s` is the copairing `desc` of the three branch rules moveRule / resizeRule / fireRule.

Compile (in lean/):  "$LEAN" -o L4Model.olean L4Model.lean ; LEAN_PATH=. "$LEAN" L4Structure.lean
-/
import Limits.Basic
import L4Model

open AWM

namespace L4S
open L4

/-! ## St = product of its slots (decomposition) -/

inductive StIx | i | j | big | up | door

def stDiagram : Diagram :=
  discrete StIx (fun | .i => Nat | .j => Nat | .big => Bool | .up => Bool | .door => Bool)

def stCone : Cone stDiagram where
  pt := St
  π
    | .i => St.i
    | .j => St.j
    | .big => St.big
    | .up => St.up
    | .door => St.door
  w f := nomatch f

def stIsLimit : IsLimit stCone where
  lift s x := ⟨s.π .i x, s.π .j x, s.π .big x, s.π .up x, s.π .door x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .i x; have h2 := h .j x; have h3 := h .big x; have h4 := h .up x; have h5 := h .door x
    cases hm : m x with
    | mk a b c d e =>
      simp only [stCone, hm] at h1 h2 h3 h4 h5
      subst h1; subst h2; subst h3; subst h4; subst h5; rfl

/-! ## Act = coproduct of its three cases (specialization of `step`) -/

inductive ActIx | move | resize | fire

def actDiagram : Diagram := discrete ActIx (fun | .move => Dir | .resize => Fin 4 | .fire => Unit)

def actCocone : Cocone actDiagram where
  pt := Act
  ι
    | .move => Act.move
    | .resize => Act.resize
    | .fire => fun _ => Act.fire
  w f := nomatch f

def actIsColimit : IsColimit actCocone where
  desc s
    | .move d => s.ι .move d
    | .resize q => s.ι .resize q
    | .fire => s.ι .fire ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | move d => exact h .move d
    | resize q => exact h .resize q
    | fire => exact h .fire ()

/-- The three branch rules as a cocone with apex `Out`. -/
def ruleCocone (s : St) : Cocone actDiagram where
  pt := Out
  ι
    | .move => moveRule s
    | .resize => resizeRule s
    | .fire => fun _ => fireRule s
  w f := nomatch f

/-- `step` is exactly the copairing of the three branch rules. -/
theorem step_is_desc (s : St) : step s = actIsColimit.desc (ruleCocone s) := by
  funext a; cases a <;> rfl

/-! ## Out = coproduct of win and continue -/

inductive OutIx | win | st

def outDiagram : Diagram := discrete OutIx (fun | .win => Unit | .st => St)

def outCocone : Cocone outDiagram where
  pt := Out
  ι
    | .win => fun _ => Out.win
    | .st => Out.st
  w f := nomatch f

def outIsColimit : IsColimit outCocone where
  desc s
    | .win => s.ι .win ()
    | .st x => s.ι .st x
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | win => exact h .win ()
    | st x => exact h .st x

/-! ## Non-vacuity: the branches really differ, and states are determined by their slots -/

theorem branches_differ :
    moveRule start .up ≠ fireRule start := by decide

theorem St.ext' (a b : St) (h1 : a.i = b.i) (h2 : a.j = b.j) (h3 : a.big = b.big)
    (h4 : a.up = b.up) (h5 : a.door = b.door) : a = b := by
  have := stIsLimit.hom_ext (X := Unit) (fun _ => a) (fun _ => b) (by
    intro j _; cases j
    · exact h1
    · exact h2
    · exact h3
    · exact h4
    · exact h5)
  exact congrFun this ()

/-! ## Attempt 2 — generalization: the fire rule for the two sizes is ONE parameterized rule
    (projectile column θ = s.j for both sizes). St is the coproduct of its small and big parts;
    fireRule is the copairing of the two size branches, each of which is `fireAt s.j`. -/

inductive SizeIx | small | big

def sizeDiagram : Diagram :=
  discrete SizeIx (fun | .small => {s : St // s.big = false} | .big => {s : St // s.big = true})

def sizeCocone : Cocone sizeDiagram where
  pt := St
  ι
    | .small => Subtype.val
    | .big => Subtype.val
  w f := nomatch f

def sizeIsColimit : IsColimit sizeCocone where
  desc c x := if h : x.big = true then c.ι .big ⟨x, h⟩ else c.ι .small ⟨x, by simpa using h⟩
  fac c j x := by
    cases j with
    | small => have h := x.2; simp [sizeCocone, h]; rfl
    | big => have h := x.2; simp [sizeCocone, h]; rfl
  uniq c m h y := by
    by_cases hb : y.big = true
    · simp only [hb, dite_true]; exact h .big ⟨y, hb⟩
    · simp only [hb]; exact h .small ⟨y, by simpa using hb⟩

/-- The parameterized operation r(θ): a projectile in lattice column θ. -/
def fireAt (θ : Nat) (s : St) : Out :=
  if s.up && !s.door && shotHits θ s.i then .st { s with door := true } else .st s

def fireCocone : Cocone sizeDiagram where
  pt := Out
  ι
    | .small => fun x => fireAt x.1.j x.1   -- 2x2: projectile in its own column
    | .big => fun x => fireAt x.1.j x.1     -- 4x4: projectile in its LEFT column
  w f := nomatch f

theorem fireRule_is_desc : fireRule = sizeIsColimit.desc fireCocone := by
  funext s
  by_cases hb : s.big = true
  · simp [sizeIsColimit, fireCocone, fireAt, fireRule, hb]
  · simp [sizeIsColimit, fireCocone, fireAt, fireRule, hb]

/-! ## Attempt 3 — the amended state St3 is the product of six slots (facing restored as `Dir`,
    pickup flag added), and step3 is again the copairing of its three branches over Act. -/

inductive St3Ix | i | j | big | face | door | picked

def st3Diagram : Diagram :=
  discrete St3Ix (fun | .i => Nat | .j => Nat | .big => Bool | .face => Dir | .door => Bool | .picked => Bool)

def st3Cone : Cone st3Diagram where
  pt := St3
  π
    | .i => St3.i
    | .j => St3.j
    | .big => St3.big
    | .face => St3.face
    | .door => St3.door
    | .picked => St3.picked
  w f := nomatch f

def st3IsLimit : IsLimit st3Cone where
  lift s x := ⟨s.π .i x, s.π .j x, s.π .big x, s.π .face x, s.π .door x, s.π .picked x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .i x; have h2 := h .j x; have h3 := h .big x
    have h4 := h .face x; have h5 := h .door x; have h6 := h .picked x
    cases hm : m x with
    | mk a b c d e f =>
      simp only [st3Cone, hm] at h1 h2 h3 h4 h5 h6
      subst h1; subst h2; subst h3; subst h4; subst h5; subst h6; rfl

def rule3Cocone (s : St3) : Cocone actDiagram where
  pt := Out3
  ι
    | .move => fun d => step3 s (.move d)
    | .resize => fun q => resize3 s q
    | .fire => fun _ => step3 s .fire
  w f := nomatch f

theorem step3_is_desc (s : St3) : step3 s = actIsColimit.desc (rule3Cocone s) := by
  funext a; cases a <;> rfl

end L4S

#print axioms L4S.stIsLimit
#print axioms L4S.actIsColimit
#print axioms L4S.step_is_desc
#print axioms L4S.outIsColimit
#print axioms L4S.branches_differ
#print axioms L4S.St.ext'
#print axioms L4S.sizeIsColimit
#print axioms L4S.fireRule_is_desc
#print axioms L4S.st3IsLimit
#print axioms L4S.step3_is_desc
