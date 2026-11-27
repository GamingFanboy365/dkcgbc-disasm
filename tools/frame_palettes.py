#!/usr/bin/env python3
"""Work out which object palette each sprite frame is drawn with.

Frames carry no palette; objects do (OBJ_PALETTE). For every object
initialiser list that sets OBJ_PALETTE, this collects the animations the
object can play: the one in the list itself, plus every animation stored
into OBJ_ANIM by code reachable from its OBJ_HANDLER (within that bank,
following handler changes). Every frame those animations show gets the
palette. Frames reached by several objects take the most common palette.

Used by tools/gfx.py preview; run directly for a summary.
"""
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_trace import make  # noqa: E402
from tracer import BANK_SIZE, off  # noqa: E402

OBJ_BANK, OBJ_HANDLER, OBJ_FRAME, OBJ_ANIM, OBJ_PALETTE = 0x01, 0x02, 0x20, 0x22, 0x2A


class FramePalettes:
    def __init__(self, rom, tracer=None):
        self.rom = rom
        self.t = tracer or make(rom)
        t = self.t
        # animation entries in order, to walk scripts
        self.anim_next = {}
        for o, item in t.data.items():
            if item[0] != "anim":
                continue
            bank = item[1]
            for ent in item[2]:
                self.anim_next[off(bank, ent[0])] = (bank, ent)
        self.lohi = {lo: (tb, target) for (lo, hi, tb, target) in t.lohi}
        self.votes = defaultdict(Counter)   # frame header offset -> palette votes
        self.sources = defaultdict(set)     # frame header offset -> init lists
        self._run()

    def anim_frames(self, ptr):
        """Frame header offsets an animation starting at ptr can show."""
        t = self.t
        seen, frames = set(), set()
        todo = [off(t.anim_bank, ptr)]
        while todo:
            o = todo.pop()
            while o in self.anim_next and o not in seen:
                seen.add(o)
                bank, ent = self.anim_next[o]
                if ent[1] == "frame":
                    frames.add(off(t.frame_bank, ent[2]))
                    o += 2
                    continue
                c, w = ent[2], ent[4]
                if c == 0:
                    todo.append(off(bank, w))
                    break
                o += 4 if w is not None else 2
        return frames

    def handler_anims(self, bank, addr):
        """Animations stored into OBJ_ANIM by code reachable from a handler."""
        t = self.t
        anims = set()
        start = off(bank, addr)
        seen = set()
        todo = [start]
        while todo:
            o = todo.pop()
            while o in t.insns and o not in seen:
                seen.add(o)
                i = t.insns[o]
                if o in self.lohi:
                    tb, target = self.lohi[o]
                    if tb == t.anim_bank:
                        anims.add(target)
                    elif tb == bank and 0x4000 <= target < 0x8000:
                        todo.append(off(bank, target))  # new OBJ_HANDLER
                if i.flow in ("jp", "jpc", "jr", "jrc", "call", "callc") and \
                        i.target is not None and 0x4000 <= i.target < 0x8000:
                    todo.append(off(bank, i.target))
                if i.flow in ("jp", "jr", "ret", "jphl"):
                    break
                o += i.length
        return anims

    def list_fields(self, o, depth=0):
        """The fields an initialiser list sets, with the lists it includes
        applied first at their place (as ApplyObjInit does)."""
        item = self.t.data.get(o)
        fields = {}
        if not item or item[0] != "objinit" or depth > 10:
            return fields
        for e in item[2]:
            if e[0] == "byte":
                fields[e[1]] = e[2]
            elif e[0] == "word":
                fields[e[1]] = e[2] & 0xFF
                fields[e[1] + 1] = e[2] >> 8
            elif e[0] == "include" and e[1] < 0x8000:
                fields.update(self.list_fields(off(0 if e[1] < 0x4000 else item[1], e[1]), depth + 1))
        return fields

    def _run(self):
        t = self.t
        for o, item in t.data.items():
            if item[0] != "objinit":
                continue
            fields = self.list_fields(o)
            if OBJ_PALETTE not in fields:
                continue
            pal = fields[OBJ_PALETTE]
            anims = set()
            if OBJ_ANIM in fields and OBJ_ANIM + 1 in fields:
                anims.add(fields[OBJ_ANIM] | fields[OBJ_ANIM + 1] << 8)
            if OBJ_HANDLER in fields and OBJ_HANDLER + 1 in fields:
                h = fields[OBJ_HANDLER] | fields[OBJ_HANDLER + 1] << 8
                hb = fields.get(OBJ_BANK, item[1])
                if 0x4000 <= h < 0x8000 and hb:
                    anims |= self.handler_anims(hb, h)
            frames = set()
            for a in anims:
                frames |= self.anim_frames(a)
            if OBJ_FRAME in fields and OBJ_FRAME + 1 in fields:
                frames.add(off(t.frame_bank, fields[OBJ_FRAME] | fields[OBJ_FRAME + 1] << 8))
            for f in frames:
                self.votes[f][pal] += 1
                self.sources[f].add(o)

    def infer(self):
        """Guess palettes for scripts with no known palette: scripts for one
        object type sit together in bank $04, so a script between two
        scripts with the same palette most likely shares it. Fills
        self.inferred (frame offset -> palette)."""
        t = self.t
        bank = t.anim_bank
        starts = sorted(o for o, pfx in t.data_labels.items()
                        if pfx == "Anim" and o // BANK_SIZE == bank)
        scripts = []  # (start offset, frame offsets, palette or None)
        for k, st in enumerate(starts):
            end = starts[k + 1] if k + 1 < len(starts) else None
            frames = []
            o = st
            while o in self.anim_next and (end is None or o < end):
                _, ent = self.anim_next[o]
                if ent[1] == "frame":
                    frames.append(off(t.frame_bank, ent[2]))
                    o += 2
                else:
                    o += 4 if ent[4] is not None else 2
            votes = Counter()
            for f in frames:
                votes.update(self.votes.get(f, {}))
            scripts.append((st, frames, votes.most_common(1)[0][0] if votes else None))
        self.inferred = {}
        known = [k for k, s_ in enumerate(scripts) if s_[2] is not None]
        for a, b in zip(known, known[1:]):
            if scripts[a][2] != scripts[b][2]:
                continue
            for k in range(a + 1, b):
                for f in scripts[k][1]:
                    if f not in self.votes:
                        self.inferred[f] = scripts[a][2]
        return self.inferred

    def palette_of(self, header_addr):
        """(palette ID, inferred?) for the frame header at header_addr in
        bank $20, or (None, False)."""
        o = off(self.t.frame_bank, header_addr)
        v = self.votes.get(o)
        if v:
            return v.most_common(1)[0][0], False
        inf = getattr(self, "inferred", None)
        if inf is None:
            inf = self.infer()
        if o in inf:
            return inf[o], True
        return None, False

    def colors(self, pal_id):
        """The 4 colors of an object palette as (r, g, b) 0-255."""
        pb, (base, _) = self.t.palette_bank, (0x4000, 64)
        o = off(pb, base + 8 * pal_id)
        out = []
        for c in range(4):
            v = self.rom[o + 2 * c] | self.rom[o + 2 * c + 1] << 8
            out.append(tuple((x << 3 | x >> 2) for x in (v & 31, v >> 5 & 31, v >> 10 & 31)))
        return out


if __name__ == "__main__":
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    fp = FramePalettes(rom)
    total = len(fp.t.frame_headers) - 1
    print("frames with a palette: %d of %d" % (len(fp.votes), total))
    print("frames with conflicting palettes: %d" % sum(1 for v in fp.votes.values() if len(v) > 1))
    print("frames with an inferred palette: %d" % len(fp.infer()))
