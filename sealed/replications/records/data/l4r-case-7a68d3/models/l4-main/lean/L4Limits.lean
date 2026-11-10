import Limits.Basic
import L4Model
/-!
# L4Limits — universal properties of the objects and rules of model M4

* `Blk` is the product (limit of a discrete diagram) of its six slots — decomposition.
* `Full` is the product of block, grid mask, counter, won flag — decomposition.
* `BAct` is the coproduct of the three rule cases (move / size toggle / beam), and the block rule
  `bstep b` is the copairing (`desc`) of the three case rules — generalization.
* `Act` is the coproduct of move / click / off-grid click.
-/
open AWM

namespace L4

/-! ## Blk = product of its slots -/

inductive BlkIx | t | l | big | face | box | item

def blkF : BlkIx → Type
  | .t => Nat | .l => Nat | .big => Bool | .face => Dir | .box => Bool | .item => Bool

def blkDiagram : Diagram := discrete BlkIx blkF

def blkCone : Cone blkDiagram where
  pt := Blk
  π
    | .t => Blk.t | .l => Blk.l | .big => Blk.big
    | .face => Blk.face | .box => Blk.box | .item => Blk.item
  w f := nomatch f

def blkIsLimit : IsLimit blkCone where
  lift s x := ⟨s.π .t x, s.π .l x, s.π .big x, s.π .face x, s.π .box x, s.π .item x⟩
  fac s j x := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .t x; have h2 := h .l x; have h3 := h .big x
    have h4 := h .face x; have h5 := h .box x; have h6 := h .item x
    cases hm : m x
    simp only [blkCone, hm] at h1 h2 h3 h4 h5 h6
    subst h1 h2 h3 h4 h5 h6; rfl

#print axioms blkIsLimit

/-! ## Full = product of block, mask, counter, won -/

inductive FullIx | b | mask | used | won

def fullF : FullIx → Type
  | .b => Blk | .mask => Nat | .used => Nat | .won => Bool

def fullDiagram : Diagram := discrete FullIx fullF

def fullCone : Cone fullDiagram where
  pt := Full
  π
    | .b => Full.b | .mask => Full.mask | .used => Full.used | .won => Full.won
  w f := nomatch f

def fullIsLimit : IsLimit fullCone where
  lift s x := ⟨s.π .b x, s.π .mask x, s.π .used x, s.π .won x⟩
  fac s j x := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .b x; have h2 := h .mask x; have h3 := h .used x; have h4 := h .won x
    cases hm : m x
    simp only [fullCone, hm] at h1 h2 h3 h4
    subst h1 h2 h3 h4; rfl

#print axioms fullIsLimit

/-! ## BAct = coproduct of the three rule cases; bstep = copairing -/

inductive RuleIx | mv | sz | beam

def ruleF : RuleIx → Type
  | .mv => Dir × Bool × Bool × Bool | .sz => Bool × Nat | .beam => Bool

def ruleDiagram : Diagram := discrete RuleIx ruleF

def bactCocone : Cocone ruleDiagram where
  pt := BAct
  ι
    | .mv => fun p => BAct.mv p.1 p.2.1 p.2.2.1 p.2.2.2
    | .sz => fun p => BAct.sz p.1 p.2
    | .beam => fun e => BAct.beam e
  w f := nomatch f

def bactIsColimit : IsColimit bactCocone where
  desc s
    | .mv d tu e h => s.ι .mv (d, tu, e, h)
    | .sz e q => s.ι .sz (e, q)
    | .beam e => s.ι .beam e
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | mv d tu e hf => exact h .mv (d, tu, e, hf)
    | sz e q => exact h .sz (e, q)
    | beam e => exact h .beam e

/-- the three case rules -/
def moveRule (qD : Nat) (b : Blk) (p : Dir × Bool × Bool × Bool) : BRes :=
  bstep qD b (.mv p.1 p.2.1 p.2.2.1 p.2.2.2)
def sizeRule (qD : Nat) (b : Blk) (p : Bool × Nat) : BRes := bstep qD b (.sz p.1 p.2)
def beamRule (qD : Nat) (b : Blk) (e : Bool) : BRes := bstep qD b (.beam e)

def ruleCocone (qD : Nat) (b : Blk) : Cocone ruleDiagram where
  pt := BRes
  ι
    | .mv => moveRule qD b
    | .sz => sizeRule qD b
    | .beam => beamRule qD b
  w f := nomatch f

/-- **bstep is the copairing of move / size-toggle / beam.** -/
theorem bstep_is_desc (qD : Nat) (b : Blk) : bstep qD b = bactIsColimit.desc (ruleCocone qD b) := by
  funext a; cases a <;> rfl

#print axioms bactIsColimit
#print axioms bstep_is_desc

/-! ## Act = coproduct of move / grid click / off-grid click -/

inductive ActIx | mv | click | off

def actF : ActIx → Type
  | .mv => Dir × Bool × Bool × Bool | .click => Nat × Bool × Nat | .off => Unit

def actDiagram : Diagram := discrete ActIx actF

def actCocone : Cocone actDiagram where
  pt := Act
  ι
    | .mv => fun p => Act.mv p.1 p.2.1 p.2.2.1 p.2.2.2
    | .click => fun p => Act.click p.1 p.2.1 p.2.2
    | .off => fun _ => Act.off
  w f := nomatch f

def actIsColimit : IsColimit actCocone where
  desc s
    | .mv d tu e h => s.ι .mv (d, tu, e, h)
    | .click c e q => s.ι .click (c, e, q)
    | .off => s.ι .off ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | mv d tu e hf => exact h .mv (d, tu, e, hf)
    | click c e q => exact h .click (c, e, q)
    | off => exact h .off ()

#print axioms actIsColimit

/-! non-vacuity: the copairing really branches -/
theorem rules_differ : sizeRule 0 ⟨25, 37, true, .D, false, true⟩ (false, 0) ≠
    beamRule 0 ⟨25, 37, true, .D, false, true⟩ false := by decide

/-! ## Specialization (attempt 2): the eat rule splits by block size (coproduct over {small, big}) -/

inductive SizeIx | small | big

def sizeF : SizeIx → Type
  | .small => Blk | .big => Blk

def sizeDiagram : Diagram := discrete SizeIx sizeF

/-- a block tagged by its size case -/
inductive Sized
  | small (b : Blk)
  | big (b : Blk)

def sizedCocone : Cocone sizeDiagram where
  pt := Sized
  ι
    | .small => Sized.small
    | .big => Sized.big
  w f := nomatch f

def sizedIsColimit : IsColimit sizedCocone where
  desc s
    | .small b => s.ι .small b
    | .big b => s.ι .big b
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | small b => exact h .small b
    | big b => exact h .big b

/-- the two specialized eat rules: 2x2 overlap; 4x4 front-half overlap -/
def eatSmall (b : Blk) : Bool := anyItem b.t b.l 2
def eatBig (b : Blk) : Bool := anyCell 4 (fun i j => inFront b.face 4 i j && isItem (b.t + i) (b.l + j))

def eatCocone : Cocone sizeDiagram where
  pt := Bool
  ι
    | .small => eatSmall
    | .big => eatBig
  w f := nomatch f

def sized (b : Blk) : Sized := if b.big then .big b else .small b

/-- **eatsAt is the copairing of the two specialized eat rules**, read through the size tag. -/
theorem eatsAt_is_desc (b : Blk) : eatsAt b = sizedIsColimit.desc eatCocone (sized b) := by
  cases h : b.big <;> simp [eatsAt, sized, h, sizedIsColimit, eatCocone, eatSmall, eatBig]

#print axioms sizedIsColimit
#print axioms eatsAt_is_desc

#print axioms rules_differ

/-! ## Generalization (attempt 5): grow placement — four facing cases are one rule

Before: grow facing L/D/U observed (t-2,l-2), facing R a free choice. After attempt 5 all four facing
cases coincide; the facing-indexed copairing equals the single facing-independent placement. -/

inductive FaceIx | U | D | L | R

def faceF : FaceIx → Type := fun _ => Blk

def faceDiagram : Diagram := discrete FaceIx faceF

/-- a block tagged by its facing case -/
structure Faced where
  d : FaceIx
  b : Blk

def facedCocone : Cocone faceDiagram where
  pt := Faced
  ι d b := ⟨d, b⟩
  w f := nomatch f

def facedIsColimit : IsColimit facedCocone where
  desc s y := s.ι y.d y.b
  fac _ _ _ := rfl
  uniq s m h y := by cases y with | mk d b => exact h d b

/-- the per-facing grow placement rule (each case is the model's grow offset) -/
def growCase (_d : FaceIx) (b : Blk) : Nat × Nat := (b.t + grT 0 b - 2, b.l + grL 0 b - 2)

def growCocone : Cocone faceDiagram where
  pt := Nat × Nat
  ι := growCase
  w f := nomatch f

/-- **the copairing of the four facing cases is the single rule (t-2, l-2)** -/
theorem grow_generalized (d : FaceIx) (b : Blk) :
    facedIsColimit.desc growCocone ⟨d, b⟩ = (b.t - 2, b.l - 2) := by
  simp [facedIsColimit, growCocone, growCase, grT, grL]

#print axioms facedIsColimit
#print axioms grow_generalized

end L4
