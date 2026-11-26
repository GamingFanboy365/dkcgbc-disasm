"""Music and sound effect streams (sound driver in bank 0, $2F5A-$3607).

Music: each of a song's four channels reads a byte stream. A byte >= $81 is a
note (index into NotePeriods after both transposes), $80 a rest; either is
followed by a length byte unless a fixed length is set (channel [$27]).
Bytes < $80 are commands, dispatched through the table at $3F0A.

Sound effects: a speed byte, then the three argument bytes of SFX command
$02, then commands (even bytes < $80, table at $3F00) and notes ($80 | index,
followed by a length unless the effect has a fixed length).

  python3 tools/music.py [baserom.gbc]   decodes everything and reports
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hints  # noqa: E402

BANK = 0x4000

# opcode: (macro, argument kinds). Kinds: b byte, w little-endian address,
# W big-endian address, r relative backward jump. Some macros cover several
# opcodes (see MULTI); their first argument selects the opcode.
MUSIC_CMDS = {
    0x00: ("mus_end", ""),
    0x01: ("mus_jump", "W"),
    0x02: ("mus_jump_back", "r"),
    0x03: ("mus_regs", "bbb"),          # NRx1, NRx2, NRx4 (bit 6: length enable)
    0x04: ("mus_call_times", "bw"),     # count, target; returns with a mus_ret*
    0x05: ("mus_ret", ""),
    0x06: ("mus_pan_left", ""),
    0x07: ("mus_pan_right", ""),
    0x08: ("mus_pan_center", ""),
    0x09: ("mus_sweep", "b"),           # NR10
    0x0A: ("mus_length", "b"),          # fixed note length: notes have no length byte
    0x0B: ("mus_length_off", ""),
    0x0C: ("mus_vibrato", "bbb"),       # delay, rate, depth
    0x0D: ("mus_vibrato_off", ""),
    0x0E: ("mus_pitch_slide", "bbbbb"),
    0x0F: ("mus_pitch_slide_0f", "bbbbb"),  # same handler as $0E
    0x10: ("mus_portamento", "bbb"),
    0x11: ("mus_tempo", "b"),
    0x12: ("mus_tempo_add", "b"),
    0x13: ("mus_transpose", "b"),       # semitones, channel transpose [$28]
    0x14: ("mus_transpose_add", "b"),
    0x15: ("mus_transpose_all", "b"),   # [$28] of all four channels
    0x16: ("mus_vibrato_ex", "bbbb"),
    0x26: ("mus_call", "w"),            # once
    0x2A: ("mus_regs2", "bb"),          # NRx1, NRx2
    0x32: ("mus_ret_length_off", ""),
    0x36: ("mus_echo", "b"),            # two volumes, alternating note by note
    0x37: ("mus_echo_off", ""),
    0x39: ("mus_ret_reset", ""),        # clears echo and fixed length, then returns
    0x3A: ("mus_loop2_end", ""),
    0x3B: ("mus_wave", "b"),            # wave pattern for channel 3
    0x3C: ("mus_echo_5a", ""),
    0x3D: ("mus_echo_48", ""),
    0x3E: ("mus_ret_pan_center", ""),
    0x3F: ("mus_envelope", "b"),        # NRx2
    0x40: ("mus_duty", "b"),            # NRx1
    0x43: ("mus_length_reset", ""),     # clears echo and fixed length
    0x44: ("mus_note_repeat", "bb"),    # note, count
    0x45: ("mus_key", "b"),             # second transpose [$5a]
    0x46: ("mus_loop", "b"),            # count; until mus_loop_end
    0x47: ("mus_loop_end", ""),
    0x48: ("mus_ret_transpose_off", ""),
    0x49: ("mus_sub", "w"),             # one level, returns with mus_sub_ret*
    0x4A: ("mus_sub_ret", ""),
    0x4B: ("mus_sub_ret_length_off", ""),
    0x4C: ("mus_sub_ret_reset", ""),
    0x4D: ("mus_sub_ret_pan_center", ""),
    0x4E: ("mus_sub_ret_transpose_off", ""),
    0x4F: ("mus_transpose_off", ""),
    0x50: ("mus_octave_up", ""),        # transpose +12
    0x51: ("mus_loop2", "b"),
}
# shorthand opcodes: macro -> {argument value: opcode}
MULTI = {
    "mus_call_x": ("w", {2: 0x31, 3: 0x27, 4: 0x28, 6: 0x29, 8: 0x2D, 16: 0x2F}),  # call n times
    "mus_length_x": ("", {1: 0x2C, 2: 0x2B, 4: 0x41, 6: 0x38, 8: 0x2E}),
    "mus_duty_envelope": ("b", {0: 0x33, 1: 0x34, 2: 0x35}),   # duty 12.5/25/50 %, NRx2
    "mus_volume": ("", {v: 0x16 + v for v in range(1, 16)}),   # volume 1-15
}
for name, (kinds, m) in MULTI.items():
    for v, op in m.items():
        MUSIC_CMDS[op] = (name, "=%d" % v + kinds)

SETS_LENGTH = {0x0A, 0x2B, 0x2C, 0x2E, 0x38, 0x41}
CLEARS_LENGTH = {0x0B, 0x43, 0x32, 0x39, 0x4B, 0x4C}
COUNTED_RETS = {0x05, 0x32, 0x39, 0x3E, 0x48}
SUB_RETS = {0x4A, 0x4B, 0x4C, 0x4D, 0x4E}
CALLS = {0x04, 0x26, 0x27, 0x28, 0x29, 0x2D, 0x2F, 0x31}

SFX_CMDS = {0x00: ("sfx_end", ""), 0x02: ("sfx_regs", "bbb"), 0x04: ("sfx_vibrato", "bbbb"),
            0x06: ("sfx_pitch_slide", "bbbbb"), 0x08: ("sfx_sweep", "b")}

NOTE_NAMES = ["C_", "Cs", "D_", "Ds", "E_", "F_", "Fs", "G_", "Gs", "A_", "As", "B_"]


def note_name(i):
    """NotePeriods index -> name, C_2 = index 1 (pitch on channels 1 and 2)."""
    if 1 <= i <= 62:
        return "%s%d" % (NOTE_NAMES[(i - 1) % 12], 2 + (i - 1) // 12)
    return None


def off(bank, addr):
    return addr if addr < 0x4000 else bank * BANK + addr - 0x4000


class Conflict(Exception):
    pass


class Decoder:
    """Walks streams, recording {(bank, addr): item}. An item is
    (length, kind, payload) with kind 'cmd', 'note', 'rest'."""

    def __init__(self, rom):
        self.rom = rom
        self.items = {}
        self.targets = set()   # (bank, addr) reached by a jump or call
        self.conflicts = []

    def put(self, key, item):
        old = self.items.get(key)
        if old is not None and old != item:
            self.conflicts.append((key, old, item))
        self.items[key] = item

    def music(self, bank, start):
        self.targets.add((bank, start))
        self._walk(bank, start, False, 0, set())

    def _walk(self, bank, pc, fixed, depth, seen):
        """Run a stream from pc until it ends, loops back or returns.
        Returns the fixed-length state at a return, or None."""
        rom = self.rom
        if depth > 8:
            return fixed
        while True:
            if (pc, fixed) in seen:
                return None
            seen.add((pc, fixed))
            o = off(bank, pc)
            op = rom[o]
            if op >= 0x80:
                n = 1 if fixed else 2
                self.put((bank, pc), (n, "rest" if op == 0x80 else "note", (op, None if fixed else rom[o + 1])))
                pc += n
                continue
            if op not in MUSIC_CMDS:
                self.put((bank, pc), (1, "bad", op))
                return None
            name, kinds = MUSIC_CMDS[op]
            ln = 1
            args = []
            for k in kinds:
                if k == "=" or k.isdigit():
                    continue
                if k == "b":
                    args.append(rom[o + ln]); ln += 1
                elif k == "w":
                    args.append(rom[o + ln] | rom[o + ln + 1] << 8); ln += 2
                elif k == "W":
                    args.append(rom[o + ln] << 8 | rom[o + ln + 1]); ln += 2
                elif k == "r":
                    args.append(pc + 1 + rom[o + ln] - 0x100); ln += 1
            if op == 0x44:
                ln += 0 if fixed else 1  # the first repetition's length
            self.put((bank, pc), (ln, "cmd", (op, tuple(args))))
            nxt = pc + ln
            if op == 0x00:
                return None
            if op in (0x01, 0x02):
                tgt = args[-1]
                self.targets.add((bank, tgt))
                pc = tgt
                continue
            if op in CALLS or op == 0x49:
                tgt = args[-1]
                self.targets.add((bank, tgt))
                r = self._walk(bank, tgt, fixed, depth + 1, set())
                fixed = fixed if r is None else r
                pc = nxt
                continue
            if op in COUNTED_RETS or op in SUB_RETS:
                return False if op in CLEARS_LENGTH else fixed
            if op in SETS_LENGTH:
                fixed = True
            elif op in CLEARS_LENGTH:
                fixed = False
            pc = nxt

    def sfx(self, bank, start):
        rom = self.rom
        o = off(bank, start)
        fixed = rom[o + 3] & 0x3F
        self.put((bank, start), (4, "sfxhead", tuple(rom[o:o + 4])))
        pc = start + 4
        while True:
            o = off(bank, pc)
            op = rom[o]
            if op >= 0x80:
                n = 1 if fixed else 2
                self.put((bank, pc), (n, "sfxnote", (op, None if fixed else rom[o + 1])))
                pc += n
                continue
            if op not in SFX_CMDS:
                self.put((bank, pc), (1, "bad", op))
                return
            name, kinds = SFX_CMDS[op]
            ln = 1 + len(kinds)
            self.put((bank, pc), (ln, "sfxcmd", (op, tuple(rom[o + 1:o + ln]))))
            if op == 0x00:
                return
            if op == 0x02:
                fixed = rom[o + 3] & 0x3F
            pc += ln


def decode_all(rom):
    c = hints.SOUND
    d = Decoder(rom)
    n = c["songs"]
    for s in range(n):
        b = rom[c["song_banks"] + s]
        for p in struct.unpack("<4H", rom[c["song_table"] + 8 * s:c["song_table"] + 8 * s + 8]):
            d.music(b if p >= 0x4000 else 0, p)
    sb, st = c["sfx_table"]
    a = st
    while True:
        p = rom[off(sb, a)] | rom[off(sb, a) + 1] << 8
        if not st <= p < 0x8000:
            break
        d.sfx(sb, p)
        a += 2
    d.reached = set(d.items)
    decode_unreached(d, rom)
    return d


def stream_areas(rom):
    import banks as bk
    s = bk.sound(rom)
    return sorted([(b, a, ln) for (b, a), ln in s["stream_lengths"].items()])


def holes(d, rom):
    cov = set()
    for (b, a), (ln, _, _) in d.items.items():
        cov.update(off(b, a) + i for i in range(ln))
    out = []
    for b, a, ln in stream_areas(rom):
        i = 0
        while i < ln:
            if off(b, a) + i in cov:
                i += 1
                continue
            j = i
            while j < ln and off(b, a) + j not in cov:
                j += 1
            out.append((b, a + i, j - i, a + ln))
            i = j
    return out


def decode_unreached(d, rom):
    """Music bytes no song reaches: decode them from each gap's start the
    same way (fixed length off, else on), keeping whichever needs no
    conflicting reading of reached bytes."""
    for _ in range(50):
        hs = holes(d, rom)
        if not hs:
            return
        progress = False
        for b, a, ln, end in hs:
            for fixed in (False, True):
                trial = Decoder(rom)
                trial.items = dict(d.items)
                trial._walk(b, a, fixed, 0, set())
                new = {k: v for k, v in trial.items.items() if k not in d.items}
                bad = any(v[1] == "bad" for v in new.values()) or trial.conflicts
                if not bad and new and all(k[1] + v[0] <= end or k in d.items for k, v in new.items()):
                    d.items.update(new)
                    d.targets.update(trial.targets)
                    progress = True
                    break
        if not progress:
            return


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    d = decode_all(rom)
    print("items:", len(d.items), "conflicts:", len(d.conflicts))
    for cf in d.conflicts[:10]:
        print("  conflict", cf)
    bad = [k for k, v in d.items.items() if v[1] == "bad"]
    print("bad opcodes:", [("%02x:%04x" % k, d.items[k][2]) for k in sorted(bad)][:20])
    hs = holes(d, rom)
    print("undecoded gaps:", [("%02x:%04x" % (b, a), n) for b, a, n, _ in hs])
    un = sorted(k for k in d.items if k not in d.reached)
    print("unreached items:", len(un), "bytes:", sum(d.items[k][0] for k in un))
    from collections import Counter
    ops = Counter(v[2][0] for v in d.items.values() if v[1] == "cmd")
    print("opcodes used:", " ".join("%02x:%d" % kv for kv in sorted(ops.items())))
    print("unused opcodes:", " ".join("%02x" % k for k in sorted(MUSIC_CMDS) if k not in ops))


if __name__ == "__main__":
    main()


# ------------------------------------------------------------ macros
def macro_table():
    """{macro: [(opcode or None, kinds, selector value)]} for music and SFX."""
    t = {}
    for op, (name, kinds) in MUSIC_CMDS.items():
        sel = None
        if kinds.startswith("="):
            sel = int(kinds[1:].rstrip("bwWr"))
            kinds = kinds[1 + len(str(sel)):]
        t.setdefault(name, []).append((op, kinds, sel))
    for op, (name, kinds) in SFX_CMDS.items():
        t.setdefault(name, []).append((op, kinds, None))
    return t


NOTE_MACROS = ("mus_note", "mus_rest", "sfx_note", "sfx_rest", "sfx_header")


def macro_size(name, nargs):
    if name in ("mus_note", "sfx_note"):
        return nargs
    if name in ("mus_rest", "sfx_rest"):
        return 1 + nargs
    if name == "sfx_header":
        return 4
    ent = macro_table()[name][0]
    return 1 + sum({"b": 1, "w": 2, "W": 2, "r": 1}[k] for k in ent[1])


def macro_encode(name, args, pc):
    """Bytes of a music/SFX macro with evaluated arguments, at address pc."""
    if name in ("mus_note", "sfx_note"):
        return bytes([0x80 | args[0]] + list(args[1:]))
    if name in ("mus_rest", "sfx_rest"):
        return bytes([0x80] + list(args))
    if name == "sfx_header":
        return bytes(args)
    ents = macro_table()[name]
    if ents[0][2] is None:
        op, kinds, _ = ents[0]
    else:
        op, kinds, _ = next(e for e in ents if e[2] == args[0])
        args = args[1:]
    out = [op]
    for k, v in zip(kinds, args):
        if k == "b":
            out.append(v & 0xFF)
        elif k == "w":
            out += [v & 0xFF, v >> 8 & 0xFF]
        elif k == "W":
            out += [v >> 8 & 0xFF, v & 0xFF]
        elif k == "r":
            out.append((v - pc + 0xFF) & 0xFF)
    return bytes(out)


def write_include(path):
    """include/music.inc: note names and the stream macros (generated)."""
    L = ["; Generated by tools/music.py: note names and music/SFX stream macros.",
         "; Note n is NotePeriods entry n; C_2 (1) is 65.4 Hz on channels 1 and 2.",
         "; Channel 3 sounds an octave lower, and channel 4 uses the entry as noise",
         "; parameters.", "IF !DEF(MUSIC_INC)", "DEF MUSIC_INC EQU 1", ""]
    for i in range(1, 63):
        L.append("DEF %-4s EQU %d" % (note_name(i), i))
    L += ["", "; a note or rest takes a length byte unless a fixed length is set",
          "MACRO mus_note", "\tdb $80 | (\\1)", "\tIF _NARG > 1", "\t\tdb \\2", "\tENDC", "ENDM", "",
          "MACRO mus_rest", "\tdb $80", "\tIF _NARG > 0", "\t\tdb \\1", "\tENDC", "ENDM", "",
          "MACRO sfx_note", "\tdb $80 | (\\1)", "\tIF _NARG > 1", "\t\tdb \\2", "\tENDC", "ENDM", "",
          "MACRO sfx_rest", "\tdb $80", "\tIF _NARG > 0", "\t\tdb \\1", "\tENDC", "ENDM", "",
          "; speed, NRx1, NRx2, flags (bit 6: length enable, bits 0-5: fixed note length)",
          "MACRO sfx_header", "\tdb \\1, \\2, \\3, \\4", "ENDM", ""]
    for name, ents in sorted(macro_table().items()):
        L.append("MACRO %s" % name)
        first = 1
        if ents[0][2] is None:
            op, kinds, _ = ents[0]
            L.append("\tdb $%02x" % op)
        else:
            kinds = ents[0][1]
            for j, (op, _, sel) in enumerate(sorted(ents, key=lambda e: e[2])):
                L.append("\t%s \\1 == %d" % ("IF" if j == 0 else "ELIF", sel))
                L.append("\t\tdb $%02x" % op)
            L.append("\tELSE")
            L.append('\t\tFAIL "%s: no opcode for \\1"' % name)
            L.append("\tENDC")
            first = 2
        for j, k in enumerate(kinds):
            a = "\\%d" % (first + j)
            if k == "b":
                L.append("\tdb %s" % a)
            elif k == "w":
                L.append("\tdw %s" % a)
            elif k == "W":
                L.append("\tdb HIGH(%s), LOW(%s)" % (a, a))
            elif k == "r":
                L.append("\tdb (%s) - @ + $100  ; @ is this byte, one past the opcode" % a)
        L.append("ENDM")
        L.append("")
    L.append("ENDC")
    open(path, "w").write("\n".join(L) + "\n")
