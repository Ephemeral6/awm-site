/-
# L5eModel — computation layer of the formal system for this game (amended in attempt 2)

Objects (work/objects.md has the distinguishability pairs):
  Dir, Blk (block: row, col, size, facing), Status,
  St (block, panel mask, gates : List Bool, status, pads : List Bool),
  Act (move d | click i), Effect, Recipe, Orient, BoxSpec, Level.

Rules (each a function St → … → St with an executable domain):
  R-move   moveRule     : ACTION1-4 (includes R-win and R-refill bookkeeping)
  R-click  clickRule    : ACTION6 on right-panel cell i (0..8, index 3*row+col)
  R-fire   applyEffect  : called by R-click when the toggled mask equals a recipe of the level
  R-open   ocBox        : when an open6 fire opens a box (copairing over Orient)
  R-tp     tpDest       : teleport destination by block size
  R-budget costOf / gainOf, checked in the Proof file (game over when an action is sent with the bar empty)

Attempt-2 amendments (attempt-1 sources kept in work/*.attempt1.lean):
  * Gate {barrierOpen, boxPresent} -> `gates : List Bool`, one flag per 6-box. The two old slots were always
    negations of each other (redundant slot dropped); L5 has two boxes.
  * The open condition is no longer a parameter `oc`: it is DEFINED by `ocBox` from the box's stalk
    (vertical: L3, L4; horizontal: L5). Established by 4 successes and 6 failures.
  * Teleport destination depends on block size (`Level.tp`): 4x4 -> 11-framed square (L2), 2x2 -> 15-pad (L5).
  * Refill pads (`Level.pads`): a 2x2 that steps exactly onto an unused 14-pad consumes it (+refill to the bar).

Attempt-3 amendment (attempt-2 sources kept in work/*.attempt2.lean):
  * The plus-ring effect is a size TOGGLE: on a 4x4 it shrinks (top-left kept, as before); on a 2x2 it grows
    to 4x4 (`growTo`): top row = old top - 2 (old bottom row kept), left column = the first of
    l-2, l-1, l whose 4x4 square is all floor; no fit -> no change (that last branch is an assumption).
    Observed on L5: (37,15) -> (35,13) on the 15-pad; (17,33) -> (15,33) in the pocket.
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

inductive Status | playing | won
  deriving DecidableEq, Repr

structure St where
  blk : Blk
  panel : Nat          -- 9-bit mask of right-panel cells currently colour 14
  gates : List Bool    -- per 6-box: opened (box gone, its barrier turned to floor)
  status : Status
  pads : List Bool     -- per 14-pad: consumed
  deriving DecidableEq, Repr

inductive Act | move (d : Dir) | click (i : Nat)
  deriving DecidableEq, Repr

inductive Effect | shrink | teleport | open6
  deriving DecidableEq, Repr

/-- which way the 2-wide stalk runs from its mouth to the box -/
inductive Orient | vert | horiz
  deriving DecidableEq, Repr

/-- vert: (row, col) = (stalk bottom row, stalk left col), box above.
    horiz: (row, col) = (stalk top row, stalk left col), box to the right. -/
structure BoxSpec where
  orient : Orient
  row : Nat
  col : Nat
  deriving DecidableEq, Repr

structure Recipe where
  mask : Nat
  eff : Effect

structure Level where
  floor : List Bool → Nat → Nat → Bool   -- may a block cell sit at (row, col)? (given which boxes are open)
  goal : Nat → Nat → Bool                -- socket interior (colour 10, not the block)
  recipes : List Recipe
  boxes : List BoxSpec
  tp : List (Nat × Nat × Nat)            -- teleport destination (size, row, col)
  pads : List (Nat × Nat)                -- 2x2 refill pads (top-left)

/-- cells of the s×s square with top-left (r, c) -/
def cells (r c s : Nat) : List (Nat × Nat) :=
  (List.range s).flatMap fun i => (List.range s).map fun j => (r + i, c + j)

/-- top-left of the square one side-length away in direction d (none if it would leave the grid) -/
def target (b : Blk) : Dir → Option (Nat × Nat)
  | .up    => if b.size ≤ b.row then some (b.row - b.size, b.col) else none
  | .down  => some (b.row + b.size, b.col)
  | .left  => if b.size ≤ b.col then some (b.row, b.col - b.size) else none
  | .right => some (b.row, b.col + b.size)

/-- R-refill bookkeeping: a 2x2 whose new top-left equals an unused pad consumes it. -/
def usePads : List (Nat × Nat) → List Bool → Nat → Nat → Nat → List Bool
  | p :: ps, u :: us, sz, r, c => (u || (sz == 2 && p.1 == r && p.2 == c)) :: usePads ps us sz r c
  | _, us, _, _, _ => us

/-- R-move (+ R-win). Win is checked before blocking (L2: the winning target overlapped non-floor). -/
def moveRule (L : Level) (s : St) (d : Dir) : St :=
  match target s.blk d with
  | none => s
  | some (r, c) =>
    let nb : Blk := { s.blk with row := r, col := c, face := d }
    if (cells r c s.blk.size).any (fun p => L.goal p.1 p.2) then
      { s with blk := nb, status := .won }
    else if (cells r c s.blk.size).all (fun p => L.floor s.gates p.1 p.2) then
      { s with blk := nb, pads := usePads L.pads s.pads s.blk.size r c }
    else s

/-- R-open (DEFINED in attempt 2): the block is at the stalk mouth, flush with the stalk's first
    row/column, facing along the stalk toward the box. A copairing over `Orient`. -/
def ocVert (bx : BoxSpec) (b : Blk) : Bool := b.face == .up && b.col == bx.col && b.row == bx.row + 1
def ocHoriz (bx : BoxSpec) (b : Blk) : Bool := b.face == .right && b.row == bx.row && b.col + b.size == bx.col

def ocBox (bx : BoxSpec) (b : Blk) : Bool :=
  match bx.orient with
  | .vert => ocVert bx b
  | .horiz => ocHoriz bx b

def openGates (b : Blk) : List BoxSpec → List Bool → List Bool
  | bx :: bxs, g :: gs => (g || ocBox bx b) :: openGates b bxs gs
  | _, gs => gs

/-- R-tp: destination for a block of size sz -/
def tpDest (L : Level) (sz : Nat) : Option (Nat × Nat) :=
  (L.tp.find? (fun t => t.1 == sz)).map (fun t => t.2)

/-- R-grow placement (attempt 3): new top-left for a 2x2 at (t, l) growing to 4x4, or none if nothing fits -/
def growTo (L : Level) (g : List Bool) (t l : Nat) : Option (Nat × Nat) :=
  if 2 ≤ t then
    [l - 2, l - 1, l].find? (fun c => 2 ≤ l && (cells (t - 2) c 4).all (fun p => L.floor g p.1 p.2))
      |>.map (fun c => (t - 2, c))
  else none

/-- R-size (attempt 3): the plus-ring effect, a copairing over the size case (shrink | grow) -/
def shrinkRule (s : St) : St := { s with blk := { s.blk with size := 2 } }
def growRule (L : Level) (s : St) : St :=
  match growTo L s.gates s.blk.row s.blk.col with
  | some (r, c) => { s with blk := { s.blk with row := r, col := c, size := 4 } }
  | none => s

def sizeToggle (L : Level) (s : St) : St :=
  if s.blk.size == 4 then shrinkRule s else if s.blk.size == 2 then growRule L s else s

/-- R-fire, one branch per effect kind. -/
def applyEffect (L : Level) (s : St) : Effect → St
  | .shrink => sizeToggle L s
  | .teleport => match tpDest L s.blk.size with
                 | some (r, c) => { s with blk := { s.blk with row := r, col := c } }
                 | none => s
  | .open6 => { s with gates := openGates s.blk L.boxes s.gates }

/-- R-click: toggle cell i; if the new mask equals a recipe of this level, the panel clears and the
    recipe's effect is applied. Only the level's own recipes fire (L3 plus-ring test). -/
def clickRule (L : Level) (s : St) (i : Nat) : St :=
  if i < 9 then
    let m := s.panel ^^^ (1 <<< i)
    match L.recipes.find? (fun rc => rc.mask == m) with
    | none => { s with panel := m }
    | some rc => applyEffect L { s with panel := 0 } rc.eff
  else s

def stepCore (L : Level) (s : St) : Act → St
  | .move d => moveRule L s d
  | .click i => clickRule L s i

def step (L : Level) (s : St) (a : Act) : St :=
  if s.status == .won then s else stepCore L s a

def run (L : Level) (s : St) : List Act → St
  | [] => s
  | a :: as => run L (step L s a) as

/-! ## cost kinds (R-budget) -/

inductive Kind | mv | ck | fire | mvR   -- mvR: a move that consumed a refill pad
  deriving DecidableEq, Repr

def fires (L : Level) (s : St) (i : Nat) : Bool :=
  i < 9 && (L.recipes.find? (fun rc => rc.mask == (s.panel ^^^ (1 <<< i)))).isSome

def kindOf (L : Level) (s : St) : Act → Kind
  | .move d => if (moveRule L s d).pads != s.pads then .mvR else .mv
  | .click i => if fires L s i then .fire else .ck

/-- the final state and the cost kind of every action -/
def trace (L : Level) (s : St) : List Act → St × List Kind
  | [] => (s, [])
  | a :: as =>
    let r := trace L (step L s a) as
    (r.1, kindOf L s a :: r.2)

structure Costs where
  move : Nat
  click : Nat
  fire : Nat
  budget : Nat
  refill : Nat := 0    -- bar cells gained by an mvR move (L5: 36)

def costOf (C : Costs) : Kind → Nat
  | .mv => C.move
  | .ck => C.click
  | .fire => C.fire
  | .mvR => C.move

def gainOf (C : Costs) : Kind → Nat
  | .mvR => C.refill
  | _ => 0

def costSum (C : Costs) : List Kind → Nat
  | [] => 0
  | k :: ks => costOf C k + costSum C ks

def gainSum (C : Costs) : List Kind → Nat
  | [] => 0
  | k :: ks => gainOf C k + gainSum C ks

/-! ## level 4 data (read off the level-4 frames, pixel coordinates) -/

def inR (lo x hi : Nat) : Bool := lo ≤ x && x ≤ hi

def gate (g : List Bool) (i : Nat) : Bool := g.getD i false

def l4floor (g : List Bool) (r c : Nat) : Bool :=
  (inR 21 r 36 && inR 21 c 44)                       -- main 2-region
  || (inR 9 r 20 && inR 31 c 32)                      -- stalk under the 6-box
  || (inR 29 r 32 && inR 48 c 56)                     -- corridor to the socket
  || (gate g 0 && inR 29 r 32 && inR 45 c 47)         -- the colour-13 barrier

def l4goal (r c : Nat) : Bool := inR 29 r 32 && inR 57 c 60

def plusRing : Nat := 2 + 8 + 32 + 128   -- cells 1,3,5,7
def vline : Nat := 2 + 16 + 128          -- cells 1,4,7
def tpMask : Nat := 1 + 2 + 16           -- cells 0,1,4

def L4 : Level :=
  { floor := l4floor, goal := l4goal,
    recipes := [⟨plusRing, .shrink⟩, ⟨vline, .open6⟩],
    boxes := [⟨.vert, 20, 31⟩], tp := [], pads := [(34, 23)] }

def l4init : St :=
  { blk := ⟨25, 37, 4, .down⟩, panel := 0, gates := [false], status := .playing, pads := [false] }

/-! ## level 5 data (read off the level-5 frames) -/

def l5floor (g : List Bool) (r c : Nat) : Bool :=
  (inR 25 r 40 && inR 13 c 28)                       -- left region (start)
  || (inR 13 r 24 && inR 21 c 22)                     -- stalk under box1 (12-interior)
  || (gate g 0 && inR 33 r 36 && inR 29 c 31)         -- colour-12 barrier (opened by box1)
  || (inR 33 r 36 && inR 32 c 36)                     -- gap between the regions
  || (inR 25 r 40 && inR 37 c 52)                     -- right region
  || (inR 21 r 24 && inR 45 c 46)                     -- vertical stalk up to the upper area
  || (inR 15 r 20 && inR 41 c 48)                     -- upper area
  || (inR 15 r 16 && inR 49 c 54)                     -- horizontal stalk to box2 (13-interior)
  || (inR 14 r 20 && inR 33 c 36)                     -- pocket (11-marked teleport square)
  || (gate g 1 && inR 11 r 13 && inR 33 c 36)         -- colour-13 barrier (opened by box2)
  || (inR 5 r 10 && inR 33 c 36)                      -- corridor up to the socket

def l5goal (r c : Nat) : Bool := inR 1 r 4 && inR 33 c 36

def L5 : Level :=
  { floor := l5floor, goal := l5goal,
    recipes := [⟨plusRing, .shrink⟩, ⟨tpMask, .teleport⟩, ⟨vline, .open6⟩],
    boxes := [⟨.vert, 24, 21⟩, ⟨.horiz, 15, 49⟩],
    -- 2x2 -> 15-pad (observed on L5); 4x4 -> 11-framed square (L2 analogy, NOT observed on L5)
    tp := [(2, 37, 15), (4, 17, 33)],
    pads := [(37, 49)] }

def l5init : St :=
  { blk := ⟨29, 17, 4, .down⟩, panel := 0, gates := [false, false], status := .playing, pads := [false] }

/-- attempt-1 candidate open condition, kept for the record (now subsumed by `ocVert`) -/
def ocCand (stalkCol stalkBottom : Nat) (b : Blk) : Bool :=
  b.col == stalkCol && b.row == stalkBottom + 1 && b.face == .up

end L5e
