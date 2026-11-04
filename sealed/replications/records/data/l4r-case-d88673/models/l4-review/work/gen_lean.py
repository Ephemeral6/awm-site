"""Generate lean/L4Model.lean from work/L4Model.template.lean + model_l4 masks + certificate table."""
import sys
from pathlib import Path
sys.set_int_max_str_digits(0)
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H))
import model_l4 as M


def mask(door, kind):
    m = 0
    for i in range(32):
        for j in range(32):
            if M.C(i, j, door) == kind:
                m |= 1 << (i * 32 + j)
    return hex(m)


d = M.dist()
tab = 0
for s in M.STATES:
    tab |= d[s] << (6 * M.key(s))
_f = H / "L4Model.template.filled.lean"
src = (_f if _f.exists() else H / "L4Model.template.lean").read_text(encoding="utf-8")
src = (src.replace("@BC@", mask(0, "B")).replace("@BO@", mask(1, "B"))
          .replace("@GM@", mask(0, "G")).replace("@DT@", hex(tab))
          .replace("@BX@", hex(sum(1 << (i*32+j) for i in range(32) for j in range(32) if M.cell_box(i, j)))))
(H.parent / "lean" / "L4Model.lean").write_text(src, encoding="utf-8")
print("d(start) =", d[M.START])
