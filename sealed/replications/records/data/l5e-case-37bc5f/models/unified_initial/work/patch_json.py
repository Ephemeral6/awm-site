import json

tp = 'work/transforms.json'
t = json.load(open(tp, encoding='utf-8'))
# attempt-1 Gate decomposition is superseded: mark it, keep it as history
for e in t:
    if e.get('lean_decl') == 'L5e.gateIsLimit':
        e['superseded_in_attempt'] = 2
        e['superseded_by'] = 'attempt-2 decomposition of St into gates : List Bool (Gate removed)'
t += [
 {"attempt": 2, "kind": "decomposition",
  "components": {"before": ["St = blk, panel, Gate{barrierOpen, boxPresent}, status"],
                 "after": ["St = blk, panel, gates : List Bool, status, pads : List Bool"]},
  "lean_file": "lean/L5eStructure.lean", "lean_decl": "L5e.stIsLimit",
  "check": "Gate.boxPresent was the negation of barrierOpen in every observed frame (both flipped together in L3 tid a4766650 and L4 tid 92fdc7d6; constant elsewhere), so one slot was dropped. It is now one flag per box because L5 has two boxes. pads was added for the L5 refill pad. Replays: L5e.l4_replay_matches (31 L4 attempt-1 actions), L5e.plan_trace (the 29 L4 attempt-2 actions; ends won, as observed) and L5e.l5_replay_matches (42 L5 actions; final block/gates/pads equal the observed final frame). L5e.l5_replay_kinds places the refill and the 4 firing clicks exactly at the observed steps."},
 {"attempt": 2, "kind": "generalization",
  "components": {"before": ["open condition as an unknown parameter oc : Blk -> Bool (attempt 1)",
                            "attempt-1 candidate ocCand (vertical stalks only)"],
                 "after": ["ocBox = copairing over Orient = vert + horiz of ocVert, ocHoriz"]},
  "lean_file": "lean/L5eStructure.lean", "lean_decl": "L5e.orIsColimit",
  "check": "L5e.ocBox_is_desc proves ocBox equals the desc. L5e.ocBox_fits_observed_fires checks all 10 observed recipe-6 fires: L3 x3, L4 attempt-1 x4 (only the last 4 had the box present), L4 attempt-2 x1, L5 x2 (one vertical, one horizontal). The vertical branch gives the same verdict as attempt-1 ocCand on every one of them."},
 {"attempt": 2, "kind": "specialization",
  "components": {"before": ["Effect.teleport r c: one fixed destination (L2)"],
                 "after": ["Effect.teleport with destination tpDest L size: 4x4 -> 11-framed square, 2x2 -> 15-pad"]},
  "lean_file": "lean/L5eStructure.lean", "lean_decl": "L5e.effIsColimit",
  "check": "L5e.applyEffect_is_desc still holds. L2's verdict is unchanged (4x4 -> the framed square). L5 attempt 2's teleport of a 2x2 to r37 c15 is reproduced inside L5e.l5_replay_matches. The L5 4x4 destination (17,33) is level data by analogy with L2, not observed."}
]
json.dump(t, open(tp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

lp = 'work/limits_table.json'
L = json.load(open(lp, encoding='utf-8'))
L = [e for e in L if e['name'] != 'Gate']
for e in L:
    if e['name'] == 'R-open6 condition oc':
        e['name'] = 'R-open condition ocBox'
        e['kind'] = 'colimit'
        e['lean_file'] = 'lean/L5eStructure.lean'
        e['lean_decl'] = 'L5e.orIsColimit'
        e['status'] = 'definition (attempt 2; ocBox_is_desc: copairing of ocVert / ocHoriz)'
        e.pop('reason', None)
    if e['name'].startswith('R-fire'):
        e['status'] = 'definition (applyEffect_is_desc; teleport destination now from Level.tp by size)'
    if e['name'].startswith('R-budget'):
        e['reason'] = 'costSum / gainSum / alive in L5eProof: an action is sent with spent < budget + refills gained; costs are hypotheses bounded by the per-level observations'
    if e['name'].startswith('colour-14 square'):
        e['name'] = 'colour-14 square covered by a 4x4 (L4)'
        e['reason'] = 'A 4x4 covering a 14-pad has no effect and the pad reappears afterwards (L4 tids a9960c82, 4385a4f9). The model only lets a 2x2 landing exactly on the pad consume it, so 4x4 cover is a no-op there too.'
        e['status'] = 'consequence of R-refill (usePads requires size 2 and an exact top-left)'
L += [
 {"name": "Orient", "kind": "colimit", "lean_file": "lean/L5eStructure.lean", "lean_decl": "L5e.orIsColimit", "status": "definition (attempt 2)"},
 {"name": "BoxSpec", "kind": "colimit", "lean_file": "lean/L5eStructure.lean", "lean_decl": "L5e.orIsColimit", "status": "definition: a BoxSpec is an Orient-tagged (row, col); orCocone is its coproduct presentation"},
 {"name": "gates : List Bool", "kind": "base", "reason": "One opened-flag per 6-box, in level order. It replaces the attempt-1 Gate record, whose two slots were always negations of each other.", "status": "definition"},
 {"name": "pads : List Bool", "kind": "base", "reason": "One consumed-flag per 14-pad. L5 tid 88632a96 consumed the pad, and it stayed floor afterwards.", "status": "definition"},
 {"name": "R-refill (usePads + Kind.mvR + Costs.refill)", "kind": "base", "reason": "A 2x2 moving exactly onto an unused 14-pad consumes it, and the bar gains 36 cells (L5). It lives inside moveRule, which is one branch of the stepCore copairing.", "status": "definition"},
 {"name": "R-tp (tpDest)", "kind": "base", "reason": "Teleport destination looked up by block size in Level.tp. It is read by the teleport branch of the applyEffect copairing.", "status": "definition"},
 {"name": "15-pad corner marks appearing when a 2x2 re-enters the pad (L5 last frame)", "kind": "base", "reason": "Seen once, in the GAME_OVER frame of attempt 2. The meaning is unknown (it may frame a 4x4 at r36-39 c14-17), and no rule reads it.", "status": "not in the model"},
 {"name": "size growth 2x2 -> 4x4", "kind": "base", "reason": "Never observed. The model has no grow rule: shrink on a 2x2 is a no-op there, but that is untested in the game. This is the gap that blocks a level-5 proof.", "status": "not in the model"}
]
json.dump(L, open(lp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i, e in enumerate(L):
    if e['kind'] == 'base':
        assert len(e.get('reason', '')) >= 20, (i, e['name'])
print('ok', len(t), len(L))
