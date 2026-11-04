# Attempt 1 — notes (game ended GAME_OVER on level 4; levels 1–3 beaten)

## Rules established (concepts/ ledger, all S=1.000 at settle; N / coverage in brackets)
- move_dir [N=35]: ACTION1/2/3/4 = up/down/left/right. The piece (4x4 or 2x2, two halves of 9 and 10(a))
  slides one piece-length; it's cut short at walls (clamp); the 9-half then faces the move direction.
  The very first action after reset produced an unchanged frame (swallowed).
- bar_tick [N=61]: the right-edge bar (cols 62-63, colour 14) only ever empties from the top, whole 2-row notches.
  Cost per action is a per-level number: L1–L3 ≈ 2 notches per 3 actions (≈48 actions total);
  **L4 ≈ 1.75 notches per action (≈18 actions)**; commits with an animation cost +2..3 extra.
  **Empty bar => the next action gives GAME_OVER.**
- click_toggle [N=16]: ACTION6 on a cell of the 3x3 panel (cells at rows 49/54/59, cols 24/29/34, 3x3 each)
  toggles 0/2 -> 14 (selected), 14 -> 2.
- commit_clears [N=8]: when the selected set equals a pattern that belongs to the level, it commits:
  panel goes all 2, piece flashes in the pattern colour, effect is applied.
  Works without the 0 hints too (L3 2nd commit, L4) — the pattern is shown in the legend panel(s) at left.
- win_touch [N=41]: a direction move whose full-step box overlaps the 9/10 goal box wins the level (partial overlap is enough).

## Pattern effects (by legend colour)
- f, plus shape (cells (0,1),(1,0),(1,2),(2,1)): shrink 4x4 -> 2x2, keeps the TOP-LEFT quadrant (seen facing up, L1 and L4).
- b, L-tromino ((0,0),(0,1),(1,1)): teleport piece onto the b corner-marks.
- 6, vertical line ((0,1),(1,1),(2,1)): when it works, removes the 6-box (top) and turns all d (13) door cells into floor.
  Worked: L3, piece 4x4 at cols 29-32 directly under stem cols 29-30 (stem under the piece's LEFT half), facing up, adjacent to the stem.
  Failed: L3 piece far away; L4 twice with 4x4 piece at cols 29-32 under stem cols 31-32 (stem under RIGHT half), facing up.
  Untested: 2x2 piece directly under / inside the stem (ran out of bar right there).

## Level 4 plan for next attempt (budget ≈18 actions — no exploring!)
Start: piece 4x4 rows 25-28 cols 37-40; stem cols 31-32 rows 9-20; 6-box rows 5-8; door d cols 45-47 rows 29-32;
goal box rows 28-33 cols 57-62; unknown 2x2 'e' object at rows 34-35 cols 23-24.
Best guess route: left, left, up (piece at rows 21-24 cols 29-32) -> shrink (4 clicks) -> 2x2 at rows 21-22 cols 29-30 ->
right (cols 31-32, under stem) -> 6-commit (3 clicks) -> then 2x2 needs ~4 down + ~13 right: TOO LONG for budget.
So the intended route is probably different: e.g. shrink first while the piece's top-left lands under col 31
is impossible (4x4 lefts are always odd); consider whether the 'e' 2x2 object refills the bar, or whether the
6-commit only needs the 2x2 piece *inside* the stem. Re-plan carefully before acting.

# Attempt 2 (stopped deliberately on L4 with ~3 actions of bar left; not GAME_OVER)
- Probe click after restart landed on a fresh L4 (full bar). Boundary transition f24f3579c4d9a836 scoped out (NA).
- e square (rows34-35 cols23-24): covered fully by the 4x4 piece -> no bar refill, square stays. Inert to touch.
- 6-commit with 4x4 at top21 left29 FACING RIGHT: no door effect. Animation (work/frames/1793614854658_*):
  piece's 9-half flashes 6 four times, then a 4-tall x 2-wide beam (colours 6/7) travels RIGHT from the
  piece front, 2 cols/frame, along rows 21-24, until col 44 (region wall), then vanishes.
  => The 6-pattern FIRES A SHOT in the facing direction from the piece's front.
     L3 success = shot went up the stem and hit the 6-box (box gone + all d -> floor).
     L4 facing-up failures = shot blocked at once (stem only under the right half).
- NEXT L4 PLAN (9 actions, fits budget ~18): from start (top25,x37): ACTION2 (top29), ACTION4 (x41, face R, rows 29-32),
  6-commit clicks (30,50),(30,55),(30,60) -> shot travels right along rows 29-32 and hits the d door at col45.
  If that opens the door: ACTION4 x4 (45,49,53, touch goal). Untested: whether a shot hitting d directly removes it.
  Fallback if not: shot must hit the 6-box (needs a 2x2 piece at col 31 facing up -> over budget).
- Attempt 2 ended GAME_OVER on L4: bar emptied after the move to x33 facing R (rows29-32); next click -> GAME_OVER (empty_bar_gameover confirmed a 2nd time). Door-shot test still untested.

# Attempt 3 (GAME_OVER on L4)
- Played the 9-action shot route: down, right (x41 y29 face R), LINE commit. Shot (frames 1793615144960_*) went INTO the
  d door (d cells drawn over by the beam), reached col 48, then vanished; d cells redrawn: door NOT removed. H_shot refuted.
- Shot left along rows 33-36 passed over the e square (cols 23-24) to the col-21 wall: e unchanged, bar unchanged.
- PLUS while facing LEFT at top33 x37: 2x2 at rows 33-34 cols 37-38 => shrink keeps TOP-LEFT regardless of facing.
- Remaining open questions for L4: how else the 6-box can be hit (only via stem col 31-32), whether PLUS on a 2x2 grows,
  whether the e square reacts to a 2x2 piece, whether budget/drain is affected by anything.

# Attempt 4 (L4, experiments)
- H1'' CONFIRMED: 2x2 at (y23,x31) facing U, LINE commit -> shot up the stem: 6-box -> floor (rows5-8 cols30-33 = 2),
  door d cols45-47 -> floor. (frames saved)
- H2 REFUTED: PLUS on a 2x2 GROWS it: 2x2 (y23,x31) -> 4x4 (y21,x29): grow shifts by (-2,-2) (not top-left kept).
  => shrink+grow moves the 4x4 lattice by 2: 4x4 at x=37 -> S+G -> x=35 -> left -> x=31.
- Off-panel clicks (e square, background, piece): FREE (no bar change), panel flashes 8 four times (13 frames), no effect.
- Clicking a legend panel (x5,y5 f-plus; x5,y15 6-line): FREE, loads that pattern into the 3x3 panel as 0-hint cells
  (replacing the previous hint). Clicking a hint cell still costs a normal click (2 notches).
- Costs this attempt: plain ~7 units (1-2 notches), commits ~14 units (3-4 notches). Budget 128 units.
- Shortest route now known (R1, 21 actions, 3 commits ~168 units > 128): PLUS(4) PLUS(4) [4x4 at y23 x35], left (x31),
  up (clamped to y21, face U), LINE(3) [door opens], down x2 (y29), right x5 (35..51), right (touch). STILL OVER BUDGET.

# Attempt 5 (GAME_OVER on L4, 16-action shot-to-goal route)
- Panel hint persisted across the restart (LINE hint loaded at end of attempt 4). PLUS selection still committed with a
  hint 0 left on the panel => commit_clears v3: commit iff the selection equals a level pattern (hints irrelevant).
- Route: D, L (4x4 at 29,33), PLUS -> 2x2 (29,33), D, L, U -> (29,31) face U, LINE -> door opened (H1'' holds at y29),
  R -> (29,33) face R, LINE -> shot ran right along rows 29-30 through the open door to cols 54-55, then vanished;
  no level change; that same action took the bar 2 notches -> 0 and returned GAME_OVER (the emptying action itself can end
  the game: empty_bar_gameover v2). H_shotwin NOT confirmed (shot stopped one column short of the goal box; confounded by
  the simultaneous GAME_OVER).
- Bar accounting matched the 7/14-unit model exactly up to the last action.

# Attempt 6 (GAME_OVER on L4, experiments)
- ACTION5/ACTION7 rejected by the service ("action must be one of [1, 2, 3, 4, 6]").
- L-tromino selection on L4: NO commit (cells stay selected) => commit_clears v4: only the level's legend patterns commit.
- e SQUARE IS A BAR REFILL: 2x2 piece moving right from (33,21) to (33,23) (front col 24 over e) consumed e and the bar
  went 12 -> 44 rows (+16 notches, refill ~68-75 units incl. the move cost). 4x4 covering e with its BACK half
  (arrived facing L, attempts 2 and 6) did NOT consume it. Open: H_front (front-half overlap triggers pickup for any size).
- Grow facing DOWN: 2x2 (35,23) -> 4x4 (33,21) = (-2,-2) again. Shrink facing DOWN keeps top-left.
- Planner (work/plan_e.py): with pickup only by 2x2 overlap, no route fits for any refill <= 75. With H_front:
  18-action route (203 units, cap 128+refill, needs refill >= ~69):
  L L L D | PLUS(shrink 29,25) | PLUS(grow -> 4x4 27,23) | D (31,23 facing D: front rows 33-34 over e -> pickup) |
  R R (31,31) | D (clamp 33,31) | U (29,31 face U) | LINE (door) | R x6 (35..51, touch).

# Attempt 7 (GAME_OVER on L4, the 18-action H_front route)
- Exact budget model (18 units; move/click 1; committing click 2; pickup +10) predicted EVERY bar reading this attempt.
- H_front CONFIRMED: 4x4 moving down to (33,23) with its front half (rows 35-36) over e consumed it; bar 3-1+10 = 12 units.
- A 4x4 at x31 facing up also opens the door (shot from col 31 works for the 4x4 too).
- Route L L L D, shrink, D, grow (4x4 29,23), D (pickup), R R U, LINE, R x5 reached (29,51) with 0 units left.
- Final R from (29,51): piece clamped to (29,53) against the goal box, state GAME_OVER, no level change.
  => a move taking the budget to -1 does not win (budget check first), OR win_touch needs the piece flush against the box
     (all three earlier wins started flush/adjacent-in-one-full-step). Either way 29 > 28: level 4 not winnable this way.

# Attempt 8 (GAME_OVER on L4, experiments)
- Second click on an already-loaded legend: free, 22-frame demo (hint cells light up one by one), no commit.
- Commit with the matching hint loaded costs the same (PLUS still 5 units). No hint discount.
- Pickup reproduced (front half of 4x4 at (33,23)): +10 units again.
- X shape and full 3x3 selection: no commit on L4 (H4 now tested on 4 shapes: L-tromino, X, all-9, plus/line positives).
- Blocked move costs 1 unit.

# Audit session, attempt A1 (service restarted; replayed L1-L3; GAME_OVER on L4)
- L1->L2 transition clears the panel selection (probe cell (2,2) gone; L2 hint loaded). With the attempt 4->5 evidence
  (restart cleared selection, kept hint): pre-selection cannot be carried into L4.
- Planner with free shrink/grow quadrants found a 28-unit route needing GROW FACING LEFT -> (0,-2). Tested: grow facing L
  -> (-2,-2). Refuted. Also shrink facing R -> top-left, grow facing R -> (-2,-2). Placement now tested on all facings.
- PICKUP RULE REVISED: 4x4 at (31,23) facing D (front rows 33-34 over e row 34) did NOT pick up => H_front refuted.
  4x4 at (33,23) facing D picked up (3rd time). All 6 contacts fit H_tl: pickup iff piece top-left == (33,23)
  (2x2 (33,23) yes; 4x4 (33,23) yes x3; 4x4 (33,21) no x2; 4x4 (31,23) no). The Lean pick rule is looser (safe).
