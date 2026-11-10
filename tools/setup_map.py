#!/usr/bin/env python3
"""ONE COMMAND to put the Shattered Continent nations on the map.

    python3 tools/setup_map.py "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"

What it does:
  1. Reads your game's state files and state names (nothing in the game folder is changed).
  2. Matches the 'match' names in setup/state_assignments.csv and setup/danger_zones.csv
     to real state IDs and writes those IDs into the CSVs.
  3. Runs tools/build_setup.py to regenerate the setup script.
  4. Writes setup/match_report.txt so you can check every match.

States you already filled in by hand are kept unless you pass --redo.
"""
import argparse, csv, difflib, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [ROOT / "setup" / "state_assignments.csv", ROOT / "setup" / "danger_zones.csv"]
REPORT = ROOT / "setup" / "match_report.txt"


def norm(s):
    s = unicodedata.normalize("NFKD", s.replace("ø", "o").replace("Ø", "O").replace("ł", "l").replace("Ł", "L"))
    return re.sub(r"[^a-z0-9]", "", s.encode("ascii", "ignore").decode().lower())


def load_states(game):
    sdir = game / "history" / "states"
    if not sdir.is_dir():
        sys.exit(f"Can't find {sdir}\nPoint this at the main Hearts of Iron IV folder (the one with hoi4.exe).")
    loc = {}
    for f in (game / "localisation").rglob("*.yml"):
        if "english" not in str(f).lower():
            continue
        for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r'\s*(STATE_\d+):\d*\s*"(.*)"', line)
            if m:
                loc[m.group(1)] = m.group(2)
    states = {}
    for f in sdir.glob("*.txt"):
        text = re.sub(r"#.*", "", f.read_text(encoding="utf-8-sig", errors="replace"))
        m = re.search(r"\bid\s*=\s*(\d+)", text)
        if not m:
            continue
        sid = int(m.group(1))
        key = re.search(r'\bname\s*=\s*"?(\w+)"?', text)
        owner = re.search(r"\bowner\s*=\s*(\w+)", text)
        names = {re.sub(r"^\d+\s*-\s*", "", f.stem)}
        if key and key.group(1) in loc:
            names.add(loc[key.group(1)])
        states[sid] = {"names": names, "owner": owner.group(1) if owner else "?",
                       "label": (loc.get(key.group(1)) if key else None) or f.stem}
    if not states:
        sys.exit(f"No state files found in {sdir}")
    return states


def match(aliases, states, taken):
    """Return (state_id, how) or (None, reason)."""
    index = {}
    for sid, s in states.items():
        for n in s["names"]:
            lst = index.setdefault(norm(n), [])
            if sid not in lst:
                lst.append(sid)
    free = lambda ids: [i for i in ids if i not in taken]
    # 1. exact match on any alias
    for a in aliases:
        ids = free(index.get(norm(a), []))
        if ids:
            return sorted(ids)[0], "exact" + (" (several states share this name!)" if len(ids) > 1 else "")
    # 2. alias contained in a state name or vice versa
    for a in aliases:
        na = norm(a)
        if len(na) < 4:
            continue
        ids = free([i for n, lst in index.items() for i in lst if na in n or (len(n) >= 4 and n in na)])
        if ids:
            return sorted(set(ids))[0], "GUESS (partial name)"
    # 3. close spelling
    for a in aliases:
        close = difflib.get_close_matches(norm(a), list(index), n=1, cutoff=0.82)
        if close:
            ids = free(index[close[0]])
            if ids:
                return ids[0], "GUESS (similar spelling)"
    return None, "NOT FOUND"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("game_dir")
    ap.add_argument("--redo", action="store_true", help="re-match rows that already have a state_id")
    a = ap.parse_args()
    states = load_states(Path(a.game_dir))
    print(f"Read {len(states)} states from the game.")

    report, taken, problems = [], {}, 0
    for path in FILES:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
            fields = list(rows[0].keys()) if rows else []
        report.append(f"\n===== {path.name} =====")
        # Keep hand-filled IDs reserved first.
        for r in rows:
            sid = (r.get("state_id") or "").strip()
            if sid.isdigit() and not a.redo:
                taken[int(sid)] = path.name
        for r in rows:
            first = next(iter(r.values())) or ""
            if first.startswith("#") or not r.get("match"):
                continue
            label = (r.get("tag") or "") + " " + r["match"].split("|")[0]
            sid = (r.get("state_id") or "").strip()
            if sid.isdigit() and not a.redo:
                s = states.get(int(sid))
                report.append(f"  kept    {label:<34} -> {sid:>4} {s['label'] if s else '(unknown id!)'}")
                continue
            found, how = match(r["match"].split("|"), states, taken)
            if found is None:
                r["state_id"] = ""
                problems += 1
                report.append(f"  MISSING {label:<34} -> no state found for: {r['match']}")
            else:
                r["state_id"] = str(found)
                taken[found] = path.name
                s = states[found]
                if how != "exact":
                    problems += 1
                report.append(f"  {'ok' if how == 'exact' else 'CHECK':<7} {label:<34} -> {found:>4} {s['label']} "
                              f"(1936 owner {s['owner']}) [{how}]")
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    REPORT.write_text("Shattered Continent state matching report\n"
                      "Lines marked CHECK or MISSING need a look: fix the 'match' names or type the state_id in by hand,\n"
                      "then run this tool again (hand-typed IDs are kept).\n" + "\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print(f"\n{problems} row(s) need checking. Full report: setup/match_report.txt\n")

    sys.path.insert(0, str(ROOT / "tools"))
    import build_setup
    build_setup.main()


if __name__ == "__main__":
    main()
