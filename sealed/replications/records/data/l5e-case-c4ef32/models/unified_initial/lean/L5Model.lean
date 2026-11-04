import L5Data
/-!
# L5Model — the formal model of level 5 (definitions only)

Objects (see work/model/rules.py for the executable twin and work/limits_table.json):
* `St`    the board state: block position (half-pixel indices; pixel = 2*i+1), size, facing,
          the two gates (switch box present ⇔ barrier closed, merged into one Bool each: transform T2),
          and whether the refill pad is still available.
* `Act`   the macro actions: a move, a size toggle with a chosen quadrant, a shot, a teleport.
          Panel clicks are folded into these macros (transform T1): a power costs |pattern| clicks,
          the firing click costing 2, so diamond = 5, line = 4, teleport = 4.

Model choices that are NOT established by observation are marked ASSUMPTION; choices that make the
model *looser* than what was observed are marked SUPERSET.
-/
namespace L5

inductive Dir | U | D | L | R
  deriving DecidableEq, Repr

inductive Quad | tl | tr | bl | br
  deriving DecidableEq, Repr

def Quad.dy : Quad → Nat | .tl => 0 | .tr => 0 | .bl => 2 | .br => 2
def Quad.dx : Quad → Nat | .tl => 0 | .tr => 2 | .bl => 0 | .br => 2

structure St where
  r  : Fin 32
  c  : Fin 32
  big : Bool
  f  : Dir
  oc : Bool
  od : Bool
  ep : Bool
  deriving DecidableEq, Repr

inductive Act
  | move (d : Dir)
  | shrink (q : Quad)
  | grow (q : Quad)
  | shot
  | tele
  deriving DecidableEq, Repr

def Act.cost : Act → Nat
  | .move _ => 1 | .shrink _ => 5 | .grow _ => 5 | .shot => 4 | .tele => 4

/-- all 14 macro actions -/
def allActs : List Act :=
  [.move .U, .move .D, .move .L, .move .R,
   .shrink .tl, .shrink .tr, .shrink .bl, .shrink .br,
   .grow .tl, .grow .tr, .grow .bl, .grow .br, .shot, .tele]

theorem mem_allActs (a : Act) : a ∈ allActs := by
  cases a with
  | move d => cases d <;> simp [allActs]
  | shrink q => cases q <;> simp [allActs]
  | grow q => cases q <;> simp [allActs]
  | shot => simp [allActs]
  | tele => simp [allActs]

/-! ## geometry -/

def px (i : Fin 32) : Nat := 2 * i.val + 1
def half (p : Nat) : Fin 32 := ⟨(p / 2) % 32, Nat.mod_lt _ (by decide)⟩
def St.n (s : St) : Nat := if s.big then 4 else 2
def St.y (s : St) : Nat := px s.r
def St.x (s : St) : Nat := px s.c

/-- walkable mask for the current gates -/
def wmask (oc od : Bool) : Nat := W0 ||| (if oc then WC else 0) ||| (if od then WD else 0)
/-- shot-passable mask: barriers are transparent to shots (SUPERSET: barrier/shot interaction
    was only seen once, on L3, where the shot stopped inside a closed barrier). -/
def pmask : Nat := W0 ||| WC ||| WD

def cell (m y x : Nat) : Bool := y < 64 && x < 64 && ((m >>> (y * 64 + x)) &&& 1) == 1
def rowOk (m y x n : Nat) : Bool :=
  y < 64 && x + n ≤ 64 && ((m >>> (y * 64 + x)) &&& (2 ^ n - 1)) == 2 ^ n - 1
/-- every cell of the n×n footprint at (y,x) is set in m -/
def fits (m y x n : Nat) : Bool := (List.range n).all (fun i => rowOk m (y + i) x n)

def overlap (y x n r0 r1 c0 c1 : Nat) : Bool := y ≤ r1 && r0 < y + n && x ≤ c1 && c0 < x + n

/-! ## rules -/

/-- the target of a `k`-pixel step in direction `d` from pixel (y,x) (none if it leaves the board) -/
def target (d : Dir) (y x n : Nat) : Option (Nat × Nat) :=
  match d with
  | .U => if n ≤ y then some (y - n, x) else none
  | .D => some (y + n, x)
  | .L => if n ≤ x then some (y, x - n) else none
  | .R => some (y, x + n)

/-- the first `k`-pixel step of a move, if the whole footprint fits there -/
def tryStep (s : St) (d : Dir) (k : Nat) : Option (Nat × Nat) :=
  match target d s.y s.x k with
  | none => none
  | some (ty, tx) => if fits (wmask s.oc s.od) ty tx s.n then some (ty, tx) else none

/-- R1 move (revised attempt 5): the move advances in 2-pixel sub-steps and stops at the last free one.
    A 2×2 has one sub-step (all or nothing); a 4×4 that cannot make its full 4-pixel step still makes a
    2-pixel step if that one fits (observed: 4×4 at (17,33) pressing up against the closed d barrier
    ended at (15,33)).  The facing is set to `d` in every case (attempt 2). -/
def ruleMove (s : St) (d : Dir) : St :=
  match tryStep s d s.n with
  | some (ty, tx) => { s with r := half ty, c := half tx, f := d }
  | none =>
    if s.big then
      match tryStep s d 2 with
      | some (ty, tx) => { s with r := half ty, c := half tx, f := d }
      | none => { s with f := d }
    else { s with f := d }

/-- R2a shrink.  Observed 3× (facing up): quadrant tl.  SUPERSET: any quadrant. -/
def ruleShrink (s : St) (q : Quad) : St :=
  if s.big then { s with big := false, r := half (s.y + q.dy), c := half (s.x + q.dx) } else s

/-- R2b grow.  Observed twice (facing right): quadrant br, i.e. 4×4 at (y-2,x-2).  SUPERSET: any quadrant.
    Growing fails (no change, the power is still paid) unless the new 4×4 footprint is walkable
    (attempt 2: 2×2 in the d-stem at (21,45), diamond fired, block flashed and stayed 2×2). -/
def ruleGrow (s : St) (q : Quad) : St :=
  if !s.big && q.dy ≤ s.y && q.dx ≤ s.x && fits (wmask s.oc s.od) (s.y - q.dy) (s.x - q.dx) 4 then
    { s with big := true, r := half (s.y - q.dy), c := half (s.x - q.dx) }
  else s

/-- first non-passable cell going up from row y-1 to row 0 in column x -/
def scanUp (x : Nat) : Nat → Option (Nat × Nat)
  | 0 => none
  | y + 1 => if cell pmask y x then scanUp x y else some (y, x)
def scanDown (x : Nat) (y : Nat) : Nat → Option (Nat × Nat)
  | 0 => none
  | k + 1 => if cell pmask y x then scanDown x (y + 1) k else some (y, x)
def scanRight (y : Nat) (x : Nat) : Nat → Option (Nat × Nat)
  | 0 => none
  | k + 1 => if cell pmask y x then scanRight y (x + 1) k else some (y, x)
def scanLeft (y : Nat) (x : Nat) : Nat → Option (Nat × Nat)
  | 0 => none
  | k + 1 => if cell pmask y (x - 1) then scanLeft y (x - 1) k else some (y, x - 1)

/-- the probe lines of a shot.  Up: the block's left column only (established: L3 hit, L4 miss).
    Down/Left/Right: every column/row of the block (SUPERSET). -/
def probes (s : St) : List (Option (Nat × Nat)) :=
  let y := s.y; let x := s.x; let n := s.n
  match s.f with
  | .U => [scanUp x y]
  | .D => (List.range n).map (fun i => scanDown (x + i) (y + n) (47 - (y + n)))
  | .L => (List.range n).map (fun i => scanLeft (y + i) x (x - 10))
  | .R => (List.range n).map (fun i => scanRight (y + i) (x + n) (60 - (x + n)))

def hitC : Option (Nat × Nat) → Bool
  | some (y, x) => overlap y x 1 9 12 20 23
  | none => false
def hitD : Option (Nat × Nat) → Bool
  | some (y, x) => overlap y x 1 14 17 55 58
  | none => false

/-- R3 shot: a hit on a present switch box removes it and opens the barrier of its colour. -/
def ruleShot (s : St) : St :=
  let ps := probes s
  { s with oc := s.oc || ps.any hitC, od := s.od || ps.any hitD }

/-- R4 teleport: 4×4 → reticle interior (17,33); 2×2 → f-pad (37,15) (observed once). -/
def ruleTele (s : St) : St :=
  if s.big then { s with r := half 17, c := half 33 } else { s with r := half 37, c := half 15 }

/-- R5 refill pad (post-condition of every action): consumed when the footprint overlaps it. -/
def post (s : St) : St :=
  if s.ep && overlap s.y s.x s.n 37 38 49 50 then { s with ep := false } else s

def raw (s : St) : Act → St
  | .move d => ruleMove s d
  | .shrink q => ruleShrink s q
  | .grow q => ruleGrow s q
  | .shot => ruleShot s
  | .tele => ruleTele s

def step (s : St) (a : Act) : St := post (raw s a)

/-- R6 win: the footprint overlaps the goal box (rows 0-4, cols 32-37). -/
def win (s : St) : Bool := overlap s.y s.x s.n 0 4 32 37

def start : St := { r := half 29, c := half 17, big := true, f := .D, oc := false, od := false, ep := true }

/-! ## runs and the budget (R7) -/

/-- the run ends at its first win: every earlier action must not win -/
def endsInWin : St → List Act → Prop
  | _, [] => False
  | s, [a] => win (step s a) = true
  | s, a :: b :: rest => win (step s a) = false ∧ endsInWin (step s a) (b :: rest)

/-- cost of every action except the last one -/
def prefixCost : St → List Act → Nat
  | _, [] => 0
  | _, [_] => 0
  | s, a :: b :: rest => a.cost + prefixCost (step s a) (b :: rest)

/-- refill still available in the state from which the last action is taken -/
def lastEp : St → List Act → Bool
  | s, [] => s.ep
  | s, [_] => s.ep
  | s, a :: b :: rest => lastEp (step s a) (b :: rest)

/-- R7 budget (fit: B = 35 per level, every action 1 unit, a firing click 2; refill +10 once;
    an action may still be taken at net spend 35 — L4 was won from rem 0, L5 ended from rem 0).
    The run is affordable iff the net spend before the last action is ≤ 35, i.e.
    prefixCost ≤ 35 + 10·[refill taken], i.e. prefixCost + 10·[refill still available] ≤ 45
    (start has the refill available). -/
def affordable (s : St) (as : List Act) : Prop :=
  prefixCost s as + 10 * (if lastEp s as then 1 else 0) ≤ 45

end L5
