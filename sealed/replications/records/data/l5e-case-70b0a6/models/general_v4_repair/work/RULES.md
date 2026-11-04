# Step-one output (run 1): rules, audit, reconciliation

Result: levels 1-4 beaten; GAME_OVER on level 5 of 5 (move bar ran out). 126 distinct transitions recorded.

## Rule table (concepts/, numbers from the final `settle`; S on held-out = all transitions minus own EVIDENCE)
| concept | claim (short) | N | S | C | notes / abstentions |
|---|---|---|---|---|---|
| move_dir | ACTION1-4 = up/down/left/right, step = agent side (4 or 2); head (9) faces the direction of motion | 66 | 1.000 | 0.537 | NA on blocked targets; one unexplained no-op (L1 first ACTION1, tid 2b3e5ed8) excluded by scope |
| blocked | a target containing 5/13 -> no move, agent turns to face that way | 0 | - | 0 | 3 evidence tids, none held out |
| bar_tick | bar (col 62, colour 14) changes by 0 or -2 per action, except pattern completions and pickups | 106 | 1.000 | 0.876 | v3 |
| panel_toggle | clicking a panel cell toggles 14 on that cell only (when it doesn't complete a pattern) | 32 | 1.000 | 0.260 | |
| panel_complete | 14-set == a target pattern -> panel is cleared to 2 | 12 | 1.000 | 0.096 | |
| shrink_f | completing the 15 pattern turns the 4x4 agent into a 2x2 at the same top-left corner | 2 | 1.000 | 0.016 | |
| teleport_b | completing the 11 pattern -> agent lands centred in some corner-marker frame (11 or 15) | 1 | 1.000 | 0.008 | does NOT say which frame; observed: the 15 frame wins whenever it exists |
| switch_6 | completing the 6 pattern with the agent facing up and its left two columns having a clear lane to a 6-box -> that box goes, and every block of its core colour becomes floor | 0 | - | 0 | the facing-right lane was observed (L5) but is out of scope (NA) |
| goal_reach | a move whose target overlaps the 9/10 goal box -> next level | 3 | 1.000 | 0.024 | |
| pickup_14 | stepping on a map 14-item raises the bar | 0 | - | 0 | 1 sample (+16 rows) |
| bar_out | bar at 0 and a non-winning action -> GAME_OVER | 0 | - | 0 | registered only |

## Reconciliation (bet before each act, then compare)
Every act had a written bet beforehand (BET.json / journal.jsonl). Bets that missed, and how each was explained:
- L1 first ACTION1 was a no-op: unexplained, scoped out (not a rule).
- L3 6-completions #1 and #2 did nothing: explained by the lane rule (switch_6 v2), which was then confirmed in L4 and L5.
- L4 first 6-completion (agent at (21,29) facing up) did nothing: this refuted v1 ("any column overlap"); the lane rule fits.
- L5 first teleport went to the 15 frame instead of the 11 pad: the rule was wrong (it assumed a single frame); scope narrowed in v2.
- L5 second teleport did not move the agent: the 15 frame has priority (not yet written as a concept).
- A blocked wall move turned the agent: `blocked` v3.
- Reading errors (not rule errors): agent finder failed next to the goal box (tid 87597ca9); target patterns hard-coded at the bottom-left (tid 981df856); 6-cells counted inside the target frames (tid 0fdbe552).

## Dropped-mechanism audit
| observed but not encoded | effect of dropping it on the model |
|---|---|
| shrinking adds 15 corner markers around the 15 item and removes the outer 11 markers | model allows MORE (it thinks teleport can reach the 11 pad when shrunk) -> it is looser than the world. This is the error that cost the game. Must be added. |
| teleport prefers the 15 frame | same as above: must not be dropped |
| bar cost per action differs by level (L1 ~0.65 units, L4/L5 ~0.95 units; 32 units in total) | model allows more -> must be modelled for planning |
| 6-box becomes wall (L3) or floor (L4/L5) | allows more/fewer cells -> unclear; currently written as {2,5} |
| unexplained first-action no-op on L1 | model allows more |
| actions not tried: ACTION5, ACTION7, clicks outside the panel, completing 15 while already 2x2 (the grow test was cut off by GAME_OVER) | unknown |

## What the next attempt on L5 should be (if the game state allows)
Fire the 12-box (agent (33,21) facing up) -> eat the 14 item in room B -> shrink at (25,45) -> climb to (15,45), step right -> fire the 13-box -> **grow back / remove the 15 frame first (untested)** -> teleport to the 11 pad as 4x4 -> 4 moves up. Watch the budget: about 32 units at ~1 unit per action.

# Attempt 2 (level 5 only; GAME_OVER again, 2 moves short of the goal)

New facts (each now a concept or a revised one):
- **grow_f**: completing the 15 pattern while 2x2 makes the agent 4x4 (2x2@(15,45) facing up -> 4x4@(15,43)), and the 15 corner markers disappear (the 15 item stays). P1 from the attempt-1 proof was false.
- **teleport after grow**: with no 15 frame, the 4x4 lands at (17,33), the centre of the outer 11 frame.
- **blocked v4**: a move whose full step is obstructed slides the largest even distance that fits (4x4 @(15,43) right -> (15,45)).
- **thumb_hint**: clicking a target thumbnail shows that pattern as 0-hints on the panel; the click didn't change the bar. It is not a one-click shortcut.
- 4x4 facing right fires along its top two rows (the 13-box was hit from (15,45)).
- Bar: plain action ~0.9 unit (1 with a free one about every 10), a completion click 2, refill +9 (38->54 rows both times). A non-winning action at bar 0, click or move, -> GAME_OVER.

Route used (43 actions to the goal, 41 taken): fire 12 from (25,21) | to (37,49) eat 14 | (25,45) shrink | up to (15,45) | grow | slide right | fire 13 | teleport | climb 4.
Final bar 0 at (13,33); needed 2 more non-winning moves. Deficit about 2 units, matching the plan5.py estimate (34.2 vs 32).
Still to find: about 2 units of savings, or a mechanism not yet seen.

# Attempt 3 (level 5; stopped while the game was still running; not won)
Probes of inputs the model treats as inert:
- ACTION5/7 are rejected by the service.
- Clicks anywhere off the panel (floor, agent, 12-box, 15 item, 11 pad, 14 item) are free: the panel blinks colour 8 for 13 frames and nothing else changes.
- Walking the big agent over the 15 item only covers it; it reappears afterwards.
- The refill is a fixed +16 rows (34 -> 50 this time, 38 -> 54 before).
- New concept **grow_place**: the grow placement depends on facing (up: (r,c-2); right: (r-2,c-2)). This makes the grid proof's optimal route physically realizable.
No mechanism found that saves an action, so the L5Grid bound (best route 42 actions, budget 41) stands.
- Shrink while facing right (4x4 at (15,45)) gave a 2x2 at (15,45): shrink keeps the top-left corner whatever the facing (shrink_f holds), unlike grow.
- The game ended with GAME_OVER on the first non-winning action after the bar read 0 (bar_out confirmed again).

# Attempt 4 (level 5; GAME_OVER exactly as L5Grid predicted)
Played the 42-action optimal route from the grid search (gen_l5grid.py witness) with no probes. Bar per batch: 54 after 15 actions; 20 after 32; 4 after the teleport; 0 after climb 2; GAME_OVER on climb 3 at (5,33), one move short of the goal.
This matches the certificate exactly (f(start) = 320: the last non-winning move starts at the cap). Prediction written before acting; reconciled 1/1.

# Attempt 5 (level 5; probe attempt, GAME_OVER)
- A small agent covering the 15 item: nothing happens (stays 2x2, 15 markers stay); the item reappears when the agent leaves.
- Moving into a 6-box (small agent at (13,21) pressing up): blocked, no switch. Touching a box does not trigger it.
- Grow with no room (2x2 in the 2-wide stem facing up, placement (13,19) is wall): it fails. The agent is unchanged, the frame stays, the panel still resets, and the completion cost is still charged (21-frame flash). grow_f v2 scope narrowed; this matches the L5Grid grow-failure branch.
- Firing point-blank from inside the stem facing up removes the 12-box and the 12 barrier (switch_6).
- The bar ran out and GAME_OVER came on the first non-winning action at 0.
None of these gives a saving; the L5Grid bound stands.

# Attempt 6 (level 5; GAME_OVER after my own panel mistake)
- Thumbnail click with 2 of 3 cells highlighted only adds the 0-hint; it doesn't complete (thumb_hint holds; no shortcut).
- **Panel click areas are larger than the drawn 3x3 cells**: a click at (27,50), in the gap, toggled cell (0,0) and cost a unit. _lib.panel_cell_at v2 widens each cell to 5x5. This stray highlight broke the following shrink: the panel never matched, and every later pattern was out of step, so the big agent teleported to the pad with the 13 barrier still present.
- blocked v4.2: markers 11/15 count as floor for sliding; vacated cells are not asserted.

# Attempt 7 (level 5; optimal route replayed cleanly)
Bar 54 after 15 actions and 20 after 32, same as attempt 4. GAME_OVER on climb 3 at (5,33), exactly as L5Grid predicts (second exact match). Checked the logs: the 14 refill item is consumed for good (cells stay 2 after the agent leaves).

# Attempt 8 (level 5; GAME_OVER)
- Cost refit on all L5 runs (work/fitcost.py): big move 0.90, small move 0.89, click 0.92, +1.0 per completion (attempt 5 excluded). Costs are effectively uniform; no cheaper action mix exists.
- **Panel click areas tile the whole panel**, including its outer frame: (23,50) and (23,48) toggled (0,0); a click on the bar column is a free blink. `_lib.panel_cell_at` v3.
- The route with 2 probe clicks ended at bar 0 right after the teleport; climb 1 -> GAME_OVER (as predicted: worse than the infeasible optimum).

# Attempt 9 (audit run; replayed L1-L4, then experiments on L5; GAME_OVER)
Audit result: the fractional cost fit was replaced by an exact mechanism.
- **bar_ticks** (work/fit_ticks.py): integer ticks with a per-level budget B, each action 1 tick, the completing click 2, refill -10 (net -9 on that move), free clicks 0, display = 2*ceil(32*(B-n)/B). Unique fit on all 8 L5 runs (B=35); L4 B=35, L3 B=50. Held-out S=1.000 on N=241.
- **X7, end-of-bar rule**: a 2-tick completing click at n=34 -> GAME_OVER. A non-winning action is refused if it would take n above B, whatever its cost (bar_out v2). So feasibility = total non-winning ticks <= 35.
- Exact search under ticks (permissive grow/lanes): minimum 36 non-winning ticks to a win-ready state. One over.
- Thumbnail: the 1st click shows hints; the 2nd and later clicks play a free demo (the pattern cells light up one by one, then revert). No completion, no state change.
- Small teleport goes to the 15 item in every tested context: from room C facing right (13 barrier gone); from room A start facing down (both barriers present, refill uneaten); with the agent covering a 15-frame corner. The 15 item survives a grow on top of it, and its frame reappears on the next shrink.
- **grow_fit** replaces grow_place (retired): the first fitting placement in order (-2,-2), {(0,-2),(-2,0)}, (0,0), independent of facing. Fits 5/5 situations (up, right, down, left, stem failure).
- Clicks on the goal, 13 barrier, 13-box and 12 barrier: free blinks.
