import Game.L4MacroCert
namespace L4M

def lookup (s : MSt) : Option Nat :=
  if s.x < 64 then ((bucket s.x).find? (fun p => p.1 == s)).map (·.2) else none

/-- Certificate condition for one entry (s, d): every action affordable from cost d is not a win,
    and leads to a certified state whose recorded cost is at most d + cost. -/
def okEntry (p : MSt × Nat) : Bool :=
  acts.all fun a => decide (19 < p.2 + cost a) ||
    (match stepM p.1 a with
     | none => false
     | some s' => match lookup s' with
       | some d' => decide (d' ≤ p.2 + cost a)
       | none => false)

def chunk (x : Nat) : Nat → List (MSt × Nat)
  | 0 => (bucket x).take 60
  | 1 => ((bucket x).drop 60).take 60
  | 2 => ((bucket x).drop 120).take 60
  | _ => (bucket x).drop 180
end L4M
