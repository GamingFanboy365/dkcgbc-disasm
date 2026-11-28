#!/usr/bin/env python3
"""Generate RGBDS source for the DKC GBC disassembly from the original ROM.

Usage: python3 tools/emit.py baserom.gbc

Traces code from the entry points in tools/hints.py, then writes:
  src/bank_XX.asm      one file per bank that contains traced code
  src/data_banks.asm   every bank with no traced code (INCBIN from baserom)
  layout.mk            list of objects for the Makefile

Bytes that are not traced as code are INCBIN'd from baserom.gbc, so no ROM
data needs to be committed. Hand-edited files listed in hints.KEEP are never
overwritten.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hints  # noqa: E402
from run_trace import make  # noqa: E402
from tracer import BANK_SIZE, off  # noqa: E402
from hwregs import HW_REGS  # noqa: E402
from gfx import frame_png_path  # noqa: E402
from backgrounds import FLOW_STATES  # noqa: E402

MBC_REGS = {0x0000: "rRAMG", 0x2000: "rROMB0", 0x3000: "rROMB1", 0x4000: "rRAMB"}
WOBJECTS = 0xC800
OBJ_SIZE = 0x40


def obj_field(f):
    """Symbolic name for an object field offset (see include/objects.inc)."""
    t = hints.OBJ_FIELD_TABLE
    if f in t:
        return t[f][0]
    if f - 1 in t and t[f - 1][1] == 2:
        return t[f - 1][0] + " + 1"
    return "OBJ_VAR_%02X" % f


def write_objects_inc(path):
    t = hints.OBJ_FIELD_TABLE
    covered = set()
    for o, (n, sz, d) in t.items():
        covered |= set(range(o, o + sz))
    lines = ["; Object slots (generated from OBJ_FIELD_TABLE in tools/hints.py).\n",
             ";\n; Objects are $40-byte slots starting at wObjects. Slot 0 is the player.\n",
             "; Every frame RunObjects maps OBJ_BANK and jumps to OBJ_HANDLER for each\n",
             "; active object, with bc = slot offset. Fields are reached with\n",
             ";     ld hl, wObjects + OBJ_FIELD\n;     add hl, bc\n",
             "; Fields named OBJ_VAR_xx belong to the object type: their meaning\n",
             "; depends on the handler.\n\n",
             "IF !DEF(OBJECTS_INC)\nDEF OBJECTS_INC EQU 1\n\n",
             "DEF wObjects EQU $%04x\nDEF wPlayer  EQU wObjects\nDEF OBJ_SIZE EQU $%02x\n\n" % (WOBJECTS, OBJ_SIZE)]
    for o in range(OBJ_SIZE):
        if o in t:
            n, sz, d = t[o]
            lines.append("DEF %-17s EQU $%02x ; %s%s\n" % (n, o, "(word) " if sz == 2 else "", d))
        elif o not in covered:
            lines.append("DEF %-17s EQU $%02x\n" % ("OBJ_VAR_%02X" % o, o))
    lines.append("\n; Other RAM (from RAM_NAMES in tools/hints.py)\n")
    for a, n in sorted(hints.RAM_NAMES.items()):
        lines.append("DEF %-17s EQU $%04x\n" % (n, a))
    lines.append("\n; Front-end routines copied to RAM (FE_RAM_NAMES in tools/hints.py)\n")
    for a, n in sorted(hints.FE_RAM_NAMES.items()):
        lines.append("DEF %-17s EQU $%04x\n" % (n, a))
    lines.append("\n; Funky's Fishing's runtime in RAM (FISHING_RAM_NAMES in tools/hints.py)\n")
    for a, n in sorted(hints.FISHING_RAM_NAMES.items()):
        lines.append("DEF %-26s EQU $%04x\n" % (n, a))
    lines.append("\nENDC\n")
    with open(path, "w") as f:
        f.write("".join(lines))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Small data gaps are written as "db" so labels and code stay readable;
# anything bigger is pulled from the base ROM.
DB_GAP_MAX = 16


def hexb(v):
    return "$%02x" % v


def conv_target(path):
    """The file the build makes from an editable data file."""
    if path.startswith("data/maps/"):
        return path[:-4] + ".lz"
    if path.startswith("data/samples/"):
        return path[:-4] + ".pcm"
    return path[:-4] + ".planar"


def hexw(v):
    return "$%04x" % v


class Emitter:
    def __init__(self, rom):
        self.rom = rom
        self.t = make(rom)
        self.names = {}      # file offset -> global label name
        self.locals = {}     # file offset -> (scope offset, local name)
        self.exported = set()  # locals referenced from other files
        self.gfx_deps = {}     # bank -> graphics files it INCBINs
        self.lohi_map = {}
        for (lo, hi, tb, target) in self.t.lohi:
            self.lohi_map[lo] = ("LOW", tb, target)
            self.lohi_map[hi] = ("HIGH", tb, target)
        self._name_labels()

    # ---------------------------------------------------------------- labels
    def _name_labels(self):
        t = self.t
        import autonames
        import names as name_table
        overrides = {off(b, a): n for (b, a), n in autonames.auto_names(self.rom).items()}
        import levelnames
        descs, ents, self.level_names, _ = levelnames.tables(self.rom)
        overrides.update({off(4, a): n for a, n in descs.items()})
        overrides.update({off(4, a): n for a, n in ents.items()})
        overrides.update({off(b, a): n for (b, a), n in name_table.NAMES.items()})
        overrides.update({off(b, a): n for (b, a), n in hints.NAMES.items()})
        ends = {o + i.length: o for o, i in t.insns.items()}  # end offset -> instruction
        by_bank = {}
        for o, kind in t.labels.items():
            if o not in t.insns:
                continue
            by_bank.setdefault(o // BANK_SIZE, []).append((o, kind))
        for o, pfx in t.data_labels.items():
            by_bank.setdefault(o // BANK_SIZE, []).append((o, "data:" + pfx))
        for bank, items in by_bank.items():
            items.sort()
            for o, kind in items:
                addr = (o % BANK_SIZE) + (0x4000 if bank else 0)
                if o in overrides:
                    self.names[o] = overrides[o]
                elif kind == "func":
                    self.names[o] = "Func_%02x_%04x" % (bank, addr)
                elif kind.startswith("data:"):
                    pfx = kind[5:]
                    self.names[o] = pfx[1:] if pfx.startswith("=") else "%s_%02x_%04x" % (pfx, bank, addr)
            # Jump targets become locals of the preceding global label; a
            # jump target with no preceding global becomes global itself.
            import bisect
            # a data label written as "=.name" is local to the function around it
            dotted = [o for o, _ in items if o in self.names and self.names[o].startswith(".")]
            globals_sorted = sorted(o for o, _ in items if o in self.names and o not in dotted)
            for o in dotted:
                k = bisect.bisect_right(globals_sorted, o) - 1
                self.locals[o] = (globals_sorted[k], self.names.pop(o))
            for o, kind in items:
                if o in self.names or o in self.locals:
                    continue
                addr = (o % BANK_SIZE) + (0x4000 if bank else 0)
                k = bisect.bisect_right(globals_sorted, o) - 1
                if k < 0:
                    self.names[o] = "Jump_%02x_%04x" % (bank, addr)
                    bisect.insort(globals_sorted, o)
                    continue
                if globals_sorted[k] not in t.insns:
                    # the label before is a table: the code after it gets a
                    # global label of its own, at its first instruction
                    start = o
                    while start in ends and ends[start] > globals_sorted[k]:
                        start = ends[start]
                    if start not in self.names:
                        self.names[start] = overrides.get(start) or "Func_%02x_%04x" % (
                            bank, (start % BANK_SIZE) + (0x4000 if bank else 0))
                        bisect.insort(globals_sorted, start)
                    if start == o:
                        continue
                    k = bisect.bisect_right(globals_sorted, o) - 1
                self.locals[o] = (globals_sorted[k], ".jump_%04x" % addr)
        # scope of every code offset, for deciding local vs qualified refs
        self.scope_starts = {}
        for bank in by_bank:
            self.scope_starts[bank] = sorted(o for o in self.names if o // BANK_SIZE == bank)

    def scope_of(self, o):
        import bisect
        lst = self.scope_starts.get(o // BANK_SIZE, [])
        k = bisect.bisect_right(lst, o) - 1
        return lst[k] if k >= 0 else None

    def qref(self, bank, addr):
        """Fully-qualified label for a ROM address, or None."""
        if addr >= 0x8000:
            return None
        o = off(bank, addr) if addr >= 0x4000 else addr
        if o in self.names:
            return self.names[o]
        if o in self.locals:
            scope, name = self.locals[o]
            self.exported.add(o)  # conservative: data may live in another file
            return self.names[scope] + name
        return None

    def ref(self, bank, addr, from_off):
        """Label text for a code address, or None."""
        if addr >= 0x8000:
            return None
        o = off(bank, addr) if addr >= 0x4000 else addr
        if o in self.names:
            return self.names[o]
        if o in self.locals:
            scope, name = self.locals[o]
            if self.scope_of(from_off) == scope:
                return name
            if from_off // BANK_SIZE != o // BANK_SIZE:
                self.exported.add(o)
            return self.names[scope] + name
        return None

    # ----------------------------------------------------------- instructions
    def fmt(self, i, o):
        t = i.text
        bank = o // BANK_SIZE
        if i.farcall:
            fb, fa = i.farcall
            lab = self.ref(fb, fa, o) if fa >= 0x4000 else None
            if lab and "." not in lab:
                return "rst_farcall %s" % lab
            return "rst $00\n\tdw %s\n\tdb %s" % (hexw(fa), hexb(fb))
        fr = getattr(i, "farref", None)
        if fr is not None:
            lab = self.qref(fr[0], fr[1])
            if lab:
                if fr[2] == "addr" and "{n16}" in t:
                    return t.replace("{n16}", lab)
                if fr[2] != "addr" and "{n8}" in t:
                    return t.replace("{n8}", "%s(%s)" % (fr[2], lab))
        if "{n16}" in t:
            v = i.imm
            txt = None
            if 0xF0 <= bank <= 0xFE and v in hints.FE_RAM_NAMES:
                txt = hints.FE_RAM_NAMES[v]
            elif 0x50 <= bank <= 0x56 and v in hints.FISHING_RAM_NAMES:
                txt = hints.FISHING_RAM_NAMES[v]
            elif i.flow in ("jp", "jpc", "call", "callc"):
                if v < 0x4000:
                    txt = self.ref(0, v, o)
                elif v < 0x8000:
                    tb = bank if bank else i.ctx
                    if tb:
                        txt = self.ref(tb, v, o)
            elif i.dataref is not None:
                txt = self.qref(*i.dataref)
            elif v in hints.RAM_NAMES and bank not in hints.SECOND_PROGRAM_BANKS:
                txt = hints.RAM_NAMES[v]
            elif (i.op in (0x21, 0x11, 0x01) and 0x4000 <= v < 0x8000 and bank
                  and bank not in hints.SECOND_PROGRAM_BANKS and off(bank, v) in self.t.data
                  and (i.op == 0x21 or self.t.data[off(bank, v)][0] != "rows")):
                # a table of this bank loaded as a constant (hl: any table;
                # de, bc: only the kinds whose format the tracer parsed)
                txt = self.qref(bank, v)
            elif (WOBJECTS <= v < WOBJECTS + OBJ_SIZE and bank not in hints.SECOND_PROGRAM_BANKS
                  and (t.startswith("ld hl,") or "[{n16}]" in t)):
                nxt = self.t.insns.get(o + i.length)
                indexed = t.startswith("ld hl,") and nxt is not None and nxt.op in (0x09, 0x19)
                txt = "%s + %s" % ("wObjects" if indexed else "wPlayer", obj_field(v - WOBJECTS))
            elif t.startswith("ld [") or t.startswith("ld a, ["):
                if v >= 0xFF00 and v in HW_REGS:
                    txt = HW_REGS[v]
                elif t.startswith("ld [") and v < 0x8000:
                    txt = MBC_REGS.get(v & 0xF000)
            t = t.replace("{n16}", txt or hexw(v))
        elif "{e8}" in t:
            v = i.target
            txt = self.ref(bank if v >= 0x4000 else 0, v, o) if v < 0x8000 else None
            if txt is None:
                d = v - i.addr
                txt = "@ %+d" % d
            t = t.replace("{e8}", txt)
        elif "{a8}" in t:
            v = 0xFF00 | i.imm
            t = t.replace("{a8}", HW_REGS.get(v, hexw(v)))
        elif "{n8}" in t:
            txt = None
            if o in self.lohi_map:
                part, tb, target = self.lohi_map[o]
                lab = self.qref(tb, target)
                if lab:
                    txt = "%s(%s)" % (part, lab)
            t = t.replace("{n8}", txt or hexb(i.imm))
        elif "{s8}" in t:
            v = i.imm - 0x100 if i.imm >= 0x80 else i.imm
            if "sp + " in t:
                t = t.replace("sp + {s8}", "sp %s %d" % ("-" if v < 0 else "+", abs(v)))
            else:
                t = t.replace("{s8}", "%d" % v)
        return t

    # ------------------------------------------------------------------ banks
    def code_banks(self):
        return sorted({o // BANK_SIZE for o in self.t.insns} | {o // BANK_SIZE for o in self.t.data})

    def emit_bank(self, bank):
        rom = self.rom
        t = self.t
        base = bank * BANK_SIZE
        vbase = 0x4000 if bank else 0
        out = []
        if bank == 0:
            out.append('INCLUDE "include/common.inc"\n')
        else:
            out.append('INCLUDE "include/common.inc"\n')
        o = base
        end = base + BANK_SIZE
        sect_start = o
        if bank == 0:
            sections = [(0x0000, 0x0100, 'SECTION "rst00", ROM0[$0000]'),
                        (0x0100, 0x0104, 'SECTION "Entry", ROM0[$0100]'),
                        (0x0104, 0x0150, None),
                        (0x0150, 0x4000, 'SECTION "Home", ROM0[$0150]')]
        else:
            sections = [(base, end, 'SECTION "Bank $%02x", ROMX[$4000], BANK[$%02x]' % (bank, bank))]

        for (s, e, header) in sections:
            if header is None:
                out.append('\nSECTION "Header", ROM0[$0104]\n')
                out.append(HEADER)
                continue
            out.append("\n" + header + "\n")
            o = s
            gap = None
            while o < e:
                if o in t.insns:
                    if gap is not None:
                        self.emit_gap(out, gap, o, base, vbase)
                        gap = None
                    i = t.insns[o]
                    if o in self.names:
                        out.append("\n%s::\n" % self.names[o])
                    elif o in self.locals:
                        out.append("%s%s\n" % (self.locals[o][1], "::" if o in self.exported else ":"))
                    out.append("\t%s\n" % self.fmt(i, o))
                    if i.flow in ("jp", "jr", "ret", "jphl"):
                        out.append("\n")
                    o += i.length
                elif o in t.data:
                    if gap is not None:
                        self.emit_gap(out, gap, o, base, vbase)
                        gap = None
                    for (lo, line) in self.fmt_data(o, t.data[o]):
                        if lo is not None and lo in self.names:
                            out.append("\n%s::\n" % self.names[lo])
                        elif lo is not None and lo in self.locals:
                            out.append("%s%s\n" % (self.locals[lo][1], "::" if lo in self.exported else ":"))
                        out.append(line[1:] + "\n" if line.startswith("\0") else "\t%s\n" % line)
                    o += t.data[o][3]
                else:
                    if gap is None:
                        gap = o
                    o += 1
            if gap is not None:
                self.emit_gap(out, gap, e, base, vbase)
        return "".join(out)

    def fmt_data(self, o, item):
        """Lines for a data item: list of (file offset or None, text)."""
        kind, bank = item[0], item[1]
        if kind == "objinit":
            lines = self.fmt_objinit(item, o)
            return [(o, lines[0])] + [(None, x) for x in lines[1:]]
        if kind == "tiles":
            path = frame_png_path(bank, o % BANK_SIZE + 0x4000)[:-4] + ".2bpp"
            self.gfx_deps.setdefault(bank, []).append(path)
            return [(o, 'INCBIN "%s"' % path.replace(os.sep, "/"))]
        if kind == "sprites":
            sb = [b - 0x100 if b >= 0x80 else b for b in item[2]]
            return [(o if k == 0 else None, "db %d, %d" % (sb[k], sb[k + 1])) for k in range(0, len(sb), 2)]
        if kind == "sprites3":
            # dx, dy and a value added to the sprite's attributes (used when the
            # object's OAM attributes have bit 4 set, DrawSpriteFrame .jump_11ce)
            sb = [b - 0x100 if b >= 0x80 else b for b in item[2]]
            return [(o if k == 0 else None, "db %d, %d, $%02x" % (sb[k], sb[k + 1], item[2][k + 2]) +
                     (" ; dx, dy, attribute add" if k == 0 else "")) for k in range(0, len(sb), 3)]
        if kind == "frames":
            res = []
            for (a, tiles, spr, n, gb) in item[2]:
                fo = off(bank, a)
                if n == 0 and tiles == spr == gb == 0:
                    res.append((fo, "frame_none"))
                    continue
                tl, sl = self.qref(gb, tiles), self.qref(gb, spr)
                if tl and sl:
                    res.append((fo, "frame %s, %s, %d" % (tl, sl, n)))
                else:
                    res.append((fo, "dw %s, %s\n\tdb %d, %s" % (hexw(tiles), hexw(spr), n, hexb(gb))))
            return res
        if kind == "palette":
            rom = self.rom
            res = []
            for k in range(item[2]):
                cols = []
                for c in range(4):
                    v = rom[o + 8 * k + 2 * c] | rom[o + 8 * k + 2 * c + 1] << 8
                    cols.append("%2d, %2d, %2d" % (v & 31, v >> 5 & 31, v >> 10 & 31))
                res.append((o if k == 0 else None, "rgb " + ",  ".join(cols)))
            return res
        if kind == "preload":
            return [(o, "obj_pal_preload " + ", ".join("%d" % x for x in item[2]))]
        if kind == "framestruct":
            fb = self.t.frame_bank
            recs, cols = item[2]
            return [(o if k == 0 else None,
                     "dw " + ", ".join((self.qref(fb, v) or hexw(v)) if j in cols else hexw(v) for j, v in enumerate(r)))
                    for k, r in enumerate(recs)]
        if kind == "animptrs":
            ab = self.t.anim_bank
            names = [self.qref(ab, v) or hexw(v) for v in item[2]]
            return [(o if k == 0 else None, "dw " + ", ".join(names[k:k + 4])) for k in range(0, len(names), 4)]
        if kind == "incbin":
            return [(o, 'INCBIN "baserom.gbc", $%06x, $%04x' % (o, item[3]))]
        if kind == "ramcode":
            # code copied to RAM: disassembled at its RAM address (tools/ramcode.py)
            import ramcode
            dst, pbanks, extra = item[2]
            n = item[3]
            buf = self.rom[o:o + n]

            class _T:
                insns = {x: i for x, i in self.t.insns.items() if x // BANK_SIZE in pbanks}
            ents = ramcode.entries_from(_T, self.rom, dst, n) | set(extra)
            name_of = lambda a: "RAMCode_%02x_%04x" % (bank, a)  # noqa: E731

            def ext_name(v, tmpl):
                if tmpl == "ldh" or (v >= 0xFF00 and ("[{n16}]" in tmpl)):
                    return HW_REGS.get(v)
                if (tmpl.startswith("jp") or tmpl.startswith("call")) and v < 0x4000:
                    return self.qref(0, v)
                return None
            consts, body = ramcode.lines(buf, dst, ents, name_of, ext_name)
            res = [(o, "; runs from $%04x" % dst)]
            res += [(None, "DEF %s EQU $%04x" % (nm, a)) for nm, a in consts]
            # comment lines and blank lines go out unindented (marked with \0)
            res += [(None, ln[1:] if ln.startswith("\t") else "\0" + ln) for ln in body]
            return res
        if kind == "convfile":
            # stored in an editable form; the Makefile converts it back
            # (map layers: tools/lzcomp.py, blocks and terrain: tools/leveldata.py)
            built = conv_target(item[2])
            self.gfx_deps.setdefault(bank, []).append(built)
            return [(o, 'INCBIN "%s"' % built)]
        if kind == "rows":
            # rows: (directive, tokens, comment); a token is literal text or
            # ("ref", bank, addr, width) and becomes a label when there is one
            res = []
            for k, (d, toks, com) in enumerate(item[2]):
                parts = []
                for tk in toks:
                    if isinstance(tk, tuple):
                        _, rb, ra, wd = tk
                        parts.append(self.qref(rb, ra) or (hexw(ra) if wd == 2 else hexb(ra)))
                    else:
                        parts.append(tk)
                line = "%s %s" % (d, ", ".join(parts))
                if com:
                    line += " ; " + com
                res.append((o if k == 0 else None, line))
            return res
        if kind == "bgtiles":
            res = []
            for k, (path, a, n, w) in enumerate(item[2]):
                two = (path[:-4] + ".2bpp").replace(os.sep, "/")
                self.gfx_deps.setdefault(bank, []).append(two)
                res.append((o if k == 0 else None, 'INCBIN "%s"' % two))
            return res
        if kind == "mapheader":
            h = item[2]
            ts = self.qref(h["ts_bank"], h["ts"]) or hexw(h["ts"])
            lay = [self.qref(h["map_bank"], p) or hexw(p) for p in h["layers"]]
            res = [(o, "db BANK(LevelBlocks_%02x), BANK(LevelTerrain_%02x), %s ; block bank, terrain bank, flags"
                    % (h["blocks"], h["terrain"], hexb(h["flags"]))),
                   (None, "dw %s ; ($c45c)" % hexw(h["c45c"])),
                   (None, "db BANK(%s)" % ts), (None, "dw %s ; tileset" % ts),
                   (None, "db BANK(%s)" % lay[0]),
                   (None, "dw %s ; block numbers, block attributes, terrain" % ", ".join(lay[:3]))]
            if len(lay) > 3:
                res.append((None, "dw %s ; same, second half" % ", ".join(lay[3:])))
            return res
        if kind == "ptrtable":
            return [(o if k == 0 else None, "dw %s" % (self.qref(bank, v) or hexw(v))) for k, v in enumerate(item[2])]
        if kind == "worldmap":
            wm = item[2]
            r = wm["raw"]
            ts = self.qref(wm["ts_bank"], wm["ts"]) or hexw(wm["ts"])
            return [(o, "db %s ; scroll limit, ?, level markers (pointer)" % ", ".join(hexb(x) for x in r[:4])),
                    (None, "dw %s ; tile map" % (self.qref(0x0F, wm["map"]) or hexw(wm["map"]))),
                    (None, "dw %s ; list copied to $c500" % hexw(wm["list"])),
                    (None, "dw %s ; BG palettes" % (self.qref(0x0F, wm["palettes"]) or hexw(wm["palettes"]))),
                    (None, "dw %s" % ts), (None, "db BANK(%s) ; tileset" % ts)]
        if kind == "worldtiles":
            rom, n = self.rom, item[2]
            res = [(o, "db %d ; width in tiles; then per column 18 tiles, 18 attributes" % n)]
            for c in range(n):
                b = o + 1 + 36 * c
                res.append((None, "db " + ", ".join(hexb(x) for x in rom[b:b + 18])))
                res.append((None, "db " + ", ".join(hexb(x) for x in rom[b + 18:b + 36])))
            return res
        if kind == "screen":
            r = item[2]
            names = [self.qref(bank, r[k]) or hexw(r[k]) for k in ("palettes", "map", "tiles")]
            return [(o, "dw %s ; palettes, tile map, tiles" % ", ".join(names))]
        if kind == "pictable":
            res = []
            for k, r in enumerate(item[2]):
                names = [self.qref(*r[f]) for f in ("map", "palettes", "tiles")]
                if all(names):
                    txt = "picture %s, %s, %s ; %d" % (names[0], names[1], names[2], r["index"])
                else:
                    txt = "db %s\n\tdw %s\n\tdb %s\n\tdw %s\n\tdb %s\n\tdw %s ; %d (placeholder)" % (
                        hexb(r["map"][0]), hexw(r["map"][1]), hexb(r["palettes"][0]), hexw(r["palettes"][1]),
                        hexb(r["tiles"][0]), hexw(r["tiles"][1]), r["index"])
                res.append((o if k == 0 else None, txt))
            return res
        if kind == "maprun":
            rom = self.rom
            labs = set(item[2])
            res, k, n = [], 0, item[3]
            while k < n:
                step = 20
                for x in sorted(labs):
                    if o + k < x < o + k + step:
                        step = x - (o + k)
                step = min(step, n - k)
                res.append((o + k if (o + k) in labs or k == 0 else None,
                            "db " + ", ".join(hexb(x) for x in rom[o + k:o + k + step])))
                k += step
            return res
        if kind == "titletables":
            tt = item[2]
            rom = self.rom
            rw_ = lambda a: rom[off(bank, a)] | rom[off(bank, a) + 1] << 8  # noqa: E731
            n = tt["count"]
            res = [(o, "dw " + ", ".join(self.qref(bank, rw_(tt["maps"] + 2 * k)) or hexw(rw_(tt["maps"] + 2 * k))
                                        for k in range(n)) + " ; maps")]
            res.append((None, "dw " + ", ".join(self.qref(bank, rw_(tt["palettes"] + 2 * k)) or
                                                 hexw(rw_(tt["palettes"] + 2 * k)) for k in range(n)) + " ; palettes"))
            for k in range(n):
                tb_, ta = rom[off(bank, tt["tilesets"] + 3 * k)], rw_(tt["tilesets"] + 3 * k + 1)
                lab = self.qref(tb_, ta)
                res.append((None, ("db BANK(%s)\n\tdw %s" % (lab, lab)) if lab else "db %s\n\tdw %s" % (hexb(tb_), hexw(ta))))
            res.append((None, "dw " + ", ".join(self.qref(bank, rw_(tt["lists"] + 2 * k)) or
                                                 hexw(rw_(tt["lists"] + 2 * k)) for k in range(n)) + " ; palette swaps"))
            return res
        if kind == "titlemap":
            rom = self.rom
            return [(o if k == 0 else None, "db " + ", ".join(hexb(x) for x in rom[o + 20 * k:o + 20 * k + 20])
                     + (" ; tiles" if k % 2 == 0 else " ; attributes"))
                    for k in range(72)]
        if kind == "titlelist":
            res = [(o if k == 0 else None, "db %d, %s, %s ; at line %d, palette %d -> slot %d"
                    % (L, hexb(e), ("$80 | %d" % (b & 0x7F)) if b & 0x80 else hexb(b), L, e // 8, (b & 0x7F) // 8))
                   for k, (L, e, b) in enumerate(item[2])]
            res.append((None, "db $ff"))
            return res
        if kind == "boxmap":
            w, h = item[2]
            rom = self.rom
            res = []
            for k in range(2 * h):
                row = rom[o + w * k:o + w * k + w]
                res.append((o if k == 0 else None, "db " + ", ".join(hexb(x) for x in row)
                            + (" ; %s" % ("attributes" if k == 0 else "tiles") if k in (0, h) else "")))
            return res
        if kind == "screenmap":
            rom = self.rom
            res = []
            for k in range(36):
                part = "attributes" if k < 18 else "tiles"
                row = rom[o + 20 * k:o + 20 * k + 20]
                res.append((o if k == 0 else None, "db " + ", ".join(hexb(x) for x in row)
                            + (" ; %s" % part if k in (0, 18) else "")))
            return res
        if kind == "flow":
            entries, labels = item[2]
            res = []
            for a, c in entries:
                fo = off(bank, a)
                if c[0] == "jump":
                    res.append((fo, "flow_jump %s" % (self.qref(bank, c[1]) or hexw(c[1]))))
                    continue
                st, args = c[1], c[2]
                if st == 0x1F:
                    p, b = args[0] | args[1] << 8, args[2]
                    lab = self.qref(b, p)
                    res.append((fo, "flow_load_screen %s" % lab if lab else
                                "db FLOW_LOAD_SCREEN\n\tdw %s\n\tdb %s" % (hexw(p), hexb(b))))
                elif st == 0x4C:
                    res.append((fo, "flow_wait %d" % (args[0] | args[1] << 8)))
                elif st == 0x19:
                    res.append((fo, "flow_play_song %s" % hexb(args[0])))
                elif st == 0x1C:
                    res.append((fo, "flow_fade %s" % hexb(args[0])))
                else:
                    res.append((fo, "db %s" % FLOW_STATES.get(st, "$%02x" % st)))
            return res
        if kind == "frameptrs":
            fb = self.t.frame_bank
            names = [self.qref(fb, v) or hexw(v) for v in item[2]]
            return [(o if k == 0 else None, "dw " + ", ".join(names[k:k + 4])) for k in range(0, len(names), 4)]
        if kind == "leveltable":
            res = []
            for k, (a, b) in enumerate(item[2]):
                la = self.qref(bank, a) if a else "0"
                lb = self.qref(bank, b) if b else "0"
                res.append((o if k == 0 else None, "dw %s, %s ; level $%02x%s" % (
                    la or hexw(a), lb or hexw(b), k, " " + self.level_names[k] if k in self.level_names else "")))
            return res
        if kind == "levelentrance":
            r = self.rom[o:o + 8]
            d = r[0] | r[1] << 8
            return [(o, "dw %s" % (self.qref(bank, d) or hexw(d))),
                    (None, "db " + ", ".join(hexb(x) for x in r[2:]))]
        if kind == "leveldesc":
            r = self.rom[o:o + 12]
            w = lambda i: r[i] | r[i + 1] << 8  # noqa: E731
            pb = self.t.palette_bank
            return [(o, "db %s" % hexb(r[0])),
                    (None, "dw %s ; BG palettes" % (self.qref(pb, w(1)) or hexw(w(1)))),
                    (None, "dw %s ; OBJ palettes to preload" % (self.qref(pb, w(3)) or hexw(w(3)))),
                    (None, "dw %s, %s ; map header (Func_00_0b4f), level objects? (Func_00_1715)"
                     % (self.qref(bank, w(5)) or hexw(w(5)), hexw(w(7)))),
                    (None, "db %s ; bank of the second pointer" % hexb(r[9])),
                    (None, "db %s, %s" % (hexb(r[10]), hexb(r[11])))]
        if kind == "anim":
            res = []
            for ent in item[2]:
                fo = off(bank, ent[0])
                if ent[1] == "frame":
                    res.append((fo, "anim_frame %s" % (self.qref(self.t.frame_bank, ent[2]) or hexw(ent[2]))))
                    continue
                c, e, w = ent[2], ent[3], ent[4]
                if c == 0:
                    txt = "anim_jump %s" % (self.qref(bank, w) or hexw(w))
                elif c == 1:
                    txt = "anim_speed %d" % e
                elif c == 2:
                    txt = "anim_call %s" % (self.qref(bank if w >= 0x4000 else 0, w) or hexw(w))
                elif c == 3:
                    txt = "anim_clear_flag"
                elif c == 4:
                    txt = "anim_param %s" % hexb(e)
                elif c == 5:
                    txt = "anim_var38 %s" % hexw(w)
                elif c == 6:
                    txt = "anim_xor_attr %s" % hexb(e)
                elif 7 <= c <= 10:
                    txt = "anim_sfx %d, %s" % (c - 6, hexb(e))
                else:
                    txt = "db %s, %s" % (hexb(e), hexb(0x80 | c))
                res.append((fo, txt))
            return res
        raise ValueError(kind)

    def fmt_objinit(self, item, o):
        _, bank, entries, _ = item
        fields = {}
        for e in entries:
            if e[0] == "byte":
                fields[e[1]] = e[2]
            elif e[0] == "word":
                fields[e[1]] = e[2] & 0xFF
                fields[e[1] + 1] = e[2] >> 8
        handler = None
        if 2 in fields and 3 in fields:
            v = fields[2] | fields[3] << 8
            hb = 0 if v < 0x4000 else fields.get(1, bank)
            handler = self.qref(hb, v)
        import levelnames
        merged = levelnames.list_fields(self.rom, bank, o % 0x4000 + (0x4000 if bank else 0))
        leads = (merged.get(1), merged.get(2, 0) | merged.get(3, 0) << 8) in levelnames.ENTRANCE_HANDLERS
        e0, e1 = hints.LEVELS["entrances"]
        lines = []
        for e in entries:
            if e[0] == "byte":
                f, v = e[1], e[2]
                if f == 1 and handler and fields[2] | fields[3] << 8 >= 0x4000:
                    val = "BANK(%s)" % handler
                else:
                    val = hexb(v)
                lines.append("obj_byte %s, %s" % (obj_field(f), val))
            elif e[0] == "word":
                f, v = e[1], e[2]
                val = handler if (f == 2 and handler) else None
                if f == 0x22 and 0x4000 <= v < 0x8000:
                    val = self.qref(self.t.anim_bank, v)
                elif f == 0x20 and 0x4000 <= v < 0x8000:
                    val = self.qref(self.t.frame_bank, v)
                elif leads and f in (0x2E, 0x30) and e0 <= v < e1 and (v - e0) % 8 == 0:
                    val = self.qref(4, v)  # entrance to go to / to come back to
                elif f == 0x04 and v < 0x8000:
                    val = self.qref(9 if v >= 0x4000 else 0, v)  # see tracer.TOUCH_BANK
                elif (f, v) in getattr(self.t, "obj_ptr_refs", {}):
                    val = self.qref(self.t.obj_ptr_refs[(f, v)], v)
                elif f == 0x3B and bank in (8, 0x0E) and 0x502F <= v < 0x50DE:
                    val = self.qref(8, v)  # next initialiser in a chain (Func_08_4344)
                val = val or hexw(v)
                lines.append("obj_word %s, %s" % (obj_field(f), val))
            elif e[0] == "include":
                lab = self.qref(0 if e[1] < 0x4000 else bank, e[1])
                lines.append("obj_include %s" % (lab or hexw(e[1])))
            else:
                lines.append("obj_end" if e[1] == 0x81 else "obj_end %s" % hexb(e[1]))
        return lines

    def emit_gap(self, out, s, e, base, vbase):
        n = e - s
        addr = s - base + vbase
        if all(b == 0 for b in self.rom[s:e]) and n >= 4:
            out.append("\tds %d, $00 ; %s\n" % (n, hexw(addr)))
        elif n <= DB_GAP_MAX:
            out.append("\tdb %s\n" % ", ".join(hexb(b) for b in self.rom[s:e]))
        else:
            out.append('\tINCBIN "baserom.gbc", $%06x, $%04x ; %s\n' % (s, n, hexw(addr)))
        out.append("\n")

    # --------------------------------------------------------------- top level
    def write_all(self):
        os.makedirs(os.path.join(ROOT, "src"), exist_ok=True)
        write_objects_inc(os.path.join(ROOT, "include", "objects.inc"))
        import music
        music.write_include(os.path.join(ROOT, "include", "music.inc"))
        code = self.code_banks()
        for b in code:  # first pass only collects cross-file references
            self.emit_bank(b)
        objs = []
        for b in code:
            path = os.path.join(ROOT, "src", "bank_%02x.asm" % b)
            rel = os.path.relpath(path, ROOT)
            objs.append("src/bank_%02x.o" % b)
            if rel in hints.KEEP:
                continue
            with open(path, "w") as f:
                f.write("; Generated by tools/emit.py -- add to hints.KEEP once hand-edited.\n")
                f.write(self.emit_bank(b))
        # data-only banks
        lines = ['; Banks with no disassembled code yet (generated by tools/emit.py).\n\n',
                 'INCLUDE "include/common.inc"\n']
        for b in range(1, len(self.rom) // BANK_SIZE):
            if b in code:
                continue
            lines.append('\nSECTION "Bank $%02x", ROMX[$4000], BANK[$%02x]\n' % (b, b))
            chunk = self.rom[b * BANK_SIZE:(b + 1) * BANK_SIZE]
            if chunk.count(0) == BANK_SIZE:
                lines.append("\tds $4000, $00\n")
            else:
                lines.append('\tINCBIN "baserom.gbc", $%02x * $4000, $4000\n' % b)
        with open(os.path.join(ROOT, "src", "data_banks.asm"), "w") as f:
            f.write("".join(lines))
        objs.append("src/data_banks.o")
        with open(os.path.join(ROOT, "layout.mk"), "w") as f:
            f.write("# Generated by tools/emit.py\nOBJS := \\\n")
            f.write("".join("\t%s \\\n" % x for x in objs))
            f.write("\n")
            gfx = sorted(set(p for v in self.gfx_deps.values() for p in v))
            f.write("GFX := \\\n" + "".join("\t%s \\\n" % x for x in gfx) + "\n")
            for b in sorted(self.gfx_deps):
                f.write("src/bank_%02x.o: %s\n" % (b, " ".join(sorted(set(self.gfx_deps[b])))))
        t = self.t
        total = sum(i.length for i in t.insns.values())
        print("banks with code:", " ".join("%02x" % b for b in code))
        print("traced code bytes: %d, functions: %d" % (total, len(self.names)))


HEADER = """\
	ds $0134 - $0104, $00 ; Nintendo logo (filled in by rgbfix -v)

	db "DK COUNTRY", $00 ; title
	db "BDDE"            ; manufacturer / game code
	db CART_COMPATIBLE_GBC_ONLY
	db "01"              ; new licensee code (Nintendo)
	db $00               ; SGB flag
	db CART_ROM_MBC5_RAM_BAT
	db CART_ROM_4096KB
	db CART_SRAM_8KB
	db CART_DEST_NON_JAPANESE
	db $33               ; old licensee code (use new)
	db $00               ; mask ROM version
	db $00               ; header checksum (filled in by rgbfix -v)
	dw $0000             ; global checksum (filled in by rgbfix -v)
"""


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "baserom.gbc"), "rb").read()
    Emitter(rom).write_all()


if __name__ == "__main__":
    main()
