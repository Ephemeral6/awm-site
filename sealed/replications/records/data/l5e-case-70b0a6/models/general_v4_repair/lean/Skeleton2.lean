/-!
# 骨架二：**单调量**

同目录 `Skeleton1.lean` 用的是守恒量：一条所有动作都保持的量。
这一份用的是另一种：**每个动作最多让 Φ 变 1**，于是 n 步之内 Φ 最多变 n ——
把「至少要几步」变成一条可以直接算的量。

两种各自什么时候好使，自己判断。

**这一份不含任何一局的事实**，纯骨架，和盘面大小、动作串长度都无关，不枚举任何状态。
-/

namespace Skeleton2

/-- 走一步的结果。`reset` 那一支是**写在明处的边界**：
    下面的定理说的是「不经过重来就到不了目标」，和 `goal_never_holds_of_conserved` 同一个口径。 -/
inductive Res (S : Type) where
  | ok (s : S) : Res S
  | reset : Res S
  deriving Repr

variable {S A : Type}

/-- 一条动作串走完，**途中**有没有到过目标。碰上 `reset` 就记 false（见 `Res` 的说明）。 -/
def everGoal (step : S → A → Res S) (goal : S → Bool) : S → List A → Bool
  | s, [] => goal s
  | s, a :: rest =>
      goal s || (match step s a with
                 | .ok s' => everGoal step goal s' rest
                 | .reset => false)

/-- **核心引理**：到过目标，就说明当初的势不超过走过的步数。

    这是整份文件里唯一一次归纳，和 `goal_never_holds_of_conserved` 一样
    `generalizing s`（走一步之后换了局面，归纳假设必须对任何局面都成立）。

    写成这个形状（而不是直接写成关于预算的断言）是为了**躲开自然数减法** ——
    `budget - 1` 在 `Nat` 上会在 0 处塌掉，证起来全是边界情况。 -/
theorem potential_le_length
    (step : S → A → Res S) (goal : S → Bool) (legal : A → Prop) (Φ : S → Nat)
    (hstep : ∀ s s' a, legal a → step s a = .ok s' → Φ s ≤ Φ s' + 1)
    (hgoal : ∀ s, goal s = true → Φ s = 0) :
    ∀ (as : List A) (s : S), (∀ a ∈ as, legal a) →
      everGoal step goal s as = true → Φ s ≤ as.length := by
  intro as
  induction as with
  | nil =>
    intro s _ hwin
    simp only [everGoal] at hwin
    simp [hgoal s hwin]
  | cons a rest ih =>
    intro s hall hwin
    simp only [everGoal, Bool.or_eq_true] at hwin
    rcases hwin with hg | hrest
    · -- 这一步就已经在目标上：势是 0，怎么都不超
      simp [hgoal s hg]
    · -- 往下走了一步才到的：拆开 `step s a`
      split at hrest
      · next s' hok =>
        have h1 : Φ s' ≤ rest.length :=
          ih s' (fun b hb => hall b (by simp [hb])) hrest
        have h2 : Φ s ≤ Φ s' + 1 := hstep s s' a (hall a (by simp)) hok
        simp only [List.length_cons]
        omega
      · -- `reset`：`everGoal` 给 false，和 `hrest : false = true` 矛盾
        exact absurd hrest (by simp)

/-- **骨架**：势函数给出下界 ⇒ 预算之内到不了目标。

    `hbudget : budget < Φ s` 就是「最便宜的那条路比预算长」。
    结论对**任何**长度不超预算的合法动作串成立 —— 不是「我试过的那些」。 -/
theorem goal_never_holds_within
    (step : S → A → Res S) (goal : S → Bool) (legal : A → Prop) (Φ : S → Nat)
    (hstep : ∀ s s' a, legal a → step s a = .ok s' → Φ s ≤ Φ s' + 1)
    (hgoal : ∀ s, goal s = true → Φ s = 0)
    (s : S) (budget : Nat) (hbudget : budget < Φ s) :
    ∀ as : List A, as.length ≤ budget → (∀ a ∈ as, legal a) →
      everGoal step goal s as = false := by
  intro as hlen hall
  -- `by_contra` 是 mathlib 的，这一套是裸 `lean`（不依赖 mathlib），所以手工拆 Bool。
  have key : everGoal step goal s as = true → False := by
    intro hwin
    have h := potential_le_length step goal legal Φ hstep hgoal as s hall hwin
    omega
  cases hq : everGoal step goal s as
  case false => first | rfl | exact hq
  case true => exact (key hq).elim

/-- 一条**自洽性**检查：要是真有一条不超预算的串到过目标，那上面那条定理就不该成立。
    这一条不是装饰 —— 它钉住了 `everGoal` 的方向没写反。 -/
theorem not_both
    (step : S → A → Res S) (goal : S → Bool) (legal : A → Prop) (Φ : S → Nat)
    (hstep : ∀ s s' a, legal a → step s a = .ok s' → Φ s ≤ Φ s' + 1)
    (hgoal : ∀ s, goal s = true → Φ s = 0)
    (s : S) (budget : Nat) (hbudget : budget < Φ s)
    (as : List A) (hlen : as.length ≤ budget) (hall : ∀ a ∈ as, legal a) :
    everGoal step goal s as ≠ true := by
  rw [goal_never_holds_within step goal legal Φ hstep hgoal s budget hbudget as hlen hall]
  simp

#print axioms potential_le_length
#print axioms goal_never_holds_within
#print axioms not_both

end Skeleton2
