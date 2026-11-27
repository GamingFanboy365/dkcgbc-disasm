#!/usr/bin/env python3
"""Sprite frame graphics: PNG <-> 2bpp, with no third-party dependencies.

  python3 tools/gfx.py extract [baserom.gbc] [--force]
      Write every frame's tiles to gfx/frames/BB/AAAA.png (BB = bank and
      AAAA = address of the tiles), and every BG tileset piece to
      gfx/bgtiles/BB/AAAA.png (see tools/backgrounds.py). Existing PNGs
      are kept unless --force.

  python3 tools/gfx.py png2bpp in.png out.2bpp
      Convert a frame PNG back to 2bpp tile data. The build uses rgbgfx
      (-c dmg -Z); this pure-Python version gives the same result for the
      four grays used here and is what tools/check_asm.py uses.

  python3 tools/gfx.py preview [baserom.gbc] [outdir]
      Assemble whole frames from their tiles and sprite offsets into
      gfx/preview/ (not part of the build) so they can be looked at, in
      each frame's object palette when it can be worked out (see
      tools/frame_palettes.py; index.csv says which).

Frame PNG layout: one 8x16 sprite per column, left to right in drawing
order, so a frame with n tiles is (n / 2 * 8) x 16 pixels. Colors are
white, light gray, dark gray, black for color indexes 0-3 (0 is
transparent on sprites).
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hints  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAYS = [0xFF, 0xAA, 0x55, 0x00]
BANK = 0x4000


def off(bank, addr):
    return addr if addr < BANK else bank * BANK + addr - BANK


# ----------------------------------------------------------------- PNG I/O
def write_png(path, width, height, rows, palette=None):
    """rows: list of lists of color indexes (0-3). Writes a 2-bit PNG,
    indexed with the given RGB palette, or grayscale if palette is None."""
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for x in range(0, width, 4):
            b = 0
            for k in range(4):
                v = row[x + k] if x + k < width else 0
                if palette is None:
                    v = 3 - v  # grayscale: 3 = white
                b = b << 2 | v
            raw.append(b)

    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ctype = 0 if palette is None else 3
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 2, ctype, 0, 0, 0))
    if palette is not None:
        png += chunk(b"PLTE", b"".join(bytes(c) for c in palette))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def read_png(path):
    """Returns (width, height, rows of (r, g, b, a)). Supports non-interlaced
    PNGs of every color type at 8 bits or less per sample (and 16-bit gray/RGB)."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("%s: not a PNG" % path)
    p = 8
    idat = b""
    plte = trns = None
    while p < len(data):
        n, t = struct.unpack(">I4s", data[p:p + 8])
        d = data[p + 8:p + 8 + n]
        p += 12 + n
        if t == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", d)
        elif t == b"PLTE":
            plte = [tuple(d[i:i + 3]) for i in range(0, len(d), 3)]
        elif t == b"tRNS":
            trns = d
        elif t == b"IDAT":
            idat += d
    if interlace:
        raise ValueError("%s: interlaced PNGs are not supported" % path)
    chans = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    bpp = max(1, chans * depth // 8)
    stride = (w * chans * depth + 7) // 8
    raw = zlib.decompress(idat)
    prev = bytearray(stride)
    out = []
    q = 0
    for _ in range(h):
        ft = raw[q]
        line = bytearray(raw[q + 1:q + 1 + stride])
        q += 1 + stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ft == 1:
                line[i] = (line[i] + a) & 0xFF
            elif ft == 2:
                line[i] = (line[i] + b) & 0xFF
            elif ft == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif ft == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        prev = line
        # unpack samples
        if depth < 8:
            per = 8 // depth
            samples = [(line[i // per] >> (8 - depth * (i % per + 1))) & ((1 << depth) - 1)
                       for i in range(w * chans)]
        elif depth == 8:
            samples = list(line)
        else:
            samples = [line[i] for i in range(0, len(line), 2)]
            depth = 8
        row = []
        scale = 255 // ((1 << depth) - 1) if depth < 8 else 1
        for x in range(w):
            s = samples[x * chans:(x + 1) * chans]
            if ctype == 3:
                r, g, b = plte[s[0]]
                alpha = trns[s[0]] if trns and s[0] < len(trns) else 255
                row.append((r, g, b, alpha))
            elif ctype == 0:
                v = s[0] * scale
                row.append((v, v, v, 255))
            elif ctype == 4:
                row.append((s[0], s[0], s[0], s[1]))
            elif ctype == 2:
                row.append((s[0], s[1], s[2], 255))
            else:
                row.append(tuple(s))
        out.append(row)
    return w, h, out


# --------------------------------------------------------------- 2bpp tiles
def tiles_to_rows(data, columns_major=True):
    """2bpp data for n tiles -> rows of color indexes, laid out as 8x16
    sprites side by side (tile 2i on top of tile 2i+1)."""
    n = len(data) // 16
    w = max(1, n // 2) * 8
    rows = [[0] * w for _ in range(16)]
    for t in range(n):
        x0, y0 = (t // 2) * 8, (t % 2) * 8
        for r in range(8):
            lo, hi = data[t * 16 + 2 * r], data[t * 16 + 2 * r + 1]
            for x in range(8):
                rows[y0 + r][x0 + x] = ((hi >> (7 - x)) & 1) << 1 | ((lo >> (7 - x)) & 1)
    return w, rows


def gray_index(px):
    r, g, b, a = px
    if a < 128:
        return 0
    v = (r * 299 + g * 587 + b * 114) // 1000
    return 3 - min(3, (v + 42) // 85)


def rows_to_tiles(rows, w):
    """Row-major 8x8 tiles from rows of color indexes (BG tile PNGs)."""
    out = bytearray()
    for ty in range(len(rows) // 8):
        for tx in range(w // 8):
            for r in range(8):
                lo = hi = 0
                for x in range(8):
                    c = rows[ty * 8 + r][tx * 8 + x]
                    lo = lo << 1 | (c & 1)
                    hi = hi << 1 | (c >> 1)
                out += bytes([lo, hi])
    return bytes(out)


def tiles_to_grid(data, width):
    """2bpp tiles -> rows of color indexes, `width` tiles per row."""
    n = len(data) // 16
    h = (n + width - 1) // width
    rows = [[0] * (width * 8) for _ in range(h * 8)]
    for t in range(n):
        x0, y0 = (t % width) * 8, (t // width) * 8
        for r in range(8):
            lo, hi = data[t * 16 + 2 * r], data[t * 16 + 2 * r + 1]
            for x in range(8):
                rows[y0 + r][x0 + x] = ((hi >> (7 - x)) & 1) << 1 | ((lo >> (7 - x)) & 1)
    return rows


def bg_png_to_2bpp(path):
    w, h, rows = read_png(path)
    return rows_to_tiles([[gray_index(p) for p in row] for row in rows], w)


def png_to_2bpp(path):
    w, h, rows = read_png(path)
    if h != 16 or w % 8:
        raise ValueError("%s: frame PNGs must be 16 pixels tall and a multiple of 8 wide" % path)
    out = bytearray()
    for col in range(w // 8):
        for half in range(2):
            for r in range(8):
                lo = hi = 0
                for x in range(8):
                    c = gray_index(rows[half * 8 + r][col * 8 + x])
                    lo = lo << 1 | (c & 1)
                    hi = hi << 1 | (c >> 1)
                out += bytes([lo, hi])
    return bytes(out)


# ------------------------------------------------------------------- frames
def frames(rom):
    """Yields (header address, tiles addr, sprites addr, tile count, bank)."""
    for (bank, start, count) in hints.FRAME_TABLES:
        for k in range(count):
            a = start + 6 * k
            h = rom[off(bank, a):off(bank, a) + 6]
            yield a, h[0] | h[1] << 8, h[2] | h[3] << 8, h[4], h[5]


def frame_png_path(gbank, tiles):
    return os.path.join("gfx", "frames", "%02x" % gbank, "%04x.png" % tiles)


def extract(rom, force=False):
    written = kept = 0
    for (_, tiles, spr, n, gb) in frames(rom):
        if n == 0:
            continue
        path = os.path.join(ROOT, frame_png_path(gb, tiles))
        if os.path.exists(path) and not force:
            kept += 1
            continue
        o = off(gb, tiles)
        w, rows = tiles_to_rows(rom[o:o + n * 16])
        write_png(path, w, 16, rows)
        written += 1
    # front-end sprites (tools/feanim.py), stored like frames: 8x16 sprites side by side
    from feanim import decode as fe_decode
    for (gb, a), ln in fe_decode(rom)["tiles"].items():
        path = os.path.join(ROOT, frame_png_path(gb, a))
        if os.path.exists(path) and not force:
            kept += 1
            continue
        o = off(gb, a)
        w, rows = tiles_to_rows(rom[o:o + ln])
        write_png(path, w, 16, rows)
        written += 1
    # Funky's Fishing sprite tiles (tools/fishanim.py), stored the same way
    from fishanim import decode as fish_decode, BANK as FISH_BANK
    for a, ln in fish_decode(rom)["tiles"].items():
        path = os.path.join(ROOT, frame_png_path(FISH_BANK, a))
        if os.path.exists(path) and not force:
            kept += 1
            continue
        o = off(FISH_BANK, a)
        w, rows = tiles_to_rows(rom[o:o + ln])
        write_png(path, w, 16, rows)
        written += 1
    print("frame PNGs: %d written, %d already present" % (written, kept))
    # level map layers, decompressed (packed again by the Makefile)
    from backgrounds import map_streams, map_headers
    from lzcomp import decompress
    written = kept = 0
    for (b, a), rel in map_streams(rom).items():
        path = os.path.join(ROOT, rel)
        if os.path.exists(path) and not force:
            kept += 1
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "wb").write(decompress(rom, off(b, a))[0])
        written += 1
    print("map layers: %d written, %d already present" % (written, kept))
    # level block and terrain banks, in natural order (tools/leveldata.py)
    from leveldata import from_rom
    written = kept = 0
    seen = set()
    for _, (hdr, _) in map_headers(rom).items():
        for b, kind in ((hdr["blocks"], "blocks"), (hdr["blocks"] + 1, "blocks"), (hdr["terrain"], "terrain")):
            path = os.path.join(ROOT, "data", kind, "%02x.bin" % b)
            if path in seen:
                continue
            seen.add(path)
            if os.path.exists(path) and not force:
                kept += 1
                continue
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(from_rom(kind, rom[off(b, 0x4000):off(b, 0x8000)]))
            written += 1
    print("block and terrain banks: %d written, %d already present" % (written, kept))
    # Funky's Fishing samples as WAV files (tools/samples.py)
    from banks import samples
    from samples import to_wav
    _, _, ents, ext = samples(rom)
    written = kept = 0
    for k, (b, p, _) in enumerate(ents):
        path = os.path.join(ROOT, "data", "samples", "sample_%02x.wav" % k)
        if os.path.exists(path) and not force:
            kept += 1
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        to_wav(rom[off(b, p):off(b, p) + ext[(b, p)]], path)
        written += 1
    print("samples: %d written, %d already present" % (written, kept))
    # BG tiles (level tilesets and full screens), 16 tiles per row
    from backgrounds import bg_tile_pieces
    written = kept = 0
    for (gb, _), pieces in bg_tile_pieces(rom).items():
        for (rel, a, n, w) in pieces:
            path = os.path.join(ROOT, rel)
            if os.path.exists(path) and not force:
                kept += 1
                continue
            o = off(gb, a)
            rows = tiles_to_grid(rom[o:o + n * 16], w)
            write_png(path, w * 8, len(rows), rows)
            written += 1
    print("BG tile PNGs: %d written, %d already present" % (written, kept))


GRAY_PREVIEW = [(0xE8, 0xF0, 0xE8), (0xA8, 0xB8, 0xA8), (0x58, 0x68, 0x58), (0x10, 0x18, 0x10)]
BACKDROP = (0xE8, 0xF0, 0xE8)


def preview(rom, outdir, colored=True):
    """Assemble each frame into one image using its sprite offsets, in its
    object palette where tools/frame_palettes.py can work it out. Also
    writes index.csv: file, frame header, palette, how it was found."""
    count = 0
    fp = None
    if colored:
        from frame_palettes import FramePalettes
        fp = FramePalettes(rom)
    index = ["file,frame_header,palette,source"]
    for (a, tiles, spr, n, gb) in frames(rom):
        if n == 0:
            continue
        pal, how = GRAY_PREVIEW, "none"
        pid = None
        if fp is not None:
            pid, inferred = fp.palette_of(a)
            if pid is not None:
                pal = [BACKDROP] + fp.colors(pid)[1:]
                how = "inferred" if inferred else "object"
        name = "%02x_%04x.png" % (gb, tiles)
        index.append("%s,$%04x,%s,%s" % (name, a, "" if pid is None else "%d" % pid, how))
        o = off(gb, tiles)
        _, strip = tiles_to_rows(rom[o:o + n * 16])
        so = off(gb, spr)
        x = y = 0
        pos = []
        for k in range(n // 2):
            dx, dy = rom[so + 2 * k], rom[so + 2 * k + 1]
            x += dx - 256 if dx >= 128 else dx
            y += dy - 256 if dy >= 128 else dy
            pos.append((x, y))
        x0 = min(p[0] for p in pos)
        y0 = min(p[1] for p in pos)
        w = max(p[0] for p in pos) - x0 + 8
        h = max(p[1] for p in pos) - y0 + 16
        canvas = [[0] * w for _ in range(h)]
        for k, (px, py) in enumerate(pos):
            for r in range(16):
                for c in range(8):
                    v = strip[r][k * 8 + c]
                    if v:
                        canvas[py - y0 + r][px - x0 + c] = v
        write_png(os.path.join(outdir, name), w, h, canvas, pal)
        count += 1
    with open(os.path.join(outdir, "index.csv"), "w") as f:
        f.write("\n".join(index) + "\n")
    print("wrote %d previews to %s" % (count, outdir))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    cmd = args[0]
    if cmd == "png2bpp":
        open(args[2], "wb").write(png_to_2bpp(args[1]))
        return
    rom_path = args[1] if len(args) > 1 else os.path.join(ROOT, "baserom.gbc")
    rom = open(rom_path, "rb").read()
    if cmd == "extract":
        extract(rom, "--force" in sys.argv)
    elif cmd == "preview":
        preview(rom, args[2] if len(args) > 2 else os.path.join(ROOT, "gfx", "preview"))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
