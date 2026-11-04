/-
# L5GridObs — attempt-5 observations replayed on the grid model (consequences, not new definitions)

State: small agent at pixel (13,21) = cell (6,10) in room A's 2-wide stem, facing up, 15 frame present,
no barrier removed, refill not eaten.
-/
import L5Grid

open L5G

def stemState : S := ⟨6, 10, false, false, false, false, true, 0⟩

/-- grow with no room (placement (13,19) is wall): nothing changes, full completion cost (tid 821d9d4677ca0bb8) -/
theorem obs_grow_fails : growFit stemState = (stemState, 5) := by decide

/-- moving into the 12-box is blocked: agent stays, faces up, costs one action -/
theorem obs_touch_box_blocked : step stemState 0 = (stemState, 1) := by decide

/-- point-blank fire from inside the stem facing up removes the 12 barrier -/
theorem obs_fire_point_blank : step stemState 9 = ({ stemState with cg := true }, 4) := by decide

#print axioms obs_grow_fails
#print axioms obs_touch_box_blocked
#print axioms obs_fire_point_blank
