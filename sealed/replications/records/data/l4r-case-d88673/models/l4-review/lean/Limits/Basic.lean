/-
# Limits/Basic —— 极限与余极限的最小接口（只用 Lean core，不依赖 Mathlib）

名字照 Mathlib 取，日后要换成 Mathlib 时逐个对应：

| 这里                          | Mathlib                                         |
|-------------------------------|-------------------------------------------------|
| `Diagram`                     | `J ⥤ Type`（这里的 J 是一个箭图，即它生成的自由范畴）|
| `Diagram.LimitPoint`          | `F.sections`                                    |
| `Diagram.Colimit`             | `Types.Quot F`                                  |
| `Cone` / `Cocone`             | `Cone F` / `Cocone F`                           |
| `IsLimit` / `IsColimit`       | `IsLimit` / `IsColimit`                         |
| `limitConeIsLimit`            | `Types.limitConeIsLimit`                        |
| `colimitCoconeIsColimit`      | `Types.colimitCoconeIsColimit`                  |
| `Iso` / `IsColimit.ptIso`     | `Equiv` / `IsColimit.coconePointUniqueUpToIso`  |

图只用到三种形状：离散（积 / 和）、cospan（拉回 = 原像）、平行对（等化子 / 余等化子）。
图里不放恒等箭头与复合：一个箭图上的锥，和它生成的自由范畴上的锥是同一回事。

**计算层（`Obj/`、`Rule/`、`Step.lean`、`Proof/`）不 import 这一份。** 它只给 `Structure/` 用：
每个概念的具体载体照旧是 `structure` / `inductive` / `Quot`，`Structure/` 里再证明它满足泛性质。
-/

namespace AWM

/-- 一张类型图：下标、箭头，以及每个下标上的类型和每条箭头上的函数。 -/
structure Diagram where
  J   : Type
  Hom : J → J → Type
  F   : J → Type
  map : {i j : J} → Hom i j → F i → F j

namespace Diagram

/-- 极限的点 = 一族彼此相容的分量（Mathlib 的 `F.sections`）："元组 + 全部相容性证明"。 -/
structure LimitPoint (D : Diagram) where
  value : (j : D.J) → D.F j
  compatible : ∀ {i j : D.J} (f : D.Hom i j), D.map f (value i) = value j

/-- 箭头生成的关系：`(i, x) ~ (j, F f x)`。 -/
def Rel (D : Diagram) (p q : (j : D.J) × D.F j) : Prop := ∃ f : D.Hom p.1 q.1, D.map f p.2 = q.2

/-- 余极限 = 带标签的和，再按箭头取商（Mathlib 的 `Types.Quot F`）。
    `Quot` 接受任意关系，不必先造等价关系：它本身就是对生成的等价关系取商。 -/
def Colimit (D : Diagram) := Quot D.Rel

def ι (D : Diagram) (j : D.J) (x : D.F j) : D.Colimit := Quot.mk _ ⟨j, x⟩

end Diagram

open Diagram

structure Cone (D : Diagram) where
  pt : Type
  π  : (j : D.J) → pt → D.F j
  w  : ∀ {i j : D.J} (f : D.Hom i j) (x : pt), D.map f (π i x) = π j x

structure Cocone (D : Diagram) where
  pt : Type
  ι  : (j : D.J) → D.F j → pt
  w  : ∀ {i j : D.J} (f : D.Hom i j) (x : D.F i), ι j (D.map f x) = ι i x

/-- 极限锥的泛性质：任何别的锥都唯一地经它分解。 -/
structure IsLimit {D : Diagram} (c : Cone D) where
  lift : (s : Cone D) → s.pt → c.pt
  fac  : ∀ (s : Cone D) (j : D.J) (x : s.pt), c.π j (lift s x) = s.π j x
  uniq : ∀ (s : Cone D) (m : s.pt → c.pt), (∀ j x, c.π j (m x) = s.π j x) → ∀ x, m x = lift s x

/-- 余极限余锥的泛性质：任何别的余锥都唯一地从它分解出去（copairing）。 -/
structure IsColimit {D : Diagram} (c : Cocone D) where
  desc : (s : Cocone D) → c.pt → s.pt
  fac  : ∀ (s : Cocone D) (j : D.J) (x : D.F j), desc s (c.ι j x) = s.ι j x
  uniq : ∀ (s : Cocone D) (m : c.pt → s.pt), (∀ j x, m (c.ι j x) = s.ι j x) → ∀ y, m y = desc s y

/-- 进入极限的两个映射，只要每个投影都相等，就相等（分解的核心：整体由分量决定）。 -/
theorem IsLimit.hom_ext {D : Diagram} {c : Cone D} (h : IsLimit c) {X : Type} (m₁ m₂ : X → c.pt)
    (e : ∀ j x, c.π j (m₁ x) = c.π j (m₂ x)) : m₁ = m₂ := by
  let s : Cone D := ⟨X, fun j x => c.π j (m₁ x), fun f x => c.w f (m₁ x)⟩
  funext x
  rw [h.uniq s m₁ (fun _ _ => rfl) x, h.uniq s m₂ (fun j x => (e j x).symm) x]

/-- 从余极限出去的两个映射，只要在每个注入上相等，就相等（特化的核心：一般规则由它的各个分支决定）。 -/
theorem IsColimit.hom_ext {D : Diagram} {c : Cocone D} (h : IsColimit c) {X : Type} (m₁ m₂ : c.pt → X)
    (e : ∀ j x, m₁ (c.ι j x) = m₂ (c.ι j x)) : m₁ = m₂ := by
  let s : Cocone D := ⟨X, fun j x => m₁ (c.ι j x), fun f x => by simp only [c.w f x]⟩
  funext y
  rw [h.uniq s m₁ (fun _ _ => rfl) y, h.uniq s m₂ (fun j x => (e j x).symm) y]

/-- 用相容族实现的极限锥（Mathlib：`Types.limitCone`）。 -/
def limitCone (D : Diagram) : Cone D := ⟨D.LimitPoint, fun j p => p.value j, fun f p => p.compatible f⟩

def limitConeIsLimit (D : Diagram) : IsLimit (limitCone D) where
  lift s x := ⟨fun j => s.π j x, fun f => s.w f x⟩
  fac _ _ _ := rfl
  uniq s m h x := by
    cases hm : m x with
    | mk v c =>
      have hv : v = fun j => s.π j x := funext fun j => by
        have := h j x; rw [hm] at this; exact this
      subst hv; rfl

/-- 用商实现的余极限余锥（Mathlib：`Types.colimitCocone`）。 -/
def colimitCocone (D : Diagram) : Cocone D :=
  ⟨D.Colimit, D.ι, fun f _ => (Quot.sound ⟨f, rfl⟩).symm⟩

def colimitCoconeIsColimit (D : Diagram) : IsColimit (colimitCocone D) where
  desc s := Quot.lift (fun p => s.ι p.1 p.2) (by
    intro p q ⟨f, hf⟩; show s.ι p.1 p.2 = s.ι q.1 q.2; rw [← hf, s.w])
  fac _ _ _ := rfl
  uniq _ m h y := by
    induction y using Quot.ind with
    | mk p => exact h p.1 p.2

/-- 两个类型之间的一对互逆映射（Mathlib：`Equiv`）。 -/
structure Iso (A B : Type) where
  to : A → B
  inv : B → A
  left_inv : ∀ a, inv (to a) = a
  right_inv : ∀ b, to (inv b) = b

/-- 同一张图的两个余极限，顶点之间有唯一的同构（Mathlib：`IsColimit.coconePointUniqueUpToIso`）。
    用法：商（`Quot`）是余极限，一个可计算的标准形也是余极限 ⇒ 商与标准形等价。 -/
def IsColimit.ptIso {D : Diagram} {c₁ c₂ : Cocone D} (h₁ : IsColimit c₁) (h₂ : IsColimit c₂) : Iso c₁.pt c₂.pt where
  to := h₁.desc c₂
  inv := h₂.desc c₁
  left_inv y := by
    have a := h₁.uniq c₁ (fun y => h₂.desc c₁ (h₁.desc c₂ y))
      (fun j x => by simp only [h₁.fac, h₂.fac]) y
    have b := h₁.uniq c₁ id (fun _ _ => rfl) y
    exact a.trans b.symm
  right_inv y := by
    have a := h₂.uniq c₂ (fun y => h₁.desc c₂ (h₂.desc c₁ y))
      (fun j x => by simp only [h₁.fac, h₂.fac]) y
    have b := h₂.uniq c₂ id (fun _ _ => rfl) y
    exact a.trans b.symm

/-! ## 三种图形状 -/

/-- 离散图：没有箭头。极限 = 积，余极限 = 和。 -/
def discrete (J : Type) (F : J → Type) : Diagram := ⟨J, fun _ _ => Empty, F, fun f => nomatch f⟩

inductive CospanIx | left | right | base deriving DecidableEq
inductive CospanHom : CospanIx → CospanIx → Type
  | l : CospanHom .left .base
  | r : CospanHom .right .base

/-- cospan `A → C ← B`。极限 = 拉回 `{(a, b) | f a = g b}`（原像是它的特例）。 -/
def cospan {A B C : Type} (f : A → C) (g : B → C) : Diagram where
  J := CospanIx
  Hom := CospanHom
  F | .left => A | .right => B | .base => C
  map
    | .l => f
    | .r => g

inductive PairIx | src | tgt deriving DecidableEq
inductive PairHom : PairIx → PairIx → Type
  | fst : PairHom .src .tgt
  | snd : PairHom .src .tgt

/-- 平行对 `f, g : A ⇉ B`。极限 = 等化子 `{a | f a = g a}`；余极限 = 余等化子（商）。 -/
def parallelPair {A B : Type} (f g : A → B) : Diagram where
  J := PairIx
  Hom := PairHom
  F | .src => A | .tgt => B
  map
    | .fst => f
    | .snd => g

end AWM
