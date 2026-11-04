import sys
for u in map(int, sys.argv[1:]): print(u, 64 - 2*int(u*64/18/2 + 1e-9))
