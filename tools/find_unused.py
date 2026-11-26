#!/usr/bin/env python3
"""Look for content the game never uses.

  python3 tools/find_unused.py [baserom.gbc] [outdir]

Writes outdir/README.md (the findings) plus images: frames/ (each unused
frame assembled from its sprites), anims/ (each unused animation's frames
in order) and palettes/ (swatches). outdir defaults to unused/ in the repo,
which is gitignored: the images are the game's graphics.

"Unused" means: nothing the tracer decodes refers to it. That covers
animation scripts, object initialiser lists, code that stores pointers into
objects, frame tables, level descriptors and preload lists. Before calling
something unused, the undecoded bytes of banks $00-$0f are also searched
for its address, and any hit is reported ("loose match"): such an item may
still be used through a table that isn't decoded yet.
"""
import os
import struct
import sys
import zlib
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx  # noqa: E402
from frame_palettes import FramePalettes  # noqa: E402
from tracer import BANK_SIZE, off  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_BANKS = range(0x00, 0x10)
GRAY = [(0xF8, 0xF8, 0xF8), (0xA8, 0xA8, 0xA8), (0x58, 0x58, 0x58), (0x10, 0x10, 0x10)]


def write_rgb_png(path, w, h, pixels):
    """pixels: rows of (r, g, b). 8-bit truecolor PNG."""
    raw = b"".join(b"\x00" + bytes(c for px in row for c in px) for row in pixels)

    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def gbc_rgb(v):
    return tuple(x << 3 | x >> 2 for x in (v & 31, v >> 5 & 31, v >> 10 & 31))


class Finder:
    def __init__(self, rom):
        self.rom = rom
        self.fp = FramePalettes(rom)
        self.t = self.fp.t
        self.frame_info = {a: (tiles, spr, n, gb) for (a, tiles, spr, n, gb) in gfx.frames(rom)}

    def loose_matches(self, value):
        """Places in undecoded bytes of SEARCH_BANKS holding the word value."""
        t, rom = self.t, self.rom
        pat = bytes([value & 0xFF, value >> 8])
        hits = []
        for b in SEARCH_BANKS:
            base = b * BANK_SIZE
            chunk = rom[base:base + BANK_SIZE]
            i = chunk.find(pat)
            while i >= 0:
                if base + i not in t.owner and base + i + 1 not in t.owner:
                    hits.append("%02x:%04x" % (b, i + (0x4000 if b else 0)))
                i = chunk.find(pat, i + 1)
        return hits

    # ------------------------------------------------------------ frames
    def used_frames(self):
        t, fb = self.t, self.t.frame_bank
        used = set()
        for o, (b, ent) in self.fp.anim_next.items():
            if ent[1] == "frame":
                used.add(ent[2])
        for (lo, hi, tb, target) in t.lohi:
            if tb == fb:
                used.add(target)
        for o, item in t.data.items():
            if item[0] == "objinit":
                for e in item[2]:
                    if e[0] == "word" and e[1] == 0x20:
                        used.add(e[2])
            elif item[0] == "frameptrs":
                used |= set(item[2])
            elif item[0] == "framestruct":
                recs, cols = item[2]
                used |= set(r[j] for r in recs for j in cols)
        return used

    def render_frame(self, a, pal=None):
        tiles, spr, n, gb = self.frame_info[a]
        rom = self.rom
        o = off(gb, tiles)
        _, strip = gfx.tiles_to_rows(rom[o:o + n * 16])
        so = off(gb, spr)
        x = y = 0
        pos = []
        for k in range(n // 2):
            dx, dy = rom[so + 2 * k], rom[so + 2 * k + 1]
            x += dx - 256 if dx >= 128 else dx
            y += dy - 256 if dy >= 128 else dy
            pos.append((x, y))
        x0, y0 = min(p[0] for p in pos), min(p[1] for p in pos)
        w = max(p[0] for p in pos) - x0 + 8
        h = max(p[1] for p in pos) - y0 + 16
        canvas = [[None] * w for _ in range(h)]
        for k, (px, py) in enumerate(pos):
            for r in range(16):
                for c in range(8):
                    v = strip[r][k * 8 + c]
                    if v:
                        canvas[py - y0 + r][px - x0 + c] = v
        colors = pal or GRAY
        return [[colors[v] if v else (0xFF, 0xFF, 0xFF) for v in row] for row in canvas]

    def frame_colors(self, a):
        pid, _ = self.fp.palette_of(a)
        if pid is None:
            return None, None
        return [GRAY[0]] + self.fp.colors(pid)[1:], pid

    # ------------------------------------------------------------- anims
    def anim_scripts(self):
        """(start addr, [frame addrs]) for every labelled script in bank $04."""
        t = self.t
        starts = sorted(o for o, p in t.data_labels.items() if p == "Anim")
        out = []
        for k, st in enumerate(starts):
            end = starts[k + 1] if k + 1 < len(starts) else None
            frames, o = [], st
            while o in self.fp.anim_next and (end is None or o < end):
                _, ent = self.fp.anim_next[o]
                if ent[1] == "frame":
                    frames.append(ent[2])
                    o += 2
                else:
                    o += 4 if ent[4] is not None else 2
            out.append(((st % BANK_SIZE) + 0x4000, frames))
        return out

    def referenced_anims(self):
        t = self.t
        refs = set()
        for o, (b, ent) in self.fp.anim_next.items():
            if ent[1] == "cmd" and ent[2] == 0:
                refs.add(ent[4])
        for (lo, hi, tb, target) in t.lohi:
            if tb == t.anim_bank:
                refs.add(target)
        for o, item in t.data.items():
            if item[0] == "animptrs":
                refs |= set(item[2])
        for o, item in t.data.items():
            if item[0] == "objinit":
                for e in item[2]:
                    if e[0] == "word" and e[1] == 0x22:
                        refs.add(e[2])
        return refs

    # ---------------------------------------------------------- palettes
    def used_palettes(self):
        t = self.t
        bg, obj = set(), defaultdict(set)
        for o, item in t.data.items():
            if item[0] == "leveldesc":
                r = self.rom[o:o + 12]
                bg.add(r[1] | r[2] << 8)
            elif item[0] == "preload":
                for p in item[2]:
                    obj[p].add("preload list")
            elif item[0] == "objinit":
                for e in item[2]:
                    if e[0] == "byte" and e[1] == 0x2A:
                        obj[e[2]].add("object list")
        for o, (f, v, pl) in t.field_stores.items():
            if f == 0x2A:
                obj[v].add("code")
        # "ld a, n" shortly before "ld hl, wObjects + OBJ_PALETTE ... ld [hl], a"
        order = sorted(t.insns)
        for k, o in enumerate(order):
            i = t.insns[o]
            if i.op != 0x21 or i.imm != 0xC82A:
                continue
            store = any(t.insns[order[j]].op == 0x77 for j in range(k + 1, min(k + 4, len(order))))
            if not store:
                continue
            for j in range(k - 1, max(k - 7, -1), -1):
                if t.insns[order[j]].op == 0x3E:
                    obj[t.insns[order[j]].imm].add("code")
        return bg, obj

    # ------------------------------------------------------------ report
    def run(self, outdir):
        t, rom = self.t, self.rom
        lines = ["# Unused content in Donkey Kong Country (GBC)", "",
                 "Generated by `tools/find_unused.py`. \"Unused\" means nothing the disassembly decodes so far refers to it. "
                 "That covers animation scripts, object lists, code storing pointers into objects, frame tables, level "
                 "descriptors and preload lists. A **loose match** is the item's address turning up in bytes of banks "
                 "$00-$0F that are not decoded yet. Those items might still be used through an undecoded table, so "
                 "they are the less certain finds.", ""]

        # frames
        used = self.used_frames()
        unused = [a for a in sorted(self.frame_info) if a != 0x4000 and a not in used]
        runs = []
        for a in unused:
            if runs and a == runs[-1][-1] + 6:
                runs[-1].append(a)
            else:
                runs.append([a])
        sure = loose = 0
        rows = []
        for r in runs:
            hits = sorted(set(h for a in r for h in self.loose_matches(a)))
            for a in r:
                pal, pid = self.frame_colors(a)
                img = self.render_frame(a, pal)
                tiles, spr, n, gb = self.frame_info[a]
                write_rgb_png(os.path.join(outdir, "frames", "%04x_%02x_%04x.png" % (a, gb, tiles)),
                              len(img[0]), len(img), img)
            if hits:
                loose += len(r)
            else:
                sure += len(r)
            tiles = self.frame_info[r[0]]
            rows.append("| `Frame_20_%04x`%s | %d | `$%02X` | %s |" % (
                r[0], "–`%04x`" % r[-1] if len(r) > 1 else "", len(r), tiles[3],
                "loose match at " + ", ".join(hits[:4]) + (" …" if len(hits) > 4 else "") if hits else "none"))
        lines += ["## Sprite frames", "",
                  "%d of %d frames are unused: %d with no loose match anywhere, %d with one. Images are in `frames/`, "
                  "named `header_bank_tiles.png`, and shown in the object's palette where it is known (otherwise gray)."
                  % (len(unused), len(self.frame_info) - 1, sure, loose), "",
                  "| Frames | Count | Graphics bank | Loose matches |", "|---|---|---|---|"] + rows + [""]

        # anims
        refs = self.referenced_anims()
        anim_rows = []
        for (st, frames) in self.anim_scripts():
            if st in refs or not frames:
                continue
            hits = self.loose_matches(st)
            strip = []
            imgs = [self.render_frame(a, self.frame_colors(a)[0]) for a in frames[:24]]
            h = max(len(i) for i in imgs)
            for y in range(h):
                row = []
                for i in imgs:
                    row += (i[y] if y < len(i) else [(0xFF, 0xFF, 0xFF)] * len(i[0])) + [(0xFF, 0xFF, 0xFF)] * 2
                strip.append(row)
            write_rgb_png(os.path.join(outdir, "anims", "Anim_04_%04x.png" % st), len(strip[0]), h, strip)
            only_here = [a for a in frames if a in set(unused)]
            anim_rows.append("| `Anim_04_%04x` | %d | %s | %s |" % (
                st, len(frames), "%d" % len(only_here) if only_here else "0",
                "loose match at " + ", ".join(hits[:3]) if hits else "none"))
        lines += ["## Animation scripts", "",
                  "Scripts in bank $04 that nothing jumps to and no object or code ever starts. Most begin right after "
                  "another script's final jump, so the game simply never reaches them. `anims/` shows each one's frames "
                  "in order. The third column counts the frames that no other script uses either.", "",
                  "| Script | Frames | Frames used nowhere else | Loose matches |", "|---|---|---|---|"] + anim_rows + [""]

        # palettes
        bg_used, obj_used = self.used_palettes()
        pb = t.palette_bank
        bg_rows = []
        for k in range(55):
            a = 0x4257 + 64 * k
            if a in bg_used:
                continue
            hits = self.loose_matches(a)
            cols = [gbc_rgb(rom[off(pb, a + 2 * c)] | rom[off(pb, a + 2 * c) + 1] << 8) for c in range(32)]
            sw = [[cols[(y // 12) * 4 + x // 12] for x in range(48)] for y in range(96)]
            write_rgb_png(os.path.join(outdir, "palettes", "BGPaletteSet_%02X.png" % k), 48, 96, sw)
            bg_rows.append("| `BGPaletteSet_%02X` | `$%04x` | %s |" % (k, a, "loose match at " + ", ".join(hits[:3]) if hits else "none"))
        obj_rows = []
        for p in range(64):
            if p in obj_used:
                continue
            a = 0x4000 + 8 * p
            cols = [gbc_rgb(rom[off(pb, a + 2 * c)] | rom[off(pb, a + 2 * c) + 1] << 8) for c in range(4)]
            sw = [[cols[x // 12] for x in range(48)] for y in range(12)]
            write_rgb_png(os.path.join(outdir, "palettes", "ObjPalette_%02X.png" % p), 48, 12, sw)
            obj_rows.append("`ObjPalette_%02X`" % p)
        lines += ["## Palettes", "",
                  "BG palette sets (8 palettes each) that no level descriptor uses. The swatches in `palettes/` have one "
                  "row per palette.", "", "| Set | Address | Loose matches |", "|---|---|---|"] + bg_rows + ["",
                  "Object palettes that no object list, preload list or decoded code uses: %s. This one is the least "
                  "certain claim, because code can pick a palette from a register value the tracer can't see." % ", ".join(obj_rows), ""]
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "README.md"), "w") as f:
            f.write("\n".join(lines))
        print("unused frames: %d (%d without loose matches), scripts: %d, BG sets: %d, OBJ palettes: %d -> %s"
              % (len(unused), sure, len(anim_rows), len(bg_rows), len(obj_rows), outdir))


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "baserom.gbc"), "rb").read()
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "unused")
    Finder(rom).run(out)


if __name__ == "__main__":
    main()
