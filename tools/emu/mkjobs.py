#!/usr/bin/env python3
"""Write the job list for harvest.lua: one line per sample point,

  descriptor  entrance-byte  x  y  entrance-byte  [touch-handler  list]

A point is each level's own start plus one per 256x192-pixel cell that holds
objects of its object list. The optional last two fields make the harvester
apply an initialiser list (bank $09) to the live object with that touch
handler, 150 frames in; the boss lines use it to show the hit and defeat
frames, which no idle run reaches.

  python3 tools/emu/mkjobs.py [baserom.gbc] > jobs.txt
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import backgrounds as bg  # noqa: E402
import hints  # noqa: E402

# descriptor, boss touch handler, lists its touch handler applies to that boss
BOSS_LISTS = [(0x64BC, 0x4712, (0x47A4, 0x47BF, 0x47D8)), (0x64E0, 0x4712, (0x47A4, 0x47BF, 0x47D8)),
              (0x64C8, 0x4712, (0x47B2, 0x47CD, 0x47E4)), (0x64F8, 0x4712, (0x47B2, 0x47CD, 0x47E4)),
              (0x64D4, 0x47EF, (0x4840, 0x485E)), (0x6504, 0x487A, (0x4918, 0x4927, 0x4934))]


def off(b, a):
    return b * 0x4000 + a - 0x4000


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    descs = dict(bg.level_descriptors(rom))
    e0, e1 = hints.LEVELS["entrances"]
    ent = {}
    for a in range(e0, e1, 8):
        r = rom[off(4, a):off(4, a) + 8]
        ent.setdefault(r[0] | r[1] << 8, []).append((r[2], r[3] | r[4] << 8, r[5] | r[6] << 8, r[7]))
    first = {}
    for d, es in sorted(ent.items()):
        r = descs[d]
        o = off(r[9], r[7] | r[8] << 8)
        c444, ex, ey, v3a = es[0]
        first[d] = "%04x %02x %04x %04x %02x" % (d, c444, ex, ey, v3a)
        print(first[d])
        seen = set()
        while rom[o]:
            x, y = rom[o + 2] | rom[o + 3] << 8, rom[o + 4] | rom[o + 5] << 8
            o += 8
            if y >= 0x8000:
                y = 0x40
            if (x // 0x100, y // 0xC0) in seen:
                continue
            seen.add((x // 0x100, y // 0xC0))
            print("%04x %02x %04x %04x %02x" % (d, c444, (x // 0x100) * 0x100 + 0x80, y, v3a))
    for d, th, lists in BOSS_LISTS:
        for lst in lists:
            print("%s %04x %04x" % (first[d], th, lst))


if __name__ == "__main__":
    main()
