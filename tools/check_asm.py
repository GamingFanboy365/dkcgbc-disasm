#!/usr/bin/env python3
"""Independent re-assembler used to sanity-check the generated sources.

This understands only the subset of RGBDS syntax that tools/emit.py writes
(plus the macros in include/macros.inc). It assembles every file listed in
layout.mk, then compares the result with baserom.gbc, ignoring the header
fields that rgbfix fills in. It is NOT a replacement for building with
RGBDS -- it exists to catch label/layout mistakes in the generator.

Usage: python3 tools/check_asm.py [baserom.gbc]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sm83 import OPS, CB  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = 0x4000

FIXED = {"a", "b", "c", "d", "e", "h", "l", "[hl]", "af", "bc", "de", "hl", "sp",
         "nz", "z", "nc", "[bc]", "[de]", "[hli]", "[hld]", "[c]"}


def shape_of(text):
    m, _, rest = text.strip().partition(" ")
    ops = [x.strip() for x in rest.split(",")] if rest.strip() else []
    shp, exprs = [], []
    for x in ops:
        if x in FIXED:
            shp.append(x)
        elif x.startswith("sp +") or x.startswith("sp -"):
            shp.append("sp+#")
            exprs.append(x[2:].replace(" ", ""))
        elif x.startswith("[") and x.endswith("]"):
            shp.append("[#]")
            exprs.append(x[1:-1])
        else:
            shp.append("#")
            exprs.append(x)
    return m + " " + ",".join(shp), exprs


EXACT = {}
SHAPES = {}
for op, ent in enumerate(OPS):
    if ent is None or op == 0xCB:
        continue
    tmpl, length, flow = ent
    if "{" not in tmpl:
        EXACT[tmpl] = bytes([op]) if op != 0x10 else b"\x10\x00"
        continue
    kind = re.search(r"\{(\w+)\}", tmpl).group(1)
    probe = tmpl.replace("sp + {s8}", "sp + 0").replace("{%s}" % kind, "0")
    shp, _ = shape_of(probe)
    SHAPES[shp] = (op, kind)
for k, t in enumerate(CB):
    EXACT[t] = bytes([0xCB, k])


class Asm:
    def __init__(self):
        self.syms = {}
        self.rom = bytearray(256 * BANK)
        self.written = bytearray(256 * BANK)
        self.base = open(os.path.join(ROOT, "baserom.gbc"), "rb").read() if False else None

    def define_constants(self, path):
        for line in open(path):
            m = re.match(r"\s*DEF\s+(\w+)\s+EQU\s+(\S+)", line)
            if m:
                self.syms[m.group(1)] = self.eval(m.group(2))

    def eval(self, expr, pc=None, scope=None, bank_of=None):
        e = expr.strip()
        e = re.sub(r"BANK\(([\w.]+)\)", lambda m: str(self.label_bank(m.group(1), scope)), e)
        e = e.replace("@", str(pc) if pc is not None else "@")

        def name(m):
            n = m.group(0)
            if n.startswith("."):
                n = scope + n
            if n not in self.syms:
                raise KeyError(n)
            return str(self.syms[n])
        e = re.sub(r"\$([0-9a-fA-F]+)", lambda m: str(int(m.group(1), 16)), e)
        e = re.sub(r"(?<![\w.])[A-Za-z_.][\w.]*", name, e)
        return int(eval(e, {"__builtins__": {}}))

    def label_bank(self, n, scope):
        if n.startswith("."):
            n = scope + n
        return self.banks[n]

    def parse_files(self, files):
        """Returns list of (file, lineno, kind, data, pc_offset, scope)."""
        items = []
        self.banks = {}
        for f in files:
            pc = None
            fo = None  # file offset
            scope = None
            for ln, raw in enumerate(open(os.path.join(ROOT, f)), 1):
                line = raw.split(";", 1)[0].rstrip()
                if not line.strip():
                    continue
                s = line.strip()
                if s.startswith("INCLUDE"):
                    continue
                m = re.match(r'SECTION "[^"]*", (ROM0|ROMX)\[\$([0-9a-f]+)\](?:, BANK\[\$([0-9a-f]+)\])?', s)
                if m:
                    pc = int(m.group(2), 16)
                    bank = int(m.group(3), 16) if m.group(3) else 0
                    fo = pc if m.group(1) == "ROM0" else bank * BANK + pc - 0x4000
                    scope = None  # RGBDS resets the label scope at each SECTION
                    continue
                m = re.match(r"^([A-Za-z_][\w]*)::?$", s)
                if m and not raw[0].isspace():
                    scope = m.group(1)
                    self.syms[scope] = pc
                    self.banks[scope] = fo // BANK
                    continue
                m = re.match(r"^(\.[\w]+):{0,2}$", s)
                if m and not raw[0].isspace():
                    if scope is None:
                        raise SystemExit("%s:%d: local label %s has no global label scope" % (f, ln, m.group(1)))
                    self.syms[scope + m.group(1)] = pc
                    self.banks[scope + m.group(1)] = fo // BANK
                    continue
                size = self.size_of(s)
                items.append((f, ln, s, pc, fo, scope))
                pc += size
                fo += size
        return items

    def size_of(self, s):
        m, _, rest = s.partition(" ")
        if m == "db":
            return len(split_args(rest)) if not rest.strip().startswith('"') else self.db_len(rest)
        if m == "dw":
            return 2 * len(split_args(rest))
        if m == "ds":
            return self.eval(split_args(rest)[0])
        if m == "INCBIN":
            return self.eval(split_args(rest)[2])
        if m == "rst_farcall":
            return 4
        if m == "obj_byte":
            return 2
        if m in ("obj_word", "obj_include"):
            return 3
        if m == "obj_end":
            return 1
        if s in EXACT:
            return len(EXACT[s])
        shp, _ = shape_of(s)
        if shp not in SHAPES:
            raise SyntaxError("unknown instruction: " + s)
        return OPS[SHAPES[shp][0]][1]

    def db_len(self, rest):
        n = 0
        for a in split_args(rest):
            n += len(a) - 2 if a.startswith('"') else 1
        return n

    def assemble(self, items, base):
        for (f, ln, s, pc, fo, scope) in items:
            try:
                data = self.encode(s, pc, scope, base)
            except Exception as ex:  # noqa: BLE001
                raise SystemExit("%s:%d: %s: %s" % (f, ln, s, ex))
            self.rom[fo:fo + len(data)] = data
            for k in range(len(data)):
                self.written[fo + k] += 1

    def encode(self, s, pc, scope, base):
        m, _, rest = s.partition(" ")
        ev = lambda x: self.eval(x, pc, scope)  # noqa: E731
        if m == "db":
            out = bytearray()
            for a in split_args(rest):
                if a.startswith('"'):
                    out += a[1:-1].encode()
                else:
                    out.append(ev(a) & 0xFF)
            return bytes(out)
        if m == "dw":
            out = bytearray()
            for a in split_args(rest):
                v = ev(a)
                out += bytes([v & 0xFF, v >> 8 & 0xFF])
            return bytes(out)
        if m == "ds":
            a = split_args(rest)
            return bytes([ev(a[1]) if len(a) > 1 else 0]) * ev(a[0])
        if m == "INCBIN":
            a = split_args(rest)
            st, n = ev(a[1]), ev(a[2])
            return base[st:st + n]
        if m == "obj_byte":
            f, v = split_args(rest)
            return bytes([ev(f), ev(v) & 0xFF])
        if m == "obj_word":
            f, v = split_args(rest)
            v = ev(v)
            return bytes([0x40 | ev(f), v & 0xFF, v >> 8])
        if m == "obj_include":
            v = ev(rest)
            return bytes([0x80, v & 0xFF, v >> 8])
        if m == "obj_end":
            return bytes([ev(rest) if rest.strip() else 0x81])
        if m == "rst_farcall":
            v = ev(rest)
            return bytes([0xC7, v & 0xFF, v >> 8, self.label_bank(rest.strip(), scope)])
        if s in EXACT:
            return EXACT[s]
        shp, exprs = shape_of(s)
        op, kind = SHAPES[shp]
        v = ev(exprs[0] if len(exprs) == 1 else exprs[-1])
        if kind == "n16":
            assert 0 <= v <= 0xFFFF, v
            return bytes([op, v & 0xFF, v >> 8])
        if kind == "n8":
            assert -0x80 <= v <= 0xFF, v
            return bytes([op, v & 0xFF])
        if kind == "a8":
            assert 0xFF00 <= v <= 0xFFFF, v
            return bytes([op, v & 0xFF])
        if kind == "s8":
            assert -0x80 <= v <= 0x7F, v
            return bytes([op, v & 0xFF])
        if kind == "e8":
            d = v - (pc + 2)
            assert -0x80 <= d <= 0x7F, "jr out of range"
            return bytes([op, d & 0xFF])
        raise SyntaxError(s)


def split_args(rest):
    out, cur, q = [], "", False
    for ch in rest:
        if ch == '"':
            q = not q
        if ch == "," and not q:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def main():
    base = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "baserom.gbc"), "rb").read()
    objs = re.findall(r"(src/\S+)\.o", open(os.path.join(ROOT, "layout.mk")).read())
    files = [o + ".asm" for o in objs]
    a = Asm()
    a.define_constants(os.path.join(ROOT, "include", "hardware.inc"))
    a.define_constants(os.path.join(ROOT, "include", "macros.inc"))
    a.define_constants(os.path.join(ROOT, "include", "objects.inc"))
    items = a.parse_files(files)
    a.assemble(items, base)
    # header fields filled in by rgbfix
    for r in list(range(0x104, 0x134)) + [0x14D, 0x14E, 0x14F]:
        a.rom[r] = base[r]
        a.written[r] = max(a.written[r], 1)
    over = [i for i, w in enumerate(a.written) if w > 1]
    missing = [i for i, w in enumerate(a.written) if w == 0]
    diff = [i for i in range(len(base)) if a.rom[i] != base[i]]
    print("files: %d, statements: %d, labels: %d" % (len(files), len(items), len(a.banks)))
    print("overlapping bytes: %d, unwritten bytes: %d, differing bytes: %d" % (len(over), len(missing), len(diff)))
    for i in diff[:10]:
        print("  diff at $%06x: built %02x, base %02x" % (i, a.rom[i], base[i]))
    sys.exit(1 if (over or missing or diff) else 0)


if __name__ == "__main__":
    main()
