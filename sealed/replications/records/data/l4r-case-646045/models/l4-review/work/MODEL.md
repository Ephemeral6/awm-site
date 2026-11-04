# Formal system, attempt 1

## Objects (L4 model, lean/Game/L4Model.lean)
| slot | meaning | positions it distinguishes |
|---|---|---|
| small | piece edge 2 vs 4 | x=29 small vs big: only the small one can stand under stem col 31 after one move |
| opened | door cells floor | x=53 opened vs closed: win next step vs not |
| won | goal reached | goal predicate |
| x | piece left column | x=55 vs x=31 (opened, small): 1 vs 13 actions left |
| dP, dL | panel selection distance to PLUS / LINE | dP=1 vs dP=4: next click shrinks vs not |
Dropped: rows (looser), facing (no rule reads it), bar (enters as the length premise), e-object (untested).

## Rules (functions St -> Act -> Res St)
R_left, R_right (incl. R_win), R_noop, R_click (+R_commit, R_shrink, R_six with parameter `fires`).
Python ledger: concepts/{move_dir, bar_tick, click_toggle, commit_clears, win_touch, shrink_topleft, empty_bar_gameover}.py

## Dropped-mechanism audit
| dropped | effect on allowed transitions | ok? |
|---|---|---|
| rows / walls in rows | more transitions | ok |
| clamp to arbitrary values (only 0 or full step kept) | fewer — but in L4 all walls sit on the lattice | ok only for L4 geometry (checked by hand) |
| facing | more (no rule reads it) | ok |
| other panel patterns (L-tromino, unknown) | FEWER if they work in L4 | assumption H4 |
| e-object | FEWER if it refills the bar | assumption H3 |
| grow on PLUS when small | FEWER | hypothesis H2 (grow=false) |
| 6-commit condition | FEWER | hypothesis H1' (hfire) |
Actions not tried: ACTION5, ACTION7 (README lists only 1-4, 6).

## Attempt 2 amendments
- Slots added: `y` (top row) and `face`. Pair they distinguish: piece at (x41,y29,face R) vs (x41,y21,face R):
  a LINE commit's shot runs along the door rows 29-32 only in the first.
- Rules added: R_up, R_down (rUp/rDown). R_six re-described: LINE commit = shot from the piece front along the facing
  direction (observed in attempt-2 animation: 4-tall beam, 2 cols/frame, rows 21-24, stopped at the col-44 wall).
- e-object: touched (fully covered by 4x4) -> no refill, stays. Still "not in model".
- Ledger fix: attempt-boundary transition f24f3579c4d9a836 scoped NA in bar_tick, empty_bar_gameover.
- Reconciliation: 88 transitions, 0 counterexamples across 7 concepts.

## Attempt 3 amendments
- R_six instantiated: `fires = firesShot` (x = 31 ∧ face = U) — H1'', from the observed shot mechanism; H_shot refuted
  (shot fired right from x41,y29 entered the door, d redrawn, door stayed shut).
- Shot over the e square: no effect (e still "not in model").
- shrink_topleft: holds facing left too.

## Attempt 4 amendments (macro model lean/Game/L4Macro.lean)
- Objects: MSt = (small, opened, y, x, face). dP/dL dropped (panel folded into macro actions plus=4, line=3).
  Pair for `y`: 4x4 at (y29,x53) vs (y21,x53)... only the first can touch the goal; for `face`: (x31,U) vs (x31,L): LINE opens the door only in the first.
- Rules changed: R_grow added (PLUS on 2x2 -> 4x4 at (y-2,x-2)); clamp on all moves; corridor geometry explicit;
  H1'' confirmed; off-panel and legend clicks are free (not in model).
- Proof: L4M.L4_macro_no_win_within_19 (kernel-checked reachable set); win21_wins shows 21 actions suffice in the model.

## Attempt 5 amendments
- Rules revised (Python ledger): commit_clears v3 (commit iff selection == a level pattern; hints irrelevant);
  empty_bar_gameover v2 (the emptying action is NA: a commit that emptied the bar ended the game at once).
- Lean definitions unchanged (they already encode v3); new check L4M.replay_attempt5 (all 9 observed positions).
- Shot fired right through the opened door reached cols 54-55 and vanished, no level change: shot-win not observed.

## Attempt 6 amendments
- New object: the e square (pickup). Slot added by composition: BSt = MSt x taken. Pair it distinguishes: same board,
  spent 20: taken=true can still act, taken=false is over budget.
- Rules: commit_clears v4 (only legend patterns), bar_tick v3 (pickup steps NA), e_refill v2 (pickup refills),
  exact budget (18 units; committing click 2; pickup +10; game over below 0).
- Proof: L4M.L4_budget_no_win (lean/L4BudgetProof.lean), all action lists, H_front granted.

## Attempt 7 amendments
- H_front moved from hypothesis to established (pick definition unchanged). A 4x4 firing from x31 opens the door
  (firesShot already size-independent). The win that would take the budget to -1 did not count (winsB unchanged).
- New checks: L4M.replay_attempt7 (all 18 observed states), L4M.played7_loses.
- Python: win_touch scoped NA on GAME_OVER steps (c20aa696def56d6b).

## Audit round amendments
- R_pickup: observed rule is H_tl (top-left == (33,23)); H_front alone refuted. L4M.pick widened to the union
  (looser than the game). Certificate regenerated and re-checked; L4M.L4_budget_no_win still holds.
- Grow/shrink placement verified on all four facings; selection does not survive level transitions.
