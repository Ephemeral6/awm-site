# Run notes (attempt 1)

Result: reached level 4 of `levels_total`, 3 levels completed, then GAME_OVER (bar ran out on level 4).

## Rule table (concepts/ , settled over 97 de-duplicated transitions)

| concept | claim | N | S | C | seen | evidence ids | revisions |
|---|---|---|---|---|---|---|---|
| move_step | ACTION1/2/3/4 move the block up/down/left/right by exactly its own side (4 or 2) | 45 | 1.000 | 0.484 | 0 | 4 | v2: "4 cells" -> "own side" after the shrink |
| facing | after a move, the colour-9 half of the block is on the side it moved toward | 45 | 1.000 | 0.489 | 0 | 5 | v2: NA on a level change (tid 97aa9084) |
| bar_tick | the colour-14 bar (cols 62-63) never grows within a level; it drops in whole 4-cell units | 90 | 1.000 | 0.968 | 2 | 3 | v2: {0,4} -> multiples of 4 (a firing click cost 8) |
| centre_toggle | clicking a right-panel cell flips it 2<->14 and changes nothing else (bar aside) | 21 | 1.000 | 0.223 | 0 | 3 | v2: firing clicks carved out (tid 46e92525) |
| pattern_fire | right panel resets to all 2 exactly when the clicked cells' 14-set equals the left recipe's set | 7 | 1.000 | 0.073 | 1 | 1 | NA on L4 (two-recipe left layout not read); low coverage |
| socket_win | a move whose target square touches the socket's colour-10 interior ends the level | 53 | 1.000 | 0.552 | 0 | 1 | - |
| click_cost (retired) | every effective click costs 4 bar cells | - | - | - | - | - | retired: tid 0464fe66, toggle-back cost 0 |

Abstentions: C is the share of held-out transitions where the concept is not NA. pattern_fire abstains a lot (C=0.073) because it reads panel coordinates only for the L1/L2/L3 layout.

## Mechanisms observed but not written as concepts (drop-audit)

| mechanism | evidence | if dropped, model is | allowed to drop? |
|---|---|---|---|
| first action after /reset is swallowed (frame identical) | tid 2b3e5ed8, then the same action worked from a later state (tid 5b5228f5) | looser in the sense it predicts a move that does not happen once | allowed, but recorded |
| plus-ring recipe (colour 15) shrinks the block 4x4 -> 2x2, keeping the top-left corner and facing | L1 tid b8008204; L4 tid 0f57f600 | stricter: without it the stalk is unreachable | NOT allowed; must go in the model |
| colour-11 recipe teleports the block to the square framed by the colour-11 marks | L2 tid a97af443 | stricter | NOT allowed |
| colour-6 recipe (vertical line) sometimes deletes the colour-6 box and turns the colour-13 barrier into floor | worked once (L3 tid a4766650); no visible effect on 6 other fires (L3 x2, L4 x4) | stricter | NOT allowed; **condition unknown** (see below) |
| colour-13 barrier blocks the move (the blocked move still costs bar) | L3 tid 97fdc924 | looser if dropped (model would allow walking through) | allowed only as an over-approximation |
| colour-14 2x2 square on the board: covering it with the 4x4 block does nothing; it reappears after the block leaves | L4 tids a9960c82, 4385a4f9 | - | role unknown |
| bar empty -> next action gives GAME_OVER | L4 last transition 48b2f909 | stricter | NOT allowed |
| clicking on the board (outside the panel) does nothing | L3 tid 0a171a67 | - | allowed |
| bar cost per action: about 2/3 unit (L1, L3); about 1 per click and 2 per firing click on L4; roughly 1 per move late in L4 | table from transitions | not modelled exactly | per-level numeric data; re-measure every level |

Actions not fully explored: ACTION5/ACTION7 (not in README), ACTION6 on most board cells, and recipe 6 with the block both aligned under the stalk AND facing up after shrinking.

## Open question that cost the run (level 4)

Recipe 6 fired 7 times in total. It worked only once (L3): the 4x4 block was at r13-16 c29-32, facing up, with the stalk on cols 29-30, i.e. over the block's LEFT half.
It failed on L4 in these states:
- 3 fires with the 4x4 block at r21-24 c29-32, facing up, stalk on cols 31-32 (over the block's RIGHT half). This rules out "a fixed number of fires".
- 1 fire with a 2x2 block at r21-22 c31-32 directly under the stalk, but FACING RIGHT.

Hypothesis still alive: the block's left column must sit under the stalk AND the block must face up (9 toward the box).
Best L4 plan for a retry: first move from start (block r25-28 c37-40): shrink (plus ring) -> 2x2 at r25-26 c37-38. Then left x3 to c31, up x2 to r21 so it ends facing up. Then fire recipe 6 (3 clicks). Then down x4 to r29 and right x13 to c57 (socket). That is about 29 actions. Never waste fires.
Fallback if that fails: walk the 2x2 up the stalk into the 6 box.

## Reconciliation (bet -> act -> compare)

Every act was preceded by a written bet (play.py gate 1). Single-step outcomes vs. the bet's main prediction:
- Confirmed: the move/facing/step predictions; shrink effect (L4); teleport destination (L2); socket win (L1, L2, L3); barrier blocks (L3, rival A); toggle predictions; no fire on a foreign recipe (L3).
- Refuted (all recorded, concepts revised or retired): click cost per click; "up/left cost, down/right free"; H9 (center-last click); H1 (3 fires); colour-14 square = refill; H2-without-facing (L4 fire #4); first fire on L4 next to the stalk.
- Settle status at the end: 0 counter-examples open, 6 concepts active, 1 retired, E = 0.178.
