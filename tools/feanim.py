"""The front end's sprite animation table ($F0:5A24, drawn by Func_f0_4fa8).

47 entries of 4 bytes: a type, 0, and a pointer to an array of records,
indexed by the variant number the caller puts in [$ff82]. A record is

  sprite count, tile bank, tile address (big-endian), layout (big-endian)
  [, attribute list (big-endian)]               types 2-4 only

Types: 0 relative layout (dx, dy per sprite, signed, from the previous
one), 1 absolute layout (x, y), 2 relative + attributes, 3 absolute +
attributes, 4 relative with 8x8 sprites + attributes. The sprites are 8x16
except for type 4; the attribute list holds one byte per sprite, added to
its OAM attributes (Func_f0_517f).

  python3 tools/feanim.py [baserom.gbc]   prints the decoded table
"""
import sys

BANK, TABLE, COUNT, END = 0xF0, 0x5A24, 47, 0x6AD5
TYPE_NAMES = {0: "relative", 1: "absolute", 2: "relative+attr", 3: "absolute+attr", 4: "relative 8x8+attr"}
# animations with a known purpose (see docs/unused.md)
NAMES = {2: "SpriteAnim02_FunkyBomberTitle", 3: "SpriteAnim03_CandyKlashTitle", 7: "SpriteAnim07_ComingSoon"}
TILE_NAMES = {(0xF6, 0x54E0): "FunkyBomberTitle", (0xF6, 0x5620): "CandyKlashTitle",
              (0xF6, 0x5760): "CandyKlashTitle_French", (0xF6, 0x58A0): "FunkyBomberTitle_French",
              (0xF6, 0x59E0): "CandyKlashTitle_German", (0xF6, 0x5B20): "CandyKlashTitle_Italian",
              (0xF6, 0x5D00): "ComingSoonQ3"}


def off(bank, addr):
    return bank * 0x4000 + addr - 0x4000


def decode(rom):
    b = lambda a: rom[off(BANK, a)]  # noqa: E731
    ents = [(k, b(TABLE + 4 * k), b(TABLE + 4 * k + 2) | b(TABLE + 4 * k + 3) << 8) for k in range(COUNT)]
    starts = sorted(set(p for _, _, p in ents))
    size = lambda t: 6 if t < 2 else 8  # noqa: E731
    recs = {}
    for k, t, p in ents:
        nxt = min([s for s in starts if s > p] + [END])
        rs, a = [], p
        while a + size(t) <= nxt:
            r = rom[off(BANK, a):off(BANK, a) + size(t)]
            if r[0] == 0 or not 0xF0 <= r[1] <= 0xFF:
                break
            rs.append((a, tuple(r)))
            a += size(t)
        recs[k] = rs
    greedy = recs

    def pointers(recs):
        layouts, attrs = {}, {}
        for k, t, p in ents:
            for a, r in recs[k]:
                la = r[4] << 8 | r[5]
                layouts[la] = (max(layouts.get(la, (0, t))[0], r[0]), t)
                if t >= 2:
                    aa = r[6] << 8 | r[7]
                    attrs[aa] = max(attrs.get(aa, 0), r[0])
        return layouts, attrs

    # a record list stops where a layout or attribute list begins; repeat
    # until no bytes of a layout are mistaken for records
    recs = greedy
    for _ in range(10):
        layouts, attrs = pointers(recs)
        bounds = sorted(set([x for x in list(layouts) + list(attrs) if TABLE <= x < END] + starts + [END]))
        new = {}
        for k, t, p in ents:
            lim = min(x for x in bounds if x > p)
            new[k] = [(a, r) for a, r in greedy[k] if a + len(r) <= lim]
        if new == recs:
            break
        recs = new
    layouts, attrs = pointers(recs)
    # sprite tiles: one block per start address, up to the next start
    tiles = {}
    for k, t, p in ents:
        for a, r in recs[k]:
            key = (r[1], r[2] << 8 | r[3])
            n = r[0] * (16 if t == 4 else 32)
            tiles[key] = max(tiles.get(key, 0), n)
    blocks = {}
    for (tb, ta), n in sorted(tiles.items()):
        nxt = [x for (bb, x) in tiles if bb == tb and x > ta]
        end = min([ta + n] + nxt)
        blocks[(tb, ta)] = end - ta
    return {"entries": ents, "records": recs, "layouts": layouts, "attrs": attrs, "tiles": blocks}


def covered(rom, d):
    """Bytes of $5A24-$6AD5 not covered by the table, records, layouts or lists."""
    cov = set(range(TABLE, TABLE + 4 * COUNT))
    for rs in d["records"].values():
        for a, r in rs:
            cov.update(range(a, a + len(r)))
    for la, (n, t) in d["layouts"].items():
        cov.update(range(la, la + 2 * n))
    for aa, n in d["attrs"].items():
        cov.update(range(aa, aa + n))
    return [a for a in range(TABLE, END) if a not in cov]


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    d = decode(rom)
    for k, t, p in d["entries"]:
        rs = d["records"][k]
        print("%2d %-18s $%04x %2d records, tiles %s" % (k, TYPE_NAMES[t], p, len(rs),
                                                         sorted(set("%02x:%04x" % (r[1], r[2] << 8 | r[3]) for _, r in rs))[:4]))
    print("uncovered:", ["$%04x" % a for a in covered(rom, d)])
    print("tile blocks:", len(d["tiles"]), "bytes:", sum(d["tiles"].values()))


if __name__ == "__main__":
    main()
