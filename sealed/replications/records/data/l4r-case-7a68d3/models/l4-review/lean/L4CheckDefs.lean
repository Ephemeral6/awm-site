import L4Model
/-! Bool checkers for model M4 v3 (definitions; v3: moves carry the slide choice `half`). The kernel runs them in `L4Row*.lean`.
    v1 kept in `work/L4CheckDefs_v1.lean.bak` (v2: facing is a `Dir`, size toggle carries `q`,
    checks are made against `bstep 0`, i.e. under hypothesis H_shrinkD). -/
namespace L4

def dirs : List Dir := [Dir.U, Dir.D, Dir.L, Dir.R]
def bools : List Bool := [false, true]

def allActs : List BAct :=
  (dirs.flatMap fun d => bools.flatMap fun tu => bools.flatMap fun e => bools.map fun h => BAct.mv d tu e h) ++
  (bools.flatMap fun e => [0, 1, 2, 3].map fun q => BAct.sz e q) ++
  [.beam false, .beam true]

def okRes (b : Blk) (a : BAct) : Bool :=
  match bstep 0 b a with
  | .go b' => fitsB b' && Nat.blt b'.t 40 && Nat.blt b'.l 64 &&
      Nat.ble (phi b) (cost a + phi b') && (!b'.item || b.item)
  | .win it => Nat.ble (phi b) (cost a + (if it then 10 else 0)) && (it == b.item)

def okB (b : Blk) : Bool :=
  !(fitsB b && Nat.blt b.t 40 && Nat.blt b.l 64) || allActs.all (okRes b)

/-- states of row t with column l (all 32 slot combinations) satisfy okB -/
def checkTL (t l : Nat) : Bool :=
  bools.all fun big => dirs.all fun f => bools.all fun box => bools.all fun item =>
    okB ⟨t, l, big, f, box, item⟩

theorem lt_zero_all {P : Nat → Prop} : ∀ l, l < 0 → P l :=
  fun l h => absurd h (Nat.not_lt_zero l)
theorem lt_succ_all {P : Nat → Prop} {n : Nat} (h : ∀ l, l < n → P l) (hn : P n) :
    ∀ l, l < n + 1 → P l := by
  intro l hl
  by_cases e : l = n
  · subst e; exact hn
  · exact h l (by omega)

end L4
