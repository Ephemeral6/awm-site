/-!
# 骨架一：**守恒量**

和 `Skeleton2.lean` 配成一对。两份都是纯骨架，**不含任何一局的事实** ——
状态和动作都是类型参数，和盘面大小、动作串长度都无关，不枚举任何状态。

    Skeleton1   存在 P，所有动作都保持 P
    Skeleton2   存在 Φ，每个动作最多让 Φ 变 1

两份共用同一个 `everGoal` 口径：碰上 `reset` 记 false，
所以结论说的是「**不经过重来**」的那一段。这是写在明处的边界。
-/

namespace Skeleton1

/-- 走一步的结果。`reset` 那一支见上面的说明。 -/
inductive Res (S : Type) where
  | ok (s : S) : Res S
  | reset : Res S
  deriving Repr

variable {S A : Type}

/-- 一条动作串走完，**途中**有没有到过目标。 -/
def everGoal (step : S → A → Res S) (goal : S → Bool) : S → List A → Bool
  | s, [] => goal s
  | s, a :: rest =>
      goal s || (match step s a with
                 | .ok s' => everGoal step goal s' rest
                 | .reset => false)

/-- **骨架**：给一个状态性质 `P`
    · `hkeep` —— 走一步（不重来）之后 `P` 还在；
    · `hgoal` —— `P` 成立的状态一定不是目标。
    那么从任何满足 `P` 的状态出发，**任何**合法动作串都到不了目标。

    与盘面大小无关、与动作串多长无关，**不枚举任何状态**。 -/
theorem goal_never_holds_of_conserved
    (step : S → A → Res S) (goal : S → Bool) (legal : A → Prop) (P : S → Prop)
    (hkeep : ∀ s s' a, legal a → P s → step s a = .ok s' → P s')
    (hgoal : ∀ s, P s → goal s = false) :
    ∀ (as : List A) (s : S), P s → (∀ a ∈ as, legal a) →
      everGoal step goal s as = false := by
  intro as
  -- **对动作串做归纳**，这是整份文件里唯一一次归纳。
  -- `generalizing s` 是要害：走一步之后换了状态，归纳假设必须对**任何**满足 P 的状态成立。
  induction as with
  | nil =>
    intro s hp _
    simpa [everGoal] using hgoal s hp
  | cons a rest ih =>
    intro s hp hall
    -- `goal s` 由 hgoal 化成 false，`false || x = x`，只剩右边
    simp only [everGoal, hgoal s hp, Bool.false_or]
    split
    · next s' hok =>
      exact ih s' (hkeep s s' a (hall a (by simp)) hp hok)
                  (fun b hb => hall b (by simp [hb]))
    · rfl

/-- 自洽性：满足 `P` 就到不了目标，所以**到过目标**就说明 `P` 当初不成立。
    这一条钉住 `everGoal` 的方向没写反。 -/
theorem not_P_of_win
    (step : S → A → Res S) (goal : S → Bool) (legal : A → Prop) (P : S → Prop)
    (hkeep : ∀ s s' a, legal a → P s → step s a = .ok s' → P s')
    (hgoal : ∀ s, P s → goal s = false)
    (as : List A) (s : S) (hall : ∀ a ∈ as, legal a)
    (hwin : everGoal step goal s as = true) : ¬ P s := by
  intro hp
  rw [goal_never_holds_of_conserved step goal legal P hkeep hgoal as s hp hall] at hwin
  exact Bool.noConfusion hwin

#print axioms goal_never_holds_of_conserved
#print axioms not_P_of_win

end Skeleton1
