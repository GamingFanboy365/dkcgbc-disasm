"""Recursive-descent code tracer for the DKC GBC ROM."""
import sys
from sm83 import OPS, CB

BANK_SIZE = 0x4000

A_PRESERVING = {0xEA, 0xE0, 0xE2, 0x02, 0x12, 0x22, 0x32, 0x77, 0x47, 0x4F, 0x57, 0x5F,
                0x67, 0x6F, 0x01, 0x11, 0x21, 0x31, 0xC5, 0xD5, 0xE5, 0xF5, 0x06, 0x0E,
                0x16, 0x1E, 0x26, 0x2E, 0x36, 0x00}


def off(bank, addr):
    if addr < 0x4000:
        return addr
    return bank * BANK_SIZE + (addr - 0x4000)


class Insn:
    __slots__ = ("bank", "addr", "op", "length", "flow", "imm", "target", "text", "raw", "ctx", "farcall", "dataref")


def decode(rom, bank, addr):
    o = off(bank, addr)
    op = rom[o]
    ent = OPS[op]
    if ent is None:
        return None
    tmpl, length, flow = ent
    if (addr & 0x3FFF) + length > 0x4000:
        return None
    i = Insn()
    i.bank, i.addr, i.op, i.length, i.flow = bank, addr, op, length, flow
    i.raw = rom[o:o + length]
    i.imm = None
    i.target = None
    i.farcall = None
    i.dataref = None
    if op == 0xC7:
        # rst $00 = far call with inline arguments: dw address, db bank
        if (addr & 0x3FFF) + 4 > 0x4000:
            return None
        i.length = 4
        i.raw = rom[o:o + 4]
        i.farcall = (rom[o + 3], rom[o + 1] | rom[o + 2] << 8)
        i.flow = "farcall"
        i.text = "rst $00"
        return i
    if op == 0xCB:
        i.text = CB[rom[o + 1]]
        return i
    if op == 0x10 and rom[o + 1] != 0:
        return None
    if "{n16}" in tmpl:
        i.imm = rom[o + 1] | rom[o + 2] << 8
        if flow in ("jp", "jpc", "call", "callc"):
            i.target = i.imm
    elif "{e8}" in tmpl:
        d = rom[o + 1]
        if d >= 0x80:
            d -= 0x100
        i.target = (addr + 2 + d) & 0xFFFF
        i.imm = i.target
    elif "{n8}" in tmpl or "{a8}" in tmpl or "{s8}" in tmpl:
        i.imm = rom[o + 1]
    if flow == "rst":
        i.target = op & 0x38
    i.text = tmpl
    return i

REG8 = ("a", "b", "c", "d", "e", "h", "l")
PAIRS = {"bc": "bc", "de": "de", "hl": "hl", "af": "a", "sp": ""}


def _regs_of(x):
    x = x.strip()
    if x in REG8:
        return x
    if x in PAIRS:
        return PAIRS[x]
    return ""


def apply_regs(i, regs):
    """Very small constant propagation over a,b,c,d,e,h,l. Mutates regs."""
    t = i.text
    op = i.op
    if op == 0xCB:
        m, _, rest = t.partition(" ")
        if m != "bit":
            r = rest.split(",")[-1].strip()
            for c in _regs_of(r):
                regs[c] = None
        return
    if op == 0xAF:
        regs["a"] = 0
        return
    if i.flow in ("call", "callc", "rst"):
        for c in REG8:
            regs[c] = None
        return
    m, _, rest = t.partition(" ")
    if m in ("ld", "ldh"):
        dst, _, src = rest.partition(",")
        dst = dst.strip()
        src = src.strip()
        d = _regs_of(dst) if not dst.startswith("[") else ""
        if not d:
            return
        if src == "{n8}" and len(d) == 1:
            regs[d] = i.imm
        elif src == "{n16}" and len(d) == 2:
            regs[d[0]] = i.imm >> 8
            regs[d[1]] = i.imm & 0xFF
        elif src in REG8 and len(d) == 1:
            regs[d] = regs[src]
        else:
            for c in d:
                regs[c] = None
        return
    if m in ("inc", "dec", "pop"):
        for c in _regs_of(rest):
            regs[c] = None
        return
    if m in ("add", "adc", "sub", "sbc", "and", "xor", "or"):
        d = rest.split(",")[0].strip() if "," in rest else "a"
        for c in _regs_of(d):
            regs[c] = None
        return
    if m in ("rlca", "rrca", "rla", "rra", "daa", "cpl"):
        regs["a"] = None


OBJ_HANDLER, OBJ_TOUCH_HANDLER, OBJ_FRAME, OBJ_ANIM = 0x02, 0x04, 0x20, 0x22

# Animation commands (word >> 8 & $7f): number of extra bytes after the word
ANIM_EXTRA = {0: 2, 2: 2, 5: 2}
ANIM_NCMDS = 11

_HL_WRITERS = {0x21, 0x26, 0x2E, 0x24, 0x25, 0x2C, 0x2D, 0x23, 0x2B, 0x09, 0x19, 0x29,
               0x39, 0xE1, 0xF8, 0x22, 0x2A, 0x32, 0x3A}


def writes_hl(i):
    if i.op in _HL_WRITERS or 0x60 <= i.op <= 0x6F:
        return True
    if i.op == 0xCB:
        cb = i.raw[1]
        return (cb & 7) in (4, 5) and not (0x40 <= cb < 0x80)
    return i.flow in ("call", "callc", "rst", "farcall")


class Tracer:
    """Follows control flow from entry points, tracking the active ROMX bank."""

    def __init__(self, rom):
        self.rom = rom
        self.nbanks = len(rom) // BANK_SIZE
        self.insns = {}          # file offset -> Insn
        self.owner = {}          # file offset of every code byte -> insn start offset
        self.labels = {}         # file offset -> kind ('func', 'jump', 'data')
        self.queue = []
        self.unresolved = []     # (bank, addr, why) ROMX references with unknown bank
        self.jphl = []           # insn offsets of "jp hl"
        self.conflicts = []
        self.farcall_hl_a = set()
        self.speculated = []
        self.obj_init_funcs = set()
        self.list_only_banks = set()
        self.data = {}           # file offset -> (kind, bank, entries, length)
        self.data_labels = {}    # file offset -> label prefix ("ObjInit", "Anim", ...)
        self.anim_entries = set()  # file offsets of every parsed animation entry
        self.lohi = []           # (lo insn off, hi insn off, bank, target) pointer stores
        self.second_program = set()
        self.frame_headers = set()
        self.de_frame_refs = []      # "ld de, n" later stored into OBJ_FRAME
        self.de_loads = []           # every "ld de, n" with n in $4000-$7FFF
        self.preload_funcs = set()
        self.flow_funcs = set()
        self.farjump_stack = set()
        self.farjump_hl_stack = set()
        self.field_stores = {}   # insn offset -> (object field, value, is player)
        self.palette_bank = 0x80
        self.candidates = []
        self.fell_into_old = False

    def add(self, bank, addr, kind="func", ctx=None):
        if addr >= 0x8000:
            return
        if addr < 0x4000:
            bank = 0
        elif bank is None or bank == 0:
            self.unresolved.append((ctx, addr, kind))
            return
        if bank >= self.nbanks:
            return
        o = off(bank, addr)
        prev = self.labels.get(o)
        if prev != "func":
            self.labels[o] = kind
        self.queue.append((bank, addr, ctx))

    def run(self):
        while self.queue:
            bank, addr, ctx = self.queue.pop()
            self.trace(bank, addr, ctx)

    def trace(self, bank, addr, ctx):
        # ctx: the ROMX bank assumed mapped while executing (for bank-0 code)
        if bank != 0:
            ctx = bank
        regs = dict.fromkeys(REG8)
        first = True
        hist = []
        hl_insn = None
        de_insn = None
        pushbytes = []
        pushwords = []
        objfield = None
        player = False
        prev = None
        while True:
            o = off(bank, addr)
            if o in self.insns:
                if not first and hasattr(self.insns, "maps") and o not in self.insns.maps[0]:
                    self.fell_into_old = True
                return
            first = False
            if o in self.owner:
                self.conflicts.append((bank, addr, "mid"))
                return
            i = decode(self.rom, bank, addr)
            if i is None:
                self.conflicts.append((bank, addr, "bad"))
                return
            for k in range(1, i.length):
                if o + k in self.owner or o + k in self.insns:
                    self.conflicts.append((bank, addr, "overlap"))
                    return
            self.insns[o] = i
            for k in range(i.length):
                self.owner[o + k] = o
            i.ctx = ctx
            if i.op == 0xEA and 0x2000 <= i.imm < 0x3000 and bank == 0:
                ctx = regs["a"]
            if i.flow in ("call", "jp") and bank == 0 or i.flow in ("call", "jp") and i.target < 0x4000:
                if i.target in self.farcall_hl_a:
                    h, l, a = regs["h"], regs["l"], regs["a"]
                    if None not in (h, l, a):
                        self.add(a, h << 8 | l, "func", a)
                    else:
                        self.unresolved.append((None, 0, "farcall@%02x:%04x" % (bank, addr)))
            # "ld a, n / push af / inc sp" pushes single bytes; the far jump at
            # $3fdc switches to bank a and returns into the last two pushed
            if i.op == 0x33 and prev is not None and prev.op == 0xF5:
                pushbytes.append(regs["a"])
            # "ld hl, target / push hl / ld a, bank / jp $cb99" (bank $50
            # program): the last pushed word is the target; pushed words in
            # this bank's ROM area are return points
            if i.op == 0xE5:
                pushwords.append(None if None in (regs["h"], regs["l"]) else regs["h"] << 8 | regs["l"])
            if i.flow in ("jp", "call") and i.target in self.farjump_hl_stack and pushwords:
                a = regs["a"]
                if a is not None and pushwords[-1] is not None:
                    self.add(a, pushwords[-1], "func", a)
                    for w in pushwords[:-1]:
                        if w is not None and 0x4000 <= w < 0x8000 and bank:
                            self.candidates.append((bank, w))
                else:
                    self.unresolved.append((bank, addr, "farjump-hl"))
                pushwords = []
            if i.flow in ("jp", "call") and i.target in self.farjump_stack and len(pushbytes) >= 2:
                hi, lo, a = pushbytes[-2], pushbytes[-1], regs["a"]
                if None not in (hi, lo, a):
                    self.add(a, hi << 8 | lo, "func", a)
                else:
                    self.unresolved.append((bank, addr, "farjump-stack"))
            if i.flow in ("call", "jp") and i.target in self.flow_funcs and de_insn is not None:
                if off(0x0D, de_insn.imm) in self.data:
                    de_insn.dataref = (0x0D, de_insn.imm)
                elif off(0x0D, de_insn.imm) in self.data_labels:
                    de_insn.dataref = (0x0D, de_insn.imm)
            if i.flow in ("call", "jp") and i.target in self.preload_funcs:
                h, l = regs["h"], regs["l"]
                if None not in (h, l) and 0x4000 <= (h << 8 | l) < 0x8000:
                    self.preload_ref(h << 8 | l, hl_insn)
            if i.flow in ("call", "jp") and i.target in self.obj_init_funcs:
                h, l = regs["h"], regs["l"]
                if None not in (h, l):
                    ptr = h << 8 | l
                    lb = 0 if ptr < 0x4000 else (bank or ctx)
                    if lb is not None and ptr < 0x8000:
                        self.parse_obj_list(lb, ptr, bank or ctx, hl_insn)
                else:
                    self.unresolved.append((bank, addr, "objinit-hl"))
            apply_regs(i, regs)
            if i.op == 0x11:
                de_insn = i
            elif de_insn is not None and (regs["d"], regs["e"]) != (de_insn.imm >> 8, de_insn.imm & 0xFF):
                de_insn = None
            # "ld de, frame / ld hl, wObjects + OBJ_FRAME / add hl, bc / ld [hl], e..."
            if i.op == 0x21 and i.imm == 0xC800 + OBJ_FRAME and de_insn is not None:
                self.de_frame_refs.append(de_insn)
            # (a frame loaded into de on a branch that joins later is caught
            # by the "ld de, frame" scan below)
            if i.op == 0x11 and i.imm is not None and 0x4000 <= i.imm < 0x8000:
                self.de_loads.append(i)
            if i.op == 0x21:
                hl_insn = i
            elif hl_insn is not None and (regs["h"], regs["l"]) != (hl_insn.imm >> 8, hl_insn.imm & 0xFF):
                hl_insn = None
            # "ld [hl], LOW / inc l / ld [hl], HIGH" stores a pointer (often an
            # object handler); remember it as a candidate for speculation.
            hist = (hist + [(o, i, objfield)])[-3:]
            if len(hist) == 3 and hist[0][1].op == 0x36 and hist[1][1].op in (0x2C, 0x23) and hist[2][1].op == 0x36:
                ptr = hist[0][1].imm | hist[2][1].imm << 8
                fld = hist[0][2]
                if fld in (OBJ_ANIM, OBJ_FRAME):
                    tb = self.anim_bank if fld == OBJ_ANIM else self.frame_bank
                    if 0x4000 <= ptr < 0x8000:
                        (self.anim_ref if fld == OBJ_ANIM else self.frame_ref)(ptr)
                        self.lohi.append((hist[0][0], hist[2][0], tb, ptr))
                elif fld is None or fld in (OBJ_HANDLER, OBJ_TOUCH_HANDLER):
                    if ptr < 0x4000 or (bank and ptr < 0x8000):
                        tb = bank if ptr >= 0x4000 else 0
                        if fld == OBJ_HANDLER and tb and not getattr(self, "speculating", False):
                            self.add(tb, ptr, "func", tb)  # a new handler: always code
                        else:
                            self.candidates.append((tb, ptr))
                        if fld is not None:
                            self.lohi.append((hist[0][0], hist[2][0], tb, ptr))
            # byte stores into object fields, e.g. OBJ_PALETTE (used by
            # tools/frame_palettes.py)
            if i.op == 0x36 and objfield is not None:
                self.field_stores[o] = (objfield, i.imm, player)
            # which object field (if any) hl points at: "ld hl, wObjects + F"
            # then "add hl, bc" (any object) or no add (the player, slot 0)
            if i.op == 0x21 and 0xC800 <= i.imm < 0xC840 and bank not in self.second_program:
                objfield = i.imm - 0xC800
                player = True
            elif i.op in (0x09, 0x19) and objfield is not None and prev is not None and prev.op == 0x21:
                player = False
            elif objfield is not None and i.op in (0x2C, 0x23, 0x22, 0x2A):
                objfield += 1
            elif objfield is not None and i.op in (0x2D, 0x2B, 0x32, 0x3A):
                objfield -= 1
            elif writes_hl(i):
                objfield = None
            prev = i
            f = i.flow
            if f in ("jp", "jpc", "jr", "jrc"):
                t = i.target
                self.add(bank if t >= 0x4000 else 0, t, "jump", ctx)
                if f in ("jp", "jr"):
                    return
            elif f in ("call", "callc"):
                t = i.target
                self.add(bank if (t >= 0x4000 and bank != 0) else (ctx if t >= 0x4000 else 0), t, "func", ctx)
            elif f == "farcall":
                fb, fa = i.farcall
                self.add(fb if fa >= 0x4000 else 0, fa, "func", fb)
            elif f == "rst":
                self.add(0, i.target, "func", ctx)
                if self.on_rst(i, bank, addr, ctx):
                    return
            elif f == "ret":
                return
            elif f == "jphl":
                self.jphl.append(o)
                return
            addr += i.length
            if (addr & 0x3FFF) == 0:
                return

    def parse_obj_list(self, bank, addr, code_bank, src=None, inherited=None):
        """Parse an object initialiser list (see Func_00_188b) and queue its
        handler. Entries: $00-$3f field,byte / $40-$7f field,word /
        $80 include-pointer / $81+ end."""
        o = off(bank, addr)
        if o in self.data:
            if src is not None:
                src.dataref = (bank, addr)
            return
        rom = self.rom
        entries = []
        p = addr
        fields = dict(inherited or {})
        while True:
            if (p & 0x3FFF) + 3 > 0x4000 and rom[off(bank, p)] < 0x81:
                self.conflicts.append((bank, addr, "objlist-end"))
                return
            b = rom[off(bank, p)]
            if b < 0x40:
                v = rom[off(bank, p + 1)]
                entries.append(("byte", b, v))
                fields[b] = v
                p += 2
            elif b < 0x80:
                v = rom[off(bank, p + 1)] | rom[off(bank, p + 2)] << 8
                entries.append(("word", b & 0x3F, v))
                fields[b & 0x3F] = v & 0xFF
                fields[(b & 0x3F) + 1] = v >> 8
                p += 3
            elif b == 0x80:
                v = rom[off(bank, p + 1)] | rom[off(bank, p + 2)] << 8
                entries.append(("include", v))
                p += 3
            else:
                entries.append(("end", b))
                p += 1
                break
        length = p - addr
        for k in range(length):
            if o + k in self.owner:
                self.conflicts.append((bank, addr, "objlist-overlap"))
                return
        self.data[o] = ("objinit", bank, entries, length)
        self.data_labels[o] = "ObjInit"
        for k in range(length):
            self.owner[o + k] = -1
        if src is not None:
            src.dataref = (bank, addr)
        for e in entries:
            if e[0] == "include" and e[1] < 0x8000:
                ib = 0 if e[1] < 0x4000 else bank
                if ib or e[1] < 0x4000:
                    self.parse_obj_list(ib, e[1], code_bank, None, fields)
        for e in entries:
            if e[0] == "word" and e[1] == OBJ_ANIM:
                self.anim_ref(e[2])
            elif e[0] == "word" and e[1] == OBJ_FRAME:
                self.frame_ref(e[2])
        if 2 in fields and 3 in fields:
            handler = fields[2] | fields[3] << 8
            hb = fields.get(1)
            if handler < 0x4000:
                self.add(0, handler, "func", hb)
            elif handler < 0x8000:
                if hb is None and bank not in self.list_only_banks:
                    hb = bank or code_bank
                if hb is not None:
                    self.add(hb, handler, "func", hb)

    # ------------------------------------------------------------ animations
    anim_bank = 0x04
    frame_bank = 0x20

    def parse_anim(self, bank, start, end=None):
        """Parse animation script entries from start: up to end, or (without
        end) up to and including the first jump. See Func_00_127d."""
        rom = self.rom
        entries = []
        a = start
        o0 = off(bank, start)
        self.data_labels.setdefault(o0, "Anim")
        while True:
            if end is not None and a >= end:
                break
            if (a & 0x3FFF) + 2 > 0x4000:
                self.conflicts.append((bank, a, "anim-end"))
                return
            o = off(bank, a)
            if end is None and o in self.anim_entries:
                break  # runs into a script we already have
            e, d = rom[o], rom[o + 1]
            if not d & 0x80:
                entries.append((a, "frame", e | d << 8))
                self.frame_ref(e | d << 8)
                a += 2
                continue
            c = d & 0x7F
            n = ANIM_EXTRA.get(c, 0)
            w = rom[o + 2] | rom[o + 3] << 8 if n else None
            entries.append((a, "cmd", c, e, w))
            a += 2 + n
            if c == 0:
                if end is None:
                    break
                self.data_labels.setdefault(off(bank, a), "Anim")
        length = a - start
        for k in range(length):
            if o0 + k in self.owner:
                self.conflicts.append((bank, start, "anim-overlap"))
                return
        self.data[o0] = ("anim", bank, entries, length)
        for k in range(length):
            self.owner[o0 + k] = -1
        for ent in entries:
            self.anim_entries.add(off(bank, ent[0]))
        for ent in entries:
            if ent[1] != "cmd":
                continue
            c, w = ent[2], ent[4]
            if c == 0:
                self.anim_ref(w)
            elif c == 2 and w < 0x8000:
                self.add(bank if w >= 0x4000 else 0, w, "func", bank)

    def anim_ref(self, ptr):
        if not 0x4000 <= ptr < 0x8000:
            return
        o = off(self.anim_bank, ptr)
        if o in self.anim_entries:
            self.data_labels.setdefault(o, "Anim")
        elif o in self.owner:
            self.conflicts.append((self.anim_bank, ptr, "anim-ref-mid"))
        else:
            self.parse_anim(self.anim_bank, ptr)

    def frame_ref(self, ptr):
        o = off(self.frame_bank, ptr)
        if o not in self.frame_headers:
            self.conflicts.append((self.frame_bank, ptr, "frame-ref"))

    def parse_frame_table(self, bank, start, count):
        """Frame headers (see Func_00_1037): dw tiles, dw sprite offsets,
        db tile count, db bank of both. Header 0 is an empty frame."""
        rom = self.rom
        entries = []
        for k in range(count):
            a = start + 6 * k
            o = off(bank, a)
            h = rom[o:o + 6]
            tiles, spr, n, gb = h[0] | h[1] << 8, h[2] | h[3] << 8, h[4], h[5]
            entries.append((a, tiles, spr, n, gb))
            self.frame_headers.add(o)
            self.data_labels[o] = "Frame"
            if n == 0:
                continue
            import gfx
            three = gfx.sprite_layouts(rom).get((gb, spr), 2) == 3
            for (addr, kind, length, prefix) in ((tiles, "tiles", n * 16, "FrameTiles"),
                                                 (spr, "sprites3" if three else "sprites", n * 3 // 2 if three else n,
                                                  "FrameSprites")):
                go = off(gb, addr)
                if go in self.data:
                    continue
                if any(go + j in self.owner for j in range(length)):
                    self.conflicts.append((gb, addr, "frame-" + kind))
                    continue
                payload = list(rom[go:go + length]) if kind.startswith("sprites") else None
                self.data[go] = (kind, gb, payload, length)
                self.data_labels[go] = prefix
                for j in range(length):
                    self.owner[go + j] = -1
        o0 = off(bank, start)
        self.data[o0] = ("frames", bank, entries, 6 * count)
        for j in range(6 * count):
            self.owner[o0 + j] = -1

    # -------------------------------------------------------------- palettes
    def _claim(self, bank, addr, length, kind, payload, label):
        o = off(bank, addr)
        if o in self.data:
            return True
        if any(o + j in self.owner for j in range(length)):
            self.conflicts.append((bank, addr, kind + "-overlap"))
            return False
        self.data[o] = (kind, bank, payload, length)
        if label:
            self.data_labels[o] = label
        for j in range(length):
            self.owner[o + j] = -1
        return True

    def parse_palettes(self, cfg):
        """Object palettes, BG palette sets and preload lists (bank $80).
        Labels starting with '=' are used verbatim by the emitter."""
        bank = cfg["bank"]
        a, n = cfg["obj_palettes"]
        for k in range(n):
            self._claim(bank, a + 8 * k, 8, "palette", 1, "=ObjPalette_%02X" % k)
        a, n = cfg["bg_palette_sets"]
        for k in range(n):
            self._claim(bank, a + 64 * k, 64, "palette", 8, "=BGPaletteSet_%02X" % k)
        a, end = cfg["preload_lists"]
        while a < end:
            self.preload_ref(a)
            a += 1 + self.rom[off(bank, a)]

    def preload_ref(self, ptr, src=None):
        bank = self.palette_bank
        o = off(bank, ptr)
        n = self.rom[o]
        if o not in self.data:
            self._claim(bank, ptr, 1 + n, "preload", list(self.rom[o + 1:o + 1 + n]), "ObjPalPreload")
        if src is not None and o in self.data:
            src.dataref = (bank, ptr)

    def parse_levels(self, cfg):
        """Level table -> entrance records (8 bytes) -> level descriptors
        (12 bytes). Only far enough to label what descriptors point at."""
        bank, start, count = cfg["table"]
        rom = self.rom
        # whole runs first, so records only warps reach are decoded too
        rs, re_ = cfg["entrances"]
        for a in range(rs, re_, 8):
            self._claim(bank, a, 8, "levelentrance", None, "LevelEntrance")
        ds, de = cfg["descriptors"]
        for a in range(ds, de, 12):
            if self._claim(bank, a, 12, "leveldesc", None, "LevelDesc"):
                d = a
                self.preload_ref(rom[off(bank, d + 3)] | rom[off(bank, d + 4)] << 8)
        rd = lambda a: rom[off(bank, a)] | rom[off(bank, a) + 1] << 8  # noqa: E731
        self._claim(bank, start, 4 * count, "leveltable", [(rd(start + 4 * k), rd(start + 4 * k + 2)) for k in range(count)], "=LevelTable")
        for k in range(count):
            for rec in (rd(start + 4 * k), rd(start + 4 * k + 2)):
                if not rec:
                    continue
                self._claim(bank, rec, 8, "levelentrance", None, "LevelEntrance")
                d = rd(rec)
                if off(bank, d) in self.data:
                    continue
                if self._claim(bank, d, 12, "leveldesc", None, "LevelDesc"):
                    self.preload_ref(rd(d + 3))

    def parse_frame_struct(self, bank, start, count, width, frame_cols):
        """count records of `width` words; the words in frame_cols are frame
        header pointers, the others plain values."""
        rom = self.rom
        recs = []
        for k in range(count):
            a = start + 2 * width * k
            recs.append([rom[off(bank, a + 2 * j)] | rom[off(bank, a + 2 * j) + 1] << 8 for j in range(width)])
        self._claim(bank, start, 2 * width * count, "framestruct", (recs, set(frame_cols)), "FrameTable")

    def scan_anim_tables(self, banks, minimum=3):
        """Find tables of animation script pointers in unclaimed bytes: runs
        of at least `minimum` words that are all labelled script starts."""
        rom = self.rom
        valid = set((o % BANK_SIZE) + 0x4000 for o, p in self.data_labels.items()
                    if p == "Anim" and o // BANK_SIZE == self.anim_bank)
        found = []
        for b in banks:
            base = b * BANK_SIZE
            for parity in (0, 1):
                run = []
                for a in range(parity, BANK_SIZE - 1, 2):
                    o = base + a
                    v = rom[o] | rom[o + 1] << 8
                    if o not in self.owner and o + 1 not in self.owner and v in valid:
                        run.append(v)
                        continue
                    if len(run) >= minimum and len(set(run)) > 1:
                        found.append((b, a - 2 * len(run), list(run)))
                    run = []
        for (b, a, run) in found:
            self._claim(b, a + (0x4000 if b else 0), 2 * len(run), "animptrs", run, "AnimTable")
        return found

    def scan_frame_tables(self, banks, minimum=4):
        """Find tables of frame header pointers in bytes nothing else claims:
        runs of at least `minimum` words that are all frame headers (not the
        empty one) and not all the same."""
        rom = self.rom
        valid = set((o % BANK_SIZE) + 0x4000 for o in self.frame_headers) - {0x4000}
        found = []
        for b in banks:
            base = b * BANK_SIZE
            for parity in (0, 1):
                run = []
                for a in range(parity, BANK_SIZE - 1, 2):
                    o = base + a
                    v = rom[o] | rom[o + 1] << 8
                    if o not in self.owner and o + 1 not in self.owner and v in valid:
                        run.append(v)
                        continue
                    if len(run) >= minimum and len(set(run)) > 1:
                        found.append((b, a - 2 * len(run), list(run)))
                    run = []
        for (b, a, run) in found:
            addr = a + (0x4000 if b else 0)
            if self._claim(b, addr, 2 * len(run), "frameptrs", run, "FrameTable"):
                pass
        return found

    def parse_obj_run(self, bank, start, end):
        """Parse consecutive object initialiser lists in [start, end)."""
        a = start
        while a < end:
            o = off(bank, a)
            self.parse_obj_list(bank, a, None)
            if o not in self.data:
                self.conflicts.append((bank, a, "objrun"))
                return
            a += self.data[o][3]

    def on_rst(self, i, bank, addr, ctx):
        """Hook for rst vectors with inline arguments. Returns True to stop."""
        return False


def _plausible_start(rom, o):
    b = rom[o]
    return b not in (0x00, 0xFF, 0x7F, 0x40, 0x49, 0x52, 0x5B, 0x64, 0x6D)


class Speculator:
    """Tries to trace unreached gaps as code, keeping only clean results."""

    BAD_OPS = {0x00, 0x10, 0x76, 0xFF, 0x40, 0x49, 0x52, 0x5B, 0x64, 0x6D, 0x7F, 0x08, 0xD9}

    def __init__(self, tracer):
        self.t = tracer

    def try_at(self, bank, addr):
        from collections import ChainMap
        t = self.t
        trial = Tracer(t.rom)
        trial.speculating = True  # handler pointers stay candidates in a trial
        trial.farcall_hl_a = t.farcall_hl_a
        trial.obj_init_funcs = t.obj_init_funcs
        trial.data = ChainMap({}, t.data)
        trial.data_labels = ChainMap({}, t.data_labels)
        trial.anim_entries = t.anim_entries
        trial.frame_headers = t.frame_headers
        trial.second_program = t.second_program
        trial.list_only_banks = t.list_only_banks
        trial.flow_funcs = t.flow_funcs
        trial.farjump_stack = t.farjump_stack
        trial.farjump_hl_stack = t.farjump_hl_stack
        trial.preload_funcs = t.preload_funcs
        trial.insns = ChainMap({}, t.insns)
        trial.owner = ChainMap({}, t.owner)
        trial.labels = ChainMap({}, t.labels)
        o0 = off(bank, addr)
        w = t.rom[o0:o0 + 8]
        if len(set(w)) > 1 and (len(set(w[0::2])) == 1 or len(set(w[1::2])) == 1):
            return False  # looks like a table of words
        first = decode(t.rom, bank, addr)
        if first is None or first.flow in ("jrc", "jpc", "retc", "jr", "jp"):
            return False
        trial.add(bank, addr, "func", bank)
        trial.run()
        new = trial.insns.maps[0]
        if trial.conflicts or not new or trial.fell_into_old:
            return False
        nops = 0
        for o, i in new.items():
            if o // BANK_SIZE != off(bank, addr) // BANK_SIZE:
                continue  # code in other banks was reached through a resolved far call
            legit_stop = i.op == 0x10 and o >= 2 and t.rom[o - 2] == 0xE0 and t.rom[o - 1] in (0x00, 0x4D)
            if i.op in self.BAD_OPS and not legit_stop and not (i.op == 0x00 and rom_prev_is_halt(t.rom, o)):
                return False
            if i.flow == "rst" and i.target != 0x38:
                return False
        if len(new) < 3:
            # short stubs are fine if they branch to code we already know
            def known(i):
                if i.flow not in ("call", "jp") or i.target >= 0x8000:
                    return False
                tb = bank if i.target >= 0x4000 else 0
                return off(tb, i.target) in t.insns
            if not any(known(i) for i in new.values()):
                return False
        t.insns.update(new)
        t.owner.update(trial.owner.maps[0])
        for o, k in trial.labels.maps[0].items():
            if t.labels.get(o) != "func":
                t.labels[o] = k
        t.data.update(trial.data.maps[0])
        t.data_labels.update(trial.data_labels.maps[0])
        t.lohi += trial.lohi
        t.de_frame_refs += trial.de_frame_refs
        t.de_loads += trial.de_loads
        t.field_stores.update(trial.field_stores)
        for (ib, ia), src in []:
            pass
        t.jphl += trial.jphl
        t.candidates += trial.candidates
        t.unresolved += trial.unresolved
        t.speculated.append((bank, addr))
        return True

    def gaps(self, bank):
        t = self.t
        base = bank * BANK_SIZE
        res, s = [], None
        for o in range(base, base + BANK_SIZE):
            c = o in t.owner
            if not c and s is None:
                s = o
            if c and s is not None:
                res.append((s, o))
                s = None
        if s is not None:
            res.append((s, base + BANK_SIZE))
        return res

    def run(self, banks):
        changed = True
        while changed:
            changed = False
            while self.t.candidates:
                b, a = self.t.candidates.pop()
                if off(b, a) not in self.t.owner and self.try_at(b, a):
                    changed = True
            for bank in banks:
                for s, e in self.gaps(bank):
                    if not _plausible_start(self.t.rom, s):
                        continue
                    addr = (s % BANK_SIZE) + (0x4000 if bank else 0)
                    if self.try_at(bank, addr):
                        changed = True


def rom_prev_is_halt(rom, o):
    return o > 0 and rom[o - 1] == 0x76
