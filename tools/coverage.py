#!/usr/bin/env python3
"""How much of the ROM is disassembled, by category.

  python3 tools/coverage.py [baserom.gbc] [--banks]

Categories (by byte):
  code       traced instructions
  data       decoded into readable structures (lists, scripts, palettes...)
  graphics   built from PNGs
  files      built from other editable files (level maps, blocks, terrain)
  raw        located and labelled, format known, still raw bytes
  empty      padding (runs of 16+ identical $00/$ff bytes nothing claims)
  unknown    not identified yet, INCBIN'd from the base ROM
--banks also prints the unknown bytes per bank; --runs lists each unknown run.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_trace import make  # noqa: E402

NAMES = {
    "code": "Code disassembled into readable instructions",
    "data": "Data decoded into readable structures",
    "files": "Data converted to editable files",
    "graphics": "Graphics converted to editable PNGs",
    "raw": "Located and labelled, format known, still raw bytes",
    "unknown": "Not identified yet",
}
RAW_KINDS = {"incbin"}
FILE_KINDS = {"convfile"}
GFX_KINDS = {"tiles", "bgtiles"}


def categorize(rom, t=None):
    t = t or make(rom)
    n = len(rom)
    cat = ["unknown"] * n
    for o, i in t.insns.items():
        for k in range(i.length):
            cat[o + k] = "code"
    for o, (kind, _, _, length) in t.data.items():
        if kind == "ramcode":  # code copied to RAM (tools/ramcode.py)
            for j in range(length):
                cat[o + j] = "code"
            continue
        c = "raw" if kind in RAW_KINDS else "graphics" if kind in GFX_KINDS else "files" if kind in FILE_KINDS else "data"
        for j in range(length):
            cat[o + j] = c
    for k in range(0x104, 0x150):  # the cartridge header (written by emit.py's HEADER)
        cat[k] = "data"
    i = 0
    while i < n:
        if cat[i] == "unknown" and rom[i] in (0x00, 0xFF):
            j = i
            while j < n and cat[j] == "unknown" and rom[j] == rom[i]:
                j += 1
            if j - i >= 16:
                for k in range(i, j):
                    cat[k] = "empty"
            i = j
        else:
            i += 1
    return cat


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rom = open(args[0] if args else "baserom.gbc", "rb").read()
    cat = categorize(rom)
    c = Counter(cat)
    total = len(rom) - c["empty"]
    print("| Category | Size | Share of non-empty ROM |")
    print("|---|---|---|")
    for k in ("code", "data", "graphics", "files", "raw", "unknown"):
        print("| %s | %d KB | %.1f%% |" % (NAMES[k], round(c[k] / 1024), 100 * c[k] / total))
    print("\nEmpty padding: %d KB (not counted)." % round(c["empty"] / 1024))
    if "--banks" in sys.argv:
        for b in range(len(rom) // 0x4000):
            u = cat[b * 0x4000:(b + 1) * 0x4000].count("unknown")
            if u:
                print("bank $%02x: %5d unknown bytes" % (b, u))
    if "--runs" in sys.argv:
        i = 0
        while i < len(rom):
            if cat[i] == "unknown":
                j = i
                while j < len(rom) and cat[j] == "unknown":
                    j += 1
                b = i // 0x4000
                print("$%02x:%04x %5d" % (b, i % 0x4000 + (0x4000 if b else 0), j - i))
                i = j
            else:
                i += 1


if __name__ == "__main__":
    main()
