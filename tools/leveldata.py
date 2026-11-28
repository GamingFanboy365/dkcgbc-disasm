#!/usr/bin/env python3
"""Level block and terrain banks, between the ROM's layout and files in
natural order.

Block banks (LevelBlocks_BB). A level uses a pair of banks. A map cell's
block attribute (0-7) picks a set of 128 blocks: bit 2 the bank, bits 0-1 the
set within it; its block number (always even) picks the block. A block is
4x4 tiles. In the ROM the bank is 64 pages of 256 bytes: the tile of cell k
(0-15, row by row) of block n in set s is at page $40 + s + 4k, offset 2n,
and its CGB attribute at offset 2n + 1 (DrawMapArea, DrawMapArea_Vertical).
data/blocks/BB.bin holds the 512 blocks in order (set by set), each as 16
pairs of (tile, attribute): block s*128 + n starts at byte 32 * (s*128 + n).

Terrain banks (LevelTerrain_BB). A map cell's terrain byte picks one of 256
terrain types. For pixel column x (0-31) of the cell, page $40 + x, offset
type holds the ground height (bits 0-4) and flags (bit 5 and up), and page
$60 + x the second byte, OBJ_TERRAIN_B (GetTerrainUnderObject). data/terrain/BB.bin
holds the 256 types in order, each as its 32 column bytes followed by its 32
second bytes.

  python3 tools/leveldata.py blocks  in.bin out.planar    file -> ROM layout
  python3 tools/leveldata.py terrain in.bin out.planar
  python3 tools/leveldata.py -d blocks|terrain in.planar out.bin   ROM -> file
"""
import sys

SIZE = 0x4000


def _block_map():
    """file offset -> bank offset, for block banks"""
    m = [0] * SIZE
    for s in range(4):
        for n in range(128):
            for k in range(16):
                for j in range(2):
                    m[((s * 128 + n) * 16 + k) * 2 + j] = ((s + 4 * k) << 8) | (2 * n + j)
    return m


def _terrain_map():
    m = [0] * SIZE
    for t in range(256):
        for x in range(32):
            m[t * 64 + x] = (x << 8) | t
            m[t * 64 + 32 + x] = ((0x20 + x) << 8) | t
    return m


MAPS = {"blocks": _block_map, "terrain": _terrain_map}


def to_rom(kind, data):
    m = MAPS[kind]()
    out = bytearray(SIZE)
    for i, b in enumerate(data):
        out[m[i]] = b
    return bytes(out)


def from_rom(kind, bank):
    m = MAPS[kind]()
    return bytes(bank[m[i]] for i in range(SIZE))


def main():
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "-d":
        open(a[3], "wb").write(from_rom(a[1], open(a[2], "rb").read()))
    elif len(a) == 3:
        open(a[2], "wb").write(to_rom(a[0], open(a[1], "rb").read()))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
