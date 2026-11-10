# Sealed-level experiment archive

## Browsing replies, bounds and actions

The sidebars show each run's reported initial bound and, where applicable, its
report after external feedback. Units are explained in the selected run; an
arrow does not imply a proof or a correct revised bound. The separate
[baseline reader](baselines/) contains all 96 original attempt replies from
12 baseline runs, their final interviews and the four archived feedback rounds.

Game actions are available for all 144 original attempts and all 24 attempts
in the six selected external-feedback rounds: 6,925 accepted actions in total.
The attempt menu keeps original and feedback stages separate. Before/after
frames are offline replays on source files whose MD5 matches the logged engine.
Every recorded level, terminal state and levels-completed count was checked;
401 recorded pixel hashes in the 2a3cc5 continuation also match. No new agent
play was performed. [Replay provenance and counts](data/action-provenance.json).

Replay data uses a 4,096-character, row-major hexadecimal initial frame (one
palette index per pixel). Each action applies its listed `[start, hex]` patches
to the preceding frame. The viewer shows the last frame returned by each action;
log timestamps, action coordinates and source-line references remain attached.

This page publishes a read-only export of six historical AWM runs on sealed sc25
levels, together with two newer harness releases. Historical runs were not
executions of the new four-transform/automatic-repair releases. The new releases
have offline validation records; new live six-run results are not included.

## Run downloads

- [l4p-case-2a3cc5](downloads/l4p-case-2a3cc5.zip): level 4; 8 attempts and final interview archived; continuation included.
- [m15fw-case-69fe87](downloads/m15fw-case-69fe87.zip): level 4; 8 initial attempts and final interview archived.
- [m15fw-case-9ec8d4](downloads/m15fw-case-9ec8d4.zip): level 4; 8 initial attempts and final interview archived.
- [l5d-case-284967](downloads/l5d-case-284967.zip): level 5; 8 initial attempts and final interview archived.
- [l5d-case-4f4628](downloads/l5d-case-4f4628.zip): level 5; 8 initial attempts and final interview archived.
- [l5d-case-977714](downloads/l5d-case-977714.zip): level 5; 8 initial attempts and final interview archived.

The collaborator has completed `2a3cc5` through attempt 8 and its final interview.
The original first three attempts remain intact. Attempts 4–8 have 75/75 tracked
Python/Lean source snapshots verified by their recorded hashes.
For its original attempts 1–3, a per-attempt file-hash manifest was not archived, so a zero missing-version
count must not be read as complete source-version coverage.

## What is in a run ZIP?

- `recorded_initial_evidence/`: the original initial-stage records and proof sources.
- `raw_sessions/`: complete available user/assistant JSONL messages, tool calls
  and tool results. Session branches can share earlier history.
- `all_user_prompts.md` and `all_assistant_text.md`: text extracts for reading.
- `attempts/`: round records and source snapshots recovered by matching the
  recorded content hashes. These are historical snapshots, not new executions.
- `file_history/`: available original file backups and their index.
- `arena_at_export/`: the workspace at export time, potentially after later repairs.
- `model-version-coverage.json` and `unrecovered_source_versions.json`: snapshot
  availability and known gaps; missing sources are not reconstructed by guessing.
- `selected_external_repair/`, where present: feedback and subsequent repair
  records, separate from the initial eight attempts.

Across the five runs with per-attempt manifests, 740 of 769 tracked file
occurrences have full snapshots recovered by exact hash. The other 29 are listed
as unavailable; original tool histories are retained. These counts describe
source coverage, not proof success.

## Reading the results

The reported bound, existence of a proof artifact, validity of a proof about the
final model, and agreement of the model with the game engine are distinct claims.
The viewer does not perform a new semantic certification of old proofs.

The two selected repairs are `9ec8d4` (20 to 19 on level 4) and `977714` (47 to 37
on level 5). The latter run charges the otherwise free winning move; 37 in that
report corresponds to engine budget 36. Read the original feedback, answers and
source files for the changes, rather than interpreting every stored Lean file as
a final current-model proof.

## Harnesses

Only two releases are offered. Use the setup instructions inside each ZIP.

- [Four transforms](downloads/harness-01-four-transforms-no-auto.zip): `four-transforms-initial8-external-feedback-v1`. SHA-256: `107dccb652060c9141e1b4314aea3715a653953654d78f3b5aa456d89d2df9e3`.
- [Four transforms + automatic repair](downloads/harness-02-four-transforms-auto-repair-latest.zip): `four-transforms-cost-20261024-v2.3.1`. SHA-256: `c3dd302c9e7c2422b44a36910189e296efe306da1f53f79b91974aa1970a5e95`.

The automatic-repair release also revises cost accounting and compilation reuse;
the two releases are not a single-switch ablation. Intermediate releases and
development-run downloads are deliberately omitted.

All download hashes are in [downloads/SHA256SUMS.txt](downloads/SHA256SUMS.txt).
Model credentials and compiled caches are excluded from the export. Original
source records were not modified when preparing the archive.

## Completed continuation

`2a3cc5` now includes attempts 4–8, all available questions and answers, the
resumed third-attempt follow-up, final interview, source snapshots, actual
action logs and receiver cold-build/axiom output. Its final reported threshold
remains 19 (budget 18), with verdict `impossible_in_model_proved`, confidence 50.
Original attempts 1–3 and their gate outcomes are preserved. No newer six-run
or automatic-repair experiments were added. See `README-COMPLETE.md` and
`completed_continuation/PROVENANCE.json` in the ZIP. The public session excludes
CLI request/debug/account metadata while retaining all user/assistant messages
and tool calls/results.
