import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent.parent
d=json.loads((H/".last_frame.json").read_text())
f=d["frame"]
print("level",d.get("level"))
hexs="0123456789abcdef"
print("   "+"".join(str(x//10) for x in range(64)))
print("   "+"".join(str(x%10) for x in range(64)))
for y,r in enumerate(f): print("%2d "%y+"".join(hexs[c] for c in r))
