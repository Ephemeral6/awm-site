import Game.L4Macro
/-!
# Level-4 budget model (attempt 6 amendment): composes the macro board state with the e-pickup flag.

Exact budget (fit to every bar reading of attempts 5 and 6: notches shown = ceil(remaining*32/18)):
bar = 18 units; a move or a non-committing click costs 1; the committing click costs 2
(so `plus` = 3 + 2 = 5, `line` = 2 + 2 = 4); the e-square pickup adds 10; the game ends when the
remaining budget goes below 0 (attempt 5: a commit from 1 left ended the game; attempt 6: an action
from 1 left to 0 still ran, the next one ended the game).

Pickup rule, modelled LOOSER than established: picked up when the 2x2 piece overlaps the e square
(established, attempt 6) OR when the piece's front half (the side it faces) overlaps it (H_front, untested).
A 4x4 covering e with its back half did not pick it up (attempts 2, 6) - consistent with both.
Budget check is also loose: an action is allowed if spent + cost ≤ 18 + 10·[e taken AFTER the action].
-/
namespace L4M

def onE (y x h w : Nat) : Bool :=
  (List.range h).any fun i => (List.range w).any fun j =>
    34 ≤ y + i && y + i ≤ 35 && 23 ≤ x + j && x + j ≤ 24

def front (st : MSt) : Bool :=
  let s := size st
  let h := s / 2
  match st.face with
  | 0 => onE st.y st.x h s
  | 1 => onE (st.y + h) st.x h s
  | 2 => onE st.y st.x s h
  | _ => onE st.y (st.x + h) s h

/-- Audit A1: the observed rule is narrower (pickup iff the piece's top-left is (33,23), 6 contacts); `pick` is the
    UNION of that rule with the earlier, looser candidates, so the model stays at least as permissive as the game. -/
def pick (st : MSt) : Bool := (st.small && onE st.y st.x 2 2) || front st || (st.y == 33 && st.x == 23)

/-- Composite state: board × pickup-taken flag. -/
abbrev BSt := MSt × Bool

def bcost : MAct → Nat
  | .plus => 5
  | .line => 4
  | _ => 1

def cap (e : Bool) : Nat := if e then 28 else 18

def stepB (st : BSt) (a : MAct) : Option BSt :=
  match stepM st.1 a with
  | none => none
  | some s' => some (s', st.2 || pick s')

/-- Does the play win from `st` with `spent` budget already used? -/
def winsB : BSt → List MAct → Nat → Bool
  | _, [], _ => false
  | st, a :: r, spent =>
    match stepB st a with
    | none => decide (spent + bcost a ≤ cap st.2)
    | some st' => if spent + bcost a ≤ cap st'.2 then winsB st' r (spent + bcost a) else false

def b0 : BSt := (s0, false)
end L4M
