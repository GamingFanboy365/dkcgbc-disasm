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
OBJ_TOUCH, TOUCH_BANK = 0x04, 0x09


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

    def handler_anims(self, bank, addr, follow_lists=False, touch=False):
        """Animations stored into OBJ_ANIM by code reachable from a handler.
        With follow_lists, also the animation and handler of initialiser
        lists the code applies to the same object ("ld hl, list / call
        ApplyObjInit"), as the player does when it changes form."""
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
                if follow_lists and i.op == 0x21 and i.dataref is not None:
                    nxt = t.insns.get(o + 3)
                    if nxt is not None and nxt.flow == "call" and nxt.target == 0x188B:
                        if off(*i.dataref) in getattr(self, "form_lists", ()):
                            o += i.length
                            continue  # another form's list (it sets its own palette)
                        f = self.list_fields(off(*i.dataref))
                        if OBJ_ANIM in f and OBJ_ANIM + 1 in f:
                            anims.add(f[OBJ_ANIM] | f[OBJ_ANIM + 1] << 8)
                        if OBJ_HANDLER in f and OBJ_HANDLER + 1 in f and f.get(OBJ_BANK, bank) == bank:
                            h = f[OBJ_HANDLER] | f[OBJ_HANDLER + 1] << 8
                            if 0x4000 <= h < 0x8000:
                                todo.append(off(bank, h))
                if touch and i.op == 0x01:
                    break  # "ld bc, ...": the code turns to another object
                if i.flow in ("jp", "jpc", "jr", "jrc", "call", "callc") and \
                        i.target is not None and 0x4000 <= i.target < 0x8000 and \
                        not (touch and i.flow in ("call", "callc")):
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
        included = set()
        for o, item in t.data.items():
            if item[0] == "objinit":
                for e in item[2]:
                    if e[0] == "include" and 0x4000 <= e[1] < 0x8000:
                        included.add(off(item[1], e[1]))
        for o, item in t.data.items():
            if item[0] != "objinit":
                continue
            fields = self.list_fields(o)
            if OBJ_PALETTE not in fields:
                # the lists of bank $0E are only used to set up new objects
                # (the level spawner), whose slot AllocObject has cleared:
                # palette 0, unless the list is one included by others
                if item[1] != 0x0E or o in included:
                    continue
                fields[OBJ_PALETTE] = 0
            pal = fields[OBJ_PALETTE]
            anims = set()
            if OBJ_ANIM in fields and OBJ_ANIM + 1 in fields:
                anims.add(fields[OBJ_ANIM] | fields[OBJ_ANIM + 1] << 8)
            if OBJ_HANDLER in fields and OBJ_HANDLER + 1 in fields:
                h = fields[OBJ_HANDLER] | fields[OBJ_HANDLER + 1] << 8
                hb = fields.get(OBJ_BANK, item[1])
                if 0x4000 <= h < 0x8000 and hb:
                    anims |= self.handler_anims(hb, h)
            if OBJ_TOUCH in fields and OBJ_TOUCH + 1 in fields:
                # the touch handler (bank 9) changes the animation of the
                # object it was called for: squashed, hit, collected...
                h = fields[OBJ_TOUCH] | fields[OBJ_TOUCH + 1] << 8
                if 0x4000 <= h < 0x8000:
                    anims |= self.handler_anims(TOUCH_BANK, h, touch=True)
            frames = set()
            for a in anims:
                frames |= self.anim_frames(a)
            if OBJ_FRAME in fields and OBJ_FRAME + 1 in fields:
                frames.add(off(t.frame_bank, fields[OBJ_FRAME] | fields[OBJ_FRAME + 1] << 8))
            for f in frames:
                self.votes[f][pal] += 1
                self.sources[f].add(o)
        self._player_palettes()
        self._barrel_palettes()
        # The pause screen (Func_00_2a63) draws a frame of FrameTable_00_2a9e
        # straight into OAM with attribute 0: hardware slot 0, which every
        # level's preload list fills with palette 0 (seen in mGBA, paused).
        item = t.data.get(off(0, 0x2A9E))
        if item and item[0] == "frameptrs":
            for a in item[2]:
                self.votes[off(t.frame_bank, a)][0] += 1

    # Barrels pick their animations from a table by type (OBJ_VAR_2E):
    # 4 words per type at $09:6CAC; Barrel_Touch reads $6CAE + 8 * type and
    # Barrel_PutDown $6CB0 + 8 * type. A barrel's list sets its palette.
    BARREL_ANIMS, BARREL_TOUCH = (0x09, 0x6CAC), 0x6CCC

    def _barrel_palettes(self):
        t = self.t
        b, a = self.BARREL_ANIMS
        for o, item in t.data.items():
            if item[0] != "objinit":
                continue
            f = self.list_fields(o)
            if f.get(OBJ_TOUCH, 0) | f.get(OBJ_TOUCH + 1, 0) << 8 != self.BARREL_TOUCH:
                continue
            if OBJ_PALETTE not in f or 0x2E not in f:
                continue
            for k in range(4):
                p = a + 8 * f[0x2E] + 2 * k
                anim = self.rom[off(b, p)] | self.rom[off(b, p + 1)] << 8
                if 0x4000 <= anim < 0x8000:
                    for fr in self.anim_frames(anim):
                        self.votes[fr][f[OBJ_PALETTE]] += 1
                        self.sources[fr].add(o)

    def _player_palettes(self):
        """The player object's palette is set by SetPlayerPalette ($09:68a5)
        with a constant in a, just before the code applies the initialiser
        list that switches the player into a form (an animal buddy, say).
        Vote that palette for the frames of that list's handler."""
        t = self.t
        found = []
        for o, i in t.insns.items():
            if i.flow != "call" or i.target != 0x68A5 or o // BANK_SIZE != 0x09:
                continue
            prev = t.insns.get(o - 2)
            if prev is None or prev.op != 0x3E:
                continue
            pal = prev.imm if prev.imm is not None else t.rom[o - 1]
            p = o + 3
            for _ in range(8):  # the next "ld hl, list / call ApplyObjInit"
                j = t.insns.get(p)
                if j is None:
                    break
                if j.op == 0x21 and j.dataref is not None:
                    found.append((pal, off(*j.dataref)))
                    break
                p += j.length
        self.form_lists = {lo for _, lo in found}
        reached = {}
        for pal, lo in found:
            f = self.list_fields(lo)
            if OBJ_HANDLER not in f or OBJ_HANDLER + 1 not in f:
                continue
            h = f[OBJ_HANDLER] | f[OBJ_HANDLER + 1] << 8
            anims = self.handler_anims(f.get(OBJ_BANK, 0x09), h, follow_lists=True)
            if OBJ_ANIM in f and OBJ_ANIM + 1 in f:
                anims.add(f[OBJ_ANIM] | f[OBJ_ANIM + 1] << 8)
            for a in anims:
                for fr in self.anim_frames(a):
                    reached.setdefault(fr, {}).setdefault(pal, set()).add(lo)
        # the Kongs' own palettes (1, 2) are the default form; where an animal
        # form reaches the same frames through shared code, the animal wins
        for fr, pals in reached.items():
            own = {p: los for p, los in pals.items() if p not in (1, 2)} or pals
            for p, los in own.items():
                self.votes[fr][p] += len(los)
                self.sources[fr] |= los

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
            seen = self.observed()
            for f in frames:
                a = f % BANK_SIZE + 0x4000
                if a in seen:
                    votes[seen[a][0]] += 100   # what the game showed outweighs the code reading
                else:
                    votes.update(self.votes.get(f, {}))
            scripts.append((st, frames, votes.most_common(1)[0][0] if votes else None))
        self.inferred = {}
        # frames of a script whose other frames have a palette share it
        for st, frames, pal in scripts:
            if pal is not None:
                for f in frames:
                    if f not in self.votes and f % BANK_SIZE + 0x4000 not in self.observed():
                        self.inferred[f] = pal
        known = [k for k, s_ in enumerate(scripts) if s_[2] is not None]
        for a, b in zip(known, known[1:]):
            if scripts[a][2] != scripts[b][2]:
                continue
            for k in range(a + 1, b):
                for f in scripts[k][1]:
                    if f not in self.votes:
                        self.inferred[f] = scripts[a][2]
        self._infer_tables()
        # a script runs on into the next label and follows its jumps: frames
        # reached that way from a script with a palette are the same object
        seen = self.observed()
        for st, frames, pal in scripts:
            if pal is None:
                continue
            for f in self.anim_frames(st % BANK_SIZE + 0x4000):
                if f not in self.votes and f not in self.inferred and f % BANK_SIZE + 0x4000 not in seen:
                    self.inferred[f] = pal
        return self.inferred

    def _infer_tables(self):
        """Frames listed side by side in a table (the letters of a word, a
        platform at each fuel level, the player in a mine cart at each slope)
        belong to one object: a frame with no palette takes the one most of
        its neighbours have. Tables that alternate Donkey Kong and Diddy
        frames are split by column first."""
        t = self.t
        fb = t.frame_bank
        seen = self.observed()

        def known(a):
            if a in seen:
                return seen[a][0]
            v = self.votes.get(off(fb, a))
            return v.most_common(1)[0][0] if v else None

        def fill(group):
            c = Counter(p for p in map(known, group) if p is not None)
            if not c:
                return False
            pal = c.most_common(1)[0][0]
            for a in group:
                if known(a) is None and off(fb, a) not in self.inferred:
                    self.inferred[off(fb, a)] = pal
            return True

        for o, item in t.data.items():
            kind, payload = item[0], item[2]
            if kind == "frameptrs":
                cols = [payload[0::2], payload[1::2]]
                pals = [Counter(p for p in map(known, c) if p is not None).most_common(1) for c in cols]
                if all(pals) and pals[0][0][0] != pals[1][0][0]:
                    for c in cols:
                        fill(c)
                else:
                    fill(payload)
            elif kind == "framestruct":
                recs, fcols = payload
                for j in fcols:
                    fill([r[j] for r in recs])
            elif kind == "rows":
                group = [tok[2] for row in payload for tok in row[1]
                         if isinstance(tok, tuple) and tok[0] == "ref" and tok[1] == fb]
                if len(group) > 1:
                    fill(group)

    def observed(self):
        """{frame header addr: [palette, ...]} from tools/emu/observed_palettes.txt:
        what the running game used, most seen first."""
        if getattr(self, "_observed", None) is None:
            self._observed = {}
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emu", "observed_palettes.txt")
            if os.path.exists(path):
                for line in open(path):
                    if line.startswith("#") or ":" not in line:
                        continue
                    a, rest = line.split(":")
                    self._observed[int(a, 16)] = [int(x) for x in rest.split()[0::2]]
        return self._observed

    def palette_of(self, header_addr):
        """(palette ID, inferred?) for the frame header at header_addr in
        bank $20, or (None, False). A palette seen in the running game wins
        over one worked out from the code."""
        seen = self.observed().get(header_addr)
        if seen:
            return seen[0], False
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

    # Screens that preload their own palettes in a fixed order before
    # setting up their objects: (bank $0F routine, preload list in bank $80).
    # Large sprites add their per-sprite value to the object's hardware slot,
    # so on these screens the colours come from the next entries of the
    # list, not from the next palette numbers (checked in mGBA at Funky's
    # Flights: Funky's second slot holds palette 1, Donkey Kong's).
    SCREEN_PRELOADS = [(0x4001, 0x424E),   # Candy's Challenge
                       (0x40A9, 0x423C),   # Cranky's Cabin
                       (0x412E, 0x4245)]   # Funky's Flights

    def _screen_slots(self):
        """{frame offset: preload list} for frames of objects set up by the
        screens in SCREEN_PRELOADS."""
        if getattr(self, "_slots", None) is not None:
            return self._slots
        t = self.t
        self._slots = {}
        for func, plist in self.SCREEN_PRELOADS:
            item = t.data.get(off(t.palette_bank, plist))
            if not item or item[0] != "preload":
                continue
            order = item[2]
            seen, todo, lists = set(), [off(0x0F, func)], set()
            while todo:
                o = todo.pop()
                while o in t.insns and o not in seen:
                    seen.add(o)
                    i = t.insns[o]
                    if i.op == 0x21 and i.dataref is not None and i.dataref[0] == 0x0F:
                        lists.add(off(*i.dataref))
                    if i.flow in ("call", "callc", "jr", "jrc", "jp", "jpc") and i.target is not None \
                            and 0x4000 <= i.target < 0x8000:
                        todo.append(off(0x0F, i.target))
                    if i.flow in ("jp", "jr", "ret", "jphl"):
                        break
                    o += i.length
            for lo in lists:
                f = self.list_fields(lo)
                frames = set()
                if OBJ_ANIM in f and OBJ_ANIM + 1 in f:
                    frames |= self.anim_frames(f[OBJ_ANIM] | f[OBJ_ANIM + 1] << 8)
                if OBJ_FRAME in f and OBJ_FRAME + 1 in f:
                    frames.add(off(t.frame_bank, f[OBJ_FRAME] | f[OBJ_FRAME + 1] << 8))
                for fr in frames:
                    self._slots[fr] = order
        return self._slots

    def sprite_palette(self, header_addr, pal_id, add):
        """Palette a sprite of a large frame is drawn with: the object's
        palette pal_id plus the sprite's value add, counted in hardware
        slots."""
        order = self._screen_slots().get(off(self.t.frame_bank, header_addr))
        if order and pal_id in order and order.index(pal_id) + add < len(order):
            return order[order.index(pal_id) + add]
        return pal_id + add

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
