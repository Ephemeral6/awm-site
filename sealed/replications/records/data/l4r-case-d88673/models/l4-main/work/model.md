# Formal system (attempt 1)

## Objects (slots) — and the pair of positions each one distinguishes
| object | slots | dropping it confuses |
|---|---|---|
| player | i, j (lattice top-left), big (4x4 / 2x2), up (facing up?) | i/j: start vs one step left; big: 4x4 vs 2x2 at same spot (2x2 fits neck); up: same spot facing up vs down (fire works only facing up) |
| door/box | door (open?) | identical positions with door open (cost 6 to win) vs closed |
| board | blockClosed / blockOpen / goalMask (level data) | — |
| panel | (abstracted: macro actions) | — |
| bar | (hypothesis on total cost) | — |
Facing down/left/right are merged (no L4 rule reads them).

## Rules (functions St -> Act -> Out), domain = all St with i,j < 32
- moveRule: target rect = shift by size; blocked -> only facing changes; contains cap pixel & no blocker -> win; else move.  (concepts move_by_size, face_dir, blocked_by_nonfloor)
- resizeRule: f completion; 4x4 -> 2x2 in quadrant q; 2x2 -> 4x4 if free (looser anchor than game). (complete_f_resize)
- fireRule: 6 completion; facing up & cols overlap 30..33 & top row <= 20 -> door/box removed. (L3 observation + L4 failure at gap 12)
- cost: move 1, resize 4, fire 3 game actions.
Not in model: panel toggling as individual clicks, bar state, first-action swallow, teleport.

## Replay (frames reconciled)
work/replay_l4.py: 17 level-4 transitions checked, 17 matched, 0 mismatched, 1 skipped (GAME_OVER step: bar not modelled).
Concept settle: 5 concepts, 0 counterexamples (N = 1..47 each).

## Attempt-2 amendments
- cost (rule): unit model, move 1, resize 5, fire 4 (was 1/4/3); fitted on all 4 levels, B(L4)=18.
- fireRule (rule): projectile in column s.j, moving up, hits box -> door opens, any other blocked cell -> destroyed (was: range window). Generalized over size (L4S.sizeIsColimit, fireRule_is_desc).
- door vs 2x2: observed blocking (assumption -> established); no definition change.
- grow anchor observed (bottom-right kept when right side walled); model keeps its looser any-quadrant resize.
- Replay: 33/33 level-4 transitions matched (attempts 1+2), 1 skipped (attempt boundary).

## Attempt-3 amendments
- Objects: player gains `face` (4 values; distinguishes e.g. 4x4 at (33,23) facing down vs left: only the first
  touches the marker with its front half) and `picked` (marker present vs consumed: same position, 10 units apart).
- Rules: PICKUP (small overlap OR front-half overlap, union of untested hypotheses), REFILL (u := min 7 (u+c-10)),
  RESIZE anchors as observed (shrink top-left x5; grow keep bottom row, right if free else left x2).
- Budget enters as runB's cap (18), actions start while u <= 18.
- Replay: 57/57 positions, 0 bar mismatches (work/replay_l4b.py).

## Attempt-4 amendments (definitions changed; no structural transformation)
- resize3: grow order up-LEFT first (was up-right): refuted by tid 81e5d751d32a2557.
- PICKUP for 4x4 = front half (now observed positively); small-only hypothesis refuted.
- nu: refill = max 0 (u + c - 10) (was min 7 (...)); 'set to 7' refuted (15 -> 5).
- Retired theorem L4.l4_unwinnable_with_refill (premises refuted). New: L4.l4_winnable (cap 18), L4.l4_no_win_cap17.
- Replay: 81/81 positions, 0 bar mismatches (work/replay_l4b.py).

## Attempt-5 amendments
- Budget rule (runB5): a 4x4 move that starts at the last unit (u = 18) advances only one 2-px sub-step, then
  GAME_OVER (observed). 2x2 moves at u = 18 complete (observed x3). Unknowns read generously: a half-step that
  reaches the goal wins; clicks/completions starting at <= 18 resolve.
- New MAIN: L4.l4_unwinnable_half (cap 18, attempt-5 rule). Contrast: L4.l4_winnable (attempt-4 rule),
  L4.plan4_fails_cap18, L4.plan4_wins_cap19. Retired: L4.l4_no_win_cap17.
- Replay: 106/106 transitions (5 attempts), 0 bar mismatches.

## Attempt-6 amendments (rule table; Lean definitions unchanged)
- Budget/last action: 'half-step' reading refuted (4x4 at u=18 moved 4 px). Established: at u=18 a 4x4 whose goal
  contact comes in the 2nd sub-step does not win. lastWins (generous) already encodes exactly this; only its comment changed.
- Grow fallback with up walled observed (keep top row, extend left); model keeps the looser any-placement there.
- Legend click: free, hints only (not in model). b pattern inert on L4 (strict assumption now established).
  Completion requires exact match (supports the macro abstraction). ACTION5 rejected by the service (action set = 1-4, 6).
- Replay: 124/124 level-4 transitions (6 attempts), 0 bar mismatches; terminal positions not modelled.

## Attempt-8 amendment
- MOVE rule: sub-steps (moveSub3 in lean/L4Model.lean, model_l4b.step in Python). Observed tid ece0a2f5605e3199.
  The old atomic rule was STRICTER than the game (forbade the 2-px move); now corrected.
- Shot straight at the door: no effect (observed on L4, tid c590bb86483ad6eb) -- already implied by fireRule.
- Certificate recomputed; L4.l4_unwinnable_half still holds (cap 18). Replay 175/175, 0 bar mismatches.
