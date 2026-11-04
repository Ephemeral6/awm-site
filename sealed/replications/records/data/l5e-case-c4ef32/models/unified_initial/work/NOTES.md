# Rules learned (attempt 1)

Coordinates: ACTION6 x = column, y = row (verified: click x=30,y=55 changed cell row55 col30).

## Block (player)
- 9/10(a) square, 4x4 or 2x2. ACTION1/2/3/4 = up/down/left/right, step = own side length.
- 9 half = side facing the last move direction (facing).
- First action after /reset was swallowed (whole frame unchanged).
- Blocked by d/c barriers (move costs budget anyway). Moving onto 5 never tested.
- Win: block overlaps the goal box (9 border, a interior) — partial overlap suffices (L1 2x2 one row, L2 4x4 overlapping border row).

## Panel (bottom right 3x3, cells at x in {25,30,35}, y in {50,55,60})
- Click toggles cell 0/2 <-> 14(e). Fires when the set of e-cells EXACTLY equals one of the icons
  shown at the left (icon patterns), then panel resets to all 2. Reusable. Only icons shown on that level work
  (diamond did nothing on L3 where only the vertical-line icon was shown).
- Icons:
  - f diamond {T,L,R,B}: size toggle. 4x4 -> 2x2 (top-left quadrant kept, when facing up).
    2x2 -> 4x4 (observed: 2x2 at (37,15) facing right became 4x4 at rows35-38 cols13-16).
  - b {TL,TM,C}: teleport. 4x4 -> b-reticle interior 4x4. 2x2 -> the 2x2 'f' floor pad (L5: rows37-38 cols15-16)!
  - 6 vertical line {T,C,B}: shot in facing direction; travels while the probe (left column for an upward shot)
    is on floor; hitting a 6-bordered box removes it and removes the barrier whose colour equals the box interior.
- ee floor pad (colour 14): refill budget once (L5: +10 units), consumed.

## Budget bar (cols 62-63, colour 14)
- Per level budget B units (L3: 50, L4: 35, L5: 35, L2 ~25). Each action 1 unit, a firing panel click costs 2.
- display rows = 2*ceil(32*rem/B). At rem 0 one more action still executes (L4 won at rem 0).

## L5 failure
- Teleported as 2x2 after shooting the d-box -> went to f pad in room A, not the reticle. Should grow back to 4x4
  (diamond) inside the upper-right area (e.g. 2x2 at (17,45) area rows 17-20 cols 41-48) before teleporting,
  then 4x4 climbs 13,9,5,1 into goal. Budget was too tight for that order given my route.

## Exhaustion
- Bar reached 0 (rem 0) -> next non-winning action => GAME_OVER (whole game ended at level 5, 4 levels completed).

## Size-toggle placement (2 samples)
- shrink: 4x4 at (r,c) -> 2x2 at (r,c).  grow: 2x2 at (r,c) -> 4x4 at (r-2,c-2).

## L5 cost analysis for a next attempt (B=35, refill +10, last winning move may land at rem 0 => 46 usable)
- c-box shot from (25,21) facing up: 2 moves + 4 = 6
- to room B via refill (37,49) and on to (25,45): 14
- shrink 5; up x5 + right 1 + shot 4 = 10
- down to (17,47) 1, grow -> 4x4 (15,45) 5, teleport (4x4 -> reticle) 4, climb 13,9,5,1: 4  => 14
- total 49 > 46. Untested savers: can a 4x4 move with half its footprint over background 5 (the shot only
  probes one column)? If so climb the d-stem as 4x4 to (17,45) before shrinking (saves 2).
  Still 1 short -> some mechanic is still unknown (refill amount rule? teleport target rule?).

## Formal system (after attempt 1)
- work/model/{l5map,rules,fast,search2,variants,gen,replay}.py ; lean/L5Model.lean (defs), L5Data (map + untrusted cert),
  L5Proof + L5Rows0-3 (kernel re-check, 128 chunks), L5Main (MAIN: L5.L5_unwinnable), L5Structure (IsLimit/IsColimit).
- Replay: 41/41 observed L5 transitions reproduced.
- Strict model (full-footprint moves, grow needs walkable footprint): min net spend 36 > 35 => unwinnable (proved).
- Relaxations that make it winnable (search, work/model/variants.json): partial-footprint (top-left probe) moves -> net 34;
  grow allowed into walls -> net <= 34. Blocked-move facing change alone does not help.
- NEXT ATTEMPT plan (net 34 if partial-footprint moves work): same as before up to 4x4 at (25,45) [17 actions, refill taken],
  then U (test! into the 2-wide d-stem) , U -> (17,45); shrink -> 2x2 (17,45); R -> (17,47); grow -> 4x4 (15,45);
  shot (4x4 facing right, relies on the top row being the probe); teleport -> (17,33); U x4 into goal.

## Attempt 2 (L5 replayed; lost again, stopped at rem 0 without the game-ending action)
- Service resumed at L5 start (no /reset needed); first action not swallowed.
- A1 CONFIRMED: 4x4 at (25,45) pressing up into the 2-wide d-stem is blocked (full-footprint collision).
- NEW: a blocked move still turns the block (facing left -> up). R1 revised (Python + Lean).
- A2 CONFIRMED: diamond on 2x2 at (21,45) (no walkable 4x4 quadrant) -> block flashes colour 4, stays 2x2, cost paid.
- NEW: clicking a power icon (x=4,y=4 diamond) marks its pattern cells as 0 on the panel, costs 2, fires nothing.
- 4x4 at (15,45) facing right: shot hits the d box (top-row probe consistent).
- Budget: one step was charged ~1 less than the model (rem 8 where 7 predicted) - unexplained.
- With the revised rules the strict model still needs net 36 > 35 (gen.py H(start)=46).
- End of attempt 2: at bar 0, clicking the teleport icon (x=4,y=15) did NOT end the game and marked TL,TM,C as 0
  => icon clicks appear to cost nothing (revise: the earlier "icon click costs 2" inference is wrong; the one-unit
  discrepancy in the bar is then elsewhere). The next panel click (TL -> e) ended the game: GAME_OVER, 4 levels completed.
- Bar refit over all 43 attempt-2 transitions: B=35, move/blocked move/click 1, firing click 2, ICON CLICK 0, refill +10,
  0 mismatches; GAME_OVER exactly when rem < 0 after a non-winning action (last click took rem 0 -> -1).
  The earlier "rem 8 vs 7" discrepancy was my mis-charging of the first icon click.

## Attempt 3 (L5, exploration; GAME_OVER, 4 levels completed)
- Panel marks (0 cells) survive the level reset (teleport-icon marks from attempt 2 were still there).
- Icon click with e-cells present: replaces marks by the icon pattern, keeps e-cells; never fires (also with pattern
  minus one cell selected); cost 0.
- Walking a 4x4 over the f-pad: no effect, pad stays.
- Refill is additive +10 (taken at rem 13 -> 23; before at rem 19 -> 29).
- 2x2 teleport from room B (25,45) facing left, d closed -> f-pad again. From ON the f-pad -> stays on the f-pad.
- Grow on f-pad facing left -> 4x4 at (r-2,c-2) again (placement independent of facing). While the 2x2 sits on the
  f-pad, f-coloured corner marks are drawn around rows 35-40 cols 13-18.
- Click on an empty board cell: free, frame unchanged. Click on panel frame x=27,y=50 toggles TL and costs 1
  (cell hit areas wider than the drawn 3x3 cells).
- Final move at rem 0 -> GAME_OVER (rem<0 rule confirmed again).

## Attempt 4 (L5; GAME_OVER exactly as predicted, 4 levels completed)
- Free probes: clicks on c-box, d-box, block, barriers, reticle, goal, pads, stem, b mark, and floor cells adjacent to
  the block: all inert (frame unchanged) and free.
- Panel click on the border row y=52 toggles TM only: one cell per click, no multi-select.
- Played the model-optimal route (net 36). Every bar reading matched the model; the 4x4 reached (5,33), one move
  short of the goal, and the game ended at rem -1 exactly as R7 predicts.
- concepts/_lib.me fixed (only scanned rows 15-44).

## Attempt 5 (L5, exploration; GAME_OVER, 4 levels completed)
- NEW RULE: moves advance in 2-px sub-steps and stop at the last free one. 4x4 at (17,33) pressing up against the
  closed d barrier (rows 11-13) moved to (15,33). A 2x2 at (15,33) pressing up did NOT move 1 px (sub-step 2 px).
  R1 was stricter than the game. Re-search with sub-steps: minimum still H0 = 46 (net 36) -> no new route.
- Shrink facing down keeps top-left. 2x2 teleport facing down (room A) and facing up (reticle corridor) -> f-pad
  (now 5 samples, 4 facings). 4x4 teleport from room A (35,13) -> reticle (17,33).
- Shot up into the closed d barrier from below (d-box present): no effect.

## Attempt 6 (L5, exploration; GAME_OVER, 4 levels completed)
- Rotated shot pattern (horizontal line ML,C,MR; no such icon shown) does not fire.
- Panel corner click (27,52) toggles TL only (hit areas partition the panel; one cell per click).
- NEW: grow tries another quadrant when the default (r-2,c-2) is blocked: 2x2 at (15,43) facing left -> 4x4 at
  (15,41) (i.e. (r, c-2)). The model already allows every walkable quadrant (superset), so the bound is unaffected.
- concepts/block_move v1.4: size change -> NA (cross-reset transition).

## Attempt 7 (L5; GAME_OVER, 4 levels completed of levels_total = 6)
- levels_total = 6 (read from the response).
- Shrink while the 4x4 covers the f-pad -> 2x2 at (37,13) (top-left kept, no snapping).
- Whenever the block is 2x2, f-coloured corner marks frame the f-pad (rows 35-40 cols 13-18): the display marks the
  teleport target for the current size (b reticle for 4x4, f-pad for 2x2) - consistent with R4.
- A 2x2 walking exactly onto the f-pad: plain move, nothing triggers.

## Attempt 8 (L5; GAME_OVER exactly as predicted, 4 of 6 levels completed)
- Free probes: clicks on the budget bar, between icons, icon-frame corner (= diamond icon: marks pattern), empty
  screen right of / above the panel - all free, none affects the board.
- Played the model-optimal route again: GAME_OVER with the 4x4 at (5,33), one move short of the goal, as predicted.
