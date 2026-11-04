import Skeleton2
/-!
# Level-4 model (attempt 1).  Computation layer: objects, rules, step.  No Limits import.

Coordinates are frame pixels.  Attempt 2 amendment: the row `y` and the facing `face` are now slots,
because the 6-commit was observed (attempt 2 animation) to FIRE A SHOT in the facing direction, so the
6-effect condition `fires` may read them.  Moves left/right still ignore rows (looser than the game).

Objects / slots
* `small`  : piece edge 2 (true) or 4 (false)                 -- rule R_shrink reads/writes
* `opened` : d-door cells (cols 45-47) are floor               -- R_right, R_line read/write
* `won`    : level finished                                    -- goal
* `x`      : left column of the piece                          -- all moves, R_line (via `fires`)
* `y`      : top row of the piece (attempt 2)                   -- R_up/R_down, `fires`
* `face`   : side of the 9-half (attempt 2)                     -- set by every move, read by `fires`
* `dP,dL`  : Hamming distance of the panel selection to the two legend patterns
             PLUS={(0,1),(1,0),(1,2),(2,1)} and LINE={(0,1),(1,1),(2,1)} (abstraction of the 9-bit panel)
-/
namespace L4
open Skeleton2

inductive Dir | U | D | L | R
  deriving DecidableEq, Repr

structure St where
  small : Bool
  opened : Bool
  won : Bool
  x : Nat
  dP : Nat
  dL : Nat
  y : Nat
  face : Dir
  deriving DecidableEq, Repr

/-- `left`/`right`/`up`/`down` = ACTION3/4/1/2; `noop` = clicks off the panel;
    `click upP upL` = a panel click: it moves the selection one cell, so each distance goes up or down by 1. -/
inductive Act where
  | left
  | right
  | up
  | down
  | noop
  | click (upP upL : Bool)
  deriving DecidableEq, Repr

def size (s : St) : Nat := if s.small then 2 else 4

/-- R_left: slide one piece-length left, blocked (no move) at the region wall col 21. -/
def rLeft (s : St) : St := if 21 + size s ≤ s.x then { s with x := s.x - size s, face := .L } else { s with face := .L }

/-- R_up / R_down: slide one piece-length inside the region rows 21..36 (looser: columns ignored). -/
def rUp (s : St) : St := if 21 + size s ≤ s.y then { s with y := s.y - size s, face := .U } else { s with face := .U }
def rDown (s : St) : St := if s.y + 2 * size s ≤ 37 then { s with y := s.y + size s, face := .D } else { s with face := .D }

/-- R_right: win_touch if the door is open and the full-step box reaches col 57 (x + 2·size ≥ 58);
    else slide one piece-length if the new box stays left of the wall (44 closed door / 56 corridor end). -/
def rRight (s : St) : St :=
  if s.opened && decide (58 ≤ s.x + 2 * size s) then { s with won := true }
  else if s.x + 2 * size s ≤ (if s.opened then 57 else 45) then { s with x := s.x + size s, face := .R }
  else { s with face := .R }

/-- R_click (+ R_commit): toggle; a selection equal to PLUS commits shrink (keeps top-left, so x is kept);
    equal to LINE commits the 6-effect, which opens the door iff `fires s`.  Commit clears the panel.
    `grow` = what PLUS does to an already small piece (untested; theorem assumes `grow = false`).
    Abstract clicks violating the triangle inequality |dP-dL| ≤ 3 do not exist in the game -> `.reset` (dead). -/
def rClick (fires : St → Bool) (grow : Bool) (s : St) (upP upL : Bool) : Res St :=
  let p := if upP then s.dP + 1 else s.dP - 1
  let l := if upL then s.dL + 1 else s.dL - 1
  if p ≤ l + 3 && l ≤ p + 3 then
    if p = 0 then .ok { s with small := (if s.small then !grow else true), dP := 4, dL := 3 }
    else if l = 0 then .ok { s with opened := s.opened || fires s, dP := 4, dL := 3 }
    else .ok { s with dP := p, dL := l }
  else .reset

def step (fires : St → Bool) (grow : Bool) (s : St) : Act → Res St
  | a => if s.won then .ok s else
    match a with
    | .left => .ok (rLeft s)
    | .right => .ok (rRight s)
    | .up => .ok (rUp s)
    | .down => .ok (rDown s)
    | .noop => .ok s
    | .click u v => rClick fires grow s u v

def goal (s : St) : Bool := s.won

/-- Level-4 start: 4x4 piece, left col 37, door closed, empty panel. -/
def s0 : St := { small := false, opened := false, won := false, x := 37, dP := 4, dL := 3, y := 25, face := .D }

/-- Reachability invariant: a 4x4 piece sits on the 4-lattice x ≡ 1 (mod 4); selection triangle inequality. -/
def Inv (s : St) : Prop := (s.small = false → s.x % 4 = 1) ∧ s.dP ≤ s.dL + 3 ∧ s.dL ≤ s.dP + 3

/-- Potential = lower bound on the actions still needed. -/
def dist31 (x : Nat) : Nat := (x - 31) + (31 - x)
def Φ (s : St) : Nat :=
  if s.won then 0
  else if s.opened then (if s.small then (54 - s.x + 1) / 2 + 1 else (50 - s.x + 3) / 4 + 1)
  else if s.small then s.dL + (dist31 s.x + 1) / 2 + 13
  else s.dP + 3 + (dist31 s.x + 3) / 4 + 13

end L4
