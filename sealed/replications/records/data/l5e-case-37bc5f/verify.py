"""Offline hashes + main-theorem cold compile. No service calls or credentials."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile,os,re

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean');ap.add_argument('--hash-only',action='store_true');a=ap.parse_args()
    base=Path(__file__).resolve().parent
    sums=json.loads((base/'SHA256SUMS.json').read_text(encoding='utf-8'))
    for name,h in sums.items():
        p=(base/name).resolve()
        if not p.is_relative_to(base) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:
            raise SystemExit('Hash mismatch or unsafe path: '+name)
    print('All public package hashes verified:',len(sums))
    if a.hash_only:return
    if not a.lean:ap.error('--lean is required for cold compilation')
    version=subprocess.run([a.lean,'--version'],capture_output=True,text=True)
    if version.returncode or '4.34.1' not in version.stdout:raise SystemExit('Lean 4.34.1 is required')
    targets=json.loads((base/'proof_targets.json').read_text(encoding='utf-8'))
    if not targets:raise SystemExit('No complete main-theorem target recovered; do not infer success')
    receipts=[]
    for target in targets:
        root=(base/target['root']).resolve()
        if not root.is_relative_to(base):raise SystemExit('Unsafe model root')
        with tempfile.TemporaryDirectory(prefix='awm-public-cold-') as tmp:
            build=Path(tmp);env={**os.environ,'LEAN_PATH':str(build)};done=set();visiting=set()
            def compile_module(m):
                if m in done:return
                if m in visiting:raise RuntimeError('Cyclic local import: '+m)
                f=root/(m.replace('.','/')+'.lean')
                if not f.is_file():return # compiler resolves Lean/Std from the toolchain
                visiting.add(m)
                for dep in re.findall(r'^\s*(?:public\s+)?import\s+([A-Za-z0-9_.]+)',f.read_text(encoding='utf-8'),re.M):compile_module(dep)
                out=build/(m.replace('.','/')+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
                p=subprocess.run([a.lean,'-o',str(out),str(f)],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
                if p.returncode:raise RuntimeError(m+'\n'+p.stdout+p.stderr)
                visiting.remove(m);done.add(m)
            compile_module(target['module'])
            probe=build/'Probe.lean';probe.write_text(f"import {target['module']}\n#check {target['decl']}\n#print axioms {target['decl']}\n",encoding='utf-8')
            p=subprocess.run([a.lean,str(probe)],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
            print(target['root'],p.stdout,flush=True)
            if p.returncode:raise RuntimeError(p.stderr)
            found=re.findall(r'depends on axioms:\s*\[([^\]]*)\]',p.stdout)
            if not found and 'does not depend on any axioms' not in p.stdout:raise RuntimeError('No axiom report')
            for row in found:
                if set(x.strip() for x in row.split(',') if x.strip())-{'propext','Classical.choice','Quot.sound'}:raise RuntimeError('Unexpected axioms')
            receipts.append({'target':target,'modules':len(done),'returncode':p.returncode,'stdout':p.stdout})
    (base/'PUBLIC_COLD_RECEIPT.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8')
    print('Main-theorem closure checked. Engine correspondence is a separate obligation.')

if __name__=='__main__':main()
