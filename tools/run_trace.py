import sys
import os
import struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracer import Tracer, Speculator, off
import hints

def load(path):
    return open(path, "rb").read()

def parse_backgrounds(t, rom):
    """Level map headers and data, BG tiles, full screens and the flow
    script (see tools/backgrounds.py)."""
    import backgrounds as bg
    for h, (hdr, _) in sorted(bg.map_headers(rom).items()):
        t._claim(0x04, h, hdr["length"], "mapheader", hdr, "MapHeader")
        for p in hdr["layers"]:
            n = bg.decompress(rom, hdr["map_bank"], p)[1]
            t._claim(hdr["map_bank"], p, n, "incbin", None, "LevelMap")
        for b, name in ((hdr["blocks"], "LevelBlocks"), (hdr["blocks"] + 1, "LevelBlocks"),
                        (hdr["terrain"], "LevelTerrain")):
            t._claim(b, 0x4000, 0x4000, "incbin", None, "=%s_%02x" % (name, b))
    for (b, a), pieces in sorted(bg.bg_tile_pieces(rom).items()):
        t._claim(b, a, sum(p[2] for p in pieces) * 16, "bgtiles", pieces, "BGTiles")
    for (b, p), rec in sorted(bg.screen_records(rom).items()):
        t._claim(b, p, 6, "screen", rec, "Screen")
        # 8 BG palettes; the loader copies 128 bytes, so the "OBJ palettes" it
        # also loads are whatever follows (unused by these screens)
        t._claim(b, rec["palettes"], 64, "palette", 8, "ScreenPalettes")
        t._claim(b, rec["map"], 720, "screenmap", None, "ScreenMap")
    wb, wt, wn = hints.WORLD_MAPS
    t._claim(wb, wt, 2 * wn, "ptrtable", [rom[off(wb, wt + 2 * k)] | rom[off(wb, wt + 2 * k) + 1] << 8 for k in range(wn)],
             "=WorldMapTable")
    for wm in bg.world_maps(rom):
        t._claim(wb, wm["addr"], 13, "worldmap", wm, "WorldMap")
        t._claim(0x0F, wm["map"], 1 + 36 * wm["width"], "worldtiles", wm["width"], "WorldTileMap")
        t._claim(0x0F, wm["palettes"], 64, "palette", 8, "WorldPalettes")
    # front-end picture table
    pt = hints.PICTURES
    recs = bg.pictures(rom)
    t._claim(pt["bank"], pt["table"], 9 * pt["count"], "pictable", recs, "=PictureTable")
    for r in recs:
        if r["palette_count"]:
            t._claim(r["palettes"][0], r["palettes"][1], 8 * r["palette_count"], "palette", r["palette_count"],
                     "PicturePalettes")
    # maps: merge overlapping maps per bank into runs, labelled at each start
    spans = {}
    pal_ranges = [(bg.file_off(*r["palettes"]), bg.file_off(*r["palettes"]) + 8 * r["palette_count"]) for r in recs]
    for r in recs:
        o = bg.file_off(*r["map"])
        if any(a <= o < b for a, b in pal_ranges):
            continue  # points into the palettes: a placeholder record
        spans.setdefault(o // 0x4000, []).append((o, o + r["map_bytes"]))
    for b, sp in spans.items():
        sp.sort()
        runs = []
        for a, e in sp:
            if runs and a <= runs[-1][1]:
                runs[-1][1] = max(runs[-1][1], e)
                runs[-1][2].append(a)
            else:
                runs.append([a, e, [a]])
        for a, e, labs in runs:
            addr = a % 0x4000 + 0x4000
            if t._claim(b, addr, e - a, "maprun", sorted(set(labs)), None):
                for x in set(labs):
                    t.data_labels[x] = "PictureMap"
    for (b, a), pieces in sorted(bg.picture_tile_pieces(rom).items()):
        t._claim(b, a, sum(p[2] for p in pieces) * 16, "bgtiles", pieces,
                 "PictureTiles" if any(bg.file_off(*r["tiles"]) == b * 0x4000 + a - 0x4000 for r in recs) else None)
    tt = hints.TITLES
    tb = tt["bank"]
    t._claim(tb, tt["maps"], 0x4133 + 2 * tt["count"] - tt["maps"], "titletables", tt, "=TitleTables")
    for tv in bg.titles(rom):
        t._claim(tb, tv["map"], 36 * 40, "titlemap", None, "TitleMap")
        t._claim(tb, tv["palettes"], 256, "palette", 32, "TitlePalettes")
        t._claim(tb, tv["list"], tv["list_length"], "titlelist", tv["entries"], "TitlePaletteSwaps")
    f = hints.FISHING
    fb = f["bank"]
    for scr in f["screens"]:
        t._claim(fb, scr, 720, "screenmap", None, "FishingScreen")
    t._claim(fb, f["box"], 96, "boxmap", (12, 4), "FishingBox")
    t._claim(fb, f["bg_palettes"], 64, "palette", 8, "FishingBGPalettes")
    t._claim(fb, f["obj_palettes"], 64, "palette", 8, "FishingOBJPalettes")
    # flow script: one item per contiguous run of commands
    cmds = bg.flow_script(rom, hints.FLOW_ENTRIES)
    labels = set(hints.FLOW_ENTRIES) | {c[1] for c in cmds.values() if c[0] == "jump"}
    run = []
    for a in sorted(cmds) + [None]:
        if run and (a is None or a != run[-1][0] + run[-1][1]):
            t._claim(0x0D, run[0][0], run[-1][0] + run[-1][1] - run[0][0], "flow",
                     ([(x, c) for x, _, c in run], labels), "Flow")
            for x, _, _ in run:
                if x in labels:
                    t.data_labels[off(0x0D, x)] = "Flow"
            run = []
        if a is not None:
            c = cmds[a]
            run.append((a, 3 if c[0] == "jump" else 1 + len(c[2]), c))


SAFE_TEXT = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?'-:&()/+*%=<>@$#_[]~^|`")


def text_tokens(bs):
    """db operands for a byte string: printable ASCII in quotes, the rest
    as numbers ($0d = new line, 0 = end)."""
    toks, cur = [], ""
    for c in bs:
        ch = chr(c)
        if c < 0x80 and ch in SAFE_TEXT:
            cur += ch
            continue
        if cur:
            toks.append('"%s"' % cur)
            cur = ""
        toks.append("$%02x" % c)
    if cur:
        toks.append('"%s"' % cur)
    return toks


def text_rows(bs):
    """Split a string into rows at each new line so it reads like the screen."""
    rows, start = [], 0
    for i, c in enumerate(bs):
        if c == 0x0D or i == len(bs) - 1:
            rows.append(("db", text_tokens(bs[start:i + 1]), None))
            start = i + 1
    return rows


def hexrow(d, bs, per=16):
    return [(d, ["$%02x" % x for x in bs[k:k + per]], None) for k in range(0, len(bs), per)]


def parse_banks(t, rom):
    """Sound, camera regions, level object lists, text and samples (see
    tools/banks.py)."""
    import banks as bk
    import backgrounds as bg
    ref = lambda b, a, w=2: ("ref", b, a, w)  # noqa: E731
    # --- sound
    c = hints.SOUND
    s = bk.sound(rom)
    n = c["songs"]
    t._claim(0, c["song_banks"], n, "rows",
             [("db", ["$%02x" % b for b, _ in s["songs"][k:k + 8]], "songs $%02x-" % k) for k in range(0, n, 8)],
             "=SongBanks")
    t._claim(0, c["tempos"], n,
             "rows", [("db", ["$%02x" % x for x in rom[c["tempos"] + k:c["tempos"] + min(k + 8, n)]], None)
                      for k in range(0, n, 8)], "=SongTempos")
    t._claim(0, c["song_table"], 8 * n, "rows",
             [("dw", [ref(b if p >= 0x4000 else 0, p) for p in ptrs], "song $%02x" % k)
              for k, (b, ptrs) in enumerate(s["songs"])], "=SongChannels")
    a, cnt = c["note_periods"]
    t._claim(0, a, 2 * cnt, "rows", [("dw", ["$%04x" % rw for rw in struct.unpack("<%dH" % min(8, cnt - k),
                                       rom[a + 2 * k:a + 2 * min(k + 8, cnt)])], None) for k in range(0, cnt, 8)],
             "=NotePeriods")
    a, cnt = c["table_3685"]
    t._claim(0, a, 2 * cnt, "rows", [("dw", ["$%04x" % rw for rw in struct.unpack("<%dH" % min(8, cnt - k),
                                       rom[a + 2 * k:a + 2 * min(k + 8, cnt)])], None) for k in range(0, cnt, 8)],
             "SoundTable")
    a, cnt = c["wave_patterns"]
    t._claim(0, a, 16 * cnt, "rows", hexrow("db", rom[a:a + 16 * cnt]), "=WavePatterns")
    for (b, a), name in sorted(s["streams"].items()):
        if b:
            t._claim(b, a, s["stream_lengths"][(b, a)], "incbin", None, "=" + name)
        else:  # the empty streams in bank 0 are a single end byte
            t._claim(0, a, 1, "rows", hexrow("db", rom[a:a + 1]), "=" + name)
    sb, st = c["sfx_table"]
    t._claim(sb, st, 2 * len(s["sfx"]), "rows",
             [("dw", [ref(sb, p) for p in s["sfx"][k:k + 4]], "effects $%02x-" % (2 * k)) for k in range(0, len(s["sfx"]), 4)],
             "=SFXTable")
    for k, p in enumerate(s["sfx"]):
        ln = s["sfx_lengths"][p]
        if p in s["sfx"][:k]:
            continue
        t._claim(sb, p, ln, "incbin", None, "=SFX_%02X" % (2 * k))
    # --- camera regions
    hdrs = [h for h, _ in bg.map_headers(rom).values()]
    cb, lists = bk.camera_regions(rom, hdrs)
    for a, ln in lists:
        ln = (ln + 15) // 16 * 16  # the last box can end in padding-like zeros
        rows = []
        for k in range(0, ln, 16):
            ws = struct.unpack("<8H", rom[off(cb, a + k):off(cb, a + k) + 16])
            rows.append(("dw", ["$%04x" % x for x in ws], "left, right, top, bottom" if k == 0 else None))
        t._claim(cb, a, ln, "rows", rows, "CameraRegions")
    # --- level object lists
    descs = []
    for o, (kind, b, payload, ln) in t.data.items():
        if kind == "leveldesc":
            r = rom[o:o + 12]
            descs.append((r[9], r[7] | r[8] << 8))
    lists, strs = bk.level_objects(rom, descs)
    for (b, p), bs in sorted(strs.items()):
        t._claim(b, p, len(bs), "rows", hexrow("db", bs), "LevelObjString")
    for (b, a), recs in sorted(lists.items()):
        rows = []
        for (i, fl, x, y, p) in recs:
            kind = fl & 0x30
            pr = ref(b, p) if kind == 0x10 else ref(3, p) if kind == 0 else "$%04x" % p
            rows.append(("db", ["$%02x" % i, "$%02x" % fl], None))
            rows.append(("dw", ["$%04x" % x, "$%04x" % y, pr], "x, y, %s" % {0: "block in bank $03", 0x10: "string",
                                                                              0x30: "value"}.get(kind, "?")))
        rows.append(("db", ["0"], "end"))
        t._claim(b, a, 8 * len(recs) + 1, "rows", rows, "LevelObjects")
    # --- text
    for b in range(0x10, 0x15):
        groups, glists, strings = bk.text_bank(rom, b)
        for p, bs in sorted(strings.items()):
            t._claim(b, p, len(bs), "rows", text_rows(bs), "Text")
        for p, bs in bk.unreferenced_strings(rom, b, strings).items():
            t._claim(b, p, len(bs), "rows", text_rows(bs), "=UnusedText_%02x_%04x" % (b, p))
        t._claim(b, 0x4000, 32, "rows", [("dw", [ref(b, g) for g in groups[k:k + 4]], None) for k in range(0, 16, 4)],
                 "=TextGroups_%02x" % b)
        for g, lst in sorted(glists.items()):
            t._claim(b, g, 2 * len(lst), "rows", [("dw", [ref(b, p)], None) for p in lst], "TextGroup")
    # --- graphics found by their loaders (tiles themselves: hints.EXTRA_TILES)
    t._claim(0x40, 0x48C0, 360, "rows", hexrow("db", rom[off(0x40, 0x48C0):off(0x40, 0x48C0) + 360], 20),
             "=NotGBCMap")
    t._claim(0x41, 0x5380, 64, "palette", 8, "=WorldMapObjPalettes")
    t._claim(0x51, 0x42F4, 0x44F1 - 0x42F4, "incbin", None, "=FishingRuntime")  # copied to $cb00 and run there
    t._claim(0x52, 0x41EE, 0x8000 - 0x41EE, "incbin", None, "=FishingSpriteTiles")  # streamed to VRAM each frame
    # --- samples
    sbk, sta, ents, ext = bk.samples(rom)
    t._claim(sbk, sta, 4 * len(ents), "rows",
             [("db", ["$%02x" % b, "LOW(Sample_%02X)" % k, "HIGH(Sample_%02X)" % k, "%d" % n], "sample %d" % k)
              for k, (b, p, n) in enumerate(ents)], "=SampleTable")
    for k, (b, p, n) in enumerate(ents):
        t._claim(b, p, ext[(b, p)], "incbin", None, "=Sample_%02X" % k)


def make(rom):
    t = Tracer(rom)
    t.farcall_hl_a = set(hints.FARCALL_HL_A)
    t.obj_init_funcs = set(hints.OBJ_INIT_FUNCS)
    for (b, a) in hints.CODE:
        t.add(b, a, "func", b)
    for (b, start, count, stride) in hints.JP_TABLES:
        for k in range(count):
            t.add(b, start + k * stride, "func", b)
    for (b, start, count) in hints.PTR_TABLES:
        for k in range(count):
            o = off(b, start + 2 * k)
            a = rom[o] | rom[o + 1] << 8
            if a:
                t.add(b, a, "func", b)
    t.second_program = set(hints.SECOND_PROGRAM_BANKS)
    for (b, start, count) in hints.FRAME_TABLES:
        t.parse_frame_table(b, start, count)
    t.preload_funcs = set(hints.PRELOAD_FUNCS)
    t.flow_funcs = set(hints.FLOW_FUNCS)
    t.farjump_stack = set(hints.FARJUMP_STACK)
    t.farjump_hl_stack = set(hints.FARJUMP_HL_STACK)
    t.parse_palettes(hints.PALETTES)
    t.parse_levels(hints.LEVELS)
    for (b, start, end) in hints.ANIM_RUNS:
        t.parse_anim(b, start, end)
    parse_backgrounds(t, rom)
    parse_banks(t, rom)
    t.list_only_banks = set(b for b, _, _ in hints.OBJ_LIST_RUNS)
    for (b, start, end) in hints.OBJ_LIST_RUNS:
        t.parse_obj_run(b, start, end)
    for (b, start, count) in hints.OBJ_LIST_TABLES:
        for k in range(count):
            o = off(b, start + 2 * k)
            a = rom[o] | rom[o + 1] << 8
            t.parse_obj_list(0 if a < 0x4000 else b, a, b)
    t.run()
    for args in hints.FRAME_STRUCTS:
        t.parse_frame_struct(*args)
    t.scan_frame_tables(hints.FRAME_TABLE_SCAN_BANKS)
    t.scan_anim_tables(hints.FRAME_TABLE_SCAN_BANKS)
    Speculator(t).run(hints.SPECULATE_BANKS)
    return t

if __name__ == "__main__":
    rom = load(sys.argv[1])
    t = make(rom)
    per = {}
    for o, i in t.insns.items():
        per[o // 0x4000] = per.get(o // 0x4000, 0) + i.length
    print("code bytes per bank:", sorted(per.items()))
    print("conflicts:", [(b, hex(a)) + tuple(r) for (b, a, *r) in t.conflicts][:40], len(t.conflicts))
    un = {}
    for ctx, a, k in t.unresolved:
        un.setdefault(a, set()).add(ctx)
    print("unresolved ROMX refs:", len(un), sorted((hex(a)) for a in un)[:60])
    print("jp hl sites:", [hex(o) for o in sorted(t.jphl)])
