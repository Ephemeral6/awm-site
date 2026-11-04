# Model M4 (level 4) — objects, rules, status   (Lean: lean/L4Model.lean, proof lean/L4Proof.lean)

## Objects (slot -> pair of positions that become indistinguishable if dropped)
- Blk.t, Blk.l   block top-left. Drop -> (25,37) vs (29,31) same; but only (29,·) can enter corridor.
- Blk.big        4x4 vs 2x2. Drop -> can't tell whether the step is 4 or 2 / whether the item can be eaten.
- Blk.up         faces up. Drop -> beam at l=31 facing up (destroys box) vs facing left (does nothing).
- Blk.box        switch box destroyed. Drop -> barrier open vs closed at (29,43)+R.
- Blk.item       e item present. Drop -> refund available vs not.
- Full.mask      grid toggles. Drop -> one click from shrink vs three clicks from it.
- Full.used      counter ticks used. Drop -> 18 (one more action allowed) vs 19 (game over).
- Full.won.
Dropped slot: facing D/L/R distinctions (no M4 rule reads them).

## Rules (all are definitions in L4Model.lean; domain = any Blk / Full)
R1 move (move_step + d_block + lead_face-up): bstep .mv — target = shift by k; allowed iff all target cells passable;
   blocked moves cost 1, block stays; facing after a blocked move: free choice (turn flag) [looser than game].
R2 exit_win: a move/grow whose target meets exit core -> won. (BRes.win)
R3 size toggle (pattern f): 4x4 -> 2x2 keeping top-left (3 obs); 2x2 -> 4x4 at (t-2,l-2) (1 obs, facing left);
   grow that doesn't fit -> block unchanged [assumption].
R4 beam (pattern 6): sets box iff faces up and l = 31 [extrapolated: beam needs its left half under the
   stem; 1 failure (l=29,L4) + 1 success (L3) observed].
R5 eat (e_refill): only a 2x2 overlapping item cells eats it [premise H_eat]; eating is optional in M4.
R6 refund: the step that eats gives back 10 ticks (Nat-truncated) [premise H_ref; the one observation 18+1 -> 9
   also fits "set to 9"].
R7 counter: move 1 tick, non-completing click 1, completing click 2, off-grid click 0; an action is possible
   only while used <= 18 (fitted exactly on all 26 L4 transitions: 64*used/18 rounded down to even rows).
R8 grid: click toggles bit; mask = 170 (f) or 146 (6) fires the pattern and clears the grid.
Not in model: teleport (b) — no b panel on L4; panel/HUD clicks other than background (untested, assumed no-op).

## Replay check (work/replay_m4.py): 26 observed L4 transitions -> 26 matched, 0 mismatched, 0 abstained.

## Discard audit (mechanisms observed but abstracted)
- full facing (D/L/R) -> dropped; only beam reads facing: model allows MORE (any facing ok for non-beam) — ok.
- blocked-move facing: model allows both outcomes — more transitions — ok.
- switch-box area after destruction: model makes it passable (game: background) — more — ok.
- eating optional, 4x4 never eats — 4x4 eating is NOT allowed: this is the one place M4 may be STRICTER
  than the game (premise H_eat). Also grow anchor fixed to (t-2,l-2) (premise H_grow) and beam only at l=31
  (premise H_beam), refund exactly 10 (H_ref).
- actions possibly untried: ACTION5/7 (README lists only 1-4, 6); clicks on the top-left panels.

## v2 (after L4 attempt 2) — amendments, each tied to an observation
- Blk.up:Bool -> Blk.face:Dir. Pair that becomes indistinguishable if dropped: 4x4 at (33,23) facing D
  (front rows 35-36 on the item -> eats) vs the same block facing U (front rows 33-34, item under back -> no eat).
- R5 eat: 2x2 overlap OR 4x4 front-half overlap (tid 7e0ae8a49d1be806); a grow landing on the item may eat (looser).
- R3 size toggle: grow facing D observed (t-2,l-2) (tid 7e0ae8a49d1be806). Grow facing U/R untested -> free choice q.
  Shrink facing U/R/L keeps top-left (4 obs). Shrink facing D untested -> parameter qD; H_shrinkD: qD = 0.
- R2/R7 exit vs budget: a winning action that takes used past 18 is game over (tid c20aa696def56d6b).
- R6 refund -10 now observed twice (19->9, 16->6); set-to-9 refuted.
- R4 beam from a 4x4 at l=31 facing up works (attempt 2); destroyed box area becomes floor.
- Panel click: free, loads 0-hints, reads/changes no model slot -> abstracted into Act.off (tid 23f3ac38570477c8).
Replay v2: 54 transitions, 51 matched, 0 mismatched, 3 abstained.
Discard audit additions: hint layer of the grid dropped (no rule reads it; completion depends only on the e-set);
dropping it neither adds nor removes transitions of the model.

## v3 (after L4 attempt 3) — amendments
- R1 move: a move whose full step is blocked may move half its step (Lean `blocked`, choice `half`):
  4x4 (31,35) -D-> (33,35) observed; 2x2 one-cell slide unobserved, allowed (looser). Blocked moves charge 1 tick
  and turn the block (observed; the model keeps the turn as a free choice, looser). Background cells are walls (observed).
- R3: grow facing U observed (t-2,l-2); only facing R keeps the free placement. Shrink facing D keeps top-left
  (observed) — H_shrinkD is now an observed fact, still stated as the theorem hypothesis qD = 0.
- R5: a 4x4 eats by MOVING its front half onto the item (observed, refund -10) — already allowed in v2.
- Action set: service accepts only 1,2,3,4,6 (refusal message). Clicks on panels/objects: free no-ops (Act.off).
- Open (not in model, model is looser here): attempt-2 move into the exit with 2-column core overlap stopped after
  2 cells; the model counts any core overlap as a win.
Replay v3: 88 transitions, 83 matched, 0 mismatched, 5 abstained.

## v4 (after L4 attempt 5) — amendments
- R3 grow: facing R observed (t-2,l-2) -> grow placement is facing-independent (grT = grL = 0); the choice q is
  no longer read. Generalization recorded (L4.facedIsColimit, L4.grow_generalized).
- R8 grid: a pattern whose panel is absent from the level (L2 teleport {0,1,4}) does not fire on L4 —
  consistent with the definition (only fMask and sixMask fire); no definition change.
Replay v4: 126 transitions, 117 matched, 0 mismatched, 9 abstained (attempt boundaries + GAME_OVER steps).
Phi(start) = 29 unchanged; min budget for a win in the model = 19.

## v4 rule-table amendment (after L4 attempt 7) — no Lean definition changed
- R2 exit, refinement H1' (now observed twice: attempts 2 and 7; consistent with the L1/L2/L3 wins):
  a move whose target touches the exit core but does not lie wholly inside the exit structure
  (L4: rows 28-33, cols 56-61) is treated as blocked and slides 2. STATUS: explicitly NOT IN THE MODEL —
  the Lean model keeps the looser rule (any core overlap wins). Adding H1' could only remove wins, so the
  impossibility bound does not need it and the looser rule is the safe direction.
- Attempt 7 also checked: eating the item changes nothing outside the room (barrier/box unchanged at every eat step).
