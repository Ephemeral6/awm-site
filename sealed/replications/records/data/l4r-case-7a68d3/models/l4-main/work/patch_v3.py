"""Amend Lean model M4 v2 -> v3 (attempt 3). Backups of v2 written next to the sources."""
import shutil
shutil.copy('work/L4Model_template.lean', 'work/L4Model_template_v2.lean.bak')
shutil.copy('lean/L4CheckDefs.lean', 'work/L4CheckDefs_v2.lean.bak')
shutil.copy('work/proof_body.lean', 'work/proof_body_v2.lean.bak')

p = 'work/L4Model_template.lean'
s = open(p, encoding='utf-8').read()
s = s.replace("# L4Model — formal model M4 of level 4, version 2 (amended after L4 attempt 2). Definitions only.",
              "# L4Model — formal model M4 of level 4, version 3 (amended after L4 attempt 3). Definitions only.")
s = s.replace("* panel clicks are free no-ops on the model state (tid 23f3ac38570477c8) -> covered by `Act.off`.",
"""* panel clicks are free no-ops on the model state (tid 23f3ac38570477c8) -> covered by `Act.off`.
Changes v2 -> v3 (attempt 3; v2 template kept in `work/L4Model_template_v2.lean.bak`):
* slide: a move whose full step is blocked may move half its step (choice `half`; 4x4 two cells observed,
  tid of the (31,35) -D-> (33,35) step; 2x2 one cell unobserved, allowed = looser);
* grow facing U observed (t-2,l-2) -> only facing R keeps the free placement `q`;
* H_shrinkD (shrink facing D keeps top-left) is now observed; it stays the explicit theorem hypothesis qD = 0;
* object clicks (item, block, barrier, box, exit, counter) observed free no-ops -> `Act.off`;
  the service accepts only actions 1,2,3,4,6 (README + refusal message).""")
s = s.replace("""inductive BAct
  | mv (d : Dir) (turn eat : Bool)""", """inductive BAct
  | mv (d : Dir) (turn eat half : Bool)""")
s = s.replace("""def target (b : Blk) (d : Dir) : Option (Nat × Nat) :=""", """/-- half-step target (slide) -/
def htarget (b : Blk) (d : Dir) : Option (Nat × Nat) :=
  match d with
  | .U => if Nat.ble (kk b / 2) b.t then some (b.t - kk b / 2, b.l) else none
  | .D => some (b.t + kk b / 2, b.l)
  | .L => if Nat.ble (kk b / 2) b.l then some (b.t, b.l - kk b / 2) else none
  | .R => some (b.t, b.l + kk b / 2)

def target (b : Blk) (d : Dir) : Option (Nat × Nat) :=""")
s = s.replace("""/-- grow offset (+2 base): facings L, D observed (t-2,l-2); facings U, R untested -> free choice q -/
def grT (q : Nat) (b : Blk) : Nat := if b.face == Dir.L || b.face == Dir.D then 0 else qdt q
def grL (q : Nat) (b : Blk) : Nat := if b.face == Dir.L || b.face == Dir.D then 0 else qdl q""",
"""/-- grow offset (+2 base): facings L, D, U observed (t-2,l-2); facing R untested -> free choice q -/
def grT (q : Nat) (b : Blk) : Nat := if b.face == Dir.R then qdt q else 0
def grL (q : Nat) (b : Blk) : Nat := if b.face == Dir.R then qdl q else 0

/-- the blocked branch of a move: optional slide by half a step, else stay (optionally turning) -/
def blocked (b : Blk) (d : Dir) (turn eat half : Bool) : BRes :=
  match htarget b d with
  | some (t2, l2) =>
    if half && cellsOk b.box t2 l2 (kk b) then
      if hitsCore t2 l2 (kk b) then .win b.item
      else .go (eatOpt eat false { b with t := t2, l := l2, face := d })
    else .go (eatOpt eat false (if turn then { b with face := d } else b))
  | none => .go (eatOpt eat false (if turn then { b with face := d } else b))""")
s = s.replace("""  | .mv d turn eat =>
    match target b d with
    | some (t2, l2) =>
      if cellsOk b.box t2 l2 (kk b) then
        if hitsCore t2 l2 (kk b) then .win b.item
        else .go (eatOpt eat false { b with t := t2, l := l2, face := d })
      else .go (eatOpt eat false (if turn then { b with face := d } else b))
    | none => .go (eatOpt eat false (if turn then { b with face := d } else b))""",
"""  | .mv d turn eat half =>
    match target b d with
    | some (t2, l2) =>
      if cellsOk b.box t2 l2 (kk b) then
        if hitsCore t2 l2 (kk b) then .win b.item
        else .go (eatOpt eat false { b with t := t2, l := l2, face := d })
      else blocked b d turn eat half
    | none => blocked b d turn eat half""")
s = s.replace("""inductive Act
  | mv (d : Dir) (turn eat : Bool)""", """inductive Act
  | mv (d : Dir) (turn eat half : Bool)""")
s = s.replace("  | .mv d turn eat => applyR B x (bstep qD x.b (.mv d turn eat)) 1 x.mask",
              "  | .mv d turn eat half => applyR B x (bstep qD x.b (.mv d turn eat half)) 1 x.mask")
open(p, 'w', encoding='utf-8').write(s)

p = 'lean/L4CheckDefs.lean'
s = open(p, encoding='utf-8').read()
s = s.replace("(dirs.flatMap fun d => bools.flatMap fun tu => bools.map fun e => BAct.mv d tu e) ++",
              "(dirs.flatMap fun d => bools.flatMap fun tu => bools.flatMap fun e => bools.map fun h => BAct.mv d tu e h) ++")
s = s.replace("/-! Bool checkers for model M4 v2 (definitions).", "/-! Bool checkers for model M4 v3 (definitions; v3: moves carry the slide choice `half`).")
open(p, 'w', encoding='utf-8').write(s)

p = 'work/proof_body.lean'
s = open(p, encoding='utf-8').read()
s = s.replace("  | mv d tu e => cases d <;> cases tu <;> cases e <;> decide",
              "  | mv d tu e h => cases d <;> cases tu <;> cases e <;> cases h <;> decide")
s = s.replace("""theorem step_mv (x : Full) (d : Dir) (tu e : Bool) : step x (.mv d tu e) =
    (if x.won = true then .ok x else if 18 < x.used then .reset else
      applyR 18 x (bstep 0 x.b (.mv d tu e)) 1 x.mask) := rfl""",
"""theorem step_mv (x : Full) (d : Dir) (tu e h : Bool) : step x (.mv d tu e h) =
    (if x.won = true then .ok x else if 18 < x.used then .reset else
      applyR 18 x (bstep 0 x.b (.mv d tu e h)) 1 x.mask) := rfl""")
s = s.replace("""  | mv d turn eat =>
    rw [step_mv, if_neg hnw] at hs""", """  | mv d turn eat half =>
    rw [step_mv, if_neg hnw] at hs""")
s = s.replace("exact keep_apply x x' (BAct.mv d turn eat) trivial 1 x.mask",
              "exact keep_apply x x' (BAct.mv d turn eat half) trivial 1 x.mask")
s = s.replace("def mvA (d : Dir) (eat : Bool := false) : Act := .mv d false eat",
              "def mvA (d : Dir) (eat : Bool := false) : Act := .mv d false eat false")
s = s.replace("# L4Proof — level 4 cannot be won in model M4 v2 (from the reset position of L4)",
              "# L4Proof — level 4 cannot be won in model M4 v3 (from the reset position of L4)")
s = s.replace("v2: facing is a `Dir`;", "v3 (attempt 3): moves carry the slide choice `half`; grow facing U fixed. v2: facing is a `Dir`;")
open(p, 'w', encoding='utf-8').write(s)
print('patched')
