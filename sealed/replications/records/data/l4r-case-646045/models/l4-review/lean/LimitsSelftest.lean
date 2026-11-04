/-
# LimitsSelftest —— 怎么用 `Limits/Basic.lean` 把对象和规则写成 limit / colimit（一个与任何游戏无关的小例子）

    分解 / 组合（沿 limit）：一个组件 = 更简单的组件 + 它们之间的相容条件；Lean 核它是那张图的极限（`IsLimit`）
    泛化 / 特化（沿 colimit）：一条按情形定义的规则 = 各情形余积上的 copairing；Lean 核这些情形构成余积（`IsColimit`），
                              再核规则就是它的 `desc`

这里的类型和规则都是随手编的，只示范写法。

编译（在 lean/ 目录里）：
    "$LEAN" -o Limits/Basic.olean Limits/Basic.lean
    LEAN_PATH=. "$LEAN" LimitsSelftest.lean
-/

import Limits.Basic

open AWM

/-! ## 分解：一个带对齐条件的记录是拉回 -/

/-- 两张等长的表：一张名字、一张标记。等长就是相容条件。 -/
structure Tagged where
  names : List Nat
  flags : List Bool
  aligned : flags.length = names.length

/-- 图：两张表都映到「长度」。 -/
def taggedDiagram : Diagram := cospan (fun n : List Nat => n.length) (fun f : List Bool => f.length)

def taggedCone : Cone taggedDiagram where
  pt := Tagged
  π
    | .left => Tagged.names
    | .right => Tagged.flags
    | .base => fun t => t.names.length
  w
    | .l, _ => rfl
    | .r, t => t.aligned

/-- **`Tagged` 是这张 cospan 的极限**（拉回）：它恰好由两个分量和对齐条件决定。 -/
def taggedIsLimit : IsLimit taggedCone where
  lift s x := ⟨s.π .left x, s.π .right x, by
    have h1 := s.w .l x; have h2 := s.w .r x
    simp only [taggedDiagram, cospan] at h1 h2
    rw [h2, h1]⟩
  fac s j x := by
    cases j
    · rfl
    · rfl
    · exact s.w .l x
  uniq s m h x := by
    have h1 := h .left x
    have h2 := h .right x
    cases hm : m x with
    | mk n f al =>
      simp only [taggedCone, hm] at h1 h2
      subst h1; subst h2; rfl

#print axioms taggedIsLimit

/-! ## 泛化：一条按情形定义的规则是余积上的 copairing -/

/-- 一次输入的两种情形：空输入，或带一个数。 -/
inductive InputIx | idle | push

def inputDiagram : Diagram := discrete InputIx (fun | .idle => Unit | .push => Nat)

def inputCocone : Cocone inputDiagram where
  pt := Option Nat
  ι
    | .idle => fun _ => none
    | .push => fun n => some n
  w f := nomatch f

/-- **`Option Nat` 是这两种情形的和**（余积）：两种情形互不重叠、合起来是全部输入。 -/
def inputIsColimit : IsColimit inputCocone where
  desc s
    | none => s.ι .idle ()
    | some n => s.ι .push n
  fac _ j _ := by cases j <;> rfl
  uniq s m h y := by
    cases y with
    | none => exact h .idle ()
    | some n => exact h .push n

/-- 两条分支规则：空输入不变，带数就累加。 -/
def idleRule (acc : Nat) : Nat := acc
def pushRule (acc n : Nat) : Nat := acc + n

def inputRules (acc : Nat) : Cocone inputDiagram where
  pt := Nat
  ι
    | .idle => fun _ => idleRule acc
    | .push => fun n => pushRule acc n
  w f := nomatch f

/-- 合起来的规则。 -/
def step (acc : Nat) : Option Nat → Nat
  | none => acc
  | some n => acc + n

/-- **`step` 就是两条分支规则的 copairing**。 -/
theorem step_is_desc (acc : Nat) : step acc = inputIsColimit.desc (inputRules acc) := by
  funext o; cases o <;> rfl

#print axioms inputIsColimit
#print axioms step_is_desc

/-! ## 非空洞性：这两个泛性质确实在约束什么 -/

/-- 由投影决定：两个 `Tagged` 只要名字和标记都一样就相等。 -/
theorem Tagged.ext' (a b : Tagged) (hn : a.names = b.names) (hf : a.flags = b.flags) : a = b := by
  have := taggedIsLimit.hom_ext (X := Unit) (fun _ => a) (fun _ => b) (by
    intro j _; cases j
    · exact hn
    · exact hf
    · show a.names.length = b.names.length; rw [hn])
  exact congrFun this ()

/-- 两个分支给出不同结果：copairing 不是常函数。 -/
theorem step_branches_differ : step 1 none ≠ step 1 (some 2) := by decide

#print axioms Tagged.ext'
#print axioms step_branches_differ
