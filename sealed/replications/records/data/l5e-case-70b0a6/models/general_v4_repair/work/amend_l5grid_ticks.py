"""Attempt-9 amendment of lean/L5Grid.lean: integer ticks, after-action game-over rule, grow_fit."""
import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def R(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)


R("""/-- cost of one move in hundredths (attempt-8 refit: big 0.90, small 0.89) -/
def mc (s : S) : Int := if s.big then 90 else 89""", """/-- cost of one move in ticks (attempt 9: integer tick model `bar_ticks`, unique fit on 8 L5 runs) -/
def mc (_s : S) : Int := 1""")
R("ee := true, fc := d }, mc s - 900)", "ee := true, fc := d }, mc s - 10)")
s = s.replace(", 468)", ", 5)").replace(", 376)", ", 4)")

a = s.index("/-- grow_place (attempt 3")
b = s.index("/-- the game under the bar rule")
s = s[:a] + """/-- grow_fit (attempt 9; replaces the facing-based grow_place, retired): a small agent grows into the
    first placement that fits, trying cell offsets (-1,-1), (0,-1), (-1,0), (0,0) = codes 8, 6, 7, 5. -/
def growFit (s : S) : S × Int :=
  if (step s 8).1.big = true ∧ s.big = false then step s 8
  else if (step s 6).1.big = true ∧ s.big = false then step s 6
  else if (step s 7).1.big = true ∧ s.big = false then step s 7
  else step s 5

/-- attempt 2: 2x2 at pixel (15,45) facing up -> 4x4 at pixel (15,43) -/
theorem growFit_obs_up :
    (growFit ⟨7, 22, false, true, false, true, true, 0⟩).1 = ⟨7, 21, true, true, false, true, false, 0⟩ := by decide

/-- attempt 3: 2x2 at pixel (17,47) facing right -> 4x4 at pixel (15,45) -/
theorem growFit_obs_right :
    (growFit ⟨8, 23, false, true, false, true, true, 3⟩).1 = ⟨7, 22, true, true, false, true, false, 3⟩ := by decide

/-- attempt 9: 2x2 at pixel (37,15) facing down -> 4x4 at pixel (35,13) -/
theorem growFit_obs_down :
    (growFit ⟨18, 7, false, false, false, false, true, 1⟩).1 = ⟨17, 6, true, false, false, false, false, 1⟩ := by decide

/-- attempt 9: 2x2 at pixel (37,13) facing left -> 4x4 at pixel (35,13) -/
theorem growFit_obs_left :
    (growFit ⟨18, 6, false, false, false, false, true, 2⟩).1 = ⟨17, 6, true, false, false, false, false, 2⟩ := by decide

/-- attempt 5: 2x2 at pixel (13,21) in the 2-wide stem: no placement fits, nothing changes -/
theorem growFit_obs_stem :
    (growFit ⟨6, 10, false, false, false, false, true, 0⟩).1 = ⟨6, 10, false, false, false, false, true, 0⟩ := by decide

""" + s[b:]

R("""/-- the game under the bar rule: a winning move always goes through; any other action needs running cost < `cap` -/
def playB (cap : Int) : S → Int → List Nat → Bool
  | _, _, [] => false
  | s, r, a :: as => if wins s a then true
                     else if r < cap then playB cap (step s a).1 (r + (step s a).2) as else false

def play := playB 3200""", """/-- the game under the bar rule (attempt 9, experiment X7): a winning move always goes through;
    any other action ends the game if it would bring the tick count above `cap` -/
def playB (cap : Int) : S → Int → List Nat → Bool
  | _, _, [] => false
  | s, r, a :: as => if wins s a then true
                     else if r + (step s a).2 ≤ cap then playB cap (step s a).1 (r + (step s a).2) as else false

def play := playB 35""")
R("def raw (s : S) : Nat := (ftab (code s / 3968) >>> (16 * (code s % 3968))) % 65536",
  "def raw (s : S) : Nat := (ftab (code s / 3968) >>> (12 * (code s % 3968))) % 4096")
R("""def actOk (s : S) (a : Nat) : Bool :=
  wins s a ||
    (decide (f s ≤ (step s a).2 + f (step s a).1) &&
     (!winReady (step s a).1 || decide (f s ≤ 0)) && validB (step s a).1)""", """def actOk (s : S) (a : Nat) : Bool :=
  wins s a ||
    (decide (f s ≤ (step s a).2 + f (step s a).1) && validB (step s a).1)""")

a = s.index("def okS (s : S) : Bool :=")
b = s.index("def checkRange")
s = s[:a] + """def okS (s : S) : Bool :=
  raw s == 0 ||
    ((!winReady s || decide (f s ≤ 0)) &&
     actOk s 0 && actOk s 1 && actOk s 2 && actOk s 3 && actOk s 4 && actOk s 5 &&
     actOk s 6 && actOk s 7 && actOk s 8 && actOk s 9 && actOk s 10 && actOk s 11)

""" + s[b:]

a = s.index("theorem actOk_of_ok")
b = s.index("theorem f_start")
s = s[:a] + """theorem actOk_of_ok (s : S) (h : okS s = true) (hr : raw s ≠ 0) (a : Nat) (ha : a ≤ 11) : actOk s a = true := by
  have hn : (raw s == 0) = false := by simp [hr]
  simp only [okS, hn, Bool.false_or, Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨_, h0⟩, h1⟩, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩, h9⟩, h10⟩, h11⟩ := h
  have : a = 0 ∨ a = 1 ∨ a = 2 ∨ a = 3 ∨ a = 4 ∨ a = 5 ∨ a = 6 ∨ a = 7 ∨ a = 8 ∨ a = 9 ∨ a = 10 ∨ a = 11 := by omega
  rcases this with rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl <;> assumption

theorem ready_le (s : S) (h : okS s = true) (hr : raw s ≠ 0) (hw : winReady s = true) : f s ≤ 0 := by
  have hn : (raw s == 0) = false := by simp [hr]
  simp only [okS, hn, Bool.false_or, Bool.and_eq_true] at h
  have h0 := h.1.1.1.1.1.1.1.1.1.1.1.1
  simp only [hw, Bool.not_true, Bool.false_or, decide_eq_true_eq] at h0
  exact h0

/-- the invariant: tick count within budget, and tick count + cost-to-go > 35 -/
theorem inv (as : List Nat) : ∀ (s : S) (r : Int), validB s = true → r ≤ 35 → 36 ≤ r + f s →
    play s r as = false := by
  induction as with
  | nil => intro s r _ _ _; rfl
  | cons a as ih =>
    intro s r hv hle hf
    have hraw : raw s ≠ 0 := by
      intro h0
      simp only [f, h0, if_true] at hf
      omega
    have hok := ok_of_valid s hv
    have hw : winReady s = false := by
      cases h : winReady s
      · rfl
      · have := ready_le s hok hraw h; omega
    show playB 35 s r (a :: as) = false
    simp only [playB]
    have hwin : wins s a = false := by
      cases h : wins s a
      · rfl
      · rw [wins_ready s a h] at hw; exact absurd hw (by decide)
    simp only [hwin, Bool.false_eq_true, if_false]
    by_cases ha : a ≤ 11
    · have hA := actOk_of_ok s hok hraw a ha
      simp only [actOk, hwin, Bool.false_or, Bool.and_eq_true, decide_eq_true_eq] at hA
      obtain ⟨hc, hv2⟩ := hA
      by_cases hr : r + (step s a).2 ≤ 35
      · simp only [hr, if_true]
        exact ih _ _ hv2 hr (by omega)
      · simp [hr]
    · rw [step_big s a ha]
      have h0 : r + (0 : Int) ≤ 35 := by omega
      simp only [h0, if_true]
      exact ih s (r + 0) hv h0 (by omega)

""" + s[b:]
R("theorem f_start : f start = 3229 := by decide +kernel", "theorem f_start : f start = 36 := by decide +kernel")
R("""  exact inv as start 0 (by decide) (by rw [f_start]; omega) start_not_ready""",
  """  exact inv as start 0 (by decide) (by decide) (by rw [f_start]; omega)""")
R("/-! ## non-vacuity: with cap 3230 (0.30 unit more) the model's best route wins -/",
  "/-! ## non-vacuity: with cap 36 (one tick more) the model's best route (42 actions) wins -/")
R("theorem relaxed_budget_wins : playB 3230 start 0 witness = true := by decide +kernel",
  "theorem relaxed_budget_wins : playB 36 start 0 witness = true := by decide +kernel")
R("#print axioms L5G.growEst_obs_up\n#print axioms L5G.growEst_obs_right",
  "#print axioms L5G.growFit_obs_up\n#print axioms L5G.growFit_obs_right\n#print axioms L5G.growFit_obs_down\n"
  "#print axioms L5G.growFit_obs_left\n#print axioms L5G.growFit_obs_stem")
a = s.index("Bar (HUNDREDTHS")
b = s.index("-/", a)
s = s[:a] + """Bar (attempt 9, concept bar_ticks, unique integer fit on 8 L5 runs): every action 1 tick, the
  completing click of a pattern 2 ticks (shrink/grow 5, fire/teleport 4 as macros), the refill move
  -9 net; budget B = 35. Experiment X7 (attempt 9): a non-winning action that would bring the count
  above 35 ends the game, whatever its cost; winning moves always go through.
  (Attempts 1-8 used fitted fractional costs; that version gave f start = 3229 hundredths vs cap 3200.)
""" + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print("ok")
