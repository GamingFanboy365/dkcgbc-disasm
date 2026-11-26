"""Readers for the data banks found late: sound, camera regions, level object
lists, text and digitized samples. Each returns plain Python structures;
run_trace.parse_banks() turns them into claims.

  python3 tools/banks.py [baserom.gbc]   prints a summary
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hints  # noqa: E402

BANK = 0x4000


def off(bank, addr):
    return addr if addr < 0x4000 else bank * BANK + addr - 0x4000


def rw(rom, bank, addr):
    o = off(bank, addr)
    return rom[o] | rom[o + 1] << 8


def used_end(rom, bank):
    """Address just past the bank's data (trailing $00/$FF padding removed)."""
    d = rom[bank * BANK:(bank + 1) * BANK]
    return 0x4000 + len(d.rstrip(b"\xff").rstrip(b"\x00"))


def spans(starts, end):
    """[(start, length)] for sorted unique starts, each running to the next."""
    s = sorted(set(starts))
    return [(a, (s[i + 1] if i + 1 < len(s) else end) - a) for i, a in enumerate(s)]


# ------------------------------------------------------------------ sound
def sound(rom):
    """Song tables in bank 0 (PlaySong, $30F1), the song channel streams in
    banks $01/$02 and the sound effects in bank $02 (Func_00_2f5a)."""
    c = hints.SOUND
    n = c["songs"]
    banks = list(rom[c["song_banks"]:c["song_banks"] + n])
    songs = []
    for s in range(n):
        ptrs = struct.unpack("<4H", rom[c["song_table"] + 8 * s:c["song_table"] + 8 * s + 8])
        songs.append((banks[s], ptrs))
    streams = {}  # (bank, addr) -> name
    for s, (b, ptrs) in enumerate(songs):
        for ch, p in enumerate(ptrs):
            key = (b if p >= 0x4000 else 0, p)
            streams.setdefault(key, "Song%02X_Ch%d" % (s, ch + 1))
    sb, st = c["sfx_table"]
    sfx = []
    a = st
    while True:
        p = rw(rom, sb, a)
        if not (st <= p < 0x8000):
            break
        sfx.append(p)
        a += 2
    out = {"songs": songs, "streams": streams, "sfx_bank": sb, "sfx_table": st, "sfx": sfx}
    # stream extents per bank: each stream runs to the next stream, the SFX
    # table, or the end of the bank's data
    ext = {}
    for b in (1, 2):
        starts = [a for (bb, a) in streams if bb == b]
        end = st if b == sb else used_end(rom, b)
        for a, ln in spans(starts, end):
            ext[(b, a)] = ln
    out["stream_lengths"] = ext
    out["sfx_lengths"] = dict(spans(sfx, used_end(rom, sb)))
    return out


# ------------------------------------------------------- camera regions
def camera_regions(rom, map_headers):
    """Bank $06: lists of 16-byte boxes, one list per map header ($c45c).
    Each box is four edges (left, right, top, bottom) of 4 bytes: a flags
    byte, a byte and a 16-bit coordinate. When bit 1 of the flags is set the
    first two bytes are instead the address of another box (low nibble =
    flags) whose same edge is used (Func_00_21ad). Func_00_20dd picks the
    first box that contains the player; lists have no terminator."""
    b = hints.CAMERA_BANK
    starts = sorted(set(h["c45c"] for h in map_headers))
    return b, spans(starts, used_end(rom, b))


# ---------------------------------------------------------- level objects
def level_objects(rom, descriptors):
    """The object list of each level descriptor (Func_00_1715): 8-byte
    records (id, flags, x, y, pointer) ended by a 0 byte. Flags bits 4-5
    say what the pointer is: $00 a 16-byte block in bank $03, $10 a
    zero-terminated byte string in the list's own bank, $30 a value used
    directly."""
    lists = {}
    strings = set()
    for (b, a) in sorted(set(descriptors)):
        o = off(b, a)
        recs = []
        while rom[o]:
            r = rom[o:o + 8]
            x, y, p = struct.unpack("<3H", r[2:8])
            recs.append((r[0], r[1], x, y, p))
            if r[1] & 0x30 == 0x10:
                strings.add((b, p))
            o += 8
        lists[(b, a)] = recs
    strs = {}
    for (b, p) in strings:
        o = off(b, p)
        e = rom.index(0, o)
        strs[(b, p)] = rom[o:e + 1]
    return lists, strs


# ------------------------------------------------------------------- text
def text_bank(rom, b):
    """A text bank ($10-$14, one per language): 16 group pointers at $4000,
    each group a list of string pointers, strings ended by 0. $0D is a new
    line; letters past $7F are code page 437 (é = $82, ñ = $A4, ß = $E1)."""
    groups = [rw(rom, b, 0x4000 + 2 * k) for k in range(16)]
    order = sorted(set(groups))
    first_string = None
    lists = {}
    for i, g in enumerate(order):
        nxt = order[i + 1] if i + 1 < len(order) else None
        lst, a = [], g
        while (nxt is None or a < nxt) and (first_string is None or a < first_string):
            p = rw(rom, b, a)
            if not 0x4000 <= p < 0x8000:
                break
            lst.append(p)
            first_string = p if first_string is None else min(first_string, p)
            a += 2
        lists[g] = lst
    strings = {}
    for lst in lists.values():
        for p in lst:
            o = off(b, p)
            strings[p] = rom[o:rom.index(0, o) + 1]
    return groups, lists, strings


def unreferenced_strings(rom, b, strings):
    """Zero-terminated strings in the string area that no pointer reaches."""
    lo = min(strings)
    hi = used_end(rom, b)
    covered = set()
    for p, s in strings.items():
        covered.update(range(p, p + len(s)))
    out, a = {}, lo
    while a < hi:
        if a in covered:
            a += 1
            continue
        o = off(b, a)
        e = rom.index(0, o)
        out[a] = rom[o:e + 1]
        a += e + 1 - o
    return out


# ---------------------------------------------------------------- samples
def samples(rom):
    """Funky's Fishing's digitized sounds: a table of 4-byte entries (bank,
    address, length) at $52:41C2, read by its timer interrupt, which writes
    one byte per tick to NR50 (master volume; both nibbles hold the same
    3-bit level, 4 = silence)."""
    c = hints.SAMPLES
    b, a, n = c["bank"], c["table"], c["count"]
    ents = []
    for k in range(n):
        o = off(b, a + 4 * k)
        ents.append((rom[o], rom[o + 1] | rom[o + 2] << 8, rom[o + 3]))
    ext = {}
    for sb in sorted(set(e[0] for e in ents)):
        starts = [p for (bb, p, _) in ents if bb == sb]
        end = c.get("ends", {}).get(sb) or used_end(rom, sb)
        for p, ln in spans(starts, end):
            ext[(sb, p)] = ln
    return b, a, ents, ext


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    s = sound(rom)
    print("songs:", len(s["songs"]), "streams:", len(s["streams"]), "sfx:", len(s["sfx"]))
    for b in range(0x10, 0x15):
        g, lists, strs = text_bank(rom, b)
        print("text bank $%02x: %d strings, unreferenced %s" % (b, len(strs), unreferenced_strings(rom, b, strs)))
    print("samples:", samples(rom)[2])


if __name__ == "__main__":
    main()
