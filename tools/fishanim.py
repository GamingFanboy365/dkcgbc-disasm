#!/usr/bin/env python3
"""Funky's Fishing's sprite animations (bank $52, drawn by Func_52_4097).

FishingAnimTable ($52:41EE) holds 21 pointers. An animation starts with 4
bytes: a number, 8 (or 12, 20), the last frame's index and the bank ($52).
Then come that many frames + 1, each 6 bytes:

  sprite count, 0, tile pointer, layout pointer

The tiles are 32 bytes per 8x16 sprite, copied to VRAM when the frame is
shown. The layout has a (dx, dy) byte pair per sprite, like the main game's
sprite offset lists.

Animations 10 and 11 each have one more layout and tile block after their
last frame (9 sprites at $54F0/$5528 and $58A8/$58E0) that no frame points
to: a seventh frame the headers leave out.

  python3 tools/fishanim.py [baserom.gbc]
"""
import sys

BANK, TABLE, COUNT = 0x52, 0x41EE, 21
UNREFERENCED = [(0x54F0, 0x5528, 9), (0x58A8, 0x58E0, 9)]  # layout, tiles, sprites


def off(bank, addr):
    return bank * 0x4000 + addr - 0x4000


def decode(rom):
    b = lambda a: rom[off(BANK, a)]  # noqa: E731
    w = lambda a: b(a) | b(a + 1) << 8  # noqa: E731
    table = [w(TABLE + 2 * k) for k in range(COUNT)]
    anims, layouts, tiles = {}, {}, {}
    for a in sorted(set(table)):
        hdr = [b(a + i) for i in range(4)]
        frames = []
        for f in range(hdr[2] + 1):
            p = a + 4 + 6 * f
            n, x, tp, lp = b(p), b(p + 1), w(p + 2), w(p + 4)
            frames.append((n, x, tp, lp))
            tiles[tp] = max(tiles.get(tp, 0), 32 * n)
            layouts[lp] = max(layouts.get(lp, 0), 2 * n)
        anims[a] = (hdr, frames)
    for lp, tp, n in UNREFERENCED:
        layouts[lp] = 2 * n
        tiles[tp] = 32 * n
    return {"table": table, "anims": anims, "layouts": layouts, "tiles": tiles}


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    d = decode(rom)
    for k, a in enumerate(d["table"]):
        hdr, frames = d["anims"][a]
        print("%2d $%04x %s %d frames" % (k, a, hdr, len(frames)))
    print("layouts:", len(d["layouts"]), "tile blocks:", len(d["tiles"]), "bytes:", sum(d["tiles"].values()))


if __name__ == "__main__":
    main()
