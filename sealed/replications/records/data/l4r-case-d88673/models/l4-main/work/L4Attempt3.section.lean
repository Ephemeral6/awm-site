
/-! ## Attempt 3 amendment: facing, e-marker pickup, counter with refill and cap

Changes (everything above is kept; the new step reuses `moveRule` and `fireRule`):
* slot `face : Dir` restored (attempt 1 dropped it to `up`, but the pickup rule now reads the front half);
* slot `picked : Bool` (the single e marker, lattice cells (16,11) and (17,11), is consumed once);
* rule PICKUP (observed attempt 3: 2x2 onto it refilled; attempt 1: 4x4 covering it with its front half
  elsewhere did not). Unknown which of "small size" / "front half" triggers it: the model fires on EITHER;
* rule REFILL: counter u := min 7 (u + cost - 10, floored at 0) (lower of the two fitting readings 'set to 7'
  and 'minus 10'; observed 17 -> 7);
* rule RESIZE (amended, observed anchors): shrink keeps top-left (5 observations); grow keeps the bottom row,
  extends right if free else left (2 observations); only if both are walled may it pick any free placement;
* BUDGET premise (from the fit B = 18): an action may START only while u ≤ cap; cap is a parameter of `runB`.
  A macro (pattern) is allowed to start at u ≤ cap even though its later clicks would exceed it (looser).
-/

structure St3 where
  i : Nat
  j : Nat
  big : Bool
  face : Dir
  door : Bool
  picked : Bool
deriving DecidableEq, Repr

inductive Out3 | win | st (s : St3) (newly : Bool)
deriving DecidableEq, Repr

def toSt (s : St3) : St := { i := s.i, j := s.j, big := s.big, up := s.face == Dir.up, door := s.door }

def isE (i j : Nat) : Bool := (i == 16 || i == 17) && j == 11

/-- PICKUP trigger (union of the two hypotheses). -/
def triggers (i j : Nat) (big : Bool) (face : Dir) : Bool :=
  if !big then isE i j
  else match face with
    | .up => isE i j || isE i (j+1)
    | .down => isE (i+1) j || isE (i+1) (j+1)
    | .left => isE i j || isE (i+1) j
    | .right => isE i (j+1) || isE (i+1) (j+1)

def settle3 (s : St3) (i j : Nat) (big : Bool) (face : Dir) (door : Bool) : Out3 :=
  .st { i := i, j := j, big := big, face := face, door := door, picked := s.picked || triggers i j big face }
    (!s.picked && triggers i j big face)

def growOk (door : Bool) (i j : Nat) : Bool := !rectBlocked door true i j

/-- RESIZE with the observed anchors. -/
def resize3 (s : St3) (q : Fin 4) : Out3 :=
  if s.big then
    (if q.val == 0 then settle3 s s.i s.j false s.face s.door else .st s false)
  else
    let qi := q.val / 2
    let qj := q.val % 2
    let upR := decide (1 ≤ s.i) && growOk s.door (s.i - 1) s.j
    let upL := decide (1 ≤ s.i) && decide (1 ≤ s.j) && growOk s.door (s.i - 1) (s.j - 1)
    let allowed := if upR then qi == 1 && qj == 0 else if upL then qi == 1 && qj == 1 else true
    if !allowed || decide (s.i < qi) || decide (s.j < qj) then .st s false
    else if rectBlocked s.door true (s.i - qi) (s.j - qj) then .st s false
    else if rectGoal true (s.i - qi) (s.j - qj) then .win
    else settle3 s (s.i - qi) (s.j - qj) true s.face s.door

def step3 (s : St3) : Act → Out3
  | .move d => match moveRule (toSt s) d with
    | .win => .win
    | .st s' => settle3 s s'.i s'.j s'.big d s'.door
  | .resize q => resize3 s q
  | .fire => match fireRule (toSt s) with
    | .win => .win
    | .st s' => .st { s with door := s'.door } false

/-- REFILL / counter update. -/
def nu (u : Nat) (a : Act) (newly : Bool) : Nat :=
  if newly then (if u + cost a ≤ 10 then 0 else min 7 (u + cost a - 10)) else u + cost a

/-- Run with a budget cap: an action is taken only if it starts with counter ≤ cap. -/
def runB (cap : Nat) (s : St3) (u : Nat) : List Act → Bool
  | [] => false
  | a :: as => if u > cap then false else match step3 s a with
    | .win => true
    | .st s' n => runB cap s' (nu u a n) as

def start3 : St3 := { i := 12, j := 18, big := true, face := .down, door := false, picked := false }

/-! Certificate: g s = least counter from which no win is possible (cap 18), found by work/model_l4b.py,
    checked here against `step3`. -/
def gtab : Nat := @GT@

def dirIx : Dir → Nat | .up => 0 | .down => 1 | .left => 2 | .right => 3

def key3 (s : St3) : Nat :=
  ((((s.i * 32 + s.j) * 2 + (if s.big then 1 else 0)) * 4 + dirIx s.face) * 2 + (if s.door then 1 else 0)) * 2
    + (if s.picked then 1 else 0)

def g (s : St3) : Nat := (gtab >>> (5 * key3 s)) % 32

def valid3 (s : St3) : Bool := decide (s.i < 32) && decide (s.j < 32)

def ok3 (s : St3) (a : Act) : Bool :=
  if g s > 18 then true else
  match step3 s a with
  | .win => false
  | .st s' n => valid3 s' && decide (g s' ≤ nu (g s) a n)

def dirs : List Dir := [.up, .down, .left, .right]

def okState3 (s : St3) : Bool := allActs.all (ok3 s)

def okRow3 (i : Nat) : Bool :=
  (List.range 32).all fun j => bools.all fun b => dirs.all fun f => bools.all fun d => bools.all fun p =>
    okState3 { i := i, j := j, big := b, face := f, door := d, picked := p }

@CHUNKS@

theorem okRow3_aux (lo : Nat) (h : ((List.range 4).map (· + lo)).all okRow3 = true)
    (k : Nat) (h1 : lo ≤ k) (h2 : k < lo + 4) : okRow3 k = true := by
  rw [List.all_eq_true] at h
  exact h k (List.mem_map.mpr ⟨k - lo, List.mem_range.mpr (by omega), by omega⟩)

theorem okRow3_all (k : Nat) (hk : k < 32) : okRow3 k = true := by
@DISPATCH@

theorem mem_dirs (d : Dir) : d ∈ dirs := by cases d <;> simp [dirs]

theorem ok3_of_valid (s : St3) (hv : valid3 s = true) (a : Act) : ok3 s a = true := by
  have hv' : s.i < 32 ∧ s.j < 32 := by simpa [valid3] using hv
  have hr := okRow3_all s.i hv'.1
  simp only [okRow3, List.all_eq_true, List.mem_range] at hr
  have h := hr s.j hv'.2 s.big (mem_bools _) s.face (mem_dirs _) s.door (mem_bools _) s.picked (mem_bools _)
  have h2 : okState3 s = true := by cases s; exact h
  simp only [okState3, List.all_eq_true] at h2
  exact h2 a (mem_allActs a)

theorem nu_mono (u v : Nat) (a : Act) (n : Bool) (h : u ≤ v) : nu u a n ≤ nu v a n := by
  unfold nu
  cases n
  · simp only [Bool.false_eq_true, if_false]; omega
  · simp only [if_true]
    split <;> split <;> omega

/-- Invariant: from a valid state whose counter is at least g, no action list wins under cap 18. -/
theorem no_win_from (as : List Act) : ∀ s u, valid3 s = true → g s ≤ u → runB 18 s u as = false := by
  induction as with
  | nil => intro s u _ _; rfl
  | cons a as ih =>
    intro s u hv hg
    by_cases hu : u > 18
    · simp [runB, hu]
    · have hok := ok3_of_valid s hv a
      have hgs : ¬ g s > 18 := by omega
      unfold ok3 at hok
      simp only [hgs, if_false] at hok
      simp only [runB, hu, if_false]
      cases hs : step3 s a with
      | win => rw [hs] at hok; simp at hok
      | st s' n =>
        rw [hs] at hok
        simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
        exact ih s' (nu u a n) hok.1 (Nat.le_trans hok.2 (nu_mono _ _ a n hg))

theorem g_start : g start3 = 0 := by decide
theorem valid_start3 : valid3 start3 = true := by decide

/-- MAIN (attempt 3). With the level-4 budget (an action may start only while at most 18 units are used),
    no list of model actions wins level 4 from its start, even with the refill and the most generous
    reading of its unknowns. -/
theorem l4_unwinnable_with_refill (as : List Act) : runB 18 start3 0 as = false :=
  no_win_from as start3 0 valid_start3 (by rw [g_start]; exact Nat.le_refl 0)

/-- Non-vacuity / minimal relaxation: raising the cap by ONE unit (19) admits a win. -/
def witness3 : List Act :=
  [.move .left, .move .left, .move .left, .move .down, .move .down, .resize 0, .move .left, .move .down,
   .resize 2, .move .right, .move .right, .move .up, .fire,
   .move .right, .move .right, .move .right, .move .right, .move .right, .move .right]

theorem witness3_wins_cap19 : runB 19 start3 0 witness3 = true := by decide

/-- The pickup rule is live: a 2x2 stepping onto the marker picks it up (attempt-3 observation). -/
theorem pickup_happens :
    step3 { start3 with i := 16, j := 12, big := false, face := .down } (.move .left) =
      .st { start3 with i := 16, j := 11, big := false, face := .left, picked := true } true := by decide

/-- ... and a 4x4 covering it with its front half elsewhere does not (attempt-1 observation). -/
theorem big_cover_no_pickup :
    step3 { start3 with i := 16, j := 12, face := .left } (.move .left) =
      .st { start3 with i := 16, j := 10, face := .left } false := by decide
