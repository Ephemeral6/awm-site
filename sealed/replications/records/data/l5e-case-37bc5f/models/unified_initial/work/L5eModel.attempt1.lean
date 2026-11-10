/-
# L5eModel — computation layer of the formal system for this game (attempt 1)

Objects (work/objects.md has the distinguishability pairs):
  Dir, Blk (block: row, col, size, facing), Gate (barrier open?, 6-box present?),
  Status, St (block, panel mask, gate, status), Act (move d | click i), Effect, Recipe, Level.

Rules (each a function St → … → St with an executable domain):
  R-move   moveRule     : ACTION1-4
  R-click  clickRule    : ACTION6 on right-panel cell i (0..8, index 3*row+col)
  R-fire   applyEffect  : called by R-click when the toggled mask equals a recipe of the level
  R-win    inside moveRule (target square touches the socket interior)
  R-budget not in `step`; handled by `costOf` / Proof file (game over when spent ≥ budget
           before an action)

The 6-recipe open-condition is NOT fixed here: `step` takes it as a parameter `oc : Blk → Bool`.
That is the one rule I could not establish (see work/NOTES.md).
-/

namespace L5e

inductive Dir | up | down | left | right
  deriving DecidableEq, Repr

structure Blk where
  row : Nat
  col : Nat
  size : Nat
  face : Dir
  deriving DecidableEq, Repr

structure Gate where
  barrierOpen : Bool
  boxPresent : Bool
  deriving DecidableEq, Repr

inductive Status | playing | won
  deriving DecidableEq, Repr

structure St where
  blk : Blk
  panel : Nat          -- 9-bit mask of right-panel cells currently colour 14
  gate : Gate
  status : Status
  deriving DecidableEq, Repr

inductive Act | move (d : Dir) | click (i : Nat)
  deriving DecidableEq, Repr

inductive Effect | shrink | teleport (r c : Nat) | open6
  deriving DecidableEq, Repr

structure Recipe where
  mask : Nat
  eff : Effect

structure Level where
  floor : Gate → Nat → Nat → Bool   -- may a block cell sit at (row, col)?
  goal : Nat → Nat → Bool           -- socket interior (colour 10, not the block)
  recipes : List Recipe

/-- cells of the s×s square with top-left (r, c) -/
def cells (r c s : Nat) : List (Nat × Nat) :=
  (List.range s).flatMap fun i => (List.range s).map fun j => (r + i, c + j)

/-- top-left of the square one side-length away in direction d (none if it would leave the grid) -/
def target (b : Blk) : Dir → Option (Nat × Nat)
  | .up    => if b.size ≤ b.row then some (b.row - b.size, b.col) else none
  | .down  => some (b.row + b.size, b.col)
  | .left  => if b.size ≤ b.col then some (b.row, b.col - b.size) else none
  | .right => some (b.row, b.col + b.size)

/-- R-move (+ R-win). Win is checked before blocking (L2: the winning target overlapped non-floor). -/
def moveRule (L : Level) (s : St) (d : Dir) : St :=
  match target s.blk d with
  | none => s
  | some (r, c) =>
    let nb : Blk := { s.blk with row := r, col := c, face := d }
    if (cells r c s.blk.size).any (fun p => L.goal p.1 p.2) then
      { s with blk := nb, status := .won }
    else if (cells r c s.blk.size).all (fun p => L.floor s.gate p.1 p.2) then
      { s with blk := nb }
    else s

/-- R-fire, one branch per effect kind. -/
def applyEffect (oc : Blk → Bool) (s : St) : Effect → St
  | .shrink => if s.blk.size == 4 then { s with blk := { s.blk with size := 2 } } else s
  | .teleport r c => { s with blk := { s.blk with row := r, col := c } }
  | .open6 => if s.gate.boxPresent && oc s.blk then
                { s with gate := { barrierOpen := true, boxPresent := false } }
              else s

/-- R-click: toggle cell i; if the new mask equals a recipe of this level, the panel clears and the
    recipe's effect is applied. Only the level's own recipes fire (L3 plus-ring test). -/
def clickRule (L : Level) (oc : Blk → Bool) (s : St) (i : Nat) : St :=
  if i < 9 then
    let m := s.panel ^^^ (1 <<< i)
    match L.recipes.find? (fun rc => rc.mask == m) with
    | none => { s with panel := m }
    | some rc => applyEffect oc { s with panel := 0 } rc.eff
  else s

def stepCore (L : Level) (oc : Blk → Bool) (s : St) : Act → St
  | .move d => moveRule L s d
  | .click i => clickRule L oc s i

def step (L : Level) (oc : Blk → Bool) (s : St) (a : Act) : St :=
  if s.status == .won then s else stepCore L oc s a

def run (L : Level) (oc : Blk → Bool) (s : St) : List Act → St
  | [] => s
  | a :: as => run L oc (step L oc s a) as

/-! ## cost kinds (R-budget) -/

inductive Kind | mv | ck | fire
  deriving DecidableEq, Repr

def fires (L : Level) (s : St) (i : Nat) : Bool :=
  i < 9 && (L.recipes.find? (fun rc => rc.mask == (s.panel ^^^ (1 <<< i)))).isSome

def kindOf (L : Level) (s : St) : Act → Kind
  | .move _ => .mv
  | .click i => if fires L s i then .fire else .ck

/-- the states visited and the cost kind of every action -/
def trace (L : Level) (oc : Blk → Bool) (s : St) : List Act → St × List Kind
  | [] => (s, [])
  | a :: as =>
    let r := trace L oc (step L oc s a) as
    (r.1, kindOf L s a :: r.2)

structure Costs where
  move : Nat
  click : Nat
  fire : Nat
  budget : Nat

def costOf (C : Costs) : Kind → Nat
  | .mv => C.move
  | .ck => C.click
  | .fire => C.fire

def costSum (C : Costs) : List Kind → Nat
  | [] => 0
  | k :: ks => costOf C k + costSum C ks

/-! ## level 4 data (read off the level-4 frames, pixel coordinates) -/

def inR (lo x hi : Nat) : Bool := lo ≤ x && x ≤ hi

def l4floor (g : Gate) (r c : Nat) : Bool :=
  (inR 21 r 36 && inR 21 c 44)                       -- main 2-region
  || (inR 9 r 20 && inR 31 c 32)                      -- stalk under the 6-box
  || (inR 29 r 32 && inR 48 c 56)                     -- corridor to the socket
  || (g.barrierOpen && inR 29 r 32 && inR 45 c 47)    -- the colour-13 barrier

def l4goal (r c : Nat) : Bool := inR 29 r 32 && inR 57 c 60

def plusRing : Nat := 2 + 8 + 32 + 128   -- cells 1,3,5,7
def vline : Nat := 2 + 16 + 128          -- cells 1,4,7

def L4 : Level :=
  { floor := l4floor, goal := l4goal,
    recipes := [⟨plusRing, .shrink⟩, ⟨vline, .open6⟩] }

def l4init : St :=
  { blk := ⟨25, 37, 4, .down⟩, panel := 0,
    gate := ⟨false, true⟩, status := .playing }

/-- candidate open-condition (hypothesis H2', consistent with all 7 observed 6-fires):
    block's left column = stalk's left column, block directly below the stalk, facing up -/
def ocCand (stalkCol stalkBottom : Nat) (b : Blk) : Bool :=
  b.col == stalkCol && b.row == stalkBottom + 1 && b.face == .up

end L5e
