/-
# L5eStructure — the objects and rules of L5eModel presented as limits / colimits

  decomposition  St   = product (limit of a discrete diagram) of blk, panel, gates, status, pads
                        (attempt 2: Gate removed, gates/pads lists added)
  decomposition  Blk  = product of row, col, size, face
  generalization Act  = coproduct of move (Dir) and click (Nat);  stepCore = its copairing
  generalization Effect = coproduct of shrink, teleport, open6; applyEffect = copairing
                        (attempt 2: teleport carries no coordinates; destination comes from Level.tp)
  generalization Orient = coproduct of vert, horiz; ocBox = copairing of ocVert, ocHoriz (attempt 2)
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

/-! ## St is a product -/

inductive StIx | blk | panel | gates | status | pads

def stDiagram : Diagram :=
  discrete StIx (fun | .blk => Blk | .panel => Nat | .gates => List Bool | .status => Status
                     | .pads => List Bool)

def stCone : Cone stDiagram where
  pt := St
  π
    | .blk => St.blk
    | .panel => St.panel
    | .gates => St.gates
    | .status => St.status
    | .pads => St.pads
  w f := nomatch f

def stIsLimit : IsLimit stCone where
  lift s x := ⟨s.π .blk x, s.π .panel x, s.π .gates x, s.π .status x, s.π .pads x⟩
  fac _ j _ := by cases j <;> rfl
  uniq s m h x := by
    have h1 := h .blk x; have h2 := h .panel x; have h3 := h .gates x; have h4 := h .status x
    have h5 := h .pads x
    cases hm : m x with
    | mk b p g t u =>
      simp only [stCone, hm] at h1 h2 h3 h4 h5
      subst h1; subst h2; subst h3; subst h4; subst h5; rfl

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

def actRules (L : Level) (s : St) : Cocone actDiagram where
  pt := St
  ι
    | .mv => moveRule L s
    | .ck => clickRule L s
  w f := nomatch f

theorem stepCore_is_desc (L : Level) (s : St) :
    stepCore L s = actIsColimit.desc (actRules L s) := by
  funext a; cases a <;> rfl

/-! ## Effect is a coproduct; applyEffect is the copairing of shrink / teleport / open6 -/

inductive EffIx | shrink | teleport | open6

def effDiagram : Diagram :=
  discrete EffIx (fun | .shrink => Unit | .teleport => Unit | .open6 => Unit)

def effCocone : Cocone effDiagram where
  pt := Effect
  ι
    | .shrink => fun _ => Effect.shrink
    | .teleport => fun _ => Effect.teleport
    | .open6 => fun _ => Effect.open6
  w f := nomatch f

def effIsColimit : IsColimit effCocone where
  desc s
    | .shrink => s.ι .shrink ()
    | .teleport => s.ι .teleport ()
    | .open6 => s.ι .open6 ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | shrink => exact h .shrink ()
    | teleport => exact h .teleport ()
    | open6 => exact h .open6 ()

def effRules (L : Level) (s : St) : Cocone effDiagram where
  pt := St
  ι
    | .shrink => fun _ => applyEffect L s .shrink
    | .teleport => fun _ => applyEffect L s .teleport
    | .open6 => fun _ => applyEffect L s .open6
  w f := nomatch f

theorem applyEffect_is_desc (L : Level) (s : St) :
    applyEffect L s = effIsColimit.desc (effRules L s) := by
  funext e; cases e <;> rfl

/-! ## Orient is a coproduct; the open condition ocBox is the copairing of ocVert / ocHoriz (attempt 2) -/

inductive OrIx | vert | horiz

/-- each orientation's branch carries the stalk anchor (row, col) -/
def orDiagram : Diagram := discrete OrIx (fun _ => Nat × Nat)

def orCocone : Cocone orDiagram where
  pt := BoxSpec
  ι
    | .vert => fun p => ⟨.vert, p.1, p.2⟩
    | .horiz => fun p => ⟨.horiz, p.1, p.2⟩
  w f := nomatch f

def orIsColimit : IsColimit orCocone where
  desc s
    | ⟨.vert, r, c⟩ => s.ι .vert (r, c)
    | ⟨.horiz, r, c⟩ => s.ι .horiz (r, c)
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | mk o r c =>
      cases o with
      | vert => exact h .vert (r, c)
      | horiz => exact h .horiz (r, c)

def ocRules (b : Blk) : Cocone orDiagram where
  pt := Bool
  ι
    | .vert => fun p => ocVert ⟨.vert, p.1, p.2⟩ b
    | .horiz => fun p => ocHoriz ⟨.horiz, p.1, p.2⟩ b
  w f := nomatch f

theorem ocBox_is_desc (b : Blk) : (fun bx => ocBox bx b) = orIsColimit.desc (ocRules b) := by
  funext bx; cases bx with
  | mk o r c => cases o <;> rfl

/-! ## non-vacuity: the branches really differ -/

def stX : St := ⟨⟨21, 31, 4, .up⟩, 0, [false], .playing, []⟩

theorem effect_branches_differ :
    applyEffect L4 stX .shrink ≠ applyEffect L4 stX .open6 := by decide

/-- the two orientations disagree on the same block: the copairing is not constant -/
theorem oc_branches_differ :
    ocBox ⟨.vert, 20, 31⟩ ⟨21, 31, 2, .up⟩ ≠ ocBox ⟨.horiz, 20, 31⟩ ⟨21, 31, 2, .up⟩ := by decide

/-! ## size toggle (attempt 3): the plus-ring effect is the copairing of shrink (4x4) / grow (2x2) / identity -/

inductive SzIx | four | two | other

def szDiagram : Diagram := discrete SzIx (fun _ => St)

inductive SzCase | four (s : St) | two (s : St) | other (s : St)

def szCocone : Cocone szDiagram where
  pt := SzCase
  ι
    | .four => SzCase.four
    | .two => SzCase.two
    | .other => SzCase.other
  w f := nomatch f

def szIsColimit : IsColimit szCocone where
  desc s
    | .four x => s.ι .four x
    | .two x => s.ι .two x
    | .other x => s.ι .other x
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | four x => exact h .four x
    | two x => exact h .two x
    | other x => exact h .other x

def szRules (L : Level) : Cocone szDiagram where
  pt := St
  ι
    | .four => shrinkRule
    | .two => growRule L
    | .other => id
  w f := nomatch f

def classify (s : St) : SzCase :=
  if s.blk.size == 4 then .four s else if s.blk.size == 2 then .two s else .other s

theorem sizeToggle_is_desc (L : Level) (s : St) :
    sizeToggle L s = szIsColimit.desc (szRules L) (classify s) := by
  unfold sizeToggle classify
  split <;> (try split) <;> rfl

/-- the shrink and grow branches really differ on a level-5 state -/
theorem size_branches_differ :
    shrinkRule ⟨⟨17, 33, 4, .right⟩, 0, [false, false], .playing, [false]⟩ ≠
    growRule L5 ⟨⟨17, 33, 4, .right⟩, 0, [false, false], .playing, [false]⟩ := by decide

/-! ## move outcome (attempt 4): the sweep result is a coproduct win | moved | blocked;
    moveRule is the copairing of the win, partial/full-move (with refill) and turn branches -/

inductive MvIx | win | moved | blocked

def mvDiagram : Diagram := discrete MvIx (fun | .win => Nat × Nat | .moved => Nat × Nat | .blocked => Unit)

def mvCocone : Cocone mvDiagram where
  pt := Sum (Nat × Nat) (Option (Nat × Nat))
  ι
    | .win => fun p => .inl p
    | .moved => fun p => .inr (some p)
    | .blocked => fun _ => .inr none
  w f := nomatch f

def mvIsColimit : IsColimit mvCocone where
  desc s
    | .inl p => s.ι .win p
    | .inr (some p) => s.ι .moved p
    | .inr none => s.ι .blocked ()
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | inl p => exact h .win p
    | inr o =>
      cases o with
      | some p => exact h .moved p
      | none => exact h .blocked ()

def mvRules (L : Level) (s : St) (d : Dir) : Cocone mvDiagram where
  pt := St
  ι
    | .win => fun p => { s with blk := { s.blk with row := p.1, col := p.2, face := d }, status := .won }
    | .moved => fun p => { s with blk := { s.blk with row := p.1, col := p.2, face := d },
                                  pads := usePads L.pads s.pads s.blk.size p.1 p.2 }
    | .blocked => fun _ => { s with blk := { s.blk with face := d } }
  w f := nomatch f

theorem moveRule_is_desc (L : Level) (s : St) (d : Dir) :
    moveRule L s d = mvIsColimit.desc (mvRules L s d) (sweep L s.gates s.blk d s.blk.size 1 none) := by
  unfold moveRule
  cases sweep L s.gates s.blk d s.blk.size 1 none with
  | inl p => rfl
  | inr o => cases o <;> rfl

/-- the blocked branch is a real case: it differs from the moved branch on the same state -/
theorem mv_branches_differ :
    (⟨⟨37, 49, 4, .right⟩, 0, [true, false], .playing, [true]⟩ : St) ≠
    ⟨⟨37, 53, 4, .right⟩, 0, [true, false], .playing, [true]⟩ := by
  decide

/-- and the blocked branch is what the model actually takes there (observed tid 8e11f274) -/
theorem blocked_turn_observed :
    moveRule L5 ⟨⟨37, 49, 4, .down⟩, 0, [true, false], .playing, [true]⟩ .right =
      ⟨⟨37, 49, 4, .right⟩, 0, [true, false], .playing, [true]⟩ := by
  decide +kernel

end L5e


#print axioms L5e.blkIsLimit
#print axioms L5e.stIsLimit
#print axioms L5e.actIsColimit
#print axioms L5e.stepCore_is_desc
#print axioms L5e.effIsColimit
#print axioms L5e.applyEffect_is_desc
#print axioms L5e.effect_branches_differ
#print axioms L5e.orIsColimit
#print axioms L5e.ocBox_is_desc
#print axioms L5e.oc_branches_differ
#print axioms L5e.szIsColimit
#print axioms L5e.sizeToggle_is_desc
#print axioms L5e.size_branches_differ
#print axioms L5e.mvIsColimit
#print axioms L5e.moveRule_is_desc
#print axioms L5e.mv_branches_differ
#print axioms L5e.blocked_turn_observed
