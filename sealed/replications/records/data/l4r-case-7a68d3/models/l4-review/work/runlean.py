"""Run lean with a memory watchdog: kill if RSS > LIMIT MB. usage: runlean.py LIMIT_MB TIMEOUT_S args..."""
import subprocess, sys, time, os, psutil
lim=int(sys.argv[1])*1024*1024; to=float(sys.argv[2]); args=sys.argv[3:]
LEAN=os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
env=dict(os.environ); env['LEAN_PATH']='.'
p=subprocess.Popen([LEAN]+args,cwd='lean',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
pp=psutil.Process(p.pid); peak=0; t0=time.time(); why='ok'
while p.poll() is None:
    try: rss=pp.memory_info().rss
    except Exception: break
    peak=max(peak,rss)
    if rss>lim: why='KILLED-MEM'; p.kill(); break
    if time.time()-t0>to: why='KILLED-TIME'; p.kill(); break
    time.sleep(0.1)
out=p.communicate()[0].decode('utf-8','replace')
print(out[-6000:]); print('[%s] exit=%s peak=%.0fMB time=%.1fs'%(why,p.returncode,peak/2**20,time.time()-t0))
