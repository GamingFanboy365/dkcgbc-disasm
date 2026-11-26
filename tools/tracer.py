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
    __slots__ = ("bank", "addr", "op", "length", "flow", "imm", "target", "text", "raw", "ctx", "farcall")


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
            apply_regs(i, regs)
            # "ld [hl], LOW / inc l / ld [hl], HIGH" stores a pointer (often an
            # object handler); remember it as a candidate for speculation.
            hist = (hist + [i])[-3:]
            if len(hist) == 3 and hist[0].op == 0x36 and hist[1].op in (0x2C, 0x23) and hist[2].op == 0x36:
                ptr = hist[0].imm | hist[2].imm << 8
                if ptr < 0x4000 or (bank and ptr < 0x8000):
                    self.candidates.append((bank if ptr >= 0x4000 else 0, ptr))
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
        trial.farcall_hl_a = t.farcall_hl_a
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
            if i.op in self.BAD_OPS and not (i.op == 0x00 and rom_prev_is_halt(t.rom, o)):
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
