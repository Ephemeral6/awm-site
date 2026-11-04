p = 'lean/L5eModel.lean'
s = open(p, encoding='utf-8').read()

s = s.replace("""  * Refill pads (`Level.pads`): a 2x2 that steps exactly onto an unused 14-pad consumes it (+refill to the bar).
-/""", """  * Refill pads (`Level.pads`): a 2x2 that steps exactly onto an unused 14-pad consumes it (+refill to the bar).

Attempt-3 amendment (attempt-2 sources kept in work/*.attempt2.lean):
  * The plus-ring effect is a size TOGGLE: on a 4x4 it shrinks (top-left kept, as before); on a 2x2 it grows
    to 4x4 (`growTo`): top row = old top - 2 (old bottom row kept), left column = the first of
    l-2, l-1, l whose 4x4 square is all floor; no fit -> no change (that last branch is an assumption).
    Observed on L5: (37,15) -> (35,13) on the 15-pad; (17,33) -> (15,33) in the pocket.
-/""")

s = s.replace("""/-- R-fire, one branch per effect kind. -/
def applyEffect (L : Level) (s : St) : Effect → St
  | .shrink => if s.blk.size == 4 then { s with blk := { s.blk with size := 2 } } else s""",
"""/-- R-grow placement (attempt 3): new top-left for a 2x2 at (t, l) growing to 4x4, or none if nothing fits -/
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
  | .shrink => sizeToggle L s""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
