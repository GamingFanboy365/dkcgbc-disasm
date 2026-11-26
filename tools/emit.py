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

MBC_REGS = {0x0000: "rRAMG", 0x2000: "rROMB0", 0x3000: "rROMB1", 0x4000: "rRAMB"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Small data gaps are written as "db" so labels and code stay readable;
# anything bigger is pulled from the base ROM.
DB_GAP_MAX = 16


def hexb(v):
    return "$%02x" % v


def hexw(v):
    return "$%04x" % v


class Emitter:
    def __init__(self, rom):
        self.rom = rom
        self.t = make(rom)
        self.names = {}      # file offset -> global label name
        self.locals = {}     # file offset -> (scope offset, local name)
        self._name_labels()

    # ---------------------------------------------------------------- labels
    def _name_labels(self):
        t = self.t
        overrides = {off(b, a): n for (b, a), n in hints.NAMES.items()}
        by_bank = {}
        for o, kind in t.labels.items():
            if o not in t.insns:
                continue
            by_bank.setdefault(o // BANK_SIZE, []).append((o, kind))
        for bank, items in by_bank.items():
            items.sort()
            for o, kind in items:
                addr = (o % BANK_SIZE) + (0x4000 if bank else 0)
                if o in overrides:
                    self.names[o] = overrides[o]
                elif kind == "func":
                    self.names[o] = "Func_%02x_%04x" % (bank, addr)
            # Jump targets become locals of the preceding global label; a
            # jump target with no preceding global becomes global itself.
            globals_sorted = sorted(o for o, _ in items if o in self.names)
            import bisect
            for o, kind in items:
                if o in self.names:
                    continue
                addr = (o % BANK_SIZE) + (0x4000 if bank else 0)
                k = bisect.bisect_right(globals_sorted, o) - 1
                if k < 0:
                    self.names[o] = "Jump_%02x_%04x" % (bank, addr)
                    bisect.insort(globals_sorted, o)
                else:
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
        if "{n16}" in t:
            v = i.imm
            txt = None
            if i.flow in ("jp", "jpc", "call", "callc"):
                if v < 0x4000:
                    txt = self.ref(0, v, o)
                elif v < 0x8000:
                    tb = bank if bank else i.ctx
                    if tb:
                        txt = self.ref(tb, v, o)
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
            t = t.replace("{n8}", hexb(i.imm))
        elif "{s8}" in t:
            v = i.imm - 0x100 if i.imm >= 0x80 else i.imm
            if "sp + " in t:
                t = t.replace("sp + {s8}", "sp %s %d" % ("-" if v < 0 else "+", abs(v)))
            else:
                t = t.replace("{s8}", "%d" % v)
        return t

    # ------------------------------------------------------------------ banks
    def code_banks(self):
        return sorted({o // BANK_SIZE for o in self.t.insns})

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
                        out.append("%s:\n" % self.locals[o][1])
                    out.append("\t%s\n" % self.fmt(i, o))
                    if i.flow in ("jp", "jr", "ret", "jphl"):
                        out.append("\n")
                    o += i.length
                else:
                    if gap is None:
                        gap = o
                    o += 1
            if gap is not None:
                self.emit_gap(out, gap, e, base, vbase)
        return "".join(out)

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
        code = self.code_banks()
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
