p = 'lean/L5eStructure.lean'
s = open(p, encoding='utf-8').read()

s = s.replace("""  decomposition  St   = product (limit of a discrete diagram) of blk, panel, gate, status
  decomposition  Blk  = product of row, col, size, face
  decomposition  Gate = product of barrierOpen, boxPresent
  generalization Act  = coproduct of move (Dir) and click (Nat);  stepCore = its copairing
  generalization Effect = coproduct of shrink, teleport (Nat × Nat), open6; applyEffect = copairing""",
"""  decomposition  St   = product (limit of a discrete diagram) of blk, panel, gates, status, pads
                        (attempt 2: Gate removed, gates/pads lists added)
  decomposition  Blk  = product of row, col, size, face
  generalization Act  = coproduct of move (Dir) and click (Nat);  stepCore = its copairing
  generalization Effect = coproduct of shrink, teleport, open6; applyEffect = copairing
                        (attempt 2: teleport carries no coordinates; destination comes from Level.tp)
  generalization Orient = coproduct of vert, horiz; ocBox = copairing of ocVert, ocHoriz (attempt 2)""")

# remove Gate section
a = s.index("/-! ## Gate is a product -/")
b = s.index("/-! ## St is a product -/")
s = s[:a] + s[b:]

s = s.replace("""inductive StIx | blk | panel | gate | status

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
      subst h1; subst h2; subst h3; subst h4; rfl""",
"""inductive StIx | blk | panel | gates | status | pads

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
      subst h1; subst h2; subst h3; subst h4; subst h5; rfl""")

s = s.replace("""def actRules (L : Level) (oc : Blk → Bool) (s : St) : Cocone actDiagram where
  pt := St
  ι
    | .mv => moveRule L s
    | .ck => clickRule L oc s
  w f := nomatch f

theorem stepCore_is_desc (L : Level) (oc : Blk → Bool) (s : St) :
    stepCore L oc s = actIsColimit.desc (actRules L oc s) := by
  funext a; cases a <;> rfl""",
"""def actRules (L : Level) (s : St) : Cocone actDiagram where
  pt := St
  ι
    | .mv => moveRule L s
    | .ck => clickRule L s
  w f := nomatch f

theorem stepCore_is_desc (L : Level) (s : St) :
    stepCore L s = actIsColimit.desc (actRules L s) := by
  funext a; cases a <;> rfl""")

s = s.replace("""def effDiagram : Diagram :=
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
    applyEffect (fun _ => true) ⟨⟨0, 0, 4, .up⟩, 0, ⟨false, true⟩, .playing⟩ .open6 := by decide""",
"""def effDiagram : Diagram :=
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
    ocBox ⟨.vert, 20, 31⟩ ⟨21, 31, 2, .up⟩ ≠ ocBox ⟨.horiz, 20, 31⟩ ⟨21, 31, 2, .up⟩ := by decide""")

s = s.replace("#print axioms L5e.gateIsLimit\n", "")
s += "#print axioms L5e.orIsColimit\n#print axioms L5e.ocBox_is_desc\n#print axioms L5e.oc_branches_differ\n"
open(p, 'w', encoding='utf-8').write(s)
print("ok")
