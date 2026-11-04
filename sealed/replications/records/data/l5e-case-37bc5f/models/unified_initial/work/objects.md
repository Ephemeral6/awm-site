# Objects and rules (attempt 1) — Lean: lean/L5eModel.lean

## Objects and their slots (each kept slot has a pair of positions it separates)

| object | slot | pair that becomes indistinguishable if the slot is dropped |
|---|---|---|
| Blk | row, col | block at r25 c37 vs r21 c29 on L4: one ACTION1 moves the first to r21 c37 and the second into the stalk (blocked). Different futures. |
| Blk | size | 4x4 vs 2x2 at r21 c29: ACTION4 moves by 4 vs by 2 (move_step); only the 2x2 fits the stalk |
| Blk | face (attempt 4: also set by blocked moves) | 2x2 at r21 c31 facing up vs facing right: under the candidate open condition the 6-recipe opens the barrier only for the first (the L4 fire #4 that failed was facing right) |
| panel | 9-bit mask of colour-14 cells | mask {1,4} vs {}: clicking cell 7 fires the vertical-line recipe only from the first |
| St | gates[i] (attempt 2; replaces Gate) | identical block at r29 c41 on L4: ACTION4 enters c45 only if gates[0] (L3 tid 97fdc924: blocked when closed). The attempt-1 slot boxPresent was dropped: it always equalled not barrierOpen |
| St | pads[i] (attempt 2) | L5 2x2 at r35 c49: ACTION2 refills +36 only if pad 0 is unused (consumed in tid 88632a96, did not reappear) |
| BoxSpec | orient, row, col (attempt 2) | 2x2 at r15 c47 facing right opens L5 box2 (horizontal) but would not open a vertical box with the same anchor (oc_branches_differ) |
| Blk | size via growTo (attempt 3) | 2x2 at r17 c33 vs r37 c15 firing the plus ring: they grow to (15,33) vs (35,13) (column choice depends on the floor) |
| Level | tp (attempt 2) | the same teleport fire from a 2x2 vs a 4x4 lands at r37 c15 vs r17 c33 |
| Status | playing/won | a move after winning is a no-op in the model; it separates "level ended" from "still here" |
| Level | floor, goal, recipes | per-level data: two levels with the same St differ in which moves are blocked / win / which recipes fire |

## Rules (functions; domain = where they are executed)

- R-move `moveRule L s d` (amended attempt 4), domain: ACTION1-4, any St. The block sweeps k = 1..size cells. A square touching the socket interior wins. Otherwise it stops at the last square that is all floor (a partial move is possible). If even k = 1 does not fit, it does not move but turns to face d. Cost 1 in every case.
- R-click `clickRule L s i`, domain: ACTION6 on right-panel cell i<9. It toggles bit i. If the new mask equals a recipe of L, the panel clears and that recipe's effect applies.
- R-fire `applyEffect L s e`, a copairing of three branches:
  - shrink (attempt 3: a size TOGGLE, copairing over SzCase): 4x4 → 2x2 keeping top-left and facing; 2x2 → 4x4 via `growTo` (top row −2, first column of l−2, l−1, l that fits the floor; observed (37,15)→(35,13) and (17,33)→(15,33)).
  - teleport: moves the block to `tpDest L size` (attempt 2: destination depends on size).
  - open6: `gates[i] ||= ocBox boxes[i] blk` (attempt 2: per box, condition defined).
- R-open `ocBox`, a copairing over Orient:
  - vertical stalk: facing up, block col = stalk left col, block row = stalk bottom + 1.
  - horizontal stalk: facing right, block row = stalk top row, block col + size = stalk left col.
- R-refill (in moveRule, amended attempt 4): an unused pad lying inside the block's new square, aligned to its 2x2 sub-grid, is consumed (either size); refill = 10 units on L5.
- R-budget `alive C ks`: the action number k is sent with spent = costSum of the first k kinds, and it must be < budget + refill gained in the first k (gainSum).

Attempt 2: the open condition became a definition. Attempt 3: size growth exists (plus ring on a 2x2) and is in the model. The 15-pad turned out to have no rule of its own (marks only). Box2 does not open from a distance.

Attempt 4: moves can be partial and blocked moves turn the block. A 4x4 can take the refill. Left-panel and board clicks cost 0 and change no modelled slot. Exact unit costs: B = 35 on L5.
