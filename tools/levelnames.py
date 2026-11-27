#!/usr/bin/env python3
"""Names for the level descriptors and entrance records in bank $04.

The level names are the game's own: the text group at $10:41CE holds them in
level-number order ("ERROR" for level 0). A level's first descriptor (the one
its LevelTable entrance uses) is named after the level; the other areas
reached from it through Entrance objects (bonus rooms, caves) are numbered
_Area1, _Area2... in address order. Areas reached from several levels, or
from none that could be followed, keep their address.

  python3 tools/levelnames.py [baserom.gbc]     prints the table
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hints  # noqa: E402

LEVEL_TABLE = 0x57B4
LEVEL_COUNT = 0x2A
NAME_GROUP = (0x10, 0x41CE)
# text number of the levels that are not in the group at their own number:
# Necky Nutmare (added in this version) and the seven boss levels. Between
# them the group holds the six world names, the Kongs' places and the names
# of Candy's challenges.
TEXT_INDEX = {0x22: 0x38, 0x23: 0x28, 0x24: 0x29, 0x25: 0x2A, 0x26: 0x2B, 0x27: 0x2C, 0x28: 0x2D, 0x29: 0x2E}
# handlers of the objects whose OBJ_VAR_2E-31 hold the entrance to go to and
# the entrance to come back to (Entrance, BreakableWall, Entrance_BananaHoard)
ENTRANCE_HANDLERS = {(0x08, 0x55FA), (0x08, 0x55A0), (0x08, 0x5665)}
# animal bonus levels (Entrances_0a_58c0), by OBJ_VAR_2F of the token
ANIMAL_TABLE = (0x0A, 0x58C0, ("Rambi", "Expresso", "Enguarde", "Winky"))


def off(b, a):
    return b * 0x4000 + (a - 0x4000 if a >= 0x4000 else a)


def word(rom, b, a):
    return rom[off(b, a)] | rom[off(b, a + 1)] << 8


def camel(text):
    text = text.replace("&", " And ").replace("'", "").replace("-", " ").replace(".", "")
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"\s+", text) if w)


def level_names(rom):
    """Level number -> name as the game spells it."""
    b, a = NAME_GROUP
    names = {}
    for k in range(1, LEVEL_COUNT):
        p = word(rom, b, a + 2 * TEXT_INDEX.get(k, k))
        s = bytearray()
        while rom[off(b, p)]:
            c = rom[off(b, p)]
            s.append(0x20 if c == 0x0D else c)
            p += 1
        names[k] = re.sub(r"\s+", " ", bytes(c for c in s if c >= 0x20).decode("ascii")).strip()
    return names


def list_fields(rom, bank, addr, depth=0):
    """Fields set by an object initialiser list (includes applied in place)."""
    f = {}
    p = addr
    while depth < 8:
        c = rom[off(bank, p)]
        if c < 0x40:
            f[c] = rom[off(bank, p + 1)]
            p += 2
        elif c < 0x80:
            f[c & 0x3F] = rom[off(bank, p + 1)]
            f[(c & 0x3F) + 1] = rom[off(bank, p + 2)]
            p += 3
        elif c == 0x80:
            t = word(rom, bank, p + 1)
            f.update(list_fields(rom, bank if t >= 0x4000 else 0, t, depth + 1))
            p += 3
        else:
            break
    return f


def tables(rom):
    """(desc names, entrance names): address in bank $04 -> label."""
    e0, e1 = hints.LEVELS["entrances"]
    d0, d1 = hints.LEVELS["descriptors"]
    names = level_names(rom)

    def is_entrance(a):
        return e0 <= a < e1 and (a - e0) % 8 == 0

    def exits(desc):
        """Entrances the objects of an area lead to."""
        r = rom[off(4, desc):off(4, desc) + 12]
        o = off(r[9], r[7] | r[8] << 8)
        out = set()
        while rom[o]:
            if rom[o + 1] & 0x30 == 0x30:
                f = list_fields(rom, 0x0E, rom[o + 6] | rom[o + 7] << 8)
                if (f.get(1), f.get(2, 0) | f.get(3, 0) << 8) in ENTRANCE_HANDLERS:
                    for k in (0x2E, 0x30):
                        a = f.get(k, 0) | f.get(k + 1, 0) << 8
                        if is_entrance(a):
                            out.add(a)
            o += 8
        return out

    reach = {}  # desc -> levels that reach it
    main = {}
    for lv in range(1, LEVEL_COUNT):
        todo = [word(rom, 4, LEVEL_TABLE + 4 * lv + k) for k in (0, 2)]
        todo = [a for a in todo if a]
        main[lv] = word(rom, 4, todo[0])
        seen = set()
        while todo:
            d = word(rom, 4, todo.pop())
            if d in seen or not d0 <= d < d1:
                continue
            seen.add(d)
            reach.setdefault(d, set()).add(lv)
            todo.extend(exits(d))
    desc = {}
    for lv, d in main.items():
        desc[d] = camel(names[lv])
    count = {}
    for d in sorted(reach):
        if d not in desc and len(reach[d]) == 1:
            lv = next(iter(reach[d]))
            count[lv] = count.get(lv, 0) + 1
            desc[d] = "%s_Area%d" % (camel(names[lv]), count[lv])
    b, a, animals = ANIMAL_TABLE
    for k, n in enumerate(animals):
        d = word(rom, 4, word(rom, b, a + 2 * k))
        if d not in desc or "_Area" in desc[d]:
            desc[d] = n + "Bonus"
    ent = {}
    per = {}
    for a in range(e0, e1, 8):
        d = word(rom, 4, a)
        if d in desc:
            k = per.get(d, 0)
            per[d] = k + 1
            ent[a] = "LevelEntrance_%s_%d" % (desc[d], k)
    return {d: "LevelDesc_" + n for d, n in desc.items()}, ent, names, reach


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    desc, ent, names, reach = tables(rom)
    d0, d1 = hints.LEVELS["descriptors"]
    for d in range(d0, d1, 12):
        print("%04x %-40s %s" % (d, desc.get(d, "-"), ",".join("%02x" % x for x in sorted(reach.get(d, ())))))
    print(len(desc), "descriptors named of", (d1 - d0) // 12, ";", len(ent), "entrances named")


if __name__ == "__main__":
    main()
