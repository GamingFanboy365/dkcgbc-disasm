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
        lines += self.backgrounds(outdir)
        lines += self.game_states()
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "README.md"), "w") as f:
            f.write("\n".join(lines))
        print("unused frames: %d (%d without loose matches), scripts: %d, BG sets: %d, OBJ palettes: %d -> %s"
              % (len(unused), sure, len(anim_rows), len(bg_rows), len(obj_rows), outdir))


def _bg_methods():
    import backgrounds as bg

    def block_tiles(rom, b, hi, n):
        return [(rom[off(b, ((hi + 4 * p) & 0xFF) << 8 | n)], rom[off(b, ((hi + 4 * p) & 0xFF) << 8 | ((n + 1) & 0xFF))])
                for p in range(16)]

    def backgrounds(self, outdir):
        """Blocks no level map places, and tiles no block uses."""
        rom = self.rom
        hs = bg.map_headers(rom)
        placed, users = defaultdict(set), defaultdict(list)
        for h, (hd, descs) in sorted(hs.items()):
            users[hd["blocks"]].append((hd, descs))
            for k in range(2 if hd["flags"] & 2 else 1):
                num = bg.decompress(rom, hd["map_bank"], hd["layers"][3 * k])[0]
                att = bg.decompress(rom, hd["map_bank"], hd["layers"][3 * k + 1])[0]
                for n, a in zip(num, att):
                    placed[hd["blocks"]].add((hd["blocks"] + (1 if a & 4 else 0), (a & 0xFB) | 0x40, n))
        rows = []
        total = 0
        tile_rows = []
        for base in sorted(users):
            hd, descs = users[base][0]
            d = rom[off(0x04, descs[0]):off(0x04, descs[0]) + 12]
            pals = bg.palettes_at(rom, 0x80, d[1] | d[2] << 8)
            ts = bg.Tileset(rom, hd["ts_bank"], hd["ts"])
            defined, unused = [], []
            for b in (base, base + 1):
                for hi in (0x40, 0x41, 0x42, 0x43):
                    for n in range(0, 256, 2):
                        bt = block_tiles(rom, b, hi, n)
                        if any(t or a for t, a in bt):
                            defined.append((b, hi, n, bt))
                            if (b, hi, n) not in placed[base]:
                                unused.append((b, hi, n, bt))
            # tiles of this level's tileset that no defined block uses
            used_tiles = set()
            for (_, _, _, bt) in defined:
                for t, a in bt:
                    used_tiles.add(((a >> 3) & 1, t))
            pieces = bg.bg_tile_pieces(rom).get((hd["ts_bank"], hd["ts"]), [])
            own = sum(p[2] for p in pieces)
            lost = []
            for k in range(own):
                # stored order: VRAM bank 0 tiles 0-255, then VRAM bank 1 tiles 0-255
                vb, tid = k // 256, k % 256
                if (vb, tid) not in used_tiles:
                    px = ts.tile(vb, tid)
                    if any(any(r) for r in px):
                        lost.append((vb, tid))
            if lost:
                cols = 16
                hgt = (len(lost) + cols - 1) // cols
                canvas = [[(0xFF, 0xFF, 0xFF)] * (cols * 9) for _ in range(hgt * 9)]
                gray = [(0xF8, 0xF8, 0xF8), (0xA8, 0xA8, 0xA8), (0x58, 0x58, 0x58), (0x10, 0x10, 0x10)]
                for i, (vb, tid) in enumerate(lost):
                    px = ts.tile(vb, tid)
                    for y in range(8):
                        for x in range(8):
                            canvas[(i // cols) * 9 + y][(i % cols) * 9 + x] = gray[px[y][x]]
                write_rgb_png(os.path.join(outdir, "bg_tiles", "tileset_%02x_%04x.png" % (hd["ts_bank"], hd["ts"])),
                              len(canvas[0]), len(canvas), canvas)
                tile_rows.append("| `BGTiles_%02x_%04x` | %d | %d |" % (hd["ts_bank"], hd["ts"], own, len(lost)))
            if not unused:
                continue
            total += len(unused)
            cols = 8
            hgt = (len(unused) + cols - 1) // cols
            canvas = [[(0xFF, 0xFF, 0xFF)] * (cols * 34) for _ in range(hgt * 34)]
            for i, (b, hi, n, bt) in enumerate(unused):
                x0, y0 = (i % cols) * 34, (i // cols) * 34
                sub = [[None] * 32 for _ in range(32)]
                for p, (t, a) in enumerate(bt):
                    bg.draw_tile(sub, (p % 4) * 8, (p // 4) * 8, ts, t, a, pals)
                for y in range(32):
                    canvas[y0 + y][x0:x0 + 32] = sub[y]
            write_rgb_png(os.path.join(outdir, "bg_blocks", "blocks_%02x.png" % base), len(canvas[0]), len(canvas), canvas)
            maps = ", ".join("`MapHeader_04_%04x`" % h["addr"] for h, _ in users[base][:4]) + (" …" if len(users[base]) > 4 else "")
            rows.append("| `LevelBlocks_%02x` | %d | %d | %s |" % (base, len(defined), len(unused), maps))
        out = ["## Level blocks", "",
               "Blocks (32x32 pixels, 4x4 tiles) that are defined but never placed in any level map: %d in all. "
               "Each sheet in `bg_blocks/` shows one block bank's unplaced blocks, eight to a row, drawn with the "
               "tileset and BG palettes of the first level that uses that bank. Code that swaps blocks in at run "
               "time (breakable walls, switches, animated scenery) could still use some of these, so treat this "
               "as a list of candidates, not a final verdict." % total, "",
               "| Block bank | Defined | Never placed | Used by maps |", "|---|---|---|---|"] + rows + [""]
        out += ["## Level tiles", "",
                "Tiles in a level tileset's own data (not counting the part shared with the next tileset) that "
                "no block refers to, placed or not. Blank tiles aren't counted. Sheets are in `bg_tiles/`, in gray.", "",
                "| Tileset | Tiles | Not used by any block |", "|---|---|---|"] + tile_rows + [""]
        return out

    def game_states(self):
        """States in the $0300 jump table that neither the flow script nor
        code (ld a, n / ldh [$ff84], a) ever selects."""
        rom, t = self.rom, self.t
        used = set()
        for a, c in bg.flow_script(rom, __import__("hints").FLOW_ENTRIES).items():
            if c[0] == "state":
                used.add(c[1])
        order = sorted(t.insns)
        for k, o in enumerate(order):
            i = t.insns[o]
            if i.op == 0xE0 and i.imm == 0x84 and k and t.insns[order[k - 1]].op == 0x3E:
                used.add(t.insns[order[k - 1]].imm)
        states = range(0x01, 0x64, 3)
        unused = []
        for s_ in states:
            if s_ in used:
                continue
            j = 0x0300 + s_
            target = rom[j + 1] | rom[j + 2] << 8 if rom[j] == 0xC3 else None
            unused.append("`$%02x` (jumps to `$%04x`)" % (s_, target) if target else "`$%02x`" % s_)
        if not unused:
            return ["## Game states", "",
                    "Every state in the jump table at `$0300` is chosen by the flow script or by code that writes "
                    "it to `$FF84`, so there are no orphaned game states.", ""]
        return ["## Game states", "",
                "The main loop runs the state in `$FF84` through the jump table at `$0300`. These states are "
                "never chosen by the flow script or by code that writes a constant to `$FF84`: %s. They may still "
                "be reached through computed values, so their code is worth a look before calling them dead."
                % ", ".join(unused), ""]

    Finder.backgrounds = backgrounds
    Finder.game_states = game_states


_bg_methods()


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "baserom.gbc"), "rb").read()
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "unused")
    Finder(rom).run(out)


if __name__ == "__main__":
    main()
