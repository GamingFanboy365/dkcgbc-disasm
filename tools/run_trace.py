import sys
import os
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
