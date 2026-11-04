import shutil
shutil.copy('lean/L4Limits.lean', 'work/L4Limits_v2.lean.bak')
p = 'lean/L4Limits.lean'
s = open(p, encoding='utf-8').read()
s = s.replace("  | .mv => Dir × Bool × Bool | .sz => Bool × Nat | .beam => Bool",
              "  | .mv => Dir × Bool × Bool × Bool | .sz => Bool × Nat | .beam => Bool")
s = s.replace("    | .mv => fun p => BAct.mv p.1 p.2.1 p.2.2\n    | .sz",
              "    | .mv => fun p => BAct.mv p.1 p.2.1 p.2.2.1 p.2.2.2\n    | .sz")
s = s.replace("    | .mv d tu e => s.ι .mv (d, tu, e)\n    | .sz e q => s.ι .sz (e, q)",
              "    | .mv d tu e h => s.ι .mv (d, tu, e, h)\n    | .sz e q => s.ι .sz (e, q)")
s = s.replace("    | mv d tu e => exact h .mv (d, tu, e)\n    | sz e q => exact h .sz (e, q)",
              "    | mv d tu e hf => exact h .mv (d, tu, e, hf)\n    | sz e q => exact h .sz (e, q)")
s = s.replace("def moveRule (qD : Nat) (b : Blk) (p : Dir × Bool × Bool) : BRes := bstep qD b (.mv p.1 p.2.1 p.2.2)",
              "def moveRule (qD : Nat) (b : Blk) (p : Dir × Bool × Bool × Bool) : BRes :=\n  bstep qD b (.mv p.1 p.2.1 p.2.2.1 p.2.2.2)")
s = s.replace("  | .mv => Dir × Bool × Bool | .click => Nat × Bool × Nat | .off => Unit",
              "  | .mv => Dir × Bool × Bool × Bool | .click => Nat × Bool × Nat | .off => Unit")
s = s.replace("    | .mv => fun p => Act.mv p.1 p.2.1 p.2.2\n    | .click",
              "    | .mv => fun p => Act.mv p.1 p.2.1 p.2.2.1 p.2.2.2\n    | .click")
s = s.replace("    | .mv d tu e => s.ι .mv (d, tu, e)\n    | .click c e q",
              "    | .mv d tu e h => s.ι .mv (d, tu, e, h)\n    | .click c e q")
s = s.replace("    | mv d tu e => exact h .mv (d, tu, e)\n    | click c e q",
              "    | mv d tu e hf => exact h .mv (d, tu, e, hf)\n    | click c e q")
open(p, 'w', encoding='utf-8').write(s)
print(s.count('Bool × Bool × Bool'))
