# Level 5 plan (written before acting)
Map: socket rows 1-4 c33-36 (open below); corridor c33-36; 13-barrier r11-13 c33-36; pocket r14-20 c33-36 with
11-marks framing r17-20 c33-36 (teleport target). Box1 6-frame / 12-interior r9-12 c20-23, stalk c21-22 r13-24 down to
left region (r25-40 c13-28). 12-barrier r33-36 c29-31 joins left and right region (r25-40 c37-52).
Box2 6-frame / 13-interior r14-17 c55-58, horizontal stalk r15-16 c49-54 from upper area (r15-20 c41-48),
which connects to right region via stalk c45-46 r21-24. Items: 15-colour 2x2 r37-38 c15-16; 14-colour 2x2 r37-38 c49-50.
Block 4x4 r29-32 c17-20 facing down. Recipes: plus ring (shrink, mask 170), teleport (cells 0,1,4 mask 19), vline (open6, mask 146).
Steps: R,U -> fire vline (open 12-barrier); D,D,R x6,U,U -> r25 c45; shrink; U x5, R -> 2x2 r15 c47 facing right;
fire vline (horizontal analog of ocCand); teleport; U x7 to socket. ~38 actions.

## Attempt-2 outcome on L5 (facts)
- open6 at box1 (vertical stalk) and box2 (horizontal stalk r15-16, 2x2 at r15 c47 facing right) both worked.
- 14-square r37-38 c49-50: +36 bar cells when the 2x2 stepped exactly onto it; consumed (did not reappear).
- teleport recipe (cells 0,1,4) with a 2x2 block sent it to the 15-pad r37 c15 (left region), NOT to the 11-framed
  4x4 square r17-20 c33-36. The 15-pad is not consumed (reappears when left).
- Re-entering the 15-pad by a move (last action, GAME_OVER at bar 0): block stayed 2x2; four colour-15 corner marks
  appeared at (35,13),(35,18),(40,13),(40,18) around it. Meaning unknown (frames a 4x4 at r36-39 c14-17?).
- Costs on L5: ~4 cells per action, a few free; firing click 8.

## Attempt 3 plan (written before acting)
Budget check: every route I can build that ends with a 4x4 in the pocket costs 42-51 actions (~175-210 cells)
vs 128 + 36 refill. So a win needs an unseen mechanism; this attempt prioritises the decisive tests:
 T1 (3 moves): 4x4 L,D,D -> r37 c13, covering the 15-pad. Does a 4x4 cover do anything (shrink? marks?)
 T2: shrink (4 clicks) -> 2x2 r37 c13; R -> exactly on the pad r37 c15 (marks?); plus ring (4 clicks): grow?
 T3: teleport fired by whatever size results: where does it land (4x4 -> pocket r17 c33?)
 Keep watching: bar per action, free actions.

## Attempt-3 outcome on L5 (facts)
- 4x4 covering the 15-pad: no effect. 2x2 exactly on the pad: four 15 corner marks appear.
- Plus ring on a 2x2 GROWS it to 4x4 (on the pad: (37,15)->(35,13); off the pad in the pocket: (17,33)->(15,33)).
  The pad is not needed. Bottom row is kept; horizontal placement shifts (fit?).
- 4x4 teleport -> r17 c33 (pocket), both from the left region and from inside the pocket.
- Box2 does NOT open from a distance: 4x4 at r15 c33 facing right, in line with its stalk rows 15-16, fired vline -> nothing.
- Costs: 4 per move/click, 8 per firing click, ~1 action in 8 free. A firing click that takes the bar below 0 -> GAME_OVER at once.
Shortest known winning route (logic): R,U, vline | D,D,R x6,U,U | shrink | U x5,R | vline | grow | teleport | U x4
 = 39 actions, 5 fires -> ~156-164 cells vs 128 (refill detour is roughly cost-neutral). Still over budget.

## Attempt 4 plan (written before acting)
Model says L5 is ~8 units over budget, so look for unmodelled mechanisms, cheapest first:
 P1 click on a LEFT recipe panel (shrink recipe, x=5,y=5): does it fire / fill the right panel?
 P2 ACTION5 / ACTION7 (undocumented): rejected, no-op, or something (undo?)
 P3 4x4 move overlapping background (r29 c13 -> left): blocked?
 P4 board clicks on pads / marks / socket.
Then, if nothing changes the arithmetic, play the 38-action l5Best line and watch the bar.

## Attempt-4 outcome on L5 (facts)
- Clicking a LEFT recipe panel costs 0 units and shows that recipe as colour-0 hints on the right panel;
  clicking it again does nothing. Clicking a hint cell costs 1 unit (an ordinary panel click).
- ACTION5 is rejected by the service ("action must be one of [1, 2, 3, 4, 6]").
- Board clicks (pads, pocket) cost 0 units and change nothing.
- A 4x4 whose square covers the 14-pad aligned to its 2x2 sub-grid consumes it: refill = 10 units (same as a 2x2).
- Blocked moves cost 1 unit and still TURN the block to face the action's direction.
- Moves are partial: a 4x4 whose full target is blocked moves as far as the floor allows (r15 c43 -> c45).
- Grow of a 2x2 at r17 c45 facing up -> 4x4 r15 c43 (growTo prediction held).
- Box2 opened from the 4x4 at r15 c45 facing right (ocHoriz), reached via the partial move.
- Exact cost model: unit costs (move/click 1, firing click 2, left/board clicks 0, refill -10), B = 35,
  display = 4*ceil(32*(35-u)/35). Alive at u = 35 (display 0); the next action executes and gives GAME_OVER.
- work/l5_search.py (Dijkstra over these rules): cheapest win = 37 units > 35, for granularity 1 and 2.

## Attempt 5 plan (written before acting)
work/l5_variants.py: of the single-rule variants, only "open from a distance in line with the stalk" brings
the cheapest win under 35 (21 units): tp; shrink; U; R; vline; U x6.  Attempt 3 refuted it for a 4x4 whose rows
(15-18) do not match the 2-row stalk; a 2x2 exactly in line (rows 15-16) was never tested. Floor-only rays don't help (37).
Plan: teleport 4x4 -> pocket r17 c33; shrink -> 2x2 r17 c33; U -> r15; R -> r15 c35 facing right; vline.
 If box2 opens: climb U x6 (r13 .. r3 touches the socket). If not: ~20 units left for further probes.

## Attempt-5 outcome on L5 (facts)
- Distance opening refuted again, now for a 2x2 exactly in line with box2's stalk (r15 c35 facing right, rows 15-16): no open.
  ocBox (adjacency) holds on 13 fires.
- The 14-pad is gone for good after consumption by a 4x4 (checked in the attempt-4 record).
- A 2x2 teleport lands on the 15-pad (marks appear); teleporting again from the pad leaves it there.
- Grow on the pad -> r35 c13; partial move D -> r37 c13; blocked U turns only; u = 35 alive (display 0); next action executes + GAME_OVER.
  All predicted by the model (no counterexample except pad_grow's over-wide scope, retired).

## Attempt 6 plan (written before acting)
Model: cheapest win 37 > 35. Unread by the rules: clicks on the block itself, on boxes, barriers, socket, bar, stalk mouths.
Probe them first (board clicks so far cost 0 and did nothing). Then play l5Best37, watching for any deviation.
