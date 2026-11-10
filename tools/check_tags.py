#!/usr/bin/env python3
"""Check that none of our tags clash with tags already used by the game (or DLC).

    python3 tools/check_tags.py "<path to Hearts of Iron IV>"
"""
import re, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    tagdir = Path(sys.argv[1]) / "common" / "country_tags"
    if not tagdir.is_dir():
        sys.exit(f"Can't find {tagdir}")
    vanilla = {}
    for f in tagdir.glob("*.txt"):
        for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r'\s*([A-Z0-9]{3})\s*=\s*"([^"]+)"', line)
            if m:
                vanilla[m.group(1)] = m.group(2)
    ours = [n["tag"] for n in tomllib.loads((ROOT / "setup/nations.toml").read_text(encoding="utf-8"))["nation"]]
    clashes = [(t, vanilla[t]) for t in ours if t in vanilla]
    if clashes:
        print("CLASHES - rename these tags in setup/nations.toml (and the CSVs / scripts that use them):")
        for t, f in clashes:
            print(f"  {t} is already used by the game for {f}")
        sys.exit(1)
    print(f"No clashes: checked {len(ours)} tags against {len(vanilla)} game tags.")

if __name__ == "__main__":
    main()
