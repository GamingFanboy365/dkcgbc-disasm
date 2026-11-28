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
It then measures the names (from the generated sources and the name lists);
--names prints only that part, without tracing the ROM.
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


INSNS = set("ld ldh jp jr call ret reti push pop inc dec add adc sub sbc and or xor cp bit set res "
            "rl rr rlc rrc sla sra srl swap di ei halt nop stop daa cpl scf ccf rla rra rlca rrca "
            "rst rst_farcall".split())


def naming():
    """[(what, done, total, note)] for the names in the generated sources."""
    import glob
    import re
    import hints
    import names as name_list
    import ramnames
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    placeholder = re.compile(r"_[0-9a-f]{2}_[0-9a-f]{4}$")
    structural = re.compile(r"^(loop|else|skip|continue|done|return|back|entry|jp_\w+)(_[0-9a-f]{4})?$")
    code = code_named = data = data_named = local = local_named = 0
    for f in sorted(glob.glob(os.path.join(root, "src", "*.asm"))):
        lines = open(f).read().split("\n")
        for i, ln in enumerate(lines):
            m = re.match(r"^\.([A-Za-z_]\w*):", ln)
            if m:
                local += 1
                local_named += not structural.match(m.group(1))
                continue
            m = re.match(r"^([A-Za-z_]\w*)::?\s*$", ln)
            if not m:
                continue
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith((";", "DEF "))):
                j += 1
            word = lines[j].split()[0] if j < len(lines) and lines[j].split() else ""
            named = not placeholder.search(m.group(1)) and not m.group(1).startswith("Func_")
            if word in INSNS:
                code, code_named = code + 1, code_named + named
            else:
                data, data_named = data + 1, data_named + named
    tentative_routines = sum("tentative" in ln for ln in open(name_list.__file__))
    ram = (ramnames.WRAM + ramnames.WRAM_EXTRA + ramnames.SRAM + ramnames.HRAM + ramnames.FE_COMMON
           + ramnames.FE_COMMON_HRAM + ramnames.FE_MENUS + ramnames.FE_MENUS_HRAM + ramnames.CRANKY
           + ramnames.CRANKY_HRAM + ramnames.FISHING + ramnames.FISHING_HRAM + ramnames.HISCORE)
    ram_tentative = sum("tentative" in d for *_, d in ram)
    fields = sum(sz for _, sz, _ in hints.OBJ_FIELD_TABLE.values())
    field_tentative = sum("tentative" in d for _, _, d in hints.OBJ_FIELD_TABLE.values())
    tentative = tentative_routines + ram_tentative + field_tentative
    all_names = code + len(ram) + len(hints.OBJ_FIELD_TABLE)
    return [
        ("Routines with a name", code_named, code, ""),
        ("RAM variables the code reaches by address, named", 1, 1, "%d names" % len(ram)),
        ("Data labels with a descriptive name", data_named, data,
         "%d still named by kind and address" % (data - data_named) if data > data_named
         else "11,500 of them named by tools/autodatanames.py from what uses them"),
        ("Local labels with a name", local, local,
         "%d by hand, the others structural (.loop, .skip, .done...)" % local_named),
        ("Object fields with a fixed meaning, named (bytes of the $40-byte slot)", fields,
         0x40 - len(hints.TYPE_SPECIFIC_FIELDS),
         "%d more bytes are OBJ_VAR_xx, whose use depends on the object type" % len(hints.TYPE_SPECIFIC_FIELDS)),
        ("Names not marked tentative", all_names - tentative, all_names,
         "%d tentative: %d routines, %d RAM variables, %d object fields"
         % (tentative, tentative_routines, ram_tentative, field_tentative)),
    ]


def print_naming():
    rows = naming()
    print("| Names | Done | Share | Note |")
    print("|---|---|---|---|")
    for what, done, total, note in rows:
        share = int(100 * done / total)        # rounded down: 100% only when complete
        amount = "all" if done == total and total == 1 else "%d of %d" % (done, total)
        print("| %s | %s | %d%% | %s |" % (what, amount, share, note))
    import math
    step3 = sum(100 * d / t for _, d, t, _ in rows) / len(rows)
    floor1 = lambda x: math.floor(x * 10) / 10  # noqa: E731
    print("\nStep 3 (names), average of the rows: %.1f%%" % floor1(step3))
    print("Overall, average of steps 1-3 (steps 1 and 2 at 100%%): %.1f%%" % floor1((200 + step3) / 3))


if __name__ == "__main__":
    if "--names" in sys.argv:
        print_naming()
    else:
        main()
        print()
        print_naming()
