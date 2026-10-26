import Skeleton2

/-!
# `Skeleton2.lean` 的**非空洞性**测试

一条永远用不上的定理也会「编过」。这一份钉住三件事：

1. **用得上** —— 骨架在一个具体的小系统上真的给出了结论；
2. **方向没反** —— 同一个系统**放宽预算**之后确实到得了目标（给出见证动作串）；
3. **前提是真约束** —— 一个**不满足** `hstep` 的假势函数套不进去
   （那一段是故意注释掉的，取消注释必须编不过）。

小系统：一条长 5 的直线，起点 0，目标 5，动作只有「往前一格」和「原地」。
`Φ = 5 - pos`。预算 3 ⇒ 到不了目标；预算 5 ⇒ 到得了。
-/

namespace Skeleton2Selftest

open Skeleton2

/-- 动作：往前一格 / 原地不动。 -/
inductive Act where
  | fwd
  | stay
  deriving Repr, DecidableEq

def legal : Act → Prop := fun _ => True

/-- 状态就是位置（0..5，越界就不动）。 -/
abbrev St := Nat

def step : St → Act → Res St
  | p, .fwd => .ok (if p < 5 then p + 1 else p)
  | p, .stay => .ok p

def goal : St → Bool := fun p => p == 5

/-- 势：还差几格。 -/
def Φ : St → Nat := fun p => 5 - p

theorem hstep : ∀ s s' a, legal a → step s a = .ok s' → Φ s ≤ Φ s' + 1 := by
  intro s s' a _ h
  cases a with
  | fwd =>
    simp only [step] at h
    split at h
    · next hlt => simp only [Res.ok.injEq] at h; subst h; simp only [Φ]; omega
    · next hge => simp only [Res.ok.injEq] at h; subst h; simp only [Φ]; omega
  | stay =>
    simp only [step, Res.ok.injEq] at h; subst h; omega

theorem hgoal : ∀ s, goal s = true → Φ s = 0 := by
  intro s h
  simp only [goal, beq_iff_eq] at h
  subst h
  simp [Φ]

/-- ① **用得上**：预算 3，从 0 出发，任何合法动作串都到不了目标。
    `Φ 0 = 5 > 3`，骨架直接给结论 —— 不枚举任何动作串。 -/
theorem budget3_never_reaches :
    ∀ as : List Act, as.length ≤ 3 → (∀ a ∈ as, legal a) →
      everGoal step goal 0 as = false :=
  goal_never_holds_within step goal legal Φ hstep hgoal 0 3 (by simp [Φ])

/-- ② **方向没反**：同一个系统，走五下 `fwd` 就到了目标。
    这是正面那一侧的见证 —— 没有它，`everGoal` 要是写反了，
    「什么都到不了」会被当成定理的功劳。 -/
theorem five_fwd_wins :
    everGoal step goal 0 [Act.fwd, Act.fwd, Act.fwd, Act.fwd, Act.fwd] = true := by
  -- **不用 `native_decide`**：它往公理表里塞 `ofReduceBool` / `trustCompiler`，
  -- 而纪律是公理表只许有 propext / Quot.sound。这一条直接归约就够。
  decide

/-- ②之二：那条串长度是 5，**超出**了 ① 的预算 3 —— 两条不矛盾。 -/
example : ([Act.fwd, Act.fwd, Act.fwd, Act.fwd, Act.fwd] : List Act).length = 5 := rfl

/-! ### ③ 前提是真约束

下面这段是**故意留着不编**的。`Φbad` 一步能降 5，不满足 `hstep`，所以套不进骨架。
**取消注释必须编不过** —— 如果它编过了，说明 `hstep` 没起作用。

```lean
def Φbad : St → Nat := fun p => if p = 0 then 5 else 0

theorem hstep_bad : ∀ s s' a, legal a → step s a = .ok s' → Φbad s ≤ Φbad s' + 1 := by
  intro s s' a _ h
  cases a with
  | fwd => sorry   -- 真的证不出来：s=0 时 Φbad 0 = 5，而 Φbad 1 + 1 = 1
  | stay => sorry
```
-/

#print axioms budget3_never_reaches
#print axioms five_fwd_wins

end Skeleton2Selftest
