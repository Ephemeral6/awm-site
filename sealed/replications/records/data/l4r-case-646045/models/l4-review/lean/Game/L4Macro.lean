/-!
# Level-4 macro model (attempt 4 amendment of the L4 formal system)

Refines `Game/L4Model.lean` with what attempt 4 established:
* pixel geometry of level 4 (region, stem, former 6-box, door, corridor, goal box);
* moves slide up to one piece-length and stop at the last free position (clamp, seen on L1);
* PLUS on a 4x4 shrinks keeping the top-left; PLUS on a 2x2 GROWS to a 4x4 shifted by (-2,-2)
  (attempt 4).  Grow is modelled LOOSER than observed: allowed anywhere on the 64x64 board;
* LINE fires a shot; the door opens iff the piece's left column is 31 and it faces up (H1'',
  confirmed attempt 4: 2x2 at x31 facing up opened it; five other configurations did not);
* win_touch: a move whose full-step box overlaps the goal box (rows 28-33, cols 57-62) wins.
Panel clicks are folded into macro actions: `plus` costs 4 actions, `line` costs 3 (a commit needs
|pattern| paid clicks since the last commit; clicks in between do not change the board).
Free actions (off-panel clicks, legend clicks) change nothing on the board and cost nothing: omitted.
-/
namespace L4M

structure MSt where
  small : Bool
  opened : Bool
  y : Nat
  x : Nat
  face : Nat      -- 0 U, 1 D, 2 L, 3 R
  deriving DecidableEq, Repr

inductive MAct | up | down | left | right | plus | line
  deriving DecidableEq, Repr

def cost : MAct → Nat
  | .plus => 4
  | .line => 3
  | _ => 1

def walk (r c : Nat) (o : Bool) : Bool :=
  (21 ≤ r && r ≤ 36 && 21 ≤ c && c ≤ 44) ||
  (9 ≤ r && r ≤ 20 && 31 ≤ c && c ≤ 32) ||
  (o && 5 ≤ r && r ≤ 8 && 30 ≤ c && c ≤ 33) ||
  (o && 29 ≤ r && r ≤ 32 && 45 ≤ c && c ≤ 47) ||
  (29 ≤ r && r ≤ 32 && 48 ≤ c && c ≤ 56)

def valid (y x s : Nat) (o : Bool) : Bool :=
  (List.range s).all fun i => (List.range s).all fun j => walk (y + i) (x + j) o

def hit (y x s : Nat) : Bool :=
  (List.range s).any fun i => (List.range s).any fun j =>
    28 ≤ y + i && y + i ≤ 33 && 57 ≤ x + j && x + j ≤ 62

/-- Is the piece box shifted k cells in direction `d` free? (off the top/left edge = not free) -/
def okAt (st : MSt) (s : Nat) (d k : Nat) : Bool :=
  match d with
  | 0 => decide (k ≤ st.y) && valid (st.y - k) st.x s st.opened
  | 1 => valid (st.y + k) st.x s st.opened
  | 2 => decide (k ≤ st.x) && valid st.y (st.x - k) s st.opened
  | _ => valid st.y (st.x + k) s st.opened

def hitAt (st : MSt) (s : Nat) (d : Nat) : Bool :=
  match d with
  | 0 => decide (s ≤ st.y) && hit (st.y - s) st.x s
  | 1 => hit (st.y + s) st.x s
  | 2 => decide (s ≤ st.x) && hit st.y (st.x - s) s
  | _ => hit st.y (st.x + s) s

/-- Slide: largest k ≤ s with every shift 1..k free. -/
def slide (st : MSt) (s d : Nat) : Nat :=
  if !okAt st s d 1 then 0
  else if s < 2 || !okAt st s d 2 then 1
  else if s < 3 || !okAt st s d 3 then 2
  else if s < 4 || !okAt st s d 4 then 3
  else 4

def moveTo (st : MSt) (d k : Nat) : MSt :=
  match d with
  | 0 => { st with y := st.y - k, face := 0 }
  | 1 => { st with y := st.y + k, face := 1 }
  | 2 => { st with x := st.x - k, face := 2 }
  | _ => { st with x := st.x + k, face := 3 }

def size (st : MSt) : Nat := if st.small then 2 else 4

/-- `none` = the level is won by this action. -/
def stepM (st : MSt) : MAct → Option MSt
  | .up => mv 0 | .down => mv 1 | .left => mv 2 | .right => mv 3
  | .plus =>
    if !st.small then some { st with small := true }
    else if 2 ≤ st.y && 2 ≤ st.x && st.y ≤ 62 && st.x ≤ 62 then
      some { st with small := false, y := st.y - 2, x := st.x - 2 }
    else some st
  | .line => some { st with opened := st.opened || (st.x == 31 && st.face == 0) }
where
  mv (d : Nat) : Option MSt :=
    if hitAt st (size st) d then none else some (moveTo st d (slide st (size st) d))

def s0 : MSt := { small := false, opened := false, y := 25, x := 37, face := 1 }

def acts : List MAct := [.up, .down, .left, .right, .plus, .line]

def totalCost : List MAct → Nat
  | [] => 0
  | a :: r => cost a + totalCost r

/-- Does some prefix of the action list win from `st`? -/
def wins : MSt → List MAct → Bool
  | _, [] => false
  | st, a :: r => match stepM st a with
    | none => true
    | some st' => wins st' r

end L4M
