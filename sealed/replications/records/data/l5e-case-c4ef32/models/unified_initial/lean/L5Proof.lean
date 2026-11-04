import L5Model
/-!
# L5Proof — under the model `L5Model`, level 5 cannot be won within budget.

The table `cert` (L5Data) is produced by a search program and is NOT trusted: every entry used is
re-checked here by `decide +kernel` against `L5.step`.  It assigns to each packed state a value
`H` (a lower bound on prefixCost + 10·[refill available at the last state]) and marks the set of
states closed under `step`.
-/
namespace L5

def Dir.idx : Dir → Nat | .U => 0 | .D => 1 | .L => 2 | .R => 3
def Dir.ofIdx (n : Nat) : Dir := match n % 4 with | 0 => .U | 1 => .D | 2 => .L | _ => .R
def b2n (b : Bool) : Nat := if b then 1 else 0

def key (s : St) : Nat :=
  ((((s.r.val * 32 + s.c.val) * 2 + b2n s.big) * 4 + s.f.idx) * 8 + 4 * b2n s.oc + 2 * b2n s.od + b2n s.ep)

def unkey (k : Nat) : St where
  r := ⟨(k / 2048) % 32, Nat.mod_lt _ (by decide)⟩
  c := ⟨(k / 64) % 32, Nat.mod_lt _ (by decide)⟩
  big := (k / 32) % 2 == 1
  f := Dir.ofIdx (k / 8)
  oc := (k / 4) % 2 == 1
  od := (k / 2) % 2 == 1
  ep := k % 2 == 1

def certAt (k : Nat) : Nat := (certRow (k / 2048) >>> (6 * (k % 2048))) &&& 63
def H (s : St) : Nat := certAt (key s) - 1
def inR (s : St) : Bool := certAt (key s) != 0

/-- the local condition checked for one state and one action -/
def okAct (s : St) (a : Act) : Bool :=
  let t := step s a
  if win t then decide (H s ≤ 10 * b2n s.ep)
  else inR t && decide (H s ≤ a.cost + H t)

/-- the full local condition of one state: outside the certified set, or every action is fine -/
def stCheck (s : St) : Bool := !inR s || allActs.all (okAct s)

def allBool (p : Bool → Bool) : Bool := p false && p true
def allDir (p : Dir → Bool) : Bool := p .U && p .D && p .L && p .R
def allFin (p : Fin 32 → Bool) : Bool := (List.range 32).all (fun i => if h : i < 32 then p ⟨i, h⟩ else true)

theorem allBool_spec {p : Bool → Bool} (h : allBool p = true) (b : Bool) : p b = true := by
  simp only [allBool, Bool.and_eq_true] at h; cases b <;> simp [h]
theorem allDir_spec {p : Dir → Bool} (h : allDir p = true) (d : Dir) : p d = true := by
  simp only [allDir, Bool.and_eq_true] at h; cases d <;> simp [h]
theorem allFin_spec {p : Fin 32 → Bool} (h : allFin p = true) (i : Fin 32) : p i = true := by
  simp only [allFin, List.all_eq_true, List.mem_range] at h
  have := h i.val i.isLt
  simpa [i.isLt] using this

/-- all 64 states at block position (r, c) -/
def colCheck (r c : Fin 32) : Bool :=
  allBool fun big => allDir fun f => allBool fun oc => allBool fun od => allBool fun ep =>
    stCheck ⟨r, c, big, f, oc, od, ep⟩

/-- 512 states: row index r, column indices 8*cb .. 8*cb+7 -/
def part (r : Fin 32) (cb : Nat) : Bool :=
  (List.range 8).all fun j => if h : 8 * cb + j < 32 then colCheck r ⟨8 * cb + j, h⟩ else true

theorem colCheck_of_parts {r : Fin 32} (h0 : part r 0 = true) (h1 : part r 1 = true)
    (h2 : part r 2 = true) (h3 : part r 3 = true) (c : Fin 32) : colCheck r c = true := by
  have key : ∀ cb, part r cb = true → cb = c.val / 8 → colCheck r c = true := by
    intro cb hp hcb
    simp only [part, List.all_eq_true, List.mem_range] at hp
    have hj : c.val % 8 < 8 := Nat.mod_lt _ (by decide)
    have := hp (c.val % 8) hj
    have hlt : 8 * cb + c.val % 8 < 32 := by omega
    rw [dif_pos hlt] at this
    have e : (⟨8 * cb + c.val % 8, hlt⟩ : Fin 32) = c := Fin.ext (by simp only; omega)
    rwa [e] at this
  have hc := c.isLt
  have : c.val / 8 = 0 ∨ c.val / 8 = 1 ∨ c.val / 8 = 2 ∨ c.val / 8 = 3 := by omega
  rcases this with h | h | h | h
  · exact key 0 h0 h.symm
  · exact key 1 h1 h.symm
  · exact key 2 h2 h.symm
  · exact key 3 h3 h.symm

theorem stCheck_of_col {s : St} (h : colCheck s.r s.c = true) : stCheck s = true := by
  obtain ⟨r, c, big, f, oc, od, ep⟩ := s
  exact allBool_spec (allBool_spec (allBool_spec (allDir_spec (allBool_spec h big) f) oc) od) ep

end L5
