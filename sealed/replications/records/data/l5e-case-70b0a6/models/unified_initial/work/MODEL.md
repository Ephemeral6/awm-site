# Formal system (attempt 1; first version — nothing to amend yet)

Two layers:
- **Grid layer** = `concepts/*.py`: executable rules on 64x64 frames (domains are their SCOPE; checked by `settle`).
- **Region layer** = `lean/L5Model.lean`: an abstraction of level 5 that the proof runs on, with structure in `lean/L5Structure.lean`.

## a. Objects and slots (with a pair of positions each slot tells apart)
| object | slot | positions that become indistinguishable without it |
|---|---|---|
| Agent | pos (row,col) | agent at (25,45) vs (25,49) in L5: only the first can enter the stem |
| Agent | size 4/2 | 4x4 vs 2x2 at (25,45): only the 2x2 passes the 2-wide stem (B→C) |
| Agent | facing | L4 (19,31) small agent facing up vs facing right: only facing up fires the 6-box |
| Barrier block (colour 12/13) | present | 13-block present vs gone: Pad→goal climb blocked vs open |
| 6-box (frame 6, core k) | present, core colour | fire with the lane on the 12-box vs on the 13-box: different barrier removed (L5) |
| Corner-marker frame (11 / 15) | present | 15 frame present vs absent: teleport lands at the 15 item (room A) vs the 11 pad |
| Panel | 3x3 set of highlighted cells | {(0,1),(1,1)} vs {(0,1),(1,1),(2,1)} highlighted: the next click on (2,1) fires the switch vs only highlights |
| Target patterns | colour + cell set (per level) | L3 (6-line) vs L1 (15-cross): same clicks, different effect |
| Bar | units used (0..32) | bar 0 vs bar 2 rows: a non-winning action ends the game vs doesn't (L5) |
| 14 item | present | present vs eaten: stepping there refills the bar vs doesn't |
| Goal box | position | — (needed for goal_reach) |
Region layer keeps: loc (A/B/C/Pad/Won), big, cGone, dGone, fFrame. Dropped there: exact pos/facing (folded into walk/lane preconditions), panel (completions are atomic), bar, 14 item.

## b. Rules (grid layer = function on frames; region layer = function St → St)
| rule | grid-layer concept | region-layer definition | status in proof model |
|---|---|---|---|
| move | move_dir, blocked | `walkRule` (macro) | definition |
| panel highlight | panel_toggle | folded into atomic `complete` | consequence (atomic macro; see 5) |
| pattern completes → panel clears | panel_complete | folded into `complete` | consequence |
| shrink (15) | shrink_f + observed 15-frame appearance (L5) | `shrinkRule` | definition |
| teleport (11) | teleport_b v2 + observed priority of the 15 frame (L5, twice) | `teleportRule` | definition |
| switch (6) | switch_6 v3 (up-lane) + L5 facing-right firing (observed, outside scope) | `switchRule` | definition |
| goal | goal_reach | `climbRule` | definition |
| bar cost / refill / out | bar_tick, pickup_14, bar_out | — | **not in the model** (removing them only makes the model more permissive) |

## Not-in-model / abstraction audit (direction)
- Bar dropped → model more permissive (safe for an "unreachable" claim).
- Positions inside a region collapsed → walks are allowed whenever the region-level precondition holds → more permissive.
- Fire lanes: allowed from the whole region (A for the 12-box, C for the 13-box), any facing → more permissive. Geometry: no other cell of the L5 map has a straight lane of floor ending at either box (read off the frame).
- **Stricter than the game, possibly**: (i) no rule makes the agent big again or removes the 15 frame (untested: 15 completion while small; stepping on the 15 item); (ii) teleport with a 15 frame always goes to room A (seen 2/2); (iii) actions 5/7 and clicks outside the panel do nothing (untested).

# Attempt-2 amendments

## Objects (changed)
- Agent: unchanged slots, but **facing** now matters in the proof layer: L3 tid 0c08d5210e5ba7ba/23fa16457665e8e0 — agent at (25,29) facing right, clear up-lane to the 6-box, no fire; facing up at (21,29), fire. Without facing, the grid search found a 29.3-unit route that fires while facing the wrong way.
- 15 frame: now also *removed* (by grow), not only created by shrink.
- Bar (new in the proof layer): running cost in tenths; slot `r` of `playB`.
- 14 item: present/eaten (`ee`), now in the proof layer.

## Rules (changed / new)
| rule | grid concept | region layer (L5Model) | grid layer (L5Grid) |
|---|---|---|---|
| size toggle (15) | shrink_f + **grow_f** (new) | `sizeRule` = shrink on big, grow on small | `step` codes 4, 5-8 (grow: any of 4 placements, permissive) |
| move | move_dir + **blocked v4** (slide) | `walkRule` | `move` (slide 1 cell for big) |
| switch (6) | switch_6 v3 | `switchRule` | `laneHit`: facing direction only; any lane across the width (permissive) |
| teleport (11) | teleport_b v2 | `teleportRule` | code 11 |
| refill | pickup_14 | not in region model | `place` (-8.1 units net) |
| bar | bar_tick, bar_out | not in region model | `playB` cap 320 tenths; cost 9/action, +10 per completion |
| target thumbnail click | **thumb_hint** (new) | not in model (panel hint only; no state change) | treated as a free no-op (codes ≥ 12) |

Retired: L5Model.l5_unwinnable (its premise "nothing makes the agent big again" was falsified by grow_f).

# Attempt-3 amendments
- Rule **grow_place** (new concept `concepts/grow_place.py`): grow puts the small agent as the forward, right-hand quarter of the big one: up → (r,c-2), right → (r-2,c-2); down/left are rotations, untested. Lean: `L5G.growIdx`/`L5G.growEst`, checked against both observations (`growEst_obs_up`, `growEst_obs_right`). It is one of the four permissive grow codes, so the permissive grid model contains it (the permissive model stays in the proof; it only widens the reachable set).
- shrink_f confirmed when facing right: keeps the top-left corner whatever the facing (no change to the definition).
- Premise P3 is now mostly established: every off-panel click is free and changes nothing on the board (error blink); ACTION5/7 are rejected by the service; a big agent covering the 15 item changes nothing; the refill is a fixed +16 rows. Still untested: a small agent walking onto the 15 item.
- Objects: Facing, which was already a slot, now also selects the grow placement. Pair: small agent at pixel (17,47) facing up vs facing right → grows to (17,45) vs (15,45) (`grow_branches_differ`).

# Attempt-5 amendments
- Rule grow_f v2: scope narrowed to grows whose grow_place target fits on floor. Refuted by tid 821d9d4677ca0bb8: grow in the 2-wide stem fails, the agent and frame are unchanged, the panel clears, and the completion is charged. The Lean grid model already had this branch (`step` codes 5-8 → (s, 46) when the placement does not fit); `lean/L5GridObs.lean : obs_grow_fails` replays it.
- Touching a 6-box is blocked like a wall (`obs_touch_box_blocked`). Point-blank fire works (`obs_fire_point_blank`). A small agent covering the 15 item changes nothing (the 15 pixels are plain floor in the grid model).
- No object or slot changed.

# Attempt-6 amendments
- Object **Panel cell**: its click area is wider than the drawn 3x3 cell; a click in the gap at (27,50) toggled cell (0,0) (tid of the ACTION6:27,50 transition in attempt 6). Vocabulary `_lib.panel_cell_at` v2 now uses 5x5 hit areas. Pair it separates: panel {} vs {(0,0)} after a click at (27,50).
- Rule **blocked** v4.1/v4.2 (reading fixes, tid 718146ddcc560be2): 11 markers and the 15 item count as floor for sliding, and cells the agent vacates are not asserted (markers reappear underneath).
- Rule **thumb_hint** re-confirmed: a thumbnail click with 2 of 3 cells highlighted only adds the hint; it never completes.
- Lean grid model: no definition changes. Gap clicks are panel toggles; like any non-completing panel click they only add cost, and the atomic-completion abstraction already covers them as a lower bound. The L5Grid header now says this.

# Attempt-8 amendments
- Object **Panel**: the click area tiles the whole panel (rows 47-63, cols 22-38, frame included) 3x3; `_lib.panel_cell_at` v3. Pair it separates: a click at (23,48) toggles (0,0) vs does nothing.
- Rule **bar_tick** refined to per-action-type costs (work/fitcost.py, all L5 runs except attempt 5): big move 0.90, small move 0.89, panel click 0.92, completion +1.00, refill −9.00. Lean `L5G.step` now uses these in hundredths (`mc`, 468, 376, −810) with cap 3200. Reason: uniform 0.9 charged small moves above the fit (stricter than the game) and clicks below it. With fitted costs the certificate gives f start = 3229, a margin of 0.29 (was exactly 0). The only cost set that makes the route feasible (clicks 0.90 with small moves 0.89 → 31.95) is refuted by attempts 4 and 7, which played that exact route and lost.
