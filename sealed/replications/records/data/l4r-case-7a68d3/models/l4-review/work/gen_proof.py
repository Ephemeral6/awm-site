imports = "\n".join("import L4Row%02d" % t for t in range(40)) + "\nimport L4Credit"
rowpf = "lt_zero_all"
for t in range(40):
    rowpf = "(lt_succ_all %s row_%d)" % (rowpf, t)
src = imports + open('work/proof_body.lean', encoding='utf-8').read().replace('@@ROWPF@@', rowpf)
open('lean/L4Proof.lean', 'w', encoding='utf-8').write(src)
print('written')
