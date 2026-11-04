p = 'lean/L5eModel.lean'
s = open(p, encoding='utf-8').read()

s = s.replace("""    Observed on L5: (37,15) -> (35,13) on the 15-pad; (17,33) -> (15,33) in the pocket.
-/""", """    Observed on L5: (37,15) -> (35,13) on the 15-pad; (17,33) -> (15,33) in the pocket.

Attempt-4 amendments (attempt-3 sources kept in work/*.attempt3.lean):
  * R-move sweeps: the block advances k = 1..size cells while each square stays on floor and stops at the
    last one that fits (partial move; L5 tid 891d9c73: 4x4 r15 c43 -> c45). A square touching the socket
    interior wins. If not even k = 1 fits, the move is blocked but the block still TURNS to face d
    (L5 tid 8e11f274).
  * R-refill: a pad is consumed when its 2x2 lies inside the block's new square, aligned to the block's
    2x2 sub-grid, for either block size (L5: 4x4 at r37 c49 consumed the pad at r37 c49, refill 10 units).
  * L5 floor: an opened box's area becomes floor (observed L4/L5 frames: box cells -> colour 2).
-/""")

s = s.replace("""def usePads : List (Nat × Nat) → List Bool → Nat → Nat → Nat → List Bool
  | p :: ps, u :: us, sz, r, c => (u || (sz == 2 && p.1 == r && p.2 == c)) :: usePads ps us sz r c
  | _, us, _, _, _ => us""", """def padHit (p : Nat × Nat) (sz r c : Nat) : Bool :=
  r ≤ p.1 && c ≤ p.2 && p.1 + 2 ≤ r + sz && p.2 + 2 ≤ c + sz && (p.1 - r) % 2 == 0 && (p.2 - c) % 2 == 0

def usePads : List (Nat × Nat) → List Bool → Nat → Nat → Nat → List Bool
  | p :: ps, u :: us, sz, r, c => (u || padHit p sz r c) :: usePads ps us sz r c
  | _, us, _, _, _ => us""")

s = s.replace("""/-- R-move (+ R-win). Win is checked before blocking (L2: the winning target overlapped non-floor). -/
def moveRule (L : Level) (s : St) (d : Dir) : St :=
  match target s.blk d with
  | none => s
  | some (r, c) =>
    let nb : Blk := { s.blk with row := r, col := c, face := d }
    if (cells r c s.blk.size).any (fun p => L.goal p.1 p.2) then
      { s with blk := nb, status := .won }
    else if (cells r c s.blk.size).all (fun p => L.floor s.gates p.1 p.2) then
      { s with blk := nb, pads := usePads L.pads s.pads s.blk.size r c }
    else s""", """/-- top-left after advancing k cells in direction d (none if it would leave the grid) -/
def offset (b : Blk) (d : Dir) (k : Nat) : Option (Nat × Nat) :=
  match d with
  | .up => if k ≤ b.row then some (b.row - k, b.col) else none
  | .down => some (b.row + k, b.col)
  | .left => if k ≤ b.col then some (b.row, b.col - k) else none
  | .right => some (b.row, b.col + k)

/-- sweep k = 1, 2, … : `.inl p` = a square touching the goal was reached at p (win);
    `.inr last` = the last square that fitted (none: not even k = 1 fits). -/
def sweep (L : Level) (g : List Bool) (b : Blk) (d : Dir) : Nat → Nat → Option (Nat × Nat) →
    Sum (Nat × Nat) (Option (Nat × Nat))
  | 0, _, last => .inr last
  | fuel + 1, k, last =>
    match offset b d k with
    | none => .inr last
    | some (r, c) =>
      if (cells r c b.size).any (fun p => L.goal p.1 p.2) then .inl (r, c)
      else if (cells r c b.size).all (fun p => L.floor g p.1 p.2) then sweep L g b d fuel (k + 1) (some (r, c))
      else .inr last

/-- R-move (+ R-win, R-refill, R-turn), amended in attempt 4: partial moves and turning when blocked. -/
def moveRule (L : Level) (s : St) (d : Dir) : St :=
  match sweep L s.gates s.blk d s.blk.size 1 none with
  | .inl (r, c) => { s with blk := { s.blk with row := r, col := c, face := d }, status := .won }
  | .inr (some (r, c)) =>
    { s with blk := { s.blk with row := r, col := c, face := d },
             pads := usePads L.pads s.pads s.blk.size r c }
  | .inr none => { s with blk := { s.blk with face := d } }""")

s = s.replace("""  || (inR 5 r 10 && inR 33 c 36)                      -- corridor up to the socket

def l5goal""", """  || (inR 5 r 10 && inR 33 c 36)                      -- corridor up to the socket
  || (gate g 0 && inR 9 r 12 && inR 20 c 23)          -- box1 area once opened (attempt 4)
  || (gate g 1 && inR 14 r 17 && inR 55 c 58)         -- box2 area once opened (attempt 4)

def l5goal""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
