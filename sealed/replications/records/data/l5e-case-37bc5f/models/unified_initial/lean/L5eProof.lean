/-
# L5eProof — amended in attempts 2 and 3

L4: the open condition is now a definition (`ocBox`), so the attempt-1 hypothesis `hoc` is gone.
    The winning plan is exactly the action list played in attempt 2, which won level 4.
    MAIN-THEOREM (L4): lean/L5eProof.lean : L5e.l4_winnable

Attempt 3: the plus-ring effect is a size toggle (grow added). With it, L5 HAS a winning line in logic
(l5Best_wins, 38 actions, 5 firing clicks) but under the measured level-5 costs it runs the bar out
(l5Best_dies, l5BestR_dies), even granting one free action in 8 (observed ~1 in 9). The bar would have to
be >= 149 cells (l5Best_dies_148 / l5Best_alive_149); it is 128.
MAIN-THEOREM (L5): lean/L5eProof.lean : L5e.l5Best_dies  -- covers these plans, not every action sequence.

Attempt-2 notes on L5 (kept):
  * l5_replay_matches / l5_replay_kinds: the model replays the 42 level-5 actions of attempt 2.
  * l5_small_teleport_misses_pocket: in the model, a 2x2 that fires the teleport lands on the 15-pad, so the
    model has no way to put a block into the pocket once it is 2x2 (no grow rule is known).
  * l5opt_plan_wins + l5opt_plan_dies / l5opt_direct_dies: even under the OPTIMISTIC assumption that a
    2x2 teleport lands in the pocket, the shortest plans I can build (with and without the refill pad) run
    the bar out under the measured level-5 costs. This is the gap, not an impossibility proof: it covers
    two plans, not all action sequences.
-/
import L5eModel

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace L5e

def mv (d : Dir) : Act := .move d
def ck (i : Nat) : Act := .click i

/-! ## 0. conformance: attempt-1 level-4 trajectory -/

/-- the level-4 actions sent in attempt 1 (all accepted; none swallowed) -/
def l4observed : List Act :=
  [mv .left, mv .left, mv .up,
   ck 1, ck 4, ck 7,  ck 1, ck 7, ck 4,  ck 1, ck 4, ck 7,
   mv .down, mv .down, mv .down, mv .left, mv .left,
   mv .right, mv .right, mv .up, mv .up, mv .up,
   ck 1, ck 3, ck 5, ck 7,
   mv .right, ck 1, ck 4, ck 7,
   mv .up]

/-- observed end state (tid 48b2f90905c5eecf): 2x2 at r19 c31 facing up, barrier closed, panel clear. -/
theorem l4_replay_matches :
    run L4 l4init l4observed =
      { blk := ⟨19, 31, 2, .up⟩, panel := 0, gates := [false], status := .playing, pads := [false] } := by
  decide +kernel

theorem l4_replay_kinds :
    (trace L4 l4init l4observed).2 =
      [.mv, .mv, .mv, .ck, .ck, .fire, .ck, .ck, .fire, .ck, .ck, .fire,
       .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv,
       .ck, .ck, .ck, .fire, .mv, .ck, .ck, .fire, .mv] := by
  decide +kernel

/-- the defined open condition agrees with every observed 6-fire:
    L3 (stalk c29, bottom r12): two failures, one success; L4 attempt 1: four failures;
    L4 attempt 2: success; L5 attempt 2: box1 (vertical) success, box2 (horizontal) success. -/
theorem ocBox_fits_observed_fires :
    ocBox ⟨.vert, 12, 29⟩ ⟨17, 37, 4, .down⟩ = false ∧ ocBox ⟨.vert, 12, 29⟩ ⟨25, 25, 4, .down⟩ = false ∧
    ocBox ⟨.vert, 12, 29⟩ ⟨13, 29, 4, .up⟩ = true ∧
    ocBox ⟨.vert, 20, 31⟩ ⟨21, 29, 4, .up⟩ = false ∧ ocBox ⟨.vert, 20, 31⟩ ⟨21, 31, 2, .right⟩ = false ∧
    ocBox ⟨.vert, 20, 31⟩ ⟨21, 31, 2, .up⟩ = true ∧
    ocBox ⟨.vert, 24, 21⟩ ⟨25, 21, 4, .up⟩ = true ∧ ocBox ⟨.horiz, 15, 49⟩ ⟨25, 21, 4, .up⟩ = false ∧
    ocBox ⟨.horiz, 15, 49⟩ ⟨15, 47, 2, .right⟩ = true ∧ ocBox ⟨.vert, 24, 21⟩ ⟨15, 47, 2, .right⟩ = false ∧
    -- attempt 3: in line with box2's stalk, facing it, but 12 columns away: no open
    ocBox ⟨.horiz, 15, 49⟩ ⟨15, 33, 4, .right⟩ = false := by
  decide

/-! ## 1. level 4: the plan (= the attempt-2 action list, which won level 4) -/

def plan : List Act :=
  [ck 1, ck 3, ck 5, ck 7,                 -- plus ring -> shrink to 2x2 at r25 c37
   mv .left, mv .left, mv .left,           -- c35, c33, c31
   mv .up, mv .up,                         -- r23, r21 : under the stalk, facing up
   ck 1, ck 4, ck 7,                       -- vertical line -> open6
   mv .down, mv .down, mv .down, mv .down, -- r29
   mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   mv .right, mv .right, mv .right, mv .right, mv .right, mv .right]  -- c57: touches socket

def planKinds : List Kind :=
  [.ck, .ck, .ck, .fire, .mv, .mv, .mv, .mv, .mv, .ck, .ck, .fire] ++ List.replicate 17 .mv

theorem plan_trace :
    trace L4 l4init plan =
      -- attempt 4: with sweeping moves the win registers at the first square touching the socket (c56);
      -- the position after a winning move is not observable (the level changes), so this is not a revision
      ({ blk := ⟨29, 56, 2, .right⟩, panel := 0, gates := [true], status := .won, pads := [false] },
       planKinds) := by
  decide +kernel

/-! ## 2. budget: game over iff an action is sent while spent ≥ budget + gained -/

theorem costSum_take_le (C : Costs) : ∀ (l : List Kind) (k : Nat), costSum C (l.take k) ≤ costSum C l
  | [], _ => by simp [costSum]
  | _ :: _, 0 => by simp [costSum]
  | x :: xs, k + 1 => by
      simp only [List.take_succ_cons, costSum]
      have := costSum_take_le C xs k
      omega

def cnt (k : Kind) : List Kind → Nat
  | [] => 0
  | x :: xs => (if x == k then 1 else 0) + cnt k xs

theorem costSum_cnt (C : Costs) : ∀ l : List Kind,
    costSum C l = (cnt .mv l + cnt .mvR l) * C.move + cnt .ck l * C.click + cnt .fire l * C.fire
  | [] => by simp [costSum, cnt]
  | x :: xs => by
    have ih := costSum_cnt C xs
    cases x <;> simp [costSum, costOf, cnt, ih, Nat.add_mul] <;> omega

/-- every action k is sent while the bar is non-empty: spent before it < budget + gained before it -/
def alive (C : Costs) (ks : List Kind) : Prop :=
  ∀ k, k < ks.length → costSum C (ks.take k) < C.budget + gainSum C (ks.take k)

/-- level-4 plan survives under every cost profile within the level-4 bounds (no refill used) -/
theorem plan_kinds_alive (C : Costs) (hm : C.move ≤ 4) (hc : C.click ≤ 4) (hf : C.fire ≤ 8)
    (hb : C.budget = 128) : alive C planKinds := by
  intro k hk
  have hlen : planKinds.length = 29 := rfl
  rw [hlen] at hk
  have htk : planKinds.take k = (planKinds.take 28).take k := by
    rw [List.take_take]; congr 1; omega
  rw [htk]
  have hle := costSum_take_le C (planKinds.take 28) k
  have h28 : costSum C (planKinds.take 28) = 5 * C.click + 2 * C.fire + 21 * C.move := by
    rw [costSum_cnt]
    have e1 : cnt .mv (planKinds.take 28) = 21 := by decide
    have e1' : cnt .mvR (planKinds.take 28) = 0 := by decide
    have e2 : cnt .ck (planKinds.take 28) = 5 := by decide
    have e3 : cnt .fire (planKinds.take 28) = 2 := by decide
    rw [e1, e1', e2, e3]; omega
  omega

/-- **Level 4 is won by `plan`** in the model, for every cost profile within the observed level-4 bounds.
    No hypothesis on the open condition is needed any more: it is the definition `ocBox`. -/
theorem l4_winnable (C : Costs) (hm : C.move ≤ 4) (hc : C.click ≤ 4) (hf : C.fire ≤ 8)
    (hb : C.budget = 128) :
    (trace L4 l4init plan).1.status = .won ∧ alive C (trace L4 l4init plan).2 := by
  rw [plan_trace]
  exact ⟨rfl, plan_kinds_alive C hm hc hf hb⟩

/-- non-vacuity: the defined open condition is used — with the vertical-line clicks moved before the
    alignment moves, the same actions do not win -/
theorem plan_needs_alignment :
    (trace L4 l4init
      ([ck 1, ck 3, ck 5, ck 7, ck 1, ck 4, ck 7, mv .left, mv .left, mv .left, mv .up, mv .up] ++
        List.drop 12 plan)).1.status = .playing := by
  decide +kernel

theorem plan_dies_on_small_budget :
    ¬ alive ⟨4, 4, 8, 119, 0⟩ planKinds := by
  intro h
  have := h 28 (by decide)
  revert this; decide +kernel

theorem plan_alive_at_121 : alive ⟨4, 4, 8, 121, 0⟩ planKinds := by
  intro k hk
  revert k hk; decide +kernel

/-! ## 3. level 5: conformance with attempt 2 -/

def l5observed : List Act :=
  [mv .right, mv .up, ck 1, ck 4, ck 7,
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   ck 1, ck 3, ck 5, ck 7,
   mv .down, mv .down, mv .up, mv .left, mv .left,
   mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up,
   mv .right, ck 1, ck 4, ck 7,
   ck 0, ck 1, ck 4,
   mv .up, mv .down]

/-- observed end state (final frame of attempt 2): 2x2 on the 15-pad r37 c15 facing down,
    both boxes opened, the 14-pad consumed, panel clear. -/
theorem l5_replay_matches :
    run L5 l5init l5observed =
      { blk := ⟨37, 15, 2, .down⟩, panel := 0, gates := [true, true], status := .playing, pads := [true] } := by
  decide +kernel

/-- the cost kinds: fires exactly at the 4 observed firing clicks, the refill exactly at the observed step -/
theorem l5_replay_kinds :
    (trace L5 l5init l5observed).2 =
      [.mv, .mv, .ck, .ck, .fire,
       .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv,
       .ck, .ck, .ck, .fire,
       .mv, .mvR, .mv, .mv, .mv,
       .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv, .mv,
       .mv, .ck, .ck, .fire,
       .ck, .ck, .fire,
       .mv, .mv] := by
  decide +kernel

/-! ## 4. level 5: where the proof breaks -/

/-- in the model a 2x2 teleport always lands on the 15-pad (left region), never in the pocket -/
theorem l5_small_teleport_misses_pocket (s : St) (h : s.blk.size = 2) :
    (applyEffect L5 s .teleport).blk.row = 37 ∧ (applyEffect L5 s .teleport).blk.col = 15 := by
  simp [applyEffect, tpDest, L5, h]

/-- OPTIMISTIC variant of the level data: a 2x2 teleport lands in the pocket (r17 c33). This is NOT what
    was observed; it is the most favourable assumption for the win direction. -/
def L5opt : Level := { L5 with tp := [(2, 17, 33), (4, 17, 33)] }

/-- shortest plan I can build that uses the refill pad -/
def l5optPlan : List Act :=
  [mv .right, mv .up, ck 1, ck 4, ck 7,                                   -- open box1 (r25 c21, up)
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   ck 1, ck 3, ck 5, ck 7,                                                -- shrink at r33 c49
   mv .down, mv .down,                                                    -- r37: refill pad
   mv .left, mv .left,
   mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up,  -- r15
   mv .right, ck 1, ck 4, ck 7,                                           -- open box2 (r15 c47, right)
   ck 0, ck 1, ck 4,                                                      -- teleport
   mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up]                -- climb to the socket

/-- shortest plan without the refill pad -/
def l5optDirect : List Act :=
  [mv .right, mv .up, ck 1, ck 4, ck 7,
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .up, mv .up,
   ck 1, ck 3, ck 5, ck 7,                                                -- shrink at r25 c45
   mv .up, mv .up, mv .up, mv .up, mv .up, mv .right,
   ck 1, ck 4, ck 7,
   ck 0, ck 1, ck 4,
   mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up]

theorem l5opt_plan_wins : (trace L5opt l5init l5optPlan).1.status = .won := by decide +kernel
theorem l5opt_direct_wins : (trace L5opt l5init l5optDirect).1.status = .won := by decide +kernel

/-- with the REAL level data the same plan does not win (the teleport goes to the 15-pad) -/
theorem l5_plan_fails_real : (trace L5 l5init l5optPlan).1.status = .playing := by decide +kernel

/-- measured level-5 costs (bar cells): every move and click 4, a firing click 8, refill 36, bar 128.
    Observed free actions: about one in ten. `aliveDisc` grants up to k/10 + 1 free actions among the
    first k, i.e. it is MORE generous than the observations. -/
def C5 : Costs := ⟨4, 4, 8, 128, 36⟩

def aliveDisc (C : Costs) (ks : List Kind) : Prop :=
  ∀ k, k < ks.length → costSum C (ks.take k) < C.budget + gainSum C (ks.take k) + 4 * (k / 10 + 1)

instance (C : Costs) (ks : List Kind) : Decidable (aliveDisc C ks) := by
  unfold aliveDisc; exact inferInstance

theorem l5opt_plan_dies : ¬ aliveDisc C5 (trace L5opt l5init l5optPlan).2 := by decide +kernel
theorem l5opt_direct_dies : ¬ aliveDisc C5 (trace L5opt l5init l5optDirect).2 := by decide +kernel

/-- non-vacuity of the budget gap: with a 200-cell bar the refill plan would survive -/
theorem l5opt_plan_alive_200 : aliveDisc ⟨4, 4, 8, 200, 36⟩ (trace L5opt l5init l5optPlan).2 := by
  decide +kernel

/-! ## 5. attempt 3 (amended model with the size toggle) -/

/-- the 29 level-5 actions of attempt 3 (the first one recorded against a stale frame) -/
def l5observed3 : List Act :=
  [mv .left, mv .down, mv .down,
   ck 1, ck 3, ck 5, ck 7,            -- shrink at r37 c13
   mv .right,                         -- onto the 15-pad
   ck 1, ck 3, ck 5, ck 7,            -- GROW -> 4x4 r35 c13
   ck 0, ck 1, ck 4,                  -- teleport 4x4 -> pocket r17 c33
   ck 1, ck 3, ck 5, ck 7,            -- shrink in the pocket
   ck 1, ck 3, ck 5, ck 7,            -- GROW off the pad -> 4x4 r15 c33
   ck 1, ck 4, ck 7,                  -- vline in line with box2 but far: nothing
   ck 0, ck 1, ck 4]                  -- teleport 4x4 -> r17 c33

/-- observed final state of attempt 3: 4x4 at r17 c33 facing right, no box opened, pad unused -/
theorem l5_replay3_matches :
    run L5 l5init l5observed3 =
      { blk := ⟨17, 33, 4, .right⟩, panel := 0, gates := [false, false], status := .playing, pads := [false] } := by
  decide +kernel

/-- the shortest winning plan I can build in the amended model (38 actions, 5 firing clicks) -/
def l5Best : List Act :=
  [mv .right, mv .up, ck 1, ck 4, ck 7,                                   -- box1 at r25 c21 facing up
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   mv .up, mv .up,                                                        -- 4x4 at r25 c45
   ck 1, ck 3, ck 5, ck 7,                                                -- shrink -> 2x2 r25 c45
   mv .up, mv .up, mv .up, mv .up, mv .right,                             -- 2x2 r17 c47 facing right
   ck 1, ck 3, ck 5, ck 7,                                                -- grow -> 4x4 r15 c45 facing right
   ck 1, ck 4, ck 7,                                                      -- box2 (horizontal) opens
   ck 0, ck 1, ck 4,                                                      -- teleport 4x4 -> pocket r17 c33
   mv .up, mv .up, mv .up, mv .up]                                        -- climb: r13, r9, r5, socket

theorem l5Best_wins : (trace L5 l5init l5Best).1.status = .won := by decide +kernel
theorem l5Best_length : l5Best.length = 38 := rfl

/-- free-action discount: up to k/d + 1 free actions among the first k -/
def aliveFree (d : Nat) (C : Costs) (ks : List Kind) : Prop :=
  ∀ k, k < ks.length → costSum C (ks.take k) < C.budget + gainSum C (ks.take k) + 4 * (k / d + 1)

instance (d : Nat) (C : Costs) (ks : List Kind) : Decidable (aliveFree d C ks) := by
  unfold aliveFree; exact inferInstance

/-- measured level-5 costs: the plan runs the bar out, even granting one free action in every 8
    (observed: about one in 9-10) -/
theorem l5Best_dies : ¬ aliveFree 8 C5 (trace L5 l5init l5Best).2 := by decide +kernel

/-- the same plan detouring over the refill pad (47 actions): also runs out -/
def l5BestR : List Act :=
  [mv .right, mv .up, ck 1, ck 4, ck 7,
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,  -- 4x4 r33 c49
   ck 1, ck 3, ck 5, ck 7,                                                -- shrink -> 2x2 r33 c49
   mv .down, mv .down,                                                    -- r37 c49: refill
   mv .left, mv .left,
   mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up, mv .up,   -- r17 c45
   mv .right,
   ck 1, ck 3, ck 5, ck 7, ck 1, ck 4, ck 7, ck 0, ck 1, ck 4,
   mv .up, mv .up, mv .up, mv .up]

theorem l5BestR_wins : (trace L5 l5init l5BestR).1.status = .won := by decide +kernel
theorem l5BestR_uses_refill : (trace L5 l5init l5BestR).1.pads = [true] := by decide +kernel
theorem l5BestR_dies : ¬ aliveFree 8 C5 (trace L5 l5init l5BestR).2 := by decide +kernel

/-- non-vacuity of the budget verdict: with a 160-cell bar the 38-action plan would survive -/
theorem l5Best_alive_160 : aliveFree 8 ⟨4, 4, 8, 160, 36⟩ (trace L5 l5init l5Best).2 := by decide +kernel
/-- exact threshold under the generous discount: 148 cells kill it, 149 suffice (bar is 128) -/
theorem l5Best_dies_148 : ¬ aliveFree 8 ⟨4, 4, 8, 148, 36⟩ (trace L5 l5init l5Best).2 := by decide +kernel
theorem l5Best_alive_149 : aliveFree 8 ⟨4, 4, 8, 149, 36⟩ (trace L5 l5init l5Best).2 := by decide +kernel

/-! ## 6. attempt 4 (amended model: sweeping moves, turning when blocked, quarter-aligned refill) -/

/-- the attempt-4 level-5 actions, WITHOUT the five 0-cost clicks on the left recipe panel / the board
    (they changed no modelled slot: only the hint display; `Act` has no such clicks) -/
def l5observed4 : List Act :=
  [mv .right, mv .up, mv .up,                    -- last one blocked (overlap with background) -> turn up
   ck 1, ck 4, ck 7,                             -- box1
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   mv .down,                                     -- 4x4 at r37 c49: refill (quarter-aligned pad)
   ck 1,                                         -- a hint cell (ordinary click)
   mv .right,                                    -- blocked -> turns right
   mv .up, mv .up, mv .up, mv .left,             -- r25 c45
   ck 3, ck 5, ck 7,                             -- shrink (cell 1 already set)
   mv .up, mv .up, mv .up, mv .up,               -- 2x2 r17 c45 facing up
   ck 1, ck 3, ck 5, ck 7,                       -- grow -> 4x4 r15 c43
   mv .right,                                    -- PARTIAL move -> r15 c45, facing right
   ck 1, ck 4, ck 7,                             -- box2 opens
   ck 0, ck 1, ck 4,                             -- teleport -> pocket r17 c33
   mv .up]                                       -- sent at u = 35: GAME_OVER (the move still happened)

/-- observed final frame of attempt 4: 4x4 at r13 c33 facing up, both boxes open, pad used -/
theorem l5_replay4_matches :
    run L5 l5init l5observed4 =
      { blk := ⟨13, 33, 4, .up⟩, panel := 0, gates := [true, true], status := .playing, pads := [true] } := by
  decide +kernel

instance (C : Costs) (ks : List Kind) : Decidable (alive C ks) := by
  unfold alive; exact inferInstance

/-- exact level-5 unit costs fitted in attempt 4: move/click 1, firing click 2, refill 10, budget 35
    (display = 4 * ceil(32 * (35 - u) / 35) matched all 20 readings of attempt 4) -/
def C5u : Costs := ⟨1, 1, 2, 35, 10⟩

/-- the budget rule reproduces the observed end: every action before the last was sent with u < 35,
    and the last one was sent at u = 35 (GAME_OVER) -/
theorem l5_replay4_budget :
    (∀ k, k < l5observed4.length - 1 →
        costSum C5u ((trace L5 l5init l5observed4).2.take k) < 35 + gainSum C5u ((trace L5 l5init l5observed4).2.take k)) ∧
    costSum C5u ((trace L5 l5init l5observed4).2.take (l5observed4.length - 1)) =
      35 + gainSum C5u ((trace L5 l5init l5observed4).2.take (l5observed4.length - 1)) := by
  decide +kernel

/-- the cheapest winning line found by work/l5_search.py (exhaustive Dijkstra over these rules): 37 units -/
def l5Best37 : List Act :=
  [mv .right, mv .up, ck 1, ck 4, ck 7,
   mv .down, mv .down, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right, mv .right,
   mv .down, mv .left, mv .up, mv .up, mv .up,                     -- refill at r37 c49, then r25 c45
   ck 1, ck 3, ck 5, ck 7,                                         -- shrink
   mv .up, mv .up, mv .up, mv .up, mv .right,                      -- 2x2 r17 c47 facing right
   ck 1, ck 3, ck 5, ck 7,                                         -- grow -> 4x4 r15 c45
   ck 1, ck 4, ck 7,                                               -- box2
   ck 0, ck 1, ck 4,                                               -- teleport -> pocket
   mv .up, mv .up, mv .up, mv .up]                                 -- climb to the socket

theorem l5Best37_wins : (trace L5 l5init l5Best37).1.status = .won := by decide +kernel

/-- net units of the whole line: 37 > 35 -/
theorem l5Best37_units :
    costSum C5u (trace L5 l5init l5Best37).2 = 47 ∧ gainSum C5u (trace L5 l5init l5Best37).2 = 10 := by
  decide +kernel

/-- MAIN (L5, attempt 4): the cheapest line found runs out: some action of it is sent with u >= 35 -/
theorem l5Best37_dies : ¬ alive C5u (trace L5 l5init l5Best37).2 := by decide +kernel

/-- non-vacuity / threshold: with a 37-unit budget the same line would survive; with 36 it would not -/
theorem l5Best37_alive_37 : alive ⟨1, 1, 2, 37, 10⟩ (trace L5 l5init l5Best37).2 := by decide +kernel
theorem l5Best37_dies_36 : ¬ alive ⟨1, 1, 2, 36, 10⟩ (trace L5 l5init l5Best37).2 := by decide +kernel
theorem l5Best37_length : l5Best37.length = 42 := rfl

/-! ## 7. attempt 5: conformance only (no definition changed) -/

def l5observed5 : List Act :=
  [ck 0, ck 1, ck 4,                     -- teleport 4x4 -> pocket r17 c33
   ck 1, ck 3, ck 5, ck 7,               -- shrink -> 2x2 r17 c33
   mv .up, mv .right,                    -- r15 c35 facing right, in line with box2's stalk
   ck 1, ck 4, ck 7,                     -- vline from a distance: nothing (ocBox: adjacency only)
   ck 0, ck 1, ck 4,                     -- teleport 2x2 -> 15-pad r37 c15
   ck 0, ck 1, ck 4,                     -- teleport again from the pad: stays
   ck 1, ck 3, ck 5, ck 7,               -- grow -> 4x4 r35 c13
   mv .down,                             -- partial move -> r37 c13
   mv .right, mv .up, mv .up, mv .up,    -- r37 c17, then r33, r29, r25
   mv .up,                               -- blocked: turn only
   mv .left, mv .right]                  -- r25 c13; last one sent at u = 35 (GAME_OVER), still executed

theorem l5_replay5_matches :
    run L5 l5init l5observed5 =
      { blk := ⟨25, 17, 4, .right⟩, panel := 0, gates := [false, false], status := .playing, pads := [false] } := by
  decide +kernel

theorem l5_replay5_budget :
    (∀ k, k < l5observed5.length - 1 →
        costSum C5u ((trace L5 l5init l5observed5).2.take k) < 35 + gainSum C5u ((trace L5 l5init l5observed5).2.take k)) ∧
    costSum C5u ((trace L5 l5init l5observed5).2.take (l5observed5.length - 1)) =
      35 + gainSum C5u ((trace L5 l5init l5observed5).2.take (l5observed5.length - 1)) := by
  decide +kernel

/-- the distance fire of attempt 5 is consistent with the defined open condition -/
theorem ocBox_distance_2x2 : ocBox ⟨.horiz, 15, 49⟩ ⟨15, 35, 2, .right⟩ = false := by decide

end L5e




#print axioms L5e.l4_winnable
#print axioms L5e.l4_replay_matches
#print axioms L5e.l4_replay_kinds
#print axioms L5e.ocBox_fits_observed_fires
#print axioms L5e.plan_needs_alignment
#print axioms L5e.plan_dies_on_small_budget
#print axioms L5e.plan_alive_at_121
#print axioms L5e.l5_replay_matches
#print axioms L5e.l5_replay_kinds
#print axioms L5e.l5_small_teleport_misses_pocket
#print axioms L5e.l5opt_plan_wins
#print axioms L5e.l5opt_direct_wins
#print axioms L5e.l5_plan_fails_real
#print axioms L5e.l5opt_plan_dies
#print axioms L5e.l5opt_direct_dies
#print axioms L5e.l5opt_plan_alive_200
#print axioms L5e.l5_replay3_matches
#print axioms L5e.l5Best_wins
#print axioms L5e.l5Best_dies
#print axioms L5e.l5BestR_wins
#print axioms L5e.l5BestR_uses_refill
#print axioms L5e.l5BestR_dies
#print axioms L5e.l5Best_alive_160
#print axioms L5e.l5Best_dies_148
#print axioms L5e.l5Best_alive_149
#print axioms L5e.l5_replay4_matches
#print axioms L5e.l5_replay4_budget
#print axioms L5e.l5Best37_wins
#print axioms L5e.l5Best37_units
#print axioms L5e.l5Best37_dies
#print axioms L5e.l5Best37_alive_37
#print axioms L5e.l5Best37_dies_36
#print axioms L5e.l5_replay5_matches
#print axioms L5e.l5_replay5_budget
#print axioms L5e.ocBox_distance_2x2
