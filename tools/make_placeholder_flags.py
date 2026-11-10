#!/usr/bin/env python3
"""Draw simple placeholder flags (82x52, 41x26, 10x7 TGA) for every Shattered Continent tag.
Replace them with real artwork whenever you like: same file names, same sizes, 32-bit TGA."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "gfx" / "flags"
W, H = 820, 520

def flag(fn):
    im = Image.new("RGBA", (W, H)); fn(ImageDraw.Draw(im)); return im

designs = {
    "WST": lambda d: (d.rectangle([0, 0, W, H], fill=(60, 58, 55)), d.line([0, H, W, 0], fill=(110, 105, 95), width=60)),
    "ALP": lambda d: (d.rectangle([0, 0, W, H], fill=(25, 25, 28)), d.polygon([(160, 430), (410, 110), (660, 430)], fill=(190, 190, 195)), d.polygon([(330, 210), (410, 110), (490, 210)], fill=(245, 245, 245))),
    "FNO": lambda d: (d.rectangle([0, 0, W, H], fill=(95, 92, 78)), d.rectangle([0, 200, W, 320], fill=(20, 20, 20)), d.rectangle([0, 230, W, 290], fill=(150, 150, 150))),
    "HNS": lambda d: (d.rectangle([0, 0, W, H // 2], fill=(255, 255, 255)), d.rectangle([0, H // 2, W, H], fill=(175, 25, 35))),
    "LYO": lambda d: (d.rectangle([0, 0, W, H], fill=(190, 30, 30)), d.rectangle([0, 0, 240, H], fill=(230, 180, 40))),
    "HST": lambda d: (d.rectangle([0, 0, W, H], fill=(170, 130, 50)), d.polygon([(0, 0), (260, 0), (W, H - 260), (W, H), (560, H), (0, 260)], fill=(30, 25, 20))),
    "LGN": lambda d: (d.rectangle([0, 0, W, H], fill=(85, 105, 70)), d.polygon([(0, 0), (380, H // 2), (0, H)], fill=(235, 230, 210))),
}

for tag, fn in designs.items():
    im = flag(fn)
    for sub, size in (("", (82, 52)), ("medium", (41, 26)), ("small", (10, 7))):
        d = OUT / sub if sub else OUT
        d.mkdir(parents=True, exist_ok=True)
        im.resize(size, Image.LANCZOS).save(d / f"{tag}.tga")
print("Flags written to", OUT)
