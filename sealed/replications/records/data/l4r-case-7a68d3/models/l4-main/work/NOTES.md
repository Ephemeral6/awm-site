# Game notes (attempt 1) — rules extracted by experiment

Coordinates: ACTION6 x=col, y=row (README). Frame 64x64. Counter bar = cols 62-63, fills with 0 from top.

## Actions
- ACTION1/2/3/4 = up/down/left/right. Block moves by its own side length k (4 or 2) when target cells are floor (2).
  After a move the 9-coloured half is on the leading side ("front"); a-half behind. (move_step, lead_face)
- First action after /reset was swallowed (frame identical).
- Moving into d (13) = blocked, but action is still charged. (d_block)
- ACTION6 on the bottom 3x3 grid (cell blocks rows 49-51/54-56/59-61 x cols 25-27/30-32/35-37) toggles the
  cell e(14) <-> original. When the set of e cells equals the pattern in a pattern panel (3x3 of 2x2 marks),
  the grid resets to 2 and the panel's effect fires (multi-frame animation). Effect is by panel colour:
  - f (15): toggle size. 4x4->2x2 keeps TOP-LEFT quadrant (L1 facing up; L4 facing right).
            2x2->4x4: L4 facing left, 2x2 at (33,23) became 4x4 at (31,21) i.e. old 2x2 = bottom-right quadrant.
  - b (11): teleport block to the inner 4x4 of the b corner-marker frame (L2).
  - 6: fire beam from front in facing direction. Beam destroys a 6-bordered box holding d; that removes
       ALL d barriers (L3). Beam blocked: L4 4x4 at cols29-32 facing up under a 2-wide stem at cols 31-32
       fizzled after 2 rows; L3 4x4 at cols 29-32 under stem at cols 29-30 succeeded. => beam's LEFT half
       (cols l..l+1) must be clear floor (hypothesis). Beam hitting d directly does nothing.
- Bottom grid "0" cells in a level's start frame are a hint showing the pattern positions.
- Exit = 9-ring with 4x4 a core. Moving so target overlaps the a core = level complete (any block size).

## Counter / budget (per-level data)
- Bar of 64 rows; ticks 2 rows at a time. L1-L3: ~2/3 tick per action (~48 actions/level).
  L4: ~1.75 ticks per action (~18 actions); pattern completion step costs 3-4 ticks.
- New level -> bar reset to full.
- e (14) 2x2 item in room (L4 rows34-35 cols23-24): 4x4 covering it (counter 42/64) did NOT consume it;
  2x2 overlapping it when counter was exactly 64/64 consumed it and refunded 32 rows. (size vs exhaustion unresolved)
- At 64/64 the game was still NOT_FINISHED.

## Level solutions found
- L1: complete f-pattern (4 clicks) -> 2x2, walk left 5 / up 5 through stem into head exit.
- L2: complete b-pattern (3 clicks) -> teleport, then down 1, right 3 into exit.
- L3: block to cols29-32 rows13-16 facing up, fire 6 beam up stem -> box & d gone; left 1, down 7.
- L4 (FAILED, budget): layout: room rows21-36 cols21-44, block 4x4 at (25,37) facing down; 6-box rows5-8
  cols30-33, stem cols31-32 rows9-20; d barrier rows29-32 cols45-47; exit core rows29-32 cols57-60;
  e item rows34-35 cols23-24; panels top-left: f (shrink) and 6 (beam).
  Wasted: 4x4 beam from cols29-32 (fails). Better plan idea: A3 (4x4 -> (25,33)), shrink -> 2x2 (25,33),
  A3 -> (25,31), A1 A1 -> (21,31) facing up, beam (3 clicks), then grow or walk to exit. Budget is very tight;
  the e item refund (+32 rows) probably required.

## End of attempt 1
- Off-grid ACTION6 click: no state change, NOT charged (grid flashes 8 in the animation).
- Shrink while facing left at 4x4 (31,21) -> 2x2 (31,21) (top-left again).
- Counter exhaustion: the action that pushed the bar past full (64/64 -> beyond) returned GAME_OVER.
  (At exactly 64/64 one more move was still allowed; that move ate the e item.)
- Final: reached level 4, levels_completed = 3 of levels_total (see service), GAME_OVER on L4.
- Retry lesson for L4: never fire the 4x4 beam from cols29-32; shrink early, use 2x2 at cols31-32
  facing up (or 4x4 with left col 31), eat the e item with the 2x2 when it is on the way; count budget
  ~1.75 ticks/move, ~3-4 ticks per completing click, 32 ticks total (+16 from item).

## Attempt-1 post-mortem additions (analysis of recorded data, no new game actions)
- Counter in ticks: L4 budget B=18 ticks; move 1, grid click 1, completing click 2, off-grid 0; acting is
  allowed while used <= 18. (L1 fits B=50.) Display rows = even-floor(64*used/B).
- Formal model M4: work/MODEL_M4.md, lean/L4Model.lean, proof lean/L4Proof.lean (L4.l4_unwinnable).
- Under H_eat (only 2x2 eats), H_grow ((t-2,l-2)), H_beam (l=31), H_ref (-10): L4 unwinnable from reset;
  with 2 extra ticks (B=20) it is winnable (L4.relaxed_budget20_wins).
- If a 4x4 eats with its FRONT half and refund is -10, row-accurate search finds a 19-tick win:
  D D L L L | f-pattern | D | f-pattern(grow onto item, front eats) | R R U | 6-pattern | R x6.

## Attempt 2 (L4 only; level was reset, service still live at L4) — results
Established this attempt (all counter readings matched the tick model exactly, 26/26 steps):
- Panel click (top-left f panel, (4,1)): FREE (0 ticks); loads that panel's pattern into the grid as 0-hints.
  No effect on block. Hint cells still cost 1 tick per click.
- Grow facing DOWN: 2x2 (35,25) -> 4x4 (33,23) = (t-2,l-2), same as facing left. Shrink keeps top-left.
- A 4x4 DOES eat the item when it lands on it by growing with its front (9) half over the item
  (refund confirmed -10: 16 -> 6 ticks). Earlier non-eat: 4x4 moved left with only its back (a) half on it.
  Unresolved: front-half vs "grow placement eats" vs "any landing except by that move".
- Refund = -10 ticks (second observation; set-to-9 refuted).
- Beam from 4x4 at l=31 facing up (left half under stem cols 31-32) works: box gone, d barrier gone.
- A move that would be tick 19 (budget 18) into the exit: GAME_OVER, block drawn only 2 cells forward.
  Exit does not save you on the over-budget step.
Executed line (19 ticks, lost by 1): [panel click] D D L L L | f(4 clicks) | D | f(4 clicks, grow+eat) | R R U |
  6(3 clicks) | R x6 (last = tick 19).
Corrected search (work/hypsearch.py): under these rules no L4 win exists for any U/R grow anchor. The designer
almost surely intended a solution, so a mechanism is still missing. Cheap tests for next attempt (do FIRST):
  1. POST action 5 and action 7 (README lists only 1-4,6; may be rejected at no cost; ARC-style 7 = undo?).
  2. Click a panel a second time / click the panel while its hint is loaded (free clicks) — does it auto-fill or fire?
  3. Click the 6 panel (hint) and see if both hints combine.
  4. Does a 4x4 eat the item by MOVING with its front onto it (e.g. (29,21) -> D -> (33,21))?

## Attempt 3 (L4; service resumed at L4 start) — results. Stopped at used = 18/18 without a further action.
Established:
- H_shrinkD holds: shrink facing DOWN keeps top-left (2x2 (33,37) from 4x4 (33,37)). -> L4 proof premise observed.
- Service accepts only actions 1,2,3,4,6 ("action must be one of [1, 2, 3, 4, 6]"); refused actions are not charged.
- Second click on a panel: 22-frame demo lighting the pattern cells in order, no net change, free.
- Clicks on item, block, d barrier, switch box, exit core, counter bar: free no-ops (13-frame grid flash).
- NEW: SLIDE. A 4x4 whose full 4-cell move is blocked moves 2 cells if those are free
  ((31,35) -D-> (33,35), rows 37-38 wall). Charged 1 tick.
- A fully blocked move (into background) charges 1 tick and TURNS the block to the move direction. Background = wall.
- A 4x4 eats the item by MOVING its front half onto it ((33,27) -L-> (33,23)), refund -10 (16 -> 6).
- Grow facing UP anchors (t-2,l-2) too ((29,23) 2x2 -> (27,21) 4x4). Shrink facing up keeps top-left.
Search with slide rule (work/slidesearch.py): no L4 win from reset within 18 ticks; best lines need 19.
- Final action (used 18 -> 19): A4 from 4x4 (27,21) moved the FULL 4 cells to (27,25), then GAME_OVER.
  So the attempt-2 over-budget move into the exit stopping after 2 cells ((29,51)->(29,53)) is NOT a generic
  over-budget truncation. Open hypotheses: (H1) a move whose target only half-overlaps the exit core is treated
  as blocked and slides 2 (then the 19-tick line actually needed one more move); (H2) exit entry interacts with
  the budget check. L1 accepted a 2x2 target half on the core (row 13 core, row 14 floor), which argues against H1
  unless 4x4 differs. Test next time: in a level with budget to spare, move a 4x4 so its target overlaps the
  exit core by 2 columns only.

## Attempt 4 (L4) — GAME_OVER
- Panel click while the grid holds 3 of the 4 f cells: only adds the 0-hint on the missing cell; no completion; free.
- Toggling an e cell off returns it to its hint state (0) when a hint is loaded.
- Beam from 4x4 at l=33 (rows 29-32) facing up: travels up the open room to row 21, stops at the wall (row 20),
  box and barrier intact. Beam continues while the cells under its LEFT half are floor: l=31 passed the stem with
  the right half over wall; l=29 stopped at once (left half wall); l=33 stopped at the room top. H_beam strengthened.
- Played D D L L L, f-cells, panel test, R R U, grid reshaped to 6, beam at l=33, R R, R into barrier (tick 19).
- Still no line within 18 ticks under all observed rules.

## Attempt 5 (L4) — GAME_OVER
- L2's teleport pattern {(0,0),(0,1),(1,1)} on L4 (no b panel): no completion, cells just stay e, 1 tick each.
  -> only patterns of panels present on the level fire.
- Grow facing RIGHT: 2x2 (25,39) -> 4x4 (23,37) = (t-2,l-2). Grow anchor now observed in all 4 facings.
- Slide re-confirmed: 4x4 (31,37) -D-> (33,37).
- Over-budget plain move (18 -> 19) again went the full 4 cells, then GAME_OVER.

## Attempt 6 (L4) — GAME_OVER
- Beam facing LEFT from 2x2 (33,33) along rows 33-34 passed over the item (cells flashed 7) and on to the wall:
  item NOT eaten (H_beamEat refuted). Beams travel over the item like floor.
- 2x2 eats item by moving onto it: (33,25)->(33,23), 17 -> 7 ticks (refund -10 again).
- 2x2 beam facing up from l=31 (row 31): box destroyed, barrier gone (beam rule for 2x2 confirmed).
- Hypothesis H1' (unverified, fits all exit observations incl. the attempt-2 2-cell stop): a move enters the exit only if
  the whole target lies inside the exit structure (L4: rows 28-33, cols 56-61; L1/L2/L3 wins all satisfied this).
  Under H1' the L4 minimum is 20 ticks (19 even with beam-eat).

## Attempt 7 (L4) — GAME_OVER
- Eating the item has no side effects elsewhere on the board (checked all recorded eat steps: barrier/box unchanged).
- Replayed the 19-tick line exactly; every counter reading matched. Final move at used 18 from (29,51) toward the exit
  (target (29,55), col 55 outside the exit structure) again moved only 2 cells to (29,53), then GAME_OVER.
  Second observation consistent with H1' (exit entered only if the whole target lies inside rows 28-33 cols 56-61;
  otherwise the move is treated as blocked and slides). Over-budget plain moves elsewhere went the full 4 cells (x2).
- Search: under H1' the minimum is 20 ticks (with or without a tick-19 win allowance).

## Attempt 8 (L4) — GAME_OVER
- A 2x2 moving into the d barrier is blocked too (2x2 at (29,43) -R-> stays, 1 tick, turns right).
- A beam from a 2x2 facing right point-blank into the d barrier: d flashes and stays (same as L3's 4x4 beam).
  -> the barrier opens only via the switch box.
