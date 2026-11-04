# Rules learned (evidence = transitions.jsonl tids; concepts/ hold checkable versions)
- Player: s x s square (s=4 or 2), half 9 (front, facing side) half a(10). ACTION1/2/3/4 = up/down/left/right.
  Move by s if target rect is floor(2) (or goal); else just turn to face. First action after reset swallowed.
- Floor 2, wall/background 5. Bar at cols 62-63 (e) = budget; ~1 unit (2 rows) per move, clicks ~2/3, completion animations cost more. Full bar 32 units.
- Panel (right, 3x3 cells centers x=25/30/35, y=50/55/60): click toggles base(0/2) <-> e.
  0 cells = hint. When the set of e cells == legend pattern (left panel), "completion": panel resets to all 2, an ability fires.
- Ability depends on legend colour (one per level so far):
  f (L1, 4-edge plus): toggle player size 4<->2 (shrink keeps top-left).
  b (L2): teleport player into the b-marked box.
  6 (L3, vertical line): fire 4-wide shot in facing direction; hitting the 6-box (receiver with d inside) removes the 6-box and the d door. Hitting d door directly: nothing.
- Goal: cap = 9 border + a interior. Entering a cells (overlapping 9 border OK) => level complete.
- WARNING: read columns by index carefully (L1 neck is cols 35-36, I misread as 37-38).

# Outcome attempt 1
- Levels 1-3 beaten; game over on level 4 (bar exhausted; first action with empty bar => GAME_OVER).
- L4 lesson: shot range is per-level (L3: travelled 5 steps to box; L4: fizzled after 1 step from room top).
  Intended L4 route probably: shrink (f) -> climb neck (cols31-32) close to 6-box -> fire 6 -> back down -> right through door (cols45-47, rows29-32) -> cap (cols57-60).
  Bar on L4 costs 4 rows per move; e 2x2 marker at rows34-35 cols23-24 did nothing for a 4x4 player (untested for 2x2).

# Attempt 2 (level 4 only; service restored at L4 start)
Established this attempt (evidence: transitions.jsonl, work/anim/, work/fit_budget.py):
- BAR = units. Every accepted action costs 1 unit (blocked moves too; clicks outside the panel and the
  swallowed first action are free); every pattern completion costs +1. Shown bar = 64 - 2*floor(u*64/B/2).
  Fitted budgets (unique fit per level): L1 B=50, L2 B=25, L3 B=50, L4 B=18. Attempt-2 predictions of the
  bar (54, 40, 36, 32, 30, 16) all matched. The action that pushes u past B still resolves, then GAME_OVER.
- d door blocks a 2x2 too (decisive test, tid e78e11aeb025a492): blocked_by_nonfloor holds for both sizes.
- SHOT (6 pattern): projectile moves 2 rows/frame in facing direction and is destroyed by walls; there is
  no short per-level range: a 2x2 shot travelled 3 steps over open floor and died at the wall (anim of
  tid e1e32774af9df50e). The attempt-1 4x4 shot died after 1 step because its LEFT half (cols 29-30) met
  wall while the neck is under its right half (cols 31-32); in L3 the neck was under the left half and it
  flew 5 steps. => for facing up, the projectile is the player's left 2 columns (or col c+1; same on this lattice).
- GROW: 2x2 at rows27-28 cols43-44 (wall at cols45-46) grew to rows25-28 cols41-44 (kept bottom-right);
  earlier grow (L1) kept bottom-left with the right side free. Consistent with: keep bottom row, extend
  right if free else left. Shrink keeps top-left (4 observations, all facings).
- Revised model min cost for L4: 23 units (loose resize) / 25 (observed anchors) > 18 => still not winnable
  with known rules; the e marker (rows34-35, cols23-24) is the one element whose function is unknown.

# Attempt 3 (level 4; service restored at L4 start)
- e marker is NOT a shot receiver: 4x4 shot facing left flew over it to the wall, nothing changed (anim, tid 36719721c76834ac).
- e marker IS a bar refill: 2x2 moving onto it (rows33-34 cols23-24, overlapping its top row; facing left so its
  9 half covered col 23) consumed it and the bar jumped 8 -> 40 rows (tid b8c7d8401d65d9d4). Next 5 bars 36,32,30,26,22
  matched "counter = 7 after the pickup move" exactly (17 -> 7). Attempt 1: 4x4 fully covering it (facing left, its
  9 half on cols 21-22) did NOT trigger. Trigger = small size OR front-half overlap: NOT yet distinguished.
  Refill semantics 'set to 7' vs 'minus 10' not distinguished (pre-pickup counter was 17).
- Revised fire rule CONFIRMED positively: 2x2 at rows31-32 cols31-32 facing up (10 rows below the room top) fired;
  box and door removed (tid c2932d3ef5f9c36d). No range limit.
- work/plan_l4.py: with refill, min peak counter is 18 only for (minus10, front, loose resize); 19-21 otherwise.
  Cap 18 (an action starting at 18 still resolves). So L4 is at the edge: the remaining unknowns decide it.
- Stopped with 2 units left (u=16), game NOT_FINISHED.
- Attempt 3 ended: 3 more right moves, bars 4, 0, then the move starting at u=18 resolved and returned GAME_OVER (as predicted).

# Attempt 4 (level 4; service restored at L4 start) -- GAME_OVER
Established:
- GROW placement: 2x2 rows33-34 cols25-26 facing down (right side free) -> 4x4 rows31-34 cols23-26 (tid 81e5d751d32a2557).
  With L1 (left walled -> extended right) and attempt 2 (right walled -> extended left): rule = extend UP (keep bottom
  row) and LEFT unless walled (then right). "Right if free" (attempt-3 model) REFUTED. Up-blocked case still unobserved.
- PICKUP by a 4x4: its front half (rows33-34, facing down) overlapped e row 34 -> picked up. "Small only" REFUTED.
  Attempt 1's 4x4 had e under its BACK half -> no pickup. => trigger = front-half overlap (2x2: whole body).
- REFILL = counter minus 10: 15 -> 5 (bar 48). "Set to 7" REFUTED.
- 4x4 at cols31-34 facing up fires up the neck and opens the door (tid c346c61149a0ad41).
- Action starting at counter 18 resolves then GAME_OVER (3rd observation).
Candidate L4 plan (all components observed; counter in brackets):
  left,left,left [3] down,down [5] -> 4x4 (33,25) facing down; f pattern 4 clicks [10] -> 2x2 (33,25);
  down [11] -> 2x2 (35,25); f pattern [16] -> grow to 4x4 (33,23), front rows35-36 covers e row 35 -> pickup [6];
  right,right [8] -> (33,31); up [9] -> (29,31) facing up; 6 pattern 3 clicks [13] -> door open;
  right x6 [14..19]: the 6th (winning) move STARTS at 18. Unknown: does a winning move that starts at 18 win
  (moves starting at 18 do resolve) -- the only open question for this plan.

# Attempt 5 (level 4) -- GAME_OVER on the final move
- Executed the attempt-4 plan; every intermediate state and bar reading matched the prediction exactly
  (bars 62,58,54,50,48,30,26,44,40,36,32,18,16,12,8,4,0; e pickup at the grow, door opened by the 4x4 shot).
- Final move (4x4 rows29-32 cols51-54, right, STARTING at counter 18): 1 frame, player moved only 2 px (to cols53-56,
  adjacent to the cap), state GAME_OVER (tid c20aa696def56d6b).
- Interpretation (a) [preferred]: the move that runs past the budget executes only its first 2-px sub-step, then
  GAME_OVER. Earlier "action at 18 resolves" observations were all 2x2 moves (one sub-step = full move) or a grow,
  so they don't distinguish. (b) "move stops adjacent to a goal" is contradicted by L1 (2x2 into a+floor won) and
  L3 (4x4 into 9-border+a won).
- Consequence: a 4x4 winning move must START at counter <= 17; L4.l4_no_win_cap17 says no plan does that in the model.
  Possible remaining lever: a final move made as a 2x2 (its single 2-px sub-step completes at counter 18) -- to be
  checked in the model.
- Formal (after attempt 5): model_l4c.py / runB5 in lean/L4Model.lean: no win under cap 18 with the half-step rule
  (L4.l4_unwinnable_half); plan4 wins with cap 19. Exactly one unit short.

# Attempt 6 (level 4) -- experiments, GAME_OVER
- Clicking a legend box (f at (4,4), 6 at (4,15)) is FREE and writes that pattern into the panel as hint
  cells (colour 0); hints are cosmetic (a hint cell toggles 0 -> e at normal cost). Clicks on player, box,
  door, bar, goal: inert & free. ACTION5 is rejected by the service.
- The level-2 b pattern does nothing on L4 (only legend abilities are enabled).
- Completion requires EXACT equality: {(0,0),(0,1),(1,1),(2,1)} (superset of the 6 pattern) did not fire.
- GROW with up walled (2x2 rows21-22 cols39-40, facing right) -> 4x4 rows21-24 cols37-40: keeps TOP row,
  extends LEFT. Full rule (4 obs): extend up if free else down; extend left if free else right; facing irrelevant.
- A 4x4 move STARTING at counter 18 moved the FULL 4 px (cols33-36 -> 29-32), then GAME_OVER (tid 38c8c6ceae907237).
  => attempt-5 'half-step' explanation REFUTED. New reading: at counter 18 a move still resolves but cannot ENTER
  the goal (attempt 5 stopped adjacent to it). Either way a winning move must start at counter <= 17, which the
  model (cap 17) says no plan achieves.

# Attempt 7 (level 4) -- GAME_OVER
- A second legend click is inert; a legend click with 3 of 4 pattern cells set does NOT complete it (free, inert).
- Full scan of the L4 start frame: no unexplained cells (every non-wall cell belongs to a known object).
- Offline: a door-opening shot straight at the door would make L4 trivial (9 units), but L3 already showed a shot
  hitting the door does nothing -> ruled out by existing evidence.
- Replayed the attempt-4 plan; every transition identical to attempt 5 (same tids); terminal move at counter 18
  from cols51-54 again stopped 2 px short (tid c20aa696def56d6b) -> deterministic.

# Attempt 8 (level 4) -- experiments, GAME_OVER
- NEW RULE (confirmed): moves advance in 2-px SUB-STEPS, as many as are free. 4x4 at rows33-36 cols23-26 moving
  left (full target cols19-22 = wall) moved 2 px to cols21-24 (tid ece0a2f5605e3199). Concepts move_by_size /
  blocked_by_nonfloor revised (v2/v3). This also explains attempts 5/7: the 4x4 advanced one free sub-step and the
  second sub-step (into the goal) did not happen -- either because the goal can't be entered at counter 18
  ('touch18') or because entering requires the target inside the goal frame ('contain'); not yet distinguished.
- In this room, wall sub-steps only shift 4x4 parity from cols/rows = 3 mod 4 back to 1 mod 4 (room is aligned to
  the start lattice), so they do not replace the shrink+grow parity change needed for the col-31 shot.
- Shot fired horizontally straight at the d door (4x4 facing right, adjacent): door stays (tid c590bb86483ad6eb).
- work/model_l4e.py (sub-step moves): no plan within 18 under either goal reading; 19 suffices.
