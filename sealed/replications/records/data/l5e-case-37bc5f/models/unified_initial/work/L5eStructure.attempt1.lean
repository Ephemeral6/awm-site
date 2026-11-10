/-
# L5eStructure — the objects and rules of L5eModel presented as limits / colimits

  decomposition  St   = product (limit of a discrete diagram) of blk, panel, gate, status
  decomposition  Blk  = product of row, col, size, face
  decomposition  Gate = product of barrierOpen, boxPresent
  generalization Act  = coproduct of move (Dir) and click (Nat);  stepCore = its copairing
  generalization Effect = coproduct of shrink, teleport (Nat × Nat), open6; applyEffect = copairing
-/
import Limits.Basic
import L5eModel

open AWM

namespace L5e

/-! ## Blk is a product -/

inductive BlkIx | row | col | size | face

def blkDiagram : Diagram :=
  discrete BlkIx (fun | .row => Nat | .col => Nat | .size => Nat | .face => Dir)

def blkCone : Cone blkDiagram where
  pt := Blk
  π
    | .row => Blk.row
    | .col => Blk.col
    | .size => Blk.size
    | .face => Blk.face
  w f := nomatch f

def blkIsLimit : IsLimit blkCone where
  lift s x := ⟨s.π .row x, s.π .col x, s.π .size x, s.π .face x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .row x; have h2 := h .col x; have h3 := h .size x; have h4 := h .face x
    cases hm : m x with
    | mk r c z f =>
      simp only [blkCone, hm] at h1 h2 h3 h4
      subst h1; subst h2; subst h3; subst h4; rfl

/-! ## Gate is a product -/

inductive GateIx | barrier | box

def gateDiagram : Diagram := discrete GateIx (fun _ => Bool)

def gateCone : Cone gateDiagram where
  pt := Gate
  π
    | .barrier => Gate.barrierOpen
    | .box => Gate.boxPresent
  w f := nomatch f

def gateIsLimit : IsLimit gateCone where
  lift s x := ⟨s.π .barrier x, s.π .box x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .barrier x; have h2 := h .box x
    cases hm : m x with
    | mk a b =>
      simp only [gateCone, hm] at h1 h2
      subst h1; subst h2; rfl

/-! ## St is a product -/

inductive StIx | blk | panel | gate | status

def stDiagram : Diagram :=
  discrete StIx (fun | .blk => Blk | .panel => Nat | .gate => Gate | .status => Status)

def stCone : Cone stDiagram where
  pt := St
  π
    | .blk => St.blk
    | .panel => St.panel
    | .gate => St.gate
    | .status => St.status
  w f := nomatch f

def stIsLimit : IsLimit stCone where
  lift s x := ⟨s.π .blk x, s.π .panel x, s.π .gate x, s.π .status x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .blk x; have h2 := h .panel x; have h3 := h .gate x; have h4 := h .status x
    cases hm : m x with
    | mk b p g t =>
      simp only [stCone, hm] at h1 h2 h3 h4
      subst h1; subst h2; subst h3; subst h4; rfl

/-! ## Act is a coproduct; stepCore is the copairing of R-move and R-click -/

inductive ActIx | mv | ck

def actDiagram : Diagram := discrete ActIx (fun | .mv => Dir | .ck => Nat)

def actCocone : Cocone actDiagram where
  pt := Act
  ι
    | .mv => Act.move
    | .ck => Act.click
  w f := nomatch f

def actIsColimit : IsColimit actCocone where
  desc s
    | .move d => s.ι .mv d
    | .click i => s.ι .ck i
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | move d => exact h .mv d
    | click i => exact h .ck i

def actRules (L : Level) (oc : Blk → Bool) (s : St) : Cocone actDiagram where
  pt := St
  ι
    | .mv => moveRule L s
    | .ck => clickRule L oc s
  w f := nomatch f

theorem stepCore_is_desc (L : Level) (oc : Blk → Bool) (s : St) :
    stepCore L oc s = actIsColimit.desc (actRules L oc s) := by
  funext a; cases a <;> rfl

/-! ## Effect is a coproduct; applyEffect is the copairing of shrink / teleport / open6 -/

inductive EffIx | shrink | teleport | open6

def effDiagram : Diagram :=
  discrete EffIx (fun | .shrink => Unit | .teleport => Nat × Nat | .open6 => Unit)

def effCocone : Cocone effDiagram where
  pt := Effect
  ι
    | .shrink => fun _ => Effect.shrink
    | .teleport => fun p => Effect.teleport p.1 p.2
    | .open6 => fun _ => Effect.open6
  w f := nomatch f

def effIsColimit : IsColimit effCocone where
  desc s
    | .shrink => s.ι .shrink ()
    | .teleport r c => s.ι .teleport (r, c)
    | .open6 => s.ι .open6 ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | shrink => exact h .shrink ()
    | teleport r c => exact h .teleport (r, c)
    | open6 => exact h .open6 ()

def effRules (oc : Blk → Bool) (s : St) : Cocone effDiagram where
  pt := St
  ι
    | .shrink => fun _ => applyEffect oc s .shrink
    | .teleport => fun p => applyEffect oc s (.teleport p.1 p.2)
    | .open6 => fun _ => applyEffect oc s .open6
  w f := nomatch f

theorem applyEffect_is_desc (oc : Blk → Bool) (s : St) :
    applyEffect oc s = effIsColimit.desc (effRules oc s) := by
  funext e; cases e <;> rfl

/-! ## non-vacuity: the branches really differ -/

theorem effect_branches_differ :
    applyEffect (fun _ => true) ⟨⟨0, 0, 4, .up⟩, 0, ⟨false, true⟩, .playing⟩ .shrink ≠
    applyEffect (fun _ => true) ⟨⟨0, 0, 4, .up⟩, 0, ⟨false, true⟩, .playing⟩ .open6 := by decide

end L5e

#print axioms L5e.blkIsLimit
#print axioms L5e.gateIsLimit
#print axioms L5e.stIsLimit
#print axioms L5e.actIsColimit
#print axioms L5e.stepCore_is_desc
#print axioms L5e.effIsColimit
#print axioms L5e.applyEffect_is_desc
#print axioms L5e.effect_branches_differ
