#!/usr/bin/env python3
"""Turn harvest.lua logs into the two data files kept in this folder.

  observed_palettes.txt   palette each sprite frame was drawn with
  observed_handlers.txt   every routine seen as an object's handler: which
                          objects ran it, which handler came before it and
                          which after

  python3 tools/emu/analyze.py LOGDIR [baserom.gbc]

Needs dkc.sym (build the ROM first). An object's palette number is its
OBJ_PALETTE when that is set and matches the colours of its hardware slot;
otherwise the slot's colours are looked up in the palette table in bank $80
(ignored when more than one palette has those colours).
"""
import glob
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, ".."))


def load(logdir):
    obs = []
    for f in sorted(glob.glob(os.path.join(logdir, "*.log"))):
        job = pal = None
        for line in open(f):
            p = line.split()
            if not p:
                continue
            if p[0] == "J":
                job, pal = (f, int(p[1])), None
            elif p[0] == "P":
                pal = bytes.fromhex(p[2])
            elif p[0] == "O" and len(p) == 13:
                obs.append(dict(job=job, t=int(p[1]), slot=int(p[2]), bank=int(p[3], 16), h=int(p[4], 16),
                                th=int(p[5], 16), attr=int(p[6], 16), pf=int(p[7], 16), fr=int(p[8], 16),
                                an=int(p[9], 16), sp=int(p[10], 16), sf=int(p[11], 16), ip=int(p[12], 16), pal=pal))
    return obs


def palettes(obs, rom):
    table = [rom[0x80 * 0x4000 + 8 * i:0x80 * 0x4000 + 8 * i + 8] for i in range(128)]
    truth, cache = defaultdict(Counter), {}
    for o in obs:
        if o["pal"] is None or not 0x4000 <= o["fr"] < 0x8000:
            continue
        slot = o["attr"] & 7
        k = o["pal"][8 * slot + 2:8 * slot + 8]
        if k not in cache:
            cache[k] = [i for i, p in enumerate(table) if p[2:] == k]
        ids = cache[k]
        if o["pf"] and o["pf"] in ids:
            truth[o["fr"]][o["pf"]] += 1
        elif len(ids) == 1:
            truth[o["fr"]][ids[0]] += 1
    return truth


def handlers(obs, sym, list_handler):
    def nm(h):
        return sym.get(h, "%02x:%04x" % h)
    inst = defaultdict(list)
    for o in obs:
        inst[(o["job"], o["slot"])].append(o)
    owners, preds, succ = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for lst in inst.values():
        lst.sort(key=lambda o: o["t"])
        seg, cur = [], [lst[0]]
        for o in lst[1:]:  # a slot is reused when its spawn entry changes
            if (o["sp"], o["ip"]) != (cur[-1]["sp"], cur[-1]["ip"]):
                seg.append(cur)
                cur = [o]
            else:
                cur.append(o)
        seg.append(cur)
        for s in seg:
            o0 = s[0]
            if o0["slot"] == 0:
                root = "Player"
            elif o0["sp"] and o0["sf"] & 0x30 == 0x30:
                root = nm(list_handler.get(o0["ip"], (0x0E, o0["ip"])))
            else:
                root = None  # spawned by code: owner unknown, transitions still count
            prev = None
            for o in s:
                h = (o["bank"], o["h"])
                if root:
                    owners[h][root] += 1
                if prev is not None and prev != h:
                    preds[h][nm(prev)] += 1
                    succ[prev][nm(h)] += 1
                prev = h
    return owners, preds, succ


def main():
    logdir = sys.argv[1]
    rom = open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "baserom.gbc"), "rb").read()
    obs = load(logdir)
    truth = palettes(obs, rom)
    with open(os.path.join(HERE, "observed_palettes.txt"), "w") as f:
        f.write("# Object palettes seen in the running game, per sprite frame header (bank $20).\n"
                "# Written by tools/emu/analyze.py from an mGBA harvest of every level; read by\n"
                "# tools/frame_palettes.py. frame: palette number x times seen, most seen first.\n")
        for fr in sorted(truth):
            f.write("%04x: %s\n" % (fr, " ".join("%d x%d" % pn for pn in truth[fr].most_common())))
    sym = {}
    for line in open(os.path.join(ROOT, "dkc.sym")):
        m = re.match(r"([0-9a-f]{2}):([0-9a-f]{4}) (\S+)", line)
        if m and "." not in m.group(3):
            sym[(int(m.group(1), 16), int(m.group(2), 16))] = m.group(3)
    from frame_palettes import FramePalettes
    from tracer import off
    fp = FramePalettes(rom)
    list_handler = {}
    for o, item in fp.t.data.items():
        if item[0] == "objinit" and o // 0x4000 == 0x0E:
            fl = fp.list_fields(o)
            if 1 in fl and 2 in fl and 3 in fl:
                list_handler[o % 0x4000 + 0x4000] = (fl[1], fl[2] | fl[3] << 8)
    del off
    owners, preds, succ = handlers(obs, sym, list_handler)
    with open(os.path.join(HERE, "observed_handlers.txt"), "w") as f:
        f.write("# Routines seen as an object's handler in the running game (tools/emu/analyze.py).\n"
                "# handler | objects that ran it (by the handler their list starts with) | came from | went to\n")
        for h in sorted(set(owners) | set(preds) | set(succ)):
            if h[0] not in (0x08, 0x09, 0x0A) or not 0x4000 <= h[1] < 0x8000:
                continue
            f.write("%s | %s | %s | %s\n" % (sym.get(h, "%02x:%04x" % h),
                                           ", ".join(x for x, _ in owners[h].most_common(4)),
                                           ", ".join(x for x, _ in preds[h].most_common(4)),
                                           ", ".join(x for x, _ in succ[h].most_common(4))))
    print("frames with a palette: %d; handlers: %d" % (len(truth), len(set(owners) | set(preds) | set(succ))))


if __name__ == "__main__":
    main()
