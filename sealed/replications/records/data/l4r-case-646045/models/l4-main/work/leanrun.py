"""Run lean with a memory watchdog (kill above LIMIT bytes) and a timeout."""
import subprocess, sys, time, os, psutil
LIMIT = 2_500_000_000
LEAN = os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
args = sys.argv[1:]
env = dict(os.environ, LEAN_PATH='.')
p = subprocess.Popen([LEAN] + args, cwd='lean', env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
pp = psutil.Process(p.pid); peak = 0; t0 = time.time()
while p.poll() is None:
    try:
        rss = pp.memory_info().rss + sum(c.memory_info().rss for c in pp.children(recursive=True))
    except psutil.Error:
        rss = 0
    peak = max(peak, rss)
    if rss > LIMIT or time.time() - t0 > 900:
        p.kill(); print('KILLED rss=%d t=%.0f' % (rss, time.time() - t0)); break
    time.sleep(0.2)
out = p.stdout.read().decode('utf-8', 'replace')
print(out[-6000:])
print('exit', p.returncode, 'peak MB %.0f' % (peak / 1e6), 'secs %.0f' % (time.time() - t0))
