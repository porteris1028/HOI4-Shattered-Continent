#!/usr/bin/env python3
"""Helpers for adding provinces to the HoI4 map.

Work on a COPY of the map inside the mod (shattered_continent/map/), never on the game files.

Commands:
  check   <map_dir>                      Compare provinces.bmp with definition.csv: unknown colours,
                                         duplicate colours, gaps in IDs, tiny provinces.
  density <map_dir> x0 y0 x1 y1          How many provinces fall in a pixel box (e.g. Europe) and their
                                         average size. Use it to measure before and after splitting.
  newcolors <map_dir> N [land|sea|lake] [terrain] [continent]
                                         Print N unused colours as ready-to-paste definition.csv lines,
                                         numbered after the current highest ID. Paint the new provinces
                                         in provinces.bmp with exactly these RGB values.

Needs Pillow:  pip install pillow
"""
import csv, random, sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Needs Pillow: pip install pillow")

Image.MAX_IMAGE_PIXELS = None

def color_counts(img):
    return Counter({c: n for n, c in img.getcolors(maxcolors=img.size[0] * img.size[1])})

def load_defs(map_dir):
    defs = []
    with (Path(map_dir) / "definition.csv").open(encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) < 4 or not row[0].strip().lstrip("-").isdigit():
                continue
            defs.append((int(row[0]), (int(row[1]), int(row[2]), int(row[3])), row))
    return defs

def load_bmp(map_dir):
    img = Image.open(Path(map_dir) / "provinces.bmp").convert("RGB")
    return img, color_counts(img)

def check(map_dir):
    defs = load_defs(map_dir)
    img, counts = load_bmp(map_dir)
    by_color = {}
    dupes = []
    for pid, col, _ in defs:
        if col in by_color and pid != 0:
            dupes.append((col, by_color[col], pid))
        by_color[col] = pid
    unknown = [c for c in counts if c not in by_color]
    ids = sorted(p for p, *_ in defs)
    gaps = [i for i in range(ids[0], ids[-1] + 1) if i not in set(ids)]
    unused = [p for p, c, _ in defs if p != 0 and c not in counts]
    tiny = sorted((n, by_color[c]) for c, n in counts.items() if c in by_color and n < 8)

    print(f"provinces.bmp: {img.size[0]}x{img.size[1]}, {len(counts)} colours")
    print(f"definition.csv: {len(defs)} rows, highest id {ids[-1]}")
    report = [("Colours in bmp missing from definition.csv", unknown),
              ("Duplicate colours in definition.csv (colour, id, id)", dupes),
              ("Missing IDs (IDs must be sequential)", gaps),
              ("Defined but not painted on the map", unused),
              ("Very small provinces (<8 px) - the game may complain", tiny)]
    ok = True
    for title, items in report:
        if items:
            ok = False
            print(f"\n{title}: {len(items)}")
            for i in items[:20]:
                print("   ", i)
            if len(items) > 20:
                print("    ...")
    print("\nAll good." if ok else "\nFix the items above, then re-run.")

def density(map_dir, x0, y0, x1, y1):
    defs = load_defs(map_dir)
    by_color = {c: p for p, c, _ in defs}
    land = {c for p, c, r in defs if len(r) > 4 and r[4].strip() == "land"}
    img = Image.open(Path(map_dir) / "provinces.bmp").convert("RGB").crop((x0, y0, x1, y1))
    counts = color_counts(img)
    land_counts = {c: n for c, n in counts.items() if c in land}
    print(f"Box {x0},{y0} -> {x1},{y1}")
    print(f"  provinces (all): {len(counts)}")
    print(f"  land provinces:  {len(land_counts)}")
    if land_counts:
        print(f"  average land province size: {sum(land_counts.values()) / len(land_counts):.0f} px")

def newcolors(map_dir, n, ptype="land", terrain="plains", continent="1"):
    defs = load_defs(map_dir)
    used = {c for _, c, _ in defs}
    try:
        used |= set(load_bmp(map_dir)[1])
    except FileNotFoundError:
        pass
    next_id = max(p for p, *_ in defs) + 1
    coastal = "false"
    rng = random.Random(next_id)
    out = 0
    while out < n:
        c = (rng.randint(1, 254), rng.randint(1, 254), rng.randint(1, 254))
        if c in used:
            continue
        used.add(c)
        print(f"{next_id};{c[0]};{c[1]};{c[2]};{ptype};{coastal};{terrain};{continent}")
        next_id += 1
        out += 1

def main():
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "check":
        check(a[1])
    elif len(a) == 6 and a[0] == "density":
        density(a[1], *map(int, a[2:]))
    elif len(a) >= 3 and a[0] == "newcolors":
        newcolors(a[1], int(a[2]), *a[3:6])
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
