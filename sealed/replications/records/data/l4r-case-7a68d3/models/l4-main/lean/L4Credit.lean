import L4CheckDefs
/-! Kernel check of the grid-credit facts, in 16 chunks of 32 masks (generated). -/
namespace L4
def creditOK (m c : Nat) : Bool :=
  Nat.ble (credit (m ^^^ (1 <<< c))) (credit m + 1) && Nat.blt (m ^^^ (1 <<< c)) 512 &&
  (!((m ^^^ (1 <<< c)) == 170) || Nat.ble 3 (credit m)) && (!((m ^^^ (1 <<< c)) == 146) || Nat.ble 2 (credit m))
theorem credChunk_0 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 0 + i.val) c.val = true := by decide +kernel
theorem credChunk_1 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 1 + i.val) c.val = true := by decide +kernel
theorem credChunk_2 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 2 + i.val) c.val = true := by decide +kernel
theorem credChunk_3 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 3 + i.val) c.val = true := by decide +kernel
theorem credChunk_4 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 4 + i.val) c.val = true := by decide +kernel
theorem credChunk_5 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 5 + i.val) c.val = true := by decide +kernel
theorem credChunk_6 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 6 + i.val) c.val = true := by decide +kernel
theorem credChunk_7 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 7 + i.val) c.val = true := by decide +kernel
theorem credChunk_8 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 8 + i.val) c.val = true := by decide +kernel
theorem credChunk_9 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 9 + i.val) c.val = true := by decide +kernel
theorem credChunk_10 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 10 + i.val) c.val = true := by decide +kernel
theorem credChunk_11 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 11 + i.val) c.val = true := by decide +kernel
theorem credChunk_12 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 12 + i.val) c.val = true := by decide +kernel
theorem credChunk_13 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 13 + i.val) c.val = true := by decide +kernel
theorem credChunk_14 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 14 + i.val) c.val = true := by decide +kernel
theorem credChunk_15 : ∀ (i : Fin 32) (c : Fin 9), creditOK (32 * 15 + i.val) c.val = true := by decide +kernel
theorem credChunks : ∀ k, k < 16 → ∀ i, i < 32 → ∀ c, c < 9 → creditOK (32 * k + i) c = true :=
  (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all (lt_succ_all lt_zero_all (fun i hi c hc => credChunk_0 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_1 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_2 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_3 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_4 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_5 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_6 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_7 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_8 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_9 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_10 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_11 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_12 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_13 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_14 ⟨i, hi⟩ ⟨c, hc⟩)) (fun i hi c hc => credChunk_15 ⟨i, hi⟩ ⟨c, hc⟩))
theorem creditOK_all (m c : Nat) (hm : m < 512) (hc : c < 9) : creditOK m c = true := by
  have h := credChunks (m / 32) (by omega) (m % 32) (by omega) c hc
  have e : 32 * (m / 32) + m % 32 = m := by omega
  rw [e] at h; exact h
end L4
