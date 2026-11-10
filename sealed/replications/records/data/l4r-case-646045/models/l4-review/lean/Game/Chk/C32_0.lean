import Game.L4MacroCheck
namespace L4M
theorem chk_32_0 : (chunk 32 0).all okEntry = true := by decide +kernel
end L4M
