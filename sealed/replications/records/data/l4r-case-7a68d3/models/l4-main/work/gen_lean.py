# Generates lean/L4Model.lean (model M4 v2) from work/L4Model_template.lean + the Phi table.
# v1 generator kept in work/gen_lean_v1.py.bak.
import sys; sys.path.insert(0, 'work')
import l4mirror as M
M.QD[0] = 0                     # hypothesis H_shrinkD
phi = M.compute_phi()
rows = {}
for b, v in phi.items():
    rows[b[0]] = rows.get(b[0], 0) | (v << (7 * (M.idx(b) - b[0] * M.ROW)))
phirow = "\n".join("  | %d => %s" % (t, hex(rows.get(t, 0))) for t in range(40)) + "\n  | _ => 0"
src = open('work/L4Model_template.lean', encoding='utf-8').read().replace('@@PHIROW@@', phirow)
open('lean/L4Model.lean', 'w', encoding='utf-8').write(src)
print('phi(start)=', phi[M.START], 'ROW=', M.ROW)
