/-
# L5Model — region-level model of level 5 (computational layer; does not import Limits)

Objects (see work/MODEL.md for the slot table and what each slot distinguishes):
  Loc   where the agent is, at room granularity: A (start room), B (room with the 14 refill),
        C (small room above B, reached by a 2-wide stem), Pad (the 11-marked pad below the goal
        corridor, enclosed by walls), Won.
  St    agent region × agent big (4x4) or small (2x2) × 12-barrier gone × 13-barrier gone ×
        15-corner-frame present.
  Act   walk (macro move between regions) | complete (a panel pattern completion, parameterised
        by the pattern colour) | climb (walk from Pad up the corridor into the goal box).

Rules (each is a total function St → St; "precondition fails" = no change, which the game also
allows since an agent can always stay put):
  walk       move_dir + blocked, read on the L5 map:   A↔B needs the 12-barrier gone;
             B→C needs the small agent (stem is 2 cells wide); C→B always.
  complete   panel_complete followed by the colour's effect:
               15 shrink_f    : big → small, and the 15 frame appears (observed once, L5)
                  grow_f      : small → big, and the 15 frame disappears (attempt 2)
               11 teleport_b  : 15 frame present → agent to the 15 item in room A (observed twice);
                                otherwise → Pad (observed L2)
               6  switch_6    : core colour 12 needs a lane from room A; core colour 13 needs a lane
                                from room C (only places with a clear lane to those boxes on L5);
                                the barrier of that colour disappears
  climb      goal_reach + blocked: from Pad, needs the 13-barrier gone.

Deliberately NOT in this model: the move bar (bar_tick, pickup_14, bar_out). The bar is modelled
in lean/L5Grid.lean (attempt 2), which refines this region model to cells.
-/

namespace L5

inductive Loc | A | B | C | Pad | Won
  deriving DecidableEq, Repr

structure St where
  loc    : Loc
  big    : Bool
  cGone  : Bool   -- barrier of colour 12 removed
  dGone  : Bool   -- barrier of colour 13 removed
  fFrame : Bool   -- 15-colour corner frame (around the 15 item in room A) present
  deriving DecidableEq, Repr

inductive Walk | AB | BA | BC | CB
  deriving DecidableEq, Repr

/-- core colour of a 6-box -/
inductive Core | c12 | d13
  deriving DecidableEq, Repr

/-- one pattern completion, parameterised by the pattern colour (generalisation T2) -/
inductive Completion | shrink15 | teleport11 | switch6 (k : Core)
  deriving DecidableEq, Repr

inductive Act | walk (w : Walk) | complete (k : Completion) | climb
  deriving DecidableEq, Repr

def start : St := ⟨.A, true, false, false, false⟩

/-! ## rules -/

def walkRule (s : St) : Walk → St
  | .AB => if s.loc = .A ∧ s.cGone = true then { s with loc := .B } else s
  | .BA => if s.loc = .B ∧ s.cGone = true then { s with loc := .A } else s
  | .BC => if s.loc = .B ∧ s.big = false then { s with loc := .C } else s
  | .CB => if s.loc = .C then { s with loc := .B } else s

def shrinkRule (s : St) : St :=
  if s.big = true then { s with big := false, fFrame := true } else s

def teleportRule (s : St) : St :=
  if s.loc = .Won then s
  else if s.fFrame = true then { s with loc := .A } else { s with loc := .Pad }

def switchRule (s : St) : Core → St
  | .c12 => if s.loc = .A then { s with cGone := true } else s
  | .d13 => if s.loc = .C then { s with dGone := true } else s

/-- attempt 2: grow_f established — the 15 completion while small makes the agent big again and
    removes the 15 frame (was relaxation `completeRuleR` in attempt 1). -/
def growRule (s : St) : St :=
  if s.big = false then { s with big := true, fFrame := false } else s

def sizeRule (s : St) : St := if s.big = true then shrinkRule s else growRule s

def completeRule (s : St) : Completion → St
  | .shrink15 => sizeRule s
  | .teleport11 => teleportRule s
  | .switch6 k => switchRule s k

def climbRule (s : St) : St :=
  if s.loc = .Pad ∧ s.dGone = true then { s with loc := .Won } else s

def step (s : St) : Act → St
  | .walk w => walkRule s w
  | .complete k => completeRule s k
  | .climb => climbRule s

def run (s : St) : List Act → St
  | [] => s
  | a :: as => run (step s a) as

/-! ## attempt-1 main theorem retired

`l5_unwinnable` (no sequence reaches Won) was proved for the attempt-1 rules, in which nothing made
the agent big again. Attempt 2 observed grow_f (tid 2d6344b3b63cb07b), which falsifies that premise;
the theorem no longer holds and is removed. Its witness relaxation is now the model itself: -/

/-- with grow in the rules, the region model reaches the goal (ignoring the move bar) -/
theorem l5_region_reachable :
    (run start [.complete (.switch6 .c12), .walk .AB, .complete .shrink15, .walk .BC,
                .complete (.switch6 .d13), .complete .shrink15, .complete .teleport11,
                .climb]).loc = .Won := by decide

/-- the region model still constrains: without growing back, teleport after the 13-switch goes to A -/
theorem region_no_grow_fails :
    (run start [.complete (.switch6 .c12), .walk .AB, .complete .shrink15, .walk .BC,
                .complete (.switch6 .d13), .complete .teleport11, .climb]).loc = .A := by decide

/-- the model can move: a non-trivial sequence changes the state -/
theorem model_moves :
    run start [.complete (.switch6 .c12), .walk .AB, .complete .shrink15, .walk .BC,
               .complete (.switch6 .d13)] = ⟨.C, false, true, true, true⟩ := by decide

end L5

#print axioms L5.l5_region_reachable
#print axioms L5.region_no_grow_fails
#print axioms L5.model_moves
