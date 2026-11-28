#!/usr/bin/env python3
"""Backgrounds: level maps and full-screen pictures.

  python3 tools/backgrounds.py [baserom.gbc] [outdir]

Renders every level map and every full screen to PNGs in outdir (default
gfx/backgrounds/, which is gitignored: these are the game's graphics).

Level maps (see Func_00_0b4f, Func_00_0c24): a level descriptor points to a
map header in bank $04 (see MAP_HEADER below). The map is a grid of 32x32
pixel blocks. Two compressed layers (Func_00_03e4) give each cell's block
number and block attribute; blocks are 4x4 tiles defined in a block bank;
tiles come from an 8 KB tileset; colors from the descriptor's BG palette set.

World maps (state $0d, $1a58): see world_maps().

Full screens (Func_00_2b5f and the states after it): a screen record is
three pointers, to 128 bytes of palettes, a 20x18 tile map (360 attribute
bytes, then 360 tile numbers) and 8 KB of tiles. Records are picked by the
game's flow script (bank $0d, run by Func_00_38cd).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hints  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = 0x4000


def off(bank, addr):
    return addr if addr < BANK else bank * BANK + addr - BANK


def rw(rom, bank, addr):
    o = off(bank, addr)
    return rom[o] | rom[o + 1] << 8


# ------------------------------------------------------------ compression
def decompress(rom, bank, addr, limit=0x1000):
    """Func_00_03e4. Returns (data, compressed length)."""
    out = bytearray()
    o = start = off(bank, addr)
    while True:
        n = rom[o]
        o += 1
        if n == 0:
            break
        if n < 0x80:            # run: repeat the next byte n times
            out += bytes([rom[o]]) * n
            o += 1
        elif n < 0xC0:          # n & $3f literal bytes
            k = n & 0x3F
            out += rom[o:o + k]
            o += k
        else:                   # copy n & $3f bytes from distance d back
            k, d = n & 0x3F, rom[o]
            o += 1
            for _ in range(k):
                out.append(out[len(out) - d])
        if len(out) > limit:
            raise ValueError("decompressed past %d bytes at %02x:%04x" % (limit, bank, addr))
    return bytes(out), o - start


# --------------------------------------------------------------- headers
def level_descriptors(rom):
    bank, (start, end) = 0x04, hints.LEVELS["descriptors"]
    for a in range(start, end, 12):
        yield a, rom[off(bank, a):off(bank, a) + 12]


def map_header(rom, addr):
    """Map header in bank $04: block bank, terrain bank, flags (bit 0:
    vertical, bit 1: second half in WRAM banks 5-7), 2 bytes for $c45c,
    tileset bank and address, map data bank, then 3 or 6 layer pointers
    (WRAM banks 1, 2, 3 [, 5, 6, 7]: block numbers, block attributes,
    terrain)."""
    b = 0x04
    r = rom[off(b, addr):off(b, addr) + 21]
    n = 6 if r[2] & 2 else 3
    return {
        "addr": addr, "blocks": r[0], "terrain": r[1], "flags": r[2], "c45c": r[3] | r[4] << 8,
        "ts_bank": r[5], "ts": r[6] | r[7] << 8, "map_bank": r[8],
        "layers": [r[9 + 2 * k] | r[10 + 2 * k] << 8 for k in range(n)],
        "length": 9 + 2 * n,
    }


def map_headers(rom):
    """All map headers, in order, with the descriptors that use them."""
    uses = {}
    for a, d in level_descriptors(rom):
        uses.setdefault(d[5] | d[6] << 8, []).append(a)
    return {h: (map_header(rom, h), sorted(ds)) for h, ds in uses.items()}


MAP_ROLES = ("blocks", "attrs", "terrain")


def map_streams(rom):
    """{(bank, addr): path} for every compressed map layer. The file holds the
    layer decompressed (see tools/lzcomp.py): one byte per 32x32-pixel cell,
    16 rows of 256 for horizontal levels or 64 rows of 64 for vertical ones,
    giving the block number, block attribute or terrain of each cell."""
    out = {}
    for _, (hdr, _) in sorted(map_headers(rom).items()):
        for k, p in enumerate(hdr["layers"]):
            out[(hdr["map_bank"], p)] = "data/maps/%02x_%04x_%s.bin" % (hdr["map_bank"], p, MAP_ROLES[k % 3])
    return out


# --------------------------------------------------------------- drawing
def gbc_rgb(v):
    return tuple(x << 3 | x >> 2 for x in (v & 31, v >> 5 & 31, v >> 10 & 31))


def palettes_at(rom, bank, addr, count=8):
    o = off(bank, addr)
    return [[gbc_rgb(rom[o + 8 * p + 2 * c] | rom[o + 8 * p + 2 * c + 1] << 8) for c in range(4)]
            for p in range(count)]


def tile_pixels(rom, bank, addr):
    o = off(bank, addr)
    rows = []
    for r in range(8):
        lo, hi = rom[o + 2 * r], rom[o + 2 * r + 1]
        rows.append([((hi >> (7 - x)) & 1) << 1 | ((lo >> (7 - x)) & 1) for x in range(8)])
    return rows


class Tileset:
    """8 KB of BG tiles as the game lays them out in VRAM: from `addr`,
    VRAM bank 0 tiles 0-127 ($9000), 128-255 ($8800), then VRAM bank 1
    the same (tile numbers are used with LCDC bit 4 clear)."""

    def __init__(self, rom, bank, addr):
        self.rom, self.bank, self.addr = rom, bank, addr
        self.cache = {}

    def tile_addr(self, vbank, t):
        return self.addr + 0x1000 * vbank + (t * 16 if t < 128 else 0x800 + (t - 128) * 16)

    def tile(self, vbank, t):
        k = (vbank, t)
        if k not in self.cache:
            self.cache[k] = tile_pixels(self.rom, self.bank, self.tile_addr(vbank, t))
        return self.cache[k]


def draw_tile(canvas, x0, y0, tileset, t, attr, pals):
    px = tileset.tile((attr >> 3) & 1, t)
    pal = pals[attr & 7]
    for y in range(8):
        sy = 7 - y if attr & 0x40 else y
        row = px[sy]
        out = canvas[y0 + y]
        for x in range(8):
            out[x0 + x] = pal[row[7 - x if attr & 0x20 else x]]


def render_level(rom, hdr, pal_set_addr):
    """Render a whole level map. Returns (rows of RGB, width, height)."""
    vertical = hdr["flags"] & 1
    halves = 2 if hdr["flags"] & 2 else 1
    layers = []
    for h in range(halves):
        num = decompress(rom, hdr["map_bank"], hdr["layers"][3 * h])[0].ljust(0x1000, b"\0")
        att = decompress(rom, hdr["map_bank"], hdr["layers"][3 * h + 1])[0].ljust(0x1000, b"\0")
        layers.append((num, att))
    if vertical:
        cols, rows = 64, 64 * halves
        cell = lambda r, c: (r // 64, (r % 64) * 64 + c)  # noqa: E731
    else:
        cols, rows = 256 * halves, 16
        cell = lambda r, c: (c // 256, r * 256 + (c % 256))  # noqa: E731
    # crop to the area that has blocks
    used_r, used_c = [], []
    for r in range(rows):
        for c in range(cols):
            h, i = cell(r, c)
            if layers[h][0][i] or layers[h][1][i]:
                used_r.append(r)
                used_c.append(c)
    if not used_r:
        return None, 0, 0
    r0, r1, c0, c1 = 0, max(used_r) + 1, 0, max(used_c) + 1
    pals = palettes_at(rom, 0x80, pal_set_addr)
    ts = Tileset(rom, hdr["ts_bank"], hdr["ts"])
    w, h_ = (c1 - c0) * 32, (r1 - r0) * 32
    canvas = [[(0, 0, 0)] * w for _ in range(h_)]
    for r in range(r0, r1):
        for c in range(c0, c1):
            hh, i = cell(r, c)
            num, att = layers[hh][0][i], layers[hh][1][i]
            bbank = hdr["blocks"] + (1 if att & 4 else 0)
            hi = (att & ~4 & 0xFF) | 0x40
            for ty in range(4):
                for tx in range(4):
                    plane = 4 * ty + tx
                    t = rom[off(bbank, ((hi + 4 * plane) & 0xFF) << 8 | num)]
                    a = rom[off(bbank, ((hi + 4 * plane) & 0xFF) << 8 | (num + 1) & 0xFF)]
                    draw_tile(canvas, (c - c0) * 32 + tx * 8, (r - r0) * 32 + ty * 8, ts, t, a, pals)
    return canvas, w, h_


# ------------------------------------------------------------ full screens
def screen_record(rom, bank, addr):
    return {"bank": bank, "addr": addr, "palettes": rw(rom, bank, addr),
            "map": rw(rom, bank, addr + 2), "tiles": rw(rom, bank, addr + 4)}


def render_screen(rom, rec):
    b = rec["bank"]
    pals = palettes_at(rom, b, rec["palettes"])
    ts = Tileset(rom, b, rec["tiles"])
    mo = off(b, rec["map"])
    canvas = [[(0, 0, 0)] * 160 for _ in range(144)]
    for i in range(360):
        attr, t = rom[mo + i], rom[mo + 360 + i]
        draw_tile(canvas, (i % 20) * 8, (i // 20) * 8, ts, t, attr, pals)
    return canvas


# ------------------------------------------------------------ flow script
FLOW_ARGS = {0x1F: 3, 0x4C: 2, 0x1C: 1, 0x19: 1}


def flow_script(rom, entries):
    """Walk the flow script (bank $0d) from entries. Returns {addr: command}:
    ('jump', target) or ('state', id, args)."""
    bank = 0x0D
    seen = {}
    todo = list(entries)
    while todo:
        a = todo.pop()
        while a not in seen:
            s = rom[off(bank, a)]
            if s == 0:
                t = rw(rom, bank, a + 1)
                seen[a] = ("jump", t)
                todo.append(t)
                break
            n = FLOW_ARGS.get(s, 0)
            seen[a] = ("state", s, list(rom[off(bank, a + 1):off(bank, a + 1 + n)]))
            a += 1 + n
    return seen


def screens_in_flow(rom):
    recs = {}
    for a, cmd in flow_script(rom, hints.FLOW_ENTRIES).items():
        if cmd[0] == "state" and cmd[1] == 0x1F:
            p, bk = cmd[2][0] | cmd[2][1] << 8, cmd[2][2]
            recs.setdefault((bk, p), []).append(a)
    return recs


# --------------------------------------------------------------- world maps
def world_maps(rom):
    """World map records (bank $05, table hints.WORLD_MAPS). Each record:
    4 bytes (scroll limit and the pointer to the map's level markers), the
    tile map (bank $0f), a list copied to $c500 (ends with $ff), BG
    palettes (bank $0f) and the tileset (address, bank). The tile map is a
    width byte n, then n columns of 18 tile numbers followed by their 18
    attributes (Func_00_1f8a)."""
    bank, table, count = hints.WORLD_MAPS
    out = []
    for k in range(count):
        p = rw(rom, bank, table + 2 * k)
        r = rom[off(bank, p):off(bank, p) + 13]
        m = r[4] | r[5] << 8
        out.append({"index": k, "addr": p, "raw": bytes(r), "map": m, "list": r[6] | r[7] << 8,
                    "palettes": r[8] | r[9] << 8, "ts": r[10] | r[11] << 8, "ts_bank": r[12],
                    "width": rom[off(0x0F, m)]})
    return out


def render_world_map(rom, wm):
    pals = palettes_at(rom, 0x0F, wm["palettes"])
    ts = Tileset(rom, wm["ts_bank"], wm["ts"])
    n = wm["width"]
    canvas = [[(0, 0, 0)] * (n * 8) for _ in range(144)]
    o = off(0x0F, wm["map"]) + 1
    for c in range(n):
        for y in range(18):
            draw_tile(canvas, c * 8, y * 8, ts, rom[o + 36 * c + y], rom[o + 36 * c + 18 + y], pals)
    return canvas


# ------------------------------------------------------- front-end pictures
def file_off(bank, addr):
    """File offset of bank:addr, letting addresses past $7fff run on into
    the following banks (tile data does)."""
    return bank * BANK + addr - BANK


def pictures(rom):
    """The front end's picture table. Each record: map, palettes and tiles,
    with the sizes worked out from where the next record's data starts."""
    pt = hints.PICTURES
    b, a0, n = pt["bank"], pt["table"], pt["count"]
    recs = []
    for i in range(n):
        a = a0 + 9 * i
        r = rom[off(b, a):off(b, a) + 9]
        recs.append({"index": i, "addr": a,
                     "map": (r[0], r[1] | r[2] << 8), "palettes": (r[3], r[4] | r[5] << 8),
                     "tiles": (r[6], r[7] | r[8] << 8)})
    # tile block sizes: up to the next distinct start, but not past the end
    # of the data in the last bank
    starts = sorted({file_off(*r["tiles"]) for r in recs})
    pal_starts = sorted({file_off(*r["palettes"]) for r in recs})
    map_starts = sorted({file_off(*r["map"]) for r in recs})

    def data_end(o):
        bank_end = (o // BANK + 1) * BANK
        e = bank_end
        while e > o and rom[e - 1] == 0:
            e -= 1
        return e
    for r in recs:
        o = file_off(*r["tiles"])
        nxt = [x for x in starts if x > o]
        end = nxt[0] if nxt else data_end(o)
        if end - o > 0x2000:
            end = o + 0x2000
        if data_end(o) <= o:
            end = o  # points past the end of the bank's data
        r["tile_bytes"] = (end - o) // 16 * 16
        po = file_off(*r["palettes"])
        nxt = sorted(x for x in pal_starts + starts + map_starts if x > po)
        r["palette_count"] = min(8, ((nxt[0] - po) if nxt else 64) // 8)
        # the picture's size in tiles: heights at $F0:53BD, widths at $F0:5452
        # (PictureHeights, PictureWidths). A map is w*h tile numbers, or w*h attributes and
        # w*h tile numbers when there is room for both before the next map
        r["h"] = rom[off(b, pt["heights"] + r["index"])]
        r["w"] = rom[off(b, pt["widths"] + r["index"])]
        # the letter pieces at $F2:5574 (picture, x, y, w, h, ...) cut letters
        # out of the font sheets and reach rows below the screen height
        for k in range(61):
            lp = rom[off(0xF2, 0x5574 + 8 * k):off(0xF2, 0x5574 + 8 * k) + 5]
            if lp[0] == r["index"] and lp[0]:
                r["h"] = max(r["h"], lp[2] + lp[4])
        n = r["w"] * r["h"] or 360
        mo = file_off(*r["map"])
        nxt = sorted(x for x in map_starts + pal_starts if x > mo)
        gap = nxt[0] - mo if nxt else 2 * n
        attrs, tiles = rom[mo:mo + n], rom[mo + n:mo + 2 * n]
        looks_full = gap >= 2 * n and all(x & 0x10 == 0 for x in attrs) and len(set(tiles)) > 1
        r["map_bytes"] = 2 * n if i_is_full(r["index"]) or looks_full else n
    return recs


def picture_tile_pieces(rom):
    """Tile PNG pieces for the picture table, split at bank boundaries:
    {(bank, start): [(path, addr, tiles, width)]}."""
    out = {}
    seen = set()
    for r in pictures(rom):
        o, n = file_off(*r["tiles"]), r["tile_bytes"]
        if n == 0 or o in seen:
            continue
        seen.add(o)
        while n > 0:
            bank, addr = o // BANK, o % BANK + 0x4000
            part = min(n, 0x8000 - addr)
            tiles = part // 16
            base = os.path.join("gfx", "bgtiles", "%02x" % bank, "%04x" % addr)
            pieces = []
            if tiles >= 16:
                pieces.append((base + ".png", addr, tiles // 16 * 16, 16))
            if tiles % 16:
                pieces.append((base + ("_end.png" if tiles >= 16 else ".png"), addr + tiles // 16 * 256, tiles % 16, tiles % 16))
            out[(bank, addr)] = pieces
            o += part
            n -= part
    return out


def i_is_full(i):
    return i < hints.PICTURES["full_maps"]


def render_picture(rom, r, sequential=False):
    """Draw a picture from its map (attributes first for full maps), or, for
    sticker pictures (sequential=True), as 360 tiles in order with palette 0
    the way the Sticker Book shows them."""
    pals = palettes_at(rom, *r["palettes"], 8)
    ts = Tileset(rom, *r["tiles"])
    w, h = (r["w"], r["h"]) if r.get("w") and r.get("h") else (20, 18)
    n = w * h
    canvas = [[(0, 0, 0)] * (8 * max(w, 20)) for _ in range(8 * max(h, 18))]
    mo = file_off(*r["map"])
    for k in range(360 if sequential else n):
        if sequential:
            t, a = k % 256, (8 if k >= 256 else 0)
            x, y = k % 20, k // 20
        else:
            x, y = k % w, k // w
            if r["map_bytes"] == 2 * n:
                a, t = rom[mo + k], rom[mo + n + k]
            else:
                a, t = 0, rom[mo + k]
        draw_tile(canvas, x * 8, y * 8, ts, t, a, pals)
    return canvas


# ------------------------------------------------------------- title screen
def titles(rom):
    """The title pictures: map (36 rows, each 20 tile numbers then 20
    attributes), 32 palettes, tileset and palette-swap list per slot."""
    t = hints.TITLES
    b = t["bank"]
    out = []
    for v in range(t["count"]):
        lst = rw(rom, b, t["lists"] + 2 * v)
        ents, o = [], off(b, lst)
        while rom[o] != 0xFF:
            ents.append(tuple(rom[o:o + 3]))
            o += 3
        out.append({"slot": v, "map": rw(rom, b, t["maps"] + 2 * v), "palettes": rw(rom, b, t["palettes"] + 2 * v),
                    "ts_bank": rom[off(b, t["tilesets"] + 3 * v)], "ts": rw(rom, b, t["tilesets"] + 3 * v + 1),
                    "list": lst, "entries": ents, "list_length": 3 * len(ents) + 1})
    return out


def render_title(rom, tv):
    """Each row is drawn with the palettes in effect once the title has
    scrolled to it (the swap list is applied in scroll order)."""
    b = hints.TITLES["bank"]
    allp = palettes_at(rom, b, tv["palettes"], 32)
    ts = Tileset(rom, tv["ts_bank"], tv["ts"])
    canvas = [[(0, 0, 0)] * 160 for _ in range(288)]
    mo = off(b, tv["map"])
    for r in range(36):
        pals = list(allp[:8])
        for (line, src, dst) in tv["entries"]:
            if line <= r * 8:
                pals[(dst & 0x7F) // 8] = allp[src // 8]
        for c in range(20):
            draw_tile(canvas, c * 8, r * 8, ts, rom[mo + r * 40 + c], rom[mo + r * 40 + 20 + c], pals)
    return canvas


# ------------------------------------------------------------ Funky's Fishing
def render_fishing(rom, screen):
    """Render one of Funky's Fishing's 20x18 screens with its own VRAM loads."""
    f = hints.FISHING
    b = f["bank"]
    vram = [bytearray(0x2000), bytearray(0x2000)]
    for (src, n, vb, dst) in f["tiles"]:
        o = off(b, src)
        vram[vb][dst - 0x8000:dst - 0x8000 + n * 16] = rom[o:o + n * 16]

    class VTiles:
        def tile(self, vb, t):
            a = (0x1000 + t * 16) if t < 128 else (0x800 + (t - 128) * 16)
            d = vram[vb][a:a + 16]
            return [[((d[2 * r + 1] >> (7 - x)) & 1) << 1 | ((d[2 * r] >> (7 - x)) & 1) for x in range(8)]
                    for r in range(8)]
    pals = palettes_at(rom, b, f["bg_palettes"])
    canvas = [[(0, 0, 0)] * 160 for _ in range(144)]
    mo = off(b, screen)
    vt = VTiles()
    for i in range(360):
        draw_tile(canvas, (i % 20) * 8, (i // 20) * 8, vt, rom[mo + 360 + i], rom[mo + i], pals)
    return canvas


# ------------------------------------------------------- tiles for the build
def screen_records(rom):
    keys = list(screens_in_flow(rom)) + [k for k, _ in hints.EXTRA_SCREENS]
    return {k: screen_record(rom, *k) for k in keys}


def bg_tile_pieces(rom):
    """BG tile data as stored for the build: {(bank, start): [(path, addr,
    tiles, width in tiles)]}. Tilesets are 8 KB from their start address,
    but some overlap the next one, so each bank is split at every start.
    A segment becomes a PNG 16 tiles wide plus, if the count isn't a
    multiple of 16, a one-row PNG with the rest."""
    starts = {}
    for hdr, _ in map_headers(rom).values():
        starts.setdefault(hdr["ts_bank"], set()).add(hdr["ts"])
    for wm in world_maps(rom):
        starts.setdefault(wm["ts_bank"], set()).add(wm["ts"])
    for tv in titles(rom):
        starts.setdefault(tv["ts_bank"], set()).add(tv["ts"])
    fb = hints.FISHING["bank"]
    for (a, n, _, _) in hints.FISHING["tiles"]:
        starts.setdefault(fb, set()).add(a)
    others = {}  # other data in the same banks: tiles stop where it starts
    others.setdefault(fb, set()).update(hints.FISHING["screens"])
    for rec in screen_records(rom).values():
        starts.setdefault(rec["bank"], set()).add(rec["tiles"])
        others.setdefault(rec["bank"], set()).update((rec["addr"], rec["palettes"], rec["map"]))
    out = picture_tile_pieces(rom)
    for b, ss in starts.items():
        ss = sorted(ss)
        for i, a in enumerate(ss):
            end = a + 0x2000
            if i + 1 < len(ss) and ss[i + 1] < end:
                end = ss[i + 1]
            end = min([end] + [x for x in others.get(b, ()) if x > a])
            for (fa, fn, _, _) in (hints.FISHING["tiles"] if b == hints.FISHING["bank"] else ()):
                if fa == a:
                    end = min(end, a + fn * 16)
            n = (end - a) // 16
            base = os.path.join("gfx", "bgtiles", "%02x" % b, "%04x" % a)
            pieces = []
            if n >= 16:
                pieces.append((base + ".png", a, n // 16 * 16, 16))
            if n % 16:
                pieces.append((base + ("_end.png" if n >= 16 else ".png"), a + n // 16 * 256, n % 16, n % 16))
            out[(b, a)] = pieces
    tb, ta = hints.THUMBNAILS["table"]
    for k in range(hints.THUMBNAILS["count"]):
        r = rom[off(tb, ta + 8 * k):off(tb, ta + 8 * k) + 8]
        a, w, h = r[4] | r[5] << 8, r[6], r[7]
        out[(r[3], a)] = [(os.path.join("gfx", "bgtiles", "%02x" % r[3], "%04x.png" % a), a, w * h, w)]
    for (b, a, n, _) in hints.EXTRA_TILES:
        base = os.path.join("gfx", "bgtiles", "%02x" % b, "%04x" % a)
        pieces = []
        if n >= 16:
            pieces.append((base + ".png", a, n // 16 * 16, 16))
        if n % 16:
            pieces.append((base + ("_end.png" if n >= 16 else ".png"), a + n // 16 * 256, n % 16, n % 16))
        out[(b, a)] = pieces
    return out


FLOW_STATES = {
    0x01: "FLOW_LOAD_LEVEL", 0x0D: "FLOW_WORLD_MAP_INIT", 0x19: "FLOW_PLAY_SONG",
    0x1C: "FLOW_FADE", 0x1F: "FLOW_LOAD_SCREEN", 0x31: "FLOW_PICK_WORLD_SCREEN",
    0x49: "FLOW_WORLD_MAP", 0x4C: "FLOW_WAIT", 0x4F: "FLOW_WAIT_MUSIC_END",
    0x52: "FLOW_WAIT_BUTTON", 0x55: "FLOW_SCREEN_MAP", 0x58: "FLOW_SCREEN_PALETTES",
    0x5B: "FLOW_SCREEN_TILES_0", 0x5E: "FLOW_SCREEN_TILES_1", 0x61: "FLOW_RUN_SECOND_PROGRAM",
}


# ------------------------------------------------------------------ output
def save(path, canvas):
    from find_unused import write_rgb_png
    write_rgb_png(path, len(canvas[0]), len(canvas), canvas)


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "baserom.gbc"), "rb").read()
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "gfx", "backgrounds")
    n = 0
    for h, (hdr, descs) in sorted(map_headers(rom).items()):
        d = rom[off(0x04, descs[0]):off(0x04, descs[0]) + 12]
        canvas, w, ht = render_level(rom, hdr, d[1] | d[2] << 8)
        if canvas:
            save(os.path.join(out, "levels", "map_%04x.png" % h), canvas)
            n += 1
    s = 0
    for (bk, p) in sorted(screens_in_flow(rom)):
        save(os.path.join(out, "screens", "screen_%02x_%04x.png" % (bk, p)), render_screen(rom, screen_record(rom, bk, p)))
        s += 1
    w = 0
    for wm in world_maps(rom):
        save(os.path.join(out, "world", "world_%d_%04x.png" % (wm["index"], wm["addr"])), render_world_map(rom, wm))
        w += 1
    for scr in hints.FISHING["screens"]:
        save(os.path.join(out, "fishing", "fishing_%04x.png" % scr), render_fishing(rom, scr))
    for tv in titles(rom):
        save(os.path.join(out, "title", "title_slot%d_%04x.png" % (tv["slot"], tv["map"])), render_title(rom, tv))
    for r in pictures(rom):
        if r["tile_bytes"] == 0:
            continue
        save(os.path.join(out, "pictures", "picture_%03d.png" % r["index"]), render_picture(rom, r))
        if r["tile_bytes"] >= 360 * 16 and not i_is_full(r["index"]):
            save(os.path.join(out, "pictures", "picture_%03d_sticker_view.png" % r["index"]),
                 render_picture(rom, r, sequential=True))
    print("rendered %d level maps, %d screens, %d world maps and %d Funky's Fishing screens into %s"
          % (n, s, w, len(hints.FISHING["screens"]), out))


if __name__ == "__main__":
    main()
