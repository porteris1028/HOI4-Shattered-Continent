#!/usr/bin/env python3
"""List every state in a HoI4 install (or mod) so you can fill in setup/state_assignments.csv.

Usage:
    python3 tools/list_states.py "<path to Hearts of Iron IV>"            # all states
    python3 tools/list_states.py "<path>" --owner GER                     # only states GER owns in 1936
    python3 tools/list_states.py "<path>" --search bavaria                # name search
    python3 tools/list_states.py "<path>" --csv > states.csv              # spreadsheet

Default Steam paths:
    Windows: C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV
    Linux:   ~/.steam/steam/steamapps/common/Hearts of Iron IV
"""
import argparse, csv, re, sys
from pathlib import Path

def field(text, key):
    m = re.search(r'\b' + key + r'\s*=\s*"?([\w.]+)"?', text)
    return m.group(1) if m else ""

def provinces(text):
    m = re.search(r'provinces\s*=\s*\{([^}]*)\}', text)
    return m.group(1).split() if m else []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("game_dir")
    ap.add_argument("--owner")
    ap.add_argument("--search")
    ap.add_argument("--csv", action="store_true")
    a = ap.parse_args()

    sdir = Path(a.game_dir) / "history" / "states"
    if not sdir.is_dir():
        sys.exit(f"Can't find {sdir}. Point this at the main Hearts of Iron IV folder.")

    rows = []
    for f in sdir.glob("*.txt"):
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        text = re.sub(r'#.*', '', text)
        hist = re.search(r'history\s*=\s*\{', text)
        head = text[:hist.start()] if hist else text
        rows.append({
            "id": int(field(text, "id") or 0),
            "name": field(head, "name") or f.stem,
            "file": f.name,
            "owner_1936": field(text[hist.start():] if hist else "", "owner"),
            "category": field(head, "state_category"),
            "manpower": field(head, "manpower"),
            "provinces": len(provinces(text)),
        })
    rows.sort(key=lambda r: r["id"])
    if a.owner:
        rows = [r for r in rows if r["owner_1936"].upper() == a.owner.upper()]
    if a.search:
        rows = [r for r in rows if a.search.lower() in (r["file"] + r["name"]).lower()]

    if a.csv:
        w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()) if rows else ["id"])
        w.writeheader(); w.writerows(rows)
    else:
        for r in rows:
            print(f'{r["id"]:>5}  {r["owner_1936"]:<4} {r["category"]:<14} prov={r["provinces"]:<3} {r["file"]}')
        print(f"\n{len(rows)} states")

if __name__ == "__main__":
    main()
