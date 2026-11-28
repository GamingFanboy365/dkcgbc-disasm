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
            t._claim(hdr["map_bank"], p, n, "convfile", bg.map_streams(rom)[(hdr["map_bank"], p)], "LevelMap")
        for b, name, d in ((hdr["blocks"], "LevelBlocks", "blocks"), (hdr["blocks"] + 1, "LevelBlocks", "blocks"),
                           (hdr["terrain"], "LevelTerrain", "terrain")):
            # stored in natural order; the Makefile converts (tools/leveldata.py)
            t._claim(b, 0x4000, 0x4000, "convfile", "data/%s/%02x.bin" % (d, b), "=%s_%02x" % (name, b))
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



SIGNED_ARGS = {0x13, 0x14, 0x15, 0x45}   # transposes
DECIMAL_ARGS = {0x04, 0x0A, 0x46, 0x51, 0x11, 0x12}  # counts, lengths, tempo


def music_rows(md, bank, a, end):
    """Rows of music/SFX macros for [a, end); bytes no item covers stay db."""
    import music
    rows = []
    x = a
    while x < end:
        it = md.items.get((bank, x))
        if it is None or x + it[0] > end:
            rows.append(("db", ["$%02x" % md.rom[off(bank, x)]], None))
            x += 1
            continue
        ln, kind, pay = it
        com = None if (bank, x) in md.reached else "never reached"
        if kind in ("note", "rest", "sfxnote"):
            op, length = pay
            tail = [] if length is None else ["%d" % length]
            pre = "sfx" if kind == "sfxnote" else "mus"
            if op == 0x80:
                rows.append(("%s_rest" % pre, tail, com))
            else:
                rows.append(("%s_note" % pre, [music.note_name(op & 0x7F) or "%d" % (op & 0x7F)] + tail, com))
        elif kind == "sfxhead":
            rows.append(("sfx_header", ["%d" % pay[0]] + ["$%02x" % v for v in pay[1:]], "speed, NRx1, NRx2, flags"))
        elif kind == "sfxcmd":
            op, args = pay
            rows.append((music.SFX_CMDS[op][0], ["$%02x" % v for v in args], com))
        else:
            op, args = pay
            name, kinds = music.MUSIC_CMDS[op]
            toks = []
            if kinds.startswith("="):
                sel = kinds[1:].rstrip("bwWr")
                toks.append(sel)
                kinds = kinds[1 + len(sel):]
            for k, v in zip(kinds, args):
                if k in "wWr":
                    toks.append(("ref", bank, v, 2))
                elif op in SIGNED_ARGS:
                    toks.append("%d" % (v - 256 if v >= 128 else v))
                elif op in DECIMAL_ARGS:
                    toks.append("%d" % v)
                else:
                    toks.append("$%02x" % v)
            rows.append((name, toks, com))
        x += ln
    return rows


def claim_obj_scripts(t, rom):
    """Bank $0A object behaviour scripts (tools/objscripts.py)."""
    import objscripts as osc
    ref = lambda b, a, w=2: ("ref", b, a, w)  # noqa: E731
    runs = osc.parse(rom, osc.script_starts(t, rom))
    refs = getattr(t, "obj_ptr_refs", {})
    t.obj_ptr_refs = refs
    starts = osc.script_starts(t, rom)
    for a, it in starts.items():
        refs[(osc.INTERPRETERS[it][0], a)] = osc.BANK
    for a, (it, cs) in sorted(runs.items()):
        rows, end = [], a
        for p, c, vals, text in cs:
            kinds = osc.arg_kinds(it, c, vals)
            if c == 0:
                rows.append(("db", ["$00"], text))
                rows.append(("dw", [ref(osc.BANK, vals[0]) if vals[0] else "$0000"], None))
            elif all(k == "b" for k in kinds):
                rows.append(("db", ["$%02x" % c] + ["$%02x" % v for v in vals], text))
            else:
                rows.append(("db", ["$%02x" % c], text))
                rows.append(("dw", [ref(osc.BANK, v) if k == "o" else "$%04x" % v for k, v in zip(kinds, vals)], None))
                for k, v in zip(kinds, vals):
                    if k == "o":
                        t.parse_obj_list(osc.BANK, v, osc.BANK)
            end = p + 1 + sum(1 if k == "b" else 2 for k in kinds)
        unref = " (no object list points here)" if a in dict(osc.UNREFERENCED) else ""
        rows[0] = (rows[0][0], rows[0][1], (rows[0][2] or "") + " -- %s%s" % (_routine_name(0x0A, it), unref))
        t._claim(osc.BANK, a, end - a, "rows", rows, "ObjScript")


def _routine_name(bank, addr):
    import names
    return (hints.NAMES.get((bank, addr)) or names.NAMES.get((bank, addr))
            or "Func_%02x_%04x" % (bank, addr))


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
    import music
    md = music.decode_all(rom)
    sb, st = c["sfx_table"]
    t._claim(sb, st, 2 * len(s["sfx"]), "rows",
             [("dw", [ref(sb, p) for p in s["sfx"][k:k + 4]], "effects $%02x-" % (2 * k)) for k in range(0, len(s["sfx"]), 4)],
             "=SFXTable")
    for (b, a), name in sorted(s["streams"].items()):
        if not b:  # the empty streams in bank 0 are a single end byte
            t._claim(0, a, 1, "rows", music_rows(md, 0, a, a + 1), "=" + name)
    for (b, a), ln in sorted(s["stream_lengths"].items()):
        end = a + ln
        cuts = {a} | {x for (bb, x) in md.targets if bb == b and a < x < end}
        prev = None
        for x in range(a, end):
            k = (b, x)
            if k in md.items:
                r = k in md.reached
                # a lone end byte after a loop's jump stays with the stream before it
                trailing_end = not r and md.items[k][1] == "cmd" and md.items[k][2][0] == 0
                if prev is not None and r != prev and not trailing_end:
                    cuts.add(x)
                if not trailing_end:
                    prev = r
        cuts = sorted(cuts)
        for i, x in enumerate(cuts):
            y = cuts[i + 1] if i + 1 < len(cuts) else end
            if (b, x) in s["streams"]:
                lab = "=" + s["streams"][(b, x)]
            else:
                lab = "Mus" if (b, x) in md.reached else "MusUnused"
            t._claim(b, x, y - x, "rows", music_rows(md, b, x, y), lab)
    names = {}
    for k, p in enumerate(s["sfx"]):
        names.setdefault(p, "=SFX_%02X" % (2 * k))
    for p, ln in sorted(s["sfx_lengths"].items()):
        t._claim(sb, p, ln, "rows", music_rows(md, sb, p, p + ln), names[p])
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
            pr = ref(b, p) if kind == 0x10 else ref(3, p) if kind == 0 else ref(0x0E, p) if kind == 0x30 else "$%04x" % p
            rows.append(("db", ["$%02x" % i, "$%02x" % fl], None))
            rows.append(("dw", ["$%04x" % x, "$%04x" % y, pr], "x, y, %s" % {0: "block in bank $03", 0x10: "string",
                                                                              0x30: "object (bank $0E list)"}.get(kind, "?")))
        rows.append(("db", ["0"], "end"))
        t._claim(b, a, 8 * len(recs) + 1, "rows", rows, "LevelObjects")
    blocks = sorted(set(p for recs in lists.values() for (i, fl, x, y, p) in recs if fl & 0x30 == 0))
    for p in blocks:  # copied to $d800 + 16 * id (LoadLevelObjects)
        t._claim(3, p, 16, "rows", hexrow("db", rom[off(3, p):off(3, p) + 16]), "LevelObjBlock")
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
    # code copied to RAM (hints.RAM_CODE) is claimed here and disassembled by the emitter
    for (b, src, n, dst, pbanks, extra, name) in hints.RAM_CODE:
        t._claim(b, src, n, "ramcode", (dst, pbanks, extra), name or "=RAMCopy_%02x_%04x_to_%04x" % (b, src, dst))
    # Funky's Fishing sprite animations (tools/fishanim.py)
    import fishanim
    fd = fishanim.decode(rom)
    fb = fishanim.BANK
    t._claim(fb, fishanim.TABLE, 2 * fishanim.COUNT, "rows",
             [("dw", [ref(fb, a)], "%d" % k) for k, a in enumerate(fd["table"])], "=FishingAnimTable")
    for a, (hdr, frames) in sorted(fd["anims"].items()):
        rows = [("db", ["%d" % v for v in hdr[:3]] + ["$%02x" % hdr[3]], "number, ?, last frame, bank")]
        for n, x, tp, lp in frames:
            rows.append(("db", ["%d" % n, "%d" % x], "sprites, 0"))
            rows.append(("dw", [ref(fb, tp), ref(fb, lp)], "tiles, layout"))
        t._claim(fb, a, 4 + 6 * len(frames), "rows", rows, "FishingAnim")
    for a, n in sorted(fd["layouts"].items()):
        t._claim(fb, a, n, "sprites", list(rom[off(fb, a):off(fb, a) + n]),
                 "=FishingLayout_52_%04x" % a)
    for a, n in sorted(fd["tiles"].items()):
        t._claim(fb, a, n, "tiles", None, "=FishingTiles_52_%04x" % a)
    # Rare logo (flow state $10; RareLogo_Init, RareLogo_LoadAttributes, RareLogo_DecodeFrame)
    t._claim(0x0D, 0x4110, 32, "rows", [("db", ["$%02x" % x for x in rom[off(0x0D, 0x4110 + 4 * k):off(0x0D, 0x4110 + 4 * k) + 4]],
                                         "y, x, tile, attributes" if k == 0 else None) for k in range(8)], "=RareLogoCornerOAM")
    t._claim(0x0D, 0x42A9, 64, "palette", 8, "=RareLogoPalettes")
    # Rare logo animation (RareLogo_DecodeFrame): per frame, runs of n < $80 bytes to
    # copy into the tile map buffer, or $80 + n bytes to skip; 0 ends a frame
    d, i, rows, fr = rom[off(0x0D, 0x42E9):off(0x0D, 0x5980)], 0, [], 0
    while i < len(d):
        n = d[i]
        if n == 0:
            rows.append(("db", ["0"], "end of frame %d" % fr))
            fr += 1
            i += 1
        elif n < 0x80:
            rows.append(("db", ["%d" % n] + ["$%02x" % v for v in d[i + 1:i + 1 + n]], None))
            i += 1 + n
        else:
            rows.append(("db", ["$80 + %d" % (n - 0x80)], "skip"))
            i += 1
    t._claim(0x0D, 0x42E9, 0x5980 - 0x42E9, "rows", rows, "=RareLogoAnimation")
    t._claim(0x0D, 0x5F00, 88, "rows", hexrow("db", rom[off(0x0D, 0x5F00):off(0x0D, 0x5F00) + 88], 8), "=RareLogoAttributes")
    # Hi-Score screen (bank $55): default table, tiles (HDMA'd by Func_55_45xx),
    # the screen map and two sets of 8 palettes (HiScore_LoadScreen)
    hs = rom[off(0x55, 0x4840):off(0x55, 0x4863)]
    t._claim(0x55, 0x4840, 35, "rows", [("db", ["$%02x" % v for v in hs[k:k + 3]] + ["$%02x" % v for v in hs[k + 3:k + 7]],
                                         "name (3 tiles), score (BCD)") for k in range(0, 35, 7)], "=HiScoreDefaults")  # copied to $dd77
    t._claim(0x55, 0x4863, 13, "rows", [("ds", ["13", "$00"], "padding")], "=Padding_55_4863")
    t._claim(0x55, 0x5DE0, 720, "screenmap", None, "=HiScoreMap")  # HiScore_UploadMap: attributes, then tile numbers
    t._claim(0x55, 0x60B0, 64, "palette", 8, "=HiScorePalettes")
    t._claim(0x55, 0x60F0, 64, "palette", 8, "=HiScoreObjPalettes_55")
    # Front-end sprite animations ($f0:5a24, FE_DrawSpriteAnim; tools/feanim.py)
    import feanim
    fa = feanim.decode(rom)
    tname = lambda b, a: feanim.TILE_NAMES.get((b, a), "FESprites_%02x_%04x" % (b, a))  # noqa: E731
    for (b, a), ln in sorted(fa["tiles"].items()):
        t._claim(b, a, ln, "tiles", None, "=" + tname(b, a))
    for la, (n, ty) in sorted(fa["layouts"].items()):
        bs = rom[off(0xF0, la):off(0xF0, la) + 2 * n]
        rel = ty in (0, 2, 4)
        t._claim(0xF0, la, 2 * n, "rows", [("db", ["%d" % (x - 256 if rel and x >= 128 else x) for x in bs[k:k + 2]],
                                            ("dx, dy from the previous sprite" if rel else "x, y") if k == 0 else None)
                                           for k in range(0, 2 * n, 2)], "SpriteLayout")
    for aa, n in sorted(fa["attrs"].items()):
        t._claim(0xF0, aa, n, "rows", hexrow("db", rom[off(0xF0, aa):off(0xF0, aa) + n]), "SpriteAttrs")
    t._claim(0xF0, 0x5C82, 8, "rows", hexrow("db", rom[off(0xF0, 0x5C82):off(0xF0, 0x5C82) + 8], 2),
             "=SpriteLayoutUnused_f0_5c82")  # 4 more steps after the 2-sprite layout at $5c7e; no record uses them
    langs = ["English", "German", "French", "Italian", "Spanish"]
    anim_label = {}
    for k, ty, p in fa["entries"]:
        rs = fa["records"][k]
        rows = []
        for v, (a, r) in enumerate(rs):
            ta, la = r[2] << 8 | r[3], r[4] << 8 | r[5]
            tn = tname(r[1], ta)
            toks = ["%d" % r[0], "BANK(%s)" % tn, "HIGH(%s)" % tn, "LOW(%s)" % tn,
                    "HIGH(SpriteLayout_f0_%04x)" % la, "LOW(SpriteLayout_f0_%04x)" % la]
            if ty >= 2:
                aa = r[6] << 8 | r[7]
                toks += ["HIGH(SpriteAttrs_f0_%04x)" % aa, "LOW(SpriteAttrs_f0_%04x)" % aa]
            com = "variant %d" % v + (" (%s)" % langs[v] if k in (2, 3) else "")
            if v == 0:
                com = "sprites, tiles, layout%s; %s" % (", attributes" if ty >= 2 else "", com)
            rows.append(("db", toks, com))
        anim_label[k] = feanim.NAMES.get(k, "SpriteAnim%02d" % k)
        t._claim(0xF0, p, len(rows) * (6 if ty < 2 else 8), "rows", rows, "=" + anim_label[k])
    t._claim(0xF0, feanim.TABLE, 4 * feanim.COUNT, "rows",
             [r for k, ty, p in fa["entries"] for r in (("db", ["%d" % ty, "0"], "%d: %s" % (k, feanim.TYPE_NAMES[ty])),
                                                     ("dw", [anim_label[k]], None))],
             "=SpriteAnimTable")
    # Front-end text: per-language tables at $f0:6f21 (FE_GetTextPointer).
    # Table 0 lists menu labels as (picture sheet, row); tables 1-5 point
    # to text records in bank $ff: 4 header bytes, text with $86 for a new
    # line, $87 at the end (FE_DrawText).
    lang_names = ["English", "German", "French", "Italian", "Spanish"]
    counts, sizes = [44, 6, 4, 21, 0, 7], [2, 3, 3, 3, 3, 3]
    blocks = [rom[off(0xF0, 0x6F21 + 2 * i)] | rom[off(0xF0, 0x6F21 + 2 * i) + 1] << 8 for i in range(5)]
    t._claim(0xF0, 0x6F21, 10, "rows", [("dw", [ref(0xF0, b)], lang_names[i]) for i, b in enumerate(blocks)],
             "=FrontEndTextLanguages")
    records = set()
    for i, L in enumerate(blocks):
        tabs = [rom[off(0xF0, L + 2 * k)] | rom[off(0xF0, L + 2 * k) + 1] << 8 for k in range(6)]
        t._claim(0xF0, L, 12, "rows", [("dw", [ref(0xF0, x) for x in tabs], None)], "=FrontEndText_" + lang_names[i])
        for k, ta in enumerate(tabs):
            if not counts[k]:
                continue
            rows = []
            for e in range(counts[k]):
                bs = rom[off(0xF0, ta + sizes[k] * e):off(0xF0, ta + sizes[k] * e) + sizes[k]]
                if k == 0:
                    rows.append(("db", ["%d" % bs[0], "%d" % bs[1]], "label %d: picture sheet, row" % e if e == 0 else "label %d" % e))
                else:
                    a = bs[1] << 8 | bs[2]
                    records.add((bs[0], a))
                    rows.append(("db", ["BANK(%s)" % "FEText_%02x_%04x" % (bs[0], a), "HIGH(FEText_%02x_%04x)" % (bs[0], a),
                                        "LOW(FEText_%02x_%04x)" % (bs[0], a)], "entry %d" % e))
            t._claim(0xF0, ta, sizes[k] * counts[k], "rows", rows, "=FrontEndText_%s_%d" % (lang_names[i], k))
    recs = sorted(records)
    for i, (b, a) in enumerate(recs):
        o = off(b, a)
        e = rom.index(0x87, o + 4) + 1
        unterminated = i + 1 < len(recs) and recs[i + 1][0] == b and off(b, recs[i + 1][1]) < e
        if unterminated:  # no $87: the text runs on into the next record
            e = off(b, recs[i + 1][1])
        rows = [("db", ["$%02x" % x for x in rom[o:o + 4]], "header: position and box, tentative")]
        st = o + 4
        for j in range(o + 4, e):
            if rom[j] in (0x86, 0x87) or j == e - 1:
                rows.append(("db", text_tokens(rom[st:j + 1]), None))
                st = j + 1
        if unterminated:
            rows[-1] = (rows[-1][0], rows[-1][1], "no $87 here: the text runs on into the next record")
        t._claim(b, a, e - o, "rows", rows, "=FEText_%02x_%04x" % (b, a))
    for a, ln in hints.FE_TEXT_RUNS:
        o = off(0xFF, a)
        rows, st = [], o
        for j in range(o, o + ln):
            if rom[j] in (0x86, 0x87) or j == o + ln - 1 or j - st >= 23:
                rows.append(("db", text_tokens(rom[st:j + 1]), None))
                st = j + 1
        t._claim(0xFF, a, ln, "rows", rows, "FEWords")
    tb, ta = hints.THUMBNAILS["table"]
    rows = []
    for k in range(hints.THUMBNAILS["count"]):
        r = rom[off(tb, ta + 8 * k):off(tb, ta + 8 * k) + 8]
        lab = "BGTiles_%02x_%04x" % (r[3], r[4] | r[5] << 8)
        rows.append(("db", ["$%02x" % r[0], "%d" % r[1], "%d" % r[2], "BANK(%s)" % lab, "LOW(%s)" % lab, "HIGH(%s)" % lab,
                            "%d" % r[6], "%d" % r[7]], "slot, x, y, tiles, width, height" if k == 0 else None))
    t._claim(tb, ta, 8 * len(rows), "rows", rows, "=ThumbnailTable")
    # Crosshair Cranky animated BG tiles (Cranky_AnimateBackgroundTiles): per game type a
    # bank and a list of slots; a slot is tile count, VRAM destination, and
    # frame pointers (tiles in that bank, a multiple of 16 bytes each)
    games = ["Buddies Beware", "Barrel O'Kremlings", "Wanted", "Kremling Krackdown", "Kremlings and Kongs", "Galleon Gunner"]
    tab = 0x79CF
    rows, lists = [], []
    for g in range(6):
        o = off(0xFE, tab + 3 * g)
        abk, p = rom[o], rom[o + 1] | rom[o + 2] << 8
        rows.append(("db", ["$%02x" % abk], games[g]))
        rows.append(("dw", [ref(0xFE, p) if abk else "0"], None))
        if abk:
            lists.append((abk, p))
    t._claim(0xFE, tab, 18, "rows", rows, "=CrankyTileAnimTable")
    starts = set()
    slot_of = {}
    for abk, p in lists:
        a, sl = p, []
        while not sl or a < min(sl):
            sl.append(rom[off(0xFE, a)] | rom[off(0xFE, a) + 1] << 8)
            a += 2
        slot_of[p] = (abk, sl)
        starts.update(sl)
        starts.add(p)
    ends = sorted(starts | {0x7BA9})
    for p, (abk, sl) in slot_of.items():
        t._claim(0xFE, p, 2 * len(sl), "rows", [("dw", [ref(0xFE, x) for x in sl], None)], "CrankyTileAnimSlots")
        for x in sl:
            nxt = min(e for e in ends if e > x)
            o = off(0xFE, x)
            n, dest = rom[o], rom[o + 1] | rom[o + 2] << 8
            frames = [rom[off(0xFE, y)] | rom[off(0xFE, y) + 1] << 8 for y in range(x + 3, nxt, 2)]
            r = [("db", ["%d" % n], "tiles per frame"), ("dw", ["$%04x" % dest], "VRAM destination")]
            r += [("dw", [ref(abk, f) for f in frames[k:k + 4]], "frames" if k == 0 else None) for k in range(0, len(frames), 4)]
            t._claim(0xFE, x, nxt - x, "rows", r, "CrankyTileAnim")
    # Crosshair Cranky: background picture and song per game type (Cranky_LoadBackground)
    t._claim(0xF5, 0x45FB, 12, "rows", [("dw", [ref(0xF5, rom[off(0xF5, 0x45FB + 2 * g)] | rom[off(0xF5, 0x45FB + 2 * g) + 1] << 8)],
                                         games[g]) for g in range(6)], "=CrankyBackgrounds")
    for g in range(6):
        p = rom[off(0xF5, 0x45FB + 2 * g)] | rom[off(0xF5, 0x45FB + 2 * g) + 1] << 8
        t._claim(0xF5, p, 2, "rows", [("db", ["%d" % rom[off(0xF5, p)], "$%02x" % rom[off(0xF5, p) + 1]],
                                       "picture, song")], "CrankyBackground")
    for a, name in ((0x40BE, "=CrankyModeToGame_UnusedTable"), (0x41C5, "=CrankyModeToGameTable")):
        t._claim(0xFE, a, 6, "rows", [("db", ["%d" % x for x in rom[off(0xFE, a):off(0xFE, a) + 6]], "game type per mode")], name)
    t._claim(0xFE, 0x5934, 16, "palette", 2, "=CrankyObjPalettes")  # Cranky_SetPausePalettes writes them to OCPD
    t._claim(0xFE, 0x77E1, 22 * 8, "palette", 22, "=CrankyObjPaletteSet")
    t._claim(0xFE, 0x7BA9, 48, "rows", [("db", ["%d" % x for x in rom[off(0xFE, 0x7BA9 + 8 * g):off(0xFE, 0x7BA9 + 8 * g) + 8]],
                                         games[g]) for g in range(6)], "=CrankyPaletteChoice")  # Cranky_LoadPalettes
    t._claim(0xFE, 0x794F, 12, "rows", [("db", ["%d" % x for x in rom[off(0xFE, 0x794F + 2 * g):off(0xFE, 0x794F + 2 * g) + 2]],
                                         games[g]) for g in range(6)], "=CrankyCoords")  # Cranky_DrawCrosshairAt
    for tab, end, name, sub in ((0x789B, 0x794F, "=CrankyRecordTable", "CrankyRecords"),   # Cranky_GetTargetRecord/5081, 6 bytes per [$cbc0]
                                (0x795B, 0x79CF, "=CrankyTileAnimSetup", "CrankyTileAnimInit")):  # Cranky_DrawTargets
        ps = [rom[off(0xFE, tab + 2 * g)] | rom[off(0xFE, tab + 2 * g) + 1] << 8 for g in range(6)]
        t._claim(0xFE, tab, 12, "rows", [("dw", [ref(0xFE, x)], games[g]) for g, x in enumerate(ps)], name)
        cuts = sorted(set(ps))
        for i, x in enumerate(cuts):
            y = cuts[i + 1] if i + 1 < len(cuts) else end
            t._claim(0xFE, x, y - x, "rows", hexrow("db", rom[off(0xFE, x):off(0xFE, y)], 6 if sub == "CrankyRecords" else 8), sub)
    t._claim(0xFE, 0x7891, 10, "rows", [("db", ["$%02x" % v for v in rom[off(0xFE, 0x7891):off(0xFE, 0x789B)]],
                                         "no reader found")], "=CrankyData_fe_7891")
    B = lambda a: rom[off(0xFE, a)]  # noqa: E731
    W = lambda a: B(a) | B(a + 1) << 8  # noqa: E731
    t._claim(0xFE, 0x7BD9, 13, "rows", [("db", ["%d" % B(a), "%d" % B(a + 1)], "by [$cbf0]" if a == 0x7BD9 else None)
                                        for a in range(0x7BD9, 0x7BE5, 2)] + [("db", ["$ff"], None)], "=CrankyPairs_fe_7bd9")
    recs = [W(0x7BE6 + 2 * k) for k in range(7)]
    t._claim(0xFE, 0x7BE6, 14, "rows", [("dw", [ref(0xFE, r) for r in recs], "by [$cbfc]")], "=CrankyLevelTable")
    lists = set()
    for a in range(0x7BF4, 0x7C3C, 8):  # count, a byte, three lists
        ps = [W(a + 2 + 2 * k) for k in range(3)]
        lists.update(ps)
        t._claim(0xFE, a, 8, "rows", [("db", ["%d" % B(a), "$%02x" % B(a + 1)], None), ("dw", [ref(0xFE, p) for p in ps], None)],
                 "CrankyLevel")
    ls = sorted(lists) + [0x7D11]
    for x, y in zip(ls, ls[1:]):
        t._claim(0xFE, x, y - x, "rows", [("db", ["$%02x" % B(a) for a in range(x, y)], None)], "CrankyLevelList")
    # pause menu text: a table per language ([$c805]) of six strings, each x,
    # y, length, 0, the letters and $87 (Cranky_DrawPauseText)
    langs = [W(0x7D11 + 2 * k) for k in range(5)]
    t._claim(0xFE, 0x7D11, 10, "rows", [("dw", [ref(0xFE, p) for p in langs], "by language")], "=CrankyPauseText")
    strs = []
    for k, p in enumerate(langs):
        ss = [W(p + 2 * j) for j in range(6)]
        strs += ss
        t._claim(0xFE, p, 12, "rows", [("dw", [ref(0xFE, x) for x in ss], ("English", "German", "French", "Italian", "Spanish")[k])],
                 "CrankyPauseStrings")
    for x in sorted(set(strs)):
        n = B(x + 2)
        txt = bytes(B(x + 4 + i) for i in range(n))
        t._claim(0xFE, x, 5 + n, "rows", [("db", ["$%02x" % B(x), "$%02x" % B(x + 1), "%d" % n, "0"], "x, y, length"),
                                          ("db", text_tokens(txt) + ["$87"], None)], "CrankyPauseString")
    # sound driver handler tables at $3f00: 5 SFX commands, then 82 music commands
    ws = [rom[0x3F00 + 2 * k] | rom[0x3F01 + 2 * k] << 8 for k in range(87)]
    t._claim(0, 0x3F00, 10, "rows", [("dw", [ref(0, w) for w in ws[:5]], "SFX commands $00-$08")], "=SFXCommandHandlers")
    t._claim(0, 0x3F0A, 164, "rows", [("dw", [ref(0, w) if w else "0" for w in ws[5 + k:5 + k + 4]], "music commands $%02x-" % k)
                                      for k in range(0, 82, 4)], "=MusicCommandHandlers")
    # per-world flow script entries ($3976, see hints FLOW_ENTRIES)
    t._claim(0, 0x3976, 10, "rows", [("dw", [ref(0x0D, rom[0x3976 + 2 * k] | rom[0x3977 + 2 * k] << 8) for k in range(5)], None)],
             "=WorldFlowEntries")
    # world map palette blocks no map uses, and the unused second halves of used ones
    for a in (0x499C, 0x4A1C, 0x4A9C, 0x4D9C, 0x4E1C, 0x4E9C):
        t._claim(0x0F, a, 128, "palette", 16, "=UnusedWorldPalettes_%04x" % a)
    for a in (0x495C, 0x4B5C, 0x4BDC, 0x4C5C, 0x4CDC, 0x4D5C, 0x4F5C):
        if not any(off(0x0F, a) + j in t.owner for j in range(64)):
            t._claim(0x0F, a, 64, "palette", 8, "WorldPalettesTail")  # loaded with the block, never shown
    for b, a in ((0x42, 0x72D0), (0x43, 0x60C0), (0x43, 0x6410)):  # LoadScreen copies 128 bytes
        t._claim(b, a, 64, "palette", 8, "ScreenPalettesTail")
    # bank $03 16-byte blocks that no level object list points to
    for a in range(0x4000, 0x4FF0, 16):
        if not any(off(3, a) + j in t.owner for j in range(16)) and any(rom[off(3, a):off(3, a) + 16]):
            t._claim(3, a, 16, "rows", hexrow("db", rom[off(3, a):off(3, a) + 16]), "LevelObjBlockUnused")
    t._claim(0x0D, 0x4000, 1, "rows", [("db", ["$0d"], "bank number")], "=Bank0D_Number")
    # bytes after a frame's sprite offset list that the draw code (DrawSpriteFrame) never reads
    for b in range(0x21, 0x3B):
        spr = sorted(o for o, (k, bb, pl, ln) in t.data.items() if k in ("sprites", "sprites3") and o // 0x4000 == b)
        if not spr:
            continue
        d = rom[b * 0x4000:(b + 1) * 0x4000]
        used = b * 0x4000 + len(d.rstrip(b"\xff").rstrip(b"\x00"))
        i = spr[0]
        while i < used:
            if i in t.owner:
                i += 1
                continue
            j = i
            while j < used and j not in t.owner:
                j += 1
            tail = rom[i:j]
            sg = lambda v: "%d" % (v - 256 if v > 127 else v)  # noqa: E731
            rows = [("db", [sg(v) for v in tail[k:k + 16]], "never read; dx, dy pairs like the list above" if k == 0 else None)
                    for k in range(0, len(tail), 16)]
            t._claim(b, 0x4000 + i % 0x4000, j - i, "rows", rows, "FrameSpritesTail")
            i = j
    # world map (bank $05): metasprites for WorldMap_DrawMetasprite (4-byte steps: dy, dx, tile, attributes; $80 ends)
    mps = []
    a = 0x4022
    while True:
        nz = [x for x in mps if x]
        if nz and a >= min(nz):
            break
        mps.append(rom[off(5, a)] | rom[off(5, a) + 1] << 8)
        a += 2
    t._claim(5, 0x4022, 2 * len(mps), "rows", [("dw", [ref(5, x) if x else "0"], None) for x in mps], "=WorldMapMetasprites")
    for x in sorted(set(mps) - {0}):
        q, rows = x, []
        while rom[off(5, q)] != 0x80:
            rows.append(("db", ["%d" % (v - 256 if v >= 128 and k < 2 else v) if k < 2 else "$%02x" % v
                                for k, v in enumerate(rom[off(5, q):off(5, q) + 4])], "dy, dx, tile, attributes" if q == x else None))
            q += 4
        rows.append(("db", ["$80"], "end"))
        t._claim(5, x, q + 1 - x, "rows", rows, "WorldMapMetasprite")
    t._claim(5, 0x4254, 32, "rows", hexrow("db", rom[off(5, 0x4254):off(5, 0x4254) + 32], 4), "=WorldMapSpriteOffsets")
    t._claim(5, 0x429A, 12, "rows", [("dw", ["$%04x" % (rom[off(5, 0x429A + 2 * k)] | rom[off(5, 0x429A + 2 * k) + 1] << 8)], None)
                                     for k in range(6)], "=WorldMapTileSources")  # indexed by [$c607] (1-6) from $4298
    # per world map: the list copied to $c500 ($ff ends) and the level markers (4 bytes: location, ...; $ff entry ends)
    for wm in bg.world_maps(rom):
        a = wm["list"]
        q = a
        while rom[off(5, q)] != 0xFF:
            q += 1
        t._claim(5, a, q + 1 - a, "rows", hexrow("db", rom[off(5, a):off(5, q + 1)]), "WorldMapList")
        m = wm["raw"][2] | wm["raw"][3] << 8
        q, rows = m, []
        while True:
            bs = rom[off(5, q):off(5, q) + 4]
            rows.append(("db", ["$%02x" % v for v in bs], "x (word), y, location (0: path point)" if q == m else ("end" if bs[0] == 0xFF else None)))
            q += 4
            if bs[0] == 0xFF:
                break
        t._claim(5, m, q - m, "rows", rows, "WorldMapMarkers")
    t._claim(5, 0x491E, 392, "rows", [("db", ["$%02x" % v for v in rom[off(5, 0x491E + 4 * k):off(5, 0x491E + 4 * k) + 4]],
                                       "location %d" % k) for k in range(98)], "=WorldMapLocations")  # type in bits 0-6 of byte 2
    t._claim(5, 0x4AA6, 3, "rows", hexrow("db", rom[off(5, 0x4AA6):off(5, 0x4AA9)]), "=WorldMapLocationsTail")
    # world map movement (WorldMap_ReadNode at $1dc5 area): per location 4 path pointers, picked by the
    # pressed direction (down, up, left, right); a path lists marker numbers, $ff ends
    mv = [rom[off(5, 0x4AB9 + 2 * k)] | rom[off(5, 0x4AB9 + 2 * k) + 1] << 8 for k in range(4 * 98)]
    t._claim(5, 0x4AB9, 784, "rows", [("dw", [ref(5, x) if x else "0" for x in mv[4 * k:4 * k + 4]],
                                       "location %d: down, up, left, right" % k if k == 0 else "location %d" % k) for k in range(98)],
             "=WorldMapMoves")
    t._claim(5, 0x4DC9, 10, "rows", hexrow("db", rom[off(5, 0x4DC9):off(5, 0x4DD3)]), "=WorldMapMovesTail")
    t._claim(5, 0x4DD3, 78 * 4, "rows", [("db", ["$%02x" % v for v in rom[off(5, 0x4DD3 + 4 * k):off(5, 0x4DD3 + 4 * k) + 4]],
                                          "location %d" % (k + 1)) for k in range(78)], "=WorldMapArrows")  # WorldMap_GetPathBits
    pstarts = sorted(set(x for x in mv if x))
    for i, x in enumerate(pstarts):
        y = pstarts[i + 1] if i + 1 < len(pstarts) else rom.index(0xFF, off(5, x)) - 5 * 0x4000 + 0x4000 + 1
        t._claim(5, x, y - x, "rows", hexrow("db", rom[off(5, x):off(5, y)]), "WorldMapPath")
    for a, n in ((0x45D6, 11), (0x48CA, 2)):  # well-formed marker lists no world map record points to
        t._claim(5, a, 4 * n, "rows", [("db", ["$%02x" % v for v in rom[off(5, a + 4 * k):off(5, a + 4 * k) + 4]],
                                        "x (word), y, location" if k == 0 else None) for k in range(n)], "WorldMapMarkersUnused")
    # title screen (bank $07): sprite animation (16 steps -> 7 frames of 10 OAM entries)
    fr = [rom[off(7, 0x427A + 2 * k)] | rom[off(7, 0x427A + 2 * k) + 1] << 8 for k in range(16)]
    t._claim(7, 0x427A, 32, "rows", [("dw", [ref(7, x) for x in fr[k:k + 4]], None) for k in range(0, 16, 4)], "=TitleSpriteFrames")
    for x in sorted(set(fr)):
        t._claim(7, x, 40, "rows", [("db", ["%d" % v for v in rom[off(7, x + 4 * k):off(7, x + 4 * k) + 4]],
                                     "y, x, tile, attributes" if k == 0 else None) for k in range(10)], "TitleSpriteFrame")
    t._claim(7, 0x43FE, 48, "palette", 6, "=TitleObjPalettes")  # Title_Init copies 64 bytes from here to $c1c0
    for a in (0x452E, 0x4CCE, 0x546E):  # second half of each title palette block, read during the title
        t._claim(7, a, 256, "palette", 32, "TitlePalettesExtra")
    # small tables in the object code banks, named by what reads them
    def words(b, a, n):
        return [rom[off(b, a + 2 * k)] | rom[off(b, a + 2 * k) + 1] << 8 for k in range(n)]
    t._claim(0x0A, 0x4248, 40, "rows", [("dw", ["$%04x" % w for w in words(0x0A, 0x4248, 20)[k:k + 4]],
                                         "Y velocity by OBJ_VAR_2E" if k == 0 else None) for k in range(0, 20, 4)], "ObjYVelTable")
    t._claim(0x0A, 0x481D, 16, "rows", [("dw", ["$%04x" % w for w in words(0x0A, 0x481D + 4 * k, 2)],
                                         "target X velocity, ?" if k == 0 else None) for k in range(4)], "ObjXVelTable")  # QueenB_SetSpeed
    t._claim(0x0A, 0x4CB1, 20, "rows", [("dw", ["$%04x" % w for w in words(0x0A, 0x4CB1, 10)], "by OBJ_VAR_2E")], "ObjWordTable")
    for a in (0x63C6, 0x63D6):  # chosen by [$c445] (Player_ApplySlope at $6390 area), indexed by the terrain attribute
        t._claim(0x09, a, 16, "rows", hexrow("db", rom[off(9, a):off(9, a) + 16]), "TerrainTable")
    t._claim(0x09, 0x7F01, 0x8000 - 0x7F01, "rows", hexrow("db", rom[off(9, 0x7F01):off(9, 0x8000)]), "=RampTable_09_7f01")
    # blocks the front end copies to RAM before use ("ld hl,src / ld bc,dest / ld d,n" loops)
    for b, src, dst, n in ((0xF1, 0x57F0, 0xCCBA, 65), (0xF1, 0x5831, 0xCCFB, 8), (0xF1, 0x5839, 0xCD03, 68),
                           (0xF1, 0x587D, 0xCD47, 147), (0xF1, 0x5910, 0xCDDA, 5), (0xF1, 0x5915, 0xCDDF, 16),
                           (0xF1, 0x5925, 0xCDEF, 63), (0xF1, 0x5964, 0xCE80, 7), (0xF1, 0x596B, 0xCE2E, 82),
                           (0xF1, 0x659A, 0xDB00, 80), (0xFE, 0x761B, 0xCC0E, 134)):
        if (b, src) == (0xF1, 0x659A):  # 10 BG palettes, read from $db00 by RAMCopy_f1_57f0_to_ccba
            t._claim(b, src, n, "palette", 10, "=RAMCopy_f1_659a_to_db00")
        elif b * 0x10000 + src not in {x[0] * 0x10000 + x[1] for x in hints.RAM_CODE}:
            t._claim(b, src, n, "incbin", None, "=RAMCopy_%02x_%04x_to_%04x" % (b, src, dst))
    # 8 OBJ palettes copied to $c846 from $65e8 (FE_LoadMenuOBJPalettes); their first 2 bytes are the end of the block above
    t._claim(0xF1, 0x65EA, 62, "rows", hexrow("db", rom[off(0xF1, 0x65EA):off(0xF1, 0x6628)], 8), "=FrontEndObjPalettesRest")
    t._claim(0xF1, 0x5CC1, 16, "palette", 2, "=HiScoreObjPalettes")       # copied to $c846 (FE_ViewItems_LoadPalettes)
    # bank $f2 tables
    t._claim(0xF2, 0x4397, 52, "rows", hexrow("db", rom[off(0xF2, 0x4397):off(0xF2, 0x4397 + 52)], 16),
             "=PictureByItem")  # picture number by [$c9e5] (FE_Alphabet_ShowLetter)
    t._claim(0xF2, 0x4E0C, 360, "rows", [("db", ["$%02x" % v for v in rom[off(0xF2, 0x4E0C + 6 * k):off(0xF2, 0x4E0C + 6 * k) + 6]],
                                          "entry %d" % k) for k in range(60)], "=MenuItemRecords")  # by [$c9a0] (FE_MakeFlag_LoadKey)
    t._claim(0xF2, 0x4F74, 60, "rows", hexrow("db", rom[off(0xF2, 0x4F74):off(0xF2, 0x4F74 + 60)], 12), "=MenuItemBytes")  # FE_MakeFlag_TypeKey
    t._claim(0xF2, 0x6A22, 56, "rows", [("db", ["%d" % v for v in rom[off(0xF2, 0x6A22 + 4 * k):off(0xF2, 0x6A22 + 4 * k) + 4]],
                                         "picture, type, ?, ?" if k == 0 else None) for k in range(14)], "=PictureScreens")  # FE_LinkGameResults
    # Funky's Fishing (banks $50/$51)
    t._claim(0x50, 0x51F8, 50, "rows", [("dw", ["$%04x" % (rom[off(0x50, 0x51F8 + 2 * k)] | rom[off(0x50, 0x51F8 + 2 * k) + 1] << 8)
                                               for k in range(j, min(j + 8, 25))], None) for j in range(0, 25, 8)], "=FishingWordTable_51f8")
    t._claim(0x50, 0x52DB, 80, "rows", [("dw", ["$%04x" % (rom[off(0x50, 0x52DB + 2 * k)] | rom[off(0x50, 0x52DB + 2 * k) + 1] << 8)
                                               for k in range(j, j + 8)], None) for j in range(0, 40, 8)], "=FishingWordTable_52db")
    t._claim(0x50, 0x5F73, 37, "rows", hexrow("db", rom[off(0x50, 0x5F73):off(0x50, 0x5F73 + 37)]), "=FishingByteTable_5f73")
    te = 0x7753
    rows, st = [], off(0x50, 0x769A)
    for j in range(st, off(0x50, te)):
        if rom[j] == 0:
            rows.append(("db", text_tokens(rom[st:j + 1]), None))
            st = j + 1
    t._claim(0x50, 0x769A, te - 0x769A, "rows", rows, "=FishingPauseText")  # English, French, Spanish, Italian, German
    # Funky's Fishing tables after the text
    def bcd(v):  # 4-byte BCD, low byte first
        return "".join("%02x" % x for x in reversed(v)).lstrip("0") or "0"
    for a in range(0x7753, 0x77F3, 0x20):  # points by fish (Func_50_5aXX adds one to the score at $de9f)
        rows = [("db", ["$%02x" % v for v in rom[off(0x50, a + 4 * k):off(0x50, a + 4 * k + 4)]], "%s points (BCD)" % bcd(rom[off(0x50, a + 4 * k):off(0x50, a + 4 * k + 4)]))
                for k in range(8)]
        t._claim(0x50, a, 0x20, "rows", rows, "FishPoints")
    t._claim(0x50, 0x77F3, 36, "rows", [("db", ["$%02x" % v for v in rom[off(0x50, 0x77F3 + 4 * k):off(0x50, 0x77F7 + 4 * k)]],
                                         "%s (BCD)" % bcd(rom[off(0x50, 0x77F3 + 4 * k):off(0x50, 0x77F7 + 4 * k)])) for k in range(9)],
             "=FishingBonusPoints")  # the first is added by itself, the rest by index from $77f7
    for a, n in ((0x7817, 4), (0x781B, 20), (0x782F, 6)):  # sequences set up in $df78/$df7a (length - 1)
        t._claim(0x50, a, n, "rows", [("db", ["%d" % v for v in rom[off(0x50, a):off(0x50, a + n)]], None)], "FishingSequence")
    t._claim(0x50, 0x7835, 80, "rows", [("db", ["%d" % v for v in rom[off(0x50, a):off(0x50, a + 16)]], "by [$deb1]" if a == 0x7835 else None)
                                        for a in range(0x7835, 0x7885, 16)], "=FishingRamp")
    t._claim(0x50, 0x7885, 0x400, "rows", [("dw", ["$%04x" % (rom[off(0x50, a + 2 * k)] | rom[off(0x50, a + 2 * k + 1)] << 8) for k in range(8)],
                                            "copied to $d96f (Func_50_46xx); all below $8000" if a == 0x7885 else None)
                                           for a in range(0x7885, 0x7C85, 16)], "=FishingWords")
    sine = [rom[off(0x51, 0x44F1 + 2 * k)] | rom[off(0x51, 0x44F1 + 2 * k) + 1] << 8 for k in range(1031)]
    t._claim(0x51, 0x44F1, 2062, "rows", [("dw", ["$%04x" % w for w in sine[j:j + 8]], None) for j in range(0, 1031, 8)],
             "=FishingSineTable")
    # letters drawn from pieces of the alphabet pictures (FE_DrawBigLetter): character -> FontMapC -> record
    t._claim(0xF2, 0x5574, 61 * 8, "rows", [("db", ["%d" % v for v in rom[off(0xF2, 0x5574 + 8 * k):off(0xF2, 0x5574 + 8 * k) + 8]],
                                             "picture, x, y, width, height, ..." if k == 0 else None) for k in range(61)], "=LetterPieces")
    t._claim(0xF2, 0x575C, 4, "rows", hexrow("db", rom[off(0xF2, 0x575C):off(0xF2, 0x5760)]), "=LetterPiecesEnd")
    # font maps: character - $20 -> tile (FE_DrawText's two loops) or letter piece record
    t._claim(0xF0, 0x6CA7, 221, "rows", hexrow("db", rom[off(0xF0, 0x6CA7):off(0xF0, 0x6CA7 + 221)], 16), "=FontMapA")
    t._claim(0xF0, 0x6D84, 221, "rows", hexrow("db", rom[off(0xF0, 0x6D84):off(0xF0, 0x6D84 + 221)], 16), "=FontMapB")
    t._claim(0xF0, 0x6E61, 192, "rows", hexrow("db", rom[off(0xF0, 0x6E61):off(0xF0, 0x6F21)], 16), "=FontMapC")
    # three bytes per front-end picture (FE_GetPictureMapKind, FE_GetPictureHeight, FE_GetPictureWidth), 149 each
    for a, name in ((0x5328, "PictureMapKinds"), (0x53BD, "PictureHeights"), (0x5452, "PictureWidths")):
        t._claim(0xF0, a, 149, "rows", hexrow("db", rom[off(0xF0, a):off(0xF0, a + 149)], 16), "=" + name)
    # bank $f1 menu data
    t._claim(0xF1, 0x64CB, 0x659A - 0x64CB, "rows", hexrow("db", rom[off(0xF1, 0x64CB):off(0xF1, 0x659A)], 16), "=MenuBytes_f1_64cb")
    angles = [rom[off(0xF1, 0x6628 + 2 * k)] | rom[off(0xF1, 0x6628 + 2 * k) + 1] << 8 for k in range(6)]
    t._claim(0xF1, 0x6628, 12, "rows", [("dw", [ref(0xF1, x) if x else "0" for x in angles], "by ring item count")], "=RingAngleLists")
    for a, e in ((0x6634, 0x6639), (0x6639, 0x663D), (0x663D, 0x6640), (0x6640, 0x6642)):
        t._claim(0xF1, a, e - a, "rows", hexrow("db", rom[off(0xF1, a):off(0xF1, e)]), "RingAngles")
    t._claim(0xF1, 0x6642, 0x678A - 0x6642, "rows", [("db", ["%d" % (v - 256 if v > 127 else v) for v in rom[off(0xF1, a):off(0xF1, a) + 2]],
                                                       "x, y" if a == 0x6642 else None) for a in range(0x6642, 0x678A, 2)], "=RingCircle")
    rings = [rom[off(0xF1, 0x67BF + 2 * k)] | rom[off(0xF1, 0x67BF + 2 * k) + 1] << 8 for k in range(16)]
    t._claim(0xF1, 0x67BF, 32, "rows", [("dw", [ref(0xF1, x) if x else "0" for x in rings[k:k + 4]], None) for k in range(0, 16, 4)],
             "=RingTable")  # FE_LoadRing, by [$c96e]
    starts = sorted(set(x for x in rings if x))
    for i, x in enumerate(starts):
        y = starts[i + 1] if i + 1 < len(starts) else 0x6893
        t._claim(0xF1, x, y - x, "rows", [("db", ["%d" % rom[off(0xF1, x)]], "items")] +
                 hexrow("db", rom[off(0xF1, x + 1):off(0xF1, y)], 3), "Ring")
    # bank number bytes at the start of the main game's code banks
    for b in (4, 5, 7, 8, 9, 0x0A, 0x0F):
        if rom[off(b, 0x4000)] == b:
            t._claim(b, 0x4000, 1, "rows", [("db", ["$%02x" % b], "bank number")], "=BankNumber_%02x" % b)
    t._claim(0x0D, 0x4001, 15, "rows", hexrow("db", rom[off(0x0D, 0x4001):off(0x0D, 0x4010)]), "=Bank0D_Padding")
    # the object initialiser list tables themselves (the lists are parsed from hints.OBJ_LIST_TABLES)
    for (b, a, n) in hints.OBJ_LIST_TABLES:
        ps = [rom[off(b, a + 2 * k)] | rom[off(b, a + 2 * k) + 1] << 8 for k in range(n)]
        t._claim(b, a, 2 * n, "rows", [("dw", [ref(b, x)], None) for x in ps], "ObjInitTable")
    t._claim(0, 0x33C3, 4, "rows", [("db", ["$ee", "$dd", "$bb", "$77"], "NR51 masks per channel (GetChannelPanMask)")], "=ChannelPanMasks")
    t._claim(0, 0x1EFA, 16, "rows", [("dw", ["$%04x" % (rom[0x1EFA + 2 * k] | rom[0x1EFB + 2 * k] << 8) for k in range(8)], None)],
             "=WordTable_00_1efa")
    t._claim(0, 0x20B5, 6, "rows", [("db", ["%d" % v for v in rom[0x20B5:0x20BB]], None)], "=ByteTable_00_20b5")
    # map patches in bank $04: objects keep a pointer in OBJ_VAR_2F/30/32 and
    # pass it to ApplyMapPatch (ApplyMapPatch), which writes a block of the level
    # map (block number, block attribute, terrain byte per cell) at block x, y
    a = 0x6CB4
    t.obj_ptr_refs = {}
    while a < 0x705B:
        x, y, w, h = rom[off(4, a):off(4, a) + 4]
        rows = [("db", ["$%02x" % x, "$%02x" % y, "%d" % w, "%d" % h],
                 "block x, y%s, width, height" % (" (second layer)" if y & 0x80 else ""))]
        for r in range(h):
            cells = rom[off(4, a + 4 + 3 * w * r):off(4, a + 4 + 3 * w * (r + 1))]
            rows.append(("db", ["$%02x" % v for v in cells], None))
        t._claim(4, a, 4 + 3 * w * h, "rows", rows, "MapPatch")
        for f in (0x2F, 0x30, 0x32):
            t.obj_ptr_refs[(f, a)] = 4
        a += 4 + 3 * w * h
    # bank $08 objects that carry a second object (MatchBonus_Item_Cycle at $4652 area): indexed
    # by OBJ_VAR_2E, 8 bytes each: sprite frame and palette for the carrier,
    # then a y offset and an initialiser list for the object it spawns
    rows = []
    for k in range(17):
        r = rom[off(8, 0x4CA0 + 8 * k):off(8, 0x4CA0 + 8 * k + 8)]
        fr, yo, il = r[0] | r[1] << 8, r[4] | r[5] << 8, r[6] | r[7] << 8
        if fr == 0:
            rows.append(("db", ["$%02x" % v for v in r], "%d: none" % k))
            continue
        rows.append(("dw", [ref(t.frame_bank, fr)], "%d: sprite frame" % k))
        rows.append(("db", ["$%02x" % r[2], "$%02x" % r[3]], "palette, unused"))
        rows.append(("dw", ["$%04x" % yo, ref(8, il)], "y offset, spawned object"))
    t._claim(8, 0x4CA0, 8 * 17, "rows", rows, "=CarrierObjectTable")
    # words spelled in letter blocks by SpellBonus (pointer in OBJ_VAR_35,
    # count in OBJ_VAR_33): $80 / $81 spawn ObjInit_08_441d / ObjInit_08_442b,
    # anything else is the letter's position (its OBJ_VAR_33) and its frame
    def obj_refs(field, lo, hi):
        out = set()
        for b in (8, 0x0E):
            seg = rom[off(b, 0x4000):off(b, 0x8000)]
            for i in range(len(seg) - 2):
                v = seg[i + 1] | seg[i + 2] << 8
                if seg[i] == 0x40 | field and lo <= v < hi:
                    out.add(v)
        return out
    refd = obj_refs(0x35, 0x4E6F, 0x4F8F)
    # $4eb2 (RAREWARE) follows KONG, but the only object using $4ea2 spawns 8 entries
    starts = refd | {0x4E6F, 0x4EB2}
    a, cur, rows, letters = 0x4E6F, 0x4E6F, [], []
    while a <= 0x4F8F:
        if a in starts or a == 0x4F8F:
            if rows:
                # letter frames are Frame_20_4b82 + 6 * n; sort by position for the word
                lets = sorted((p, chr(65 + (f - 0x4B82) // 6)) for p, f in letters)
                rows[0] = (rows[0][0], rows[0][1], "spells %s%s" % ("".join(c for _, c in lets),
                                                                   "" if cur in refd else " (no object spawns this)"))
                t._claim(8, cur, a - cur, "rows", rows, "SpellWord")
                t.obj_ptr_refs[(0x35, cur)] = 8
            cur, rows, letters = a, [], []
        if a == 0x4F8F:
            break
        if rom[off(8, a)] in (0x80, 0x81):
            rows.append(("db", ["$%02x" % rom[off(8, a)]], "ObjInit_08_441d" if rom[off(8, a)] == 0x80 else "ObjInit_08_442b"))
            a += 1
        else:
            fr = rom[off(8, a + 1)] | rom[off(8, a + 2)] << 8
            rows.append(("db", ["%d" % rom[off(8, a)]], "position"))
            rows.append(("dw", [ref(t.frame_bank, fr)], "letter %s" % chr(65 + (fr - 0x4B82) // 6)))
            letters.append((rom[off(8, a)], fr))
            a += 3
    # step patterns for MatchBonus rows (pointer in OBJ_VAR_33, length in
    # OBJ_VAR_32): frames to wait, then an index into CarrierObjectTable (0 = hidden)
    starts = sorted(obj_refs(0x33, 0x4F8F, 0x502F) | {0x4F8F}) + [0x502F]
    for x, y in zip(starts, starts[1:]):
        d = rom[off(8, x):off(8, y)]
        t._claim(8, x, y - x, "rows", [("db", ["%d" % d[k], "%d" % d[k + 1]], None) for k in range(0, len(d), 2)], "MatchPattern")
        t.obj_ptr_refs[(0x33, x)] = 8
    # bank $08 small tables
    w8 = lambda a: rom[off(8, a)] | rom[off(8, a + 1)] << 8  # noqa: E731
    t._claim(8, 0x5AE3, 0xC0, "rows", [("dw", ["$%04x" % w8(a), "$%04x" % w8(a + 2)], None) for a in range(0x5AE3, 0x5BA3, 4)],
             "=SlopeVelocities")  # x and y speed by OBJ_TERRAIN_B slope (MineCart_SetSlopeVelocity)
    masks = [w8(0x5D93 + 2 * k) for k in range(4)]
    t._claim(8, 0x5D93, 8, "rows", [("dw", [ref(8, m) for m in masks], "by animal buddy ([$c445] bits 4-6), AnimalBonus_LoadMask")],
             "=AnimalMaskTable")
    for m in masks:
        w, h = rom[off(8, m)], rom[off(8, m + 1)]
        rows = [("db", ["%d" % w, "%d" % h], "bytes per row, rows; copied to WRAM 4 $d800, 16 bytes a row")]
        for r in range(h):
            rows.append(("db", ["%" + format(v, "08b") for v in rom[off(8, m + 2 + w * r):off(8, m + 2 + w * (r + 1))]], None))
        t._claim(8, m, 2 + w * h, "rows", rows, "AnimalMask")
    t._claim(8, 0x5F73, 5, "rows", hexrow("db", rom[off(8, 0x5F73):off(8, 0x5F78)]), "=AnimalMask_Unused_08_5f73")
    t._claim(8, 0x614E, 3, "rows", [("db", ["$fc", "$07", "$00"], "block, attribute, terrain (written by SetMapCell)")], "=MapCell_08_614e")
    t._claim(8, 0x615B, 8, "rows", [("dw", ["$%04x" % w8(0x615B + 2 * k) for k in range(4)], "y offset by animal buddy (TileAnimator)")],
             "=AnimalYOffsets")
    t._claim(8, 0x62B6, 20, "rows", [("db", ["%" + format(v, "08b") for v in rom[off(8, a):off(8, a + 5)]], c)
                                      for a, c in zip(range(0x62B6, 0x62CA, 5), ("x", "1", "2", "3"))],
             "=ObjectDigits")  # drawn one object per set bit by SpawnObjectDigits
    # small tables in the main game's code banks
    def words(b, a, n):
        return [rom[off(b, a + 2 * k)] | rom[off(b, a + 2 * k) + 1] << 8 for k in range(n)]

    def bytes_(b, a, n):
        return list(rom[off(b, a):off(b, a) + n])
    ct = bytes_(0, 0x042B, 224)
    t._claim(0, 0x042B, 224, "rows", [("db", ["$%02x" % v for v in ct[k:k + 16]], "characters $%02x-$%02x" % (0x20 + k, 0x2F + k))
                                      for k in range(0, 224, 16)], "=CharTileTable")
    for a, n in ((0x35, 3), (0x43, 5), (0x4C, 4), (0x53, 5), (0x5B, 5), (0xFB, 5)):
        t._claim(0, a, n, "rows", [("ds", ["%d" % n, "$00"], "padding between restart vectors")], "=Padding_00_%04x" % a)
    t._claim(0, 0xF6, 2, "rows", [("dw", ["$c329"], "a RAM address, read by FE_SoundTest_DrawNumber in bank $f1")], "=RAMPointer_00_00f6")
    t._claim(8, 0x5365, 16, "rows", [("db", ["%" + format(v, "08b") for v in bytes_(8, 0x5365, 8)], None),
                                     ("db", ["%" + format(v, "08b") for v in bytes_(8, 0x536D, 8)], None)],
             "=Flags_08_5365")  # by OBJ_VAR_38 >> 4; bits 7 and 6 tested (BarrelCannon_Fire at $5265 area)
    for a in (0x41B7, 0x4284, 0x6979, 0x6CB2, 0x6CCA):
        t._claim(9, a, 2, "rows", [("dw", ["$0000"], "empty animation table entry")], "=AnimTableNull_09_%04x" % a)
    t._claim(9, 0x41BF, 8, "rows", [("dw", ["$0000"] * 4, "empty animation table entries")], "=AnimTableNull_09_41bf")
    t._claim(9, 0x4DFD, 2, "rows", [("db", ["$95", "$39"], "with the list's end byte $c3: jp NextObject, never reached")],
             "=Unused_09_4dfd")
    hb = bytes_(9, 0x429E, 332)
    t._claim(9, 0x429E, 332, "rows", [("db", ["%d" % hb[k], "%d" % hb[k + 1], "%d" % (hb[k + 2] - 256 if hb[k + 2] > 127 else hb[k + 2]),
                                              "%d" % (hb[k + 3] - 256 if hb[k + 3] > 127 else hb[k + 3])], "%d" % (k // 4))
                                      for k in range(0, 332, 4)], "=Hitboxes")
    t._claim(0x0A, 0x42AF, 10, "rows", [("db", ["%d" % v for v in bytes_(0x0A, 0x42AF, 10)], "OBJ_VAR_30 by OBJ_VAR_2E")], "=Timers_0a_42af")
    t._claim(0x0A, 0x46A4, 10, "rows", [("dw", ["$%04x" % v for v in words(0x0A, 0x46A4, 5)], "acceleration by OBJ_VAR_2E")], "=Accel_0a_46a4")
    t._claim(0x0A, 0x4871, 16, "rows", [("dw", ["$%04x" % v for v in words(0x0A, 0x4871, 8)], "by [$c336] & $0e (QueenB_CycleColour)")], "=Cycle_0a_4871")
    t._claim(0x0A, 0x4911, 6, "rows", [("db", ["%d" % v for v in bytes_(0x0A, 0x4911, 6)], "OBJ_VAR_2F by index")], "=Timers_0a_4911")
    t._claim(0x0A, 0x4E04, 6, "rows", [("dw", ["$%04x" % v for v in words(0x0A, 0x4E04, 3)], None)], "=WordTable_0a_4e04")
    t._claim(0x0A, 0x4E56, 6, "rows", [("dw", ["$%04x" % v for v in words(0x0A, 0x4E56, 3)], "y speeds")], "=YSpeeds_0a_4e56")
    t._claim(0x0A, 0x5005, 6, "rows", [("dw", ["$%04x" % v for v in words(0x0A, 0x5005, 3)], None)], "=WordTable_0a_5005")
    # the ending's captions: x position and sprite frame; entry 11 + [$c30d]
    # (the language) is "THE END?" (KingKRool_KreditsDrawCaption at $5370 area)
    caps = ["KREDITS", "KODING", "KLAP TRAP", "KARACTERS", "KRUSHA", "KOLORING", "KRITTER", "KONCEPT",
            "KLUMP", "KOMMANDER", "KING K.ROOL", "THE END? (English)", "DAS ENDE(?) (German)",
            "FIN ? (French)", "FINE...? (Italian)", "\u00bfFIN? (Spanish)"]
    rows = []
    for k in range(16):
        x, fr = words(0x0A, 0x53BF + 4 * k, 2)
        rows.append(("dw", ["$%04x" % x, ref(t.frame_bank, fr)], caps[k]))
    t._claim(0x0A, 0x53BF, 64, "rows", rows, "=CreditsCaptions")
    t._claim(0x0A, 0x58C0, 8, "rows", [("dw", [ref(4, v) for v in words(0x0A, 0x58C0, 4)], "wLevelEntrance by OBJ_VAR_2F")], "=Entrances_0a_58c0")
    t._claim(0x0A, 0x6894, 20, "rows", [("dw", ["$%04x" % v for v in words(0x0A, 0x6894, 10)], "colour 3 of the object's palette, red to green")],
             "=FadeColours_0a_6894")
    # unreached instructions inside functions (left as bytes so the
    # surrounding function keeps its labels)
    t._claim(0, 0x03F5, 2, "rows", [("db", ["$18", "$ed"], "jr $03e4, never reached")], "=.unreached_03f5")
    t._claim(0, 0x1DB5, 1, "rows", [("db", ["$c9"], "ret, never reached")], "=.unreached_1db5")
    ct = bytes_(0x50, 0x6A58, 256)
    t._claim(0x50, 0x6A58, 256, "rows", [("db", ["$%02x" % v for v in ct[k:k + 16]], "characters $%02x-$%02x" % (k, k + 15))
                                         for k in range(0, 256, 16)], "=CharTileTable_50")  # Fishing_TextToTiles
    t._claim(0x51, 0x4CFF, 1, "rows", [("db", ["$00"], "padding")], "=Padding_51_4cff")
    # a 20x32 map in which every position has its own tile (0-255 in VRAM
    # bank 0, then again in bank 1), so code can draw into the tiles; copied
    # to WRAM 2 $d000/$d400 by FE_CopyPictureMap (.copy_unique_map), 32 bytes a row
    um = bytes_(0xF0, 0x4A9D, 1280)
    t._claim(0xF0, 0x4A9D, 1280, "rows", [("db", ["$%02x" % v for v in um[k:k + 20]],
                                            "attributes" if k == 0 else "tile numbers" if k == 640 else None)
                                           for k in range(0, 1280, 20)], "=UniqueTileMap")
    t._claim(0xF0, 0x4701, 6, "rows", [("ds", ["6", "$00"], "padding")], "=Padding_f0_4701")
    # bank $f1 (front end) tables
    t._claim(0xF1, 0x4D01, 2, "rows", [("db", ["$00", "$00"], "pads the ret entry above to 3 bytes")], "=.jp_table_pad")
    t._claim(0xF1, 0x5CA9, 24, "rows", [("db", ["$%02x" % v for v in bytes_(0xF1, 0x5CA9 + 4 * k, 4)], None) for k in range(6)],
             "=SpritePositions_f1_5ca9")  # x, y, sprite animation, direction (bit 7) for FE_ViewItems_DrawItem
    t._claim(0xF1, 0x5D0A, 30, "rows", [("db", ["$%02x" % v for v in bytes_(0xF1, 0x5D0A + 10 * k, 10)], "copied to $%04x" % d)
                                        for k, d in enumerate((0xC9E6, 0xC9FE, 0xCA08))], "=Defaults_f1_5d0a")
    t._claim(0xF1, 0x678A, 32, "rows", [("db", ["$%02x" % v for v in bytes_(0xF1, 0x678A, 10)], "not read in any session, nothing points here"),
                                        ("dw", ["$6798", "$67a1"], None),
                                        ("db", ["$%02x" % v for v in bytes_(0xF1, 0x6798, 9)], None),
                                        ("db", ["$%02x" % v for v in bytes_(0xF1, 0x67A1, 9)], None)], "=Unused_f1_678a")
    t._claim(0xF1, 0x67AA, 21, "rows", [("db", ["$%02x" % v for v in bytes_(0xF1, 0x67AA, 21)], "by [$c96e], $ff for none (FE_IsRingItemHidden)")],
             "=ByteTable_f1_67aa")
    # menus: (item count, pointer) per menu; items are 12 bytes, byte 8
    # is the item's action ([$c993], FE_StickerBook_SelectSticker)
    mt = [(rom[off(0xF1, 0x6893 + 3 * k)], words(0xF1, 0x6894 + 3 * k, 1)[0]) for k in range(5)]
    t._claim(0xF1, 0x6893, 15, "rows", [("db", ["%d" % n, "LOW(%s)" % "MenuItems_f1_%04x" % p, "HIGH(%s)" % "MenuItems_f1_%04x" % p], "items, list")
                                        for n, p in mt], "=MenuTable_f1_6893")
    for n, p in mt:
        t._claim(0xF1, p, 12 * n, "rows", [("db", ["$%02x" % v for v in bytes_(0xF1, p + 12 * k, 12)], None) for k in range(n)], "MenuItems")
    sl = words(0xF1, 0x691A, 4)
    t._claim(0xF1, 0x691A, 8, "rows", [("dw", [ref(0xF1, v) for v in sl], "by [$c989] - 1 (Func_f1_754x)")], "=SpriteLists_f1_691a")
    for v in sorted(set(sl)):
        n = rom[off(0xF1, v)]
        t._claim(0xF1, v, 1 + 3 * n, "rows", [("db", ["%d" % n], "count")] +
                 [("db", ["$%02x" % x for x in bytes_(0xF1, v + 1 + 3 * k, 3)], "variant, x, y") for k in range(n)], "SpriteList")
    for a, c in ((0x69CA, "by index (Func_f1_7xxx)"), (0x69D4, "x offsets"), (0x69DE, None)):
        t._claim(0xF1, a, 10, "rows", [("db", ["%d" % v for v in bytes_(0xF1, a, 10)], c)], "=ByteTable_f1_%04x" % a)
    t._claim(0xF1, 0x69E8, 8, "rows", [("dw", ["$%04x" % v for v in words(0xF1, 0x69E8, 4)], "RAM addresses")], "=RAMPointers_f1_69e8")
    rows = []
    for k in range(5):
        p, r = words(0xF1, 0x69F0 + 4 * k, 2)
        rows.append(("dw", [ref(0xF1, p) if p else "$0000", "$%04x" % r], None))
    t._claim(0xF1, 0x69F0, 20, "rows", rows, "=Columns_f1_69f0")  # by [$c96c] (FE_DrawRingExtras.else_545f)
    for a in range(0x6A04, 0x6A1D, 5):
        t._claim(0xF1, a, 5, "rows", [("db", ["%d" % v for v in bytes_(0xF1, a, 5)], "by language ([$c805])")], "LanguageColumns")
    lw = words(0xF1, 0x6A1D, 10)
    t._claim(0xF1, 0x6A1D, 20, "rows", [("dw", [ref(0xF1, lw[2 * k]), ref(0xF1, lw[2 * k + 1])], ("English", "German", "French", "Italian", "Spanish")[k])
                                        for k in range(5)], "=LanguageWordTiles")  # LoadLanguageWordTiles copies the first of each pair
    t._claim(0xF1, 0x6A31, 15, "rows", [("ds", ["15", "$00"], "padding")], "=.pad_6a31")
    t._claim(0xF1, 0x6FD0, 16, "rows", hexrow("db", bytes(bytes_(0xF1, 0x6FD0, 16))), "=Tile_f1_6fd0")  # a 10th tile after the 9 LoadLanguageWordTiles copies
    t._claim(0xF1, 0x6FE0, 154, "rows", [("db", ["$%02x" % v for v in bytes_(0xF1, a, 16)][:min(16, 0x707A - a)], None)
                                         for a in range(0x6FE0, 0x707A, 16)], "=Pairs_f1_6fe0")  # by [$c986]: value, offset from $c329 - 1 (FE_SoundTest_DrawNumber)
    # last front-end leftovers: unreached bytes after a ret/jr/jp
    for b, a, bs, c in ((0xF2, 0x4A38, [0xC9], "ret"), (0xF2, 0x4A4D, [0xC6, 0x18], "add a, $18"), (0xF2, 0x6F25, [0xC9], "ret"),
                        (0xFE, 0x4E37, [0xC9], "ret"), (0xFE, 0x6E52, [0xC9], "ret")):
        assert list(bytes_(b, a, len(bs))) == bs
        t._claim(b, a, len(bs), "rows", [("db", ["$%02x" % v for v in bs], "%s, never reached" % c)], "=.unreached_%04x" % a)
    t._claim(0xF5, 0x4AE2, 14, "rows", [("ds", ["14", "$00"], "padding")], "=Padding_f5_4ae2")
    t._claim(0xFE, 0x76A1, 3, "rows", [("db", ["$c3"], "jp $cc0e, copied by Cranky_SetSerialJump to the serial interrupt's"),
                                       ("dw", ["$cc0e"], "RAM trampoline (the address in the vector at $0059)")], "=SerialJump_fe_76a1")
    t._claim(0xFE, 0x47C4, 3, "rows", [("db", ["%d" % v for v in bytes_(0xFE, 0x47C4, 3)], "added to [$cbc8] by [$dc20 + [$ff9c]] - 2")],
             "=ByteTable_fe_47c4")
    t._claim(0xFE, 0x6958, 18, "rows", [("db", ["$%02x" % v for v in bytes_(0xFE, 0x6958 + 3 * k, 3)], None) for k in range(6)],
             "=Triples_fe_6958")  # d, b, c by index (Func_fe_69xx)
    t._claim(0xFE, 0x6CCE, 7, "rows", [("db", ["%d" % v for v in bytes_(0xFE, 0x6CCE, 7)], "by a random number below 7 (FE_RandomBelow)")],
             "=ByteTable_fe_6cce")
    t._claim(0x0B, 0x6C1F, 1, "rows", [("db", ["$00"], "padding")], "=Padding_0b_6c1f")
    t._claim(0x0F, 0x4568, 7, "rows", [("db", ["%d" % v for v in bytes_(0x0F, 0x4568, 7)], "by [$c30a]")], "=ByteTable_0f_4568")
    t._claim(0x0F, 0x4595, 12, "rows", [("dw", [ref(4, v) for v in words(0x0F, 0x4595, 6)], "wLevelEntrance")], "=Entrances_0f_4595")
    t._claim(0x0F, 0x46F0, 84, "rows", [("dw", ["%" + format(v, "016b") for v in words(0x0F, 0x46F0 + 8 * k, min(4, 42 - 4 * k))], None)
                                        for k in range(11)], "=Masks_0f_46f0")  # by [$c30c]
    t._claim(0x0F, 0x48B0, 25, "rows", [("db", ["%d" % v for v in bytes_(0x0F, 0x48B0, 25)], "save flag bit by level (Save_ComputeSummaries at $4830 area)")],
             "=LevelFlagBits")
    # --- samples
    sbk, sta, ents, ext = bk.samples(rom)
    t._claim(sbk, sta, 4 * len(ents), "rows",
             [("db", ["$%02x" % b, "LOW(Sample_%02X)" % k, "HIGH(Sample_%02X)" % k, "%d" % n], "sample %d" % k)
              for k, (b, p, n) in enumerate(ents)], "=SampleTable")
    for k, (b, p, n) in enumerate(ents):
        t._claim(b, p, ext[(b, p)], "convfile", "data/samples/sample_%02x.wav" % k, "=Sample_%02X" % k)


def make(rom):
    t = Tracer(rom)
    t.farcall_hl_a = set(hints.FARCALL_HL_A)
    t.obj_init_funcs = set(hints.OBJ_INIT_FUNCS)
    for (b, a) in hints.CODE:
        t.add(b, a, "func", b)
    # banks $50/$55 far-call through the RAM trampoline at $cb99 after pushing
    # their own return address: ld hl, ret / push hl / ldh a, [$ffc5] / push af /
    # ld hl, $cba7 / push hl / ... The return address continues the caller.
    import re
    for m in re.finditer(rb"\x21(..)\xe5\xf0\xc5\xf5\x21\xa7\xcb\xe5", rom, re.S):
        b = m.start() // 0x4000
        a = m.group(1)[0] | m.group(1)[1] << 8
        if b and 0x4000 <= a < 0x8000:
            t.add(b, a, "func", b)
    # banks $F0+ push a return address (high byte first), the current bank and
    # $3FD5 (which restores the bank and returns) before far-jumping through
    # $3FDC: ld a, hi / push af / inc sp / ld a, lo / push af / inc sp /
    # ldh a, [$ff81] / push af / ld a, $3f / push af / inc sp / ld a, $d5 ...
    for m in re.finditer(rb"\x3e(.)\xf5\x33\x3e(.)\xf5\x33\xf0\x81\xf5\x3e\x3f\xf5\x33\x3e\xd5\xf5\x33", rom, re.S):
        b = m.start() // 0x4000
        a = m.group(1)[0] << 8 | m.group(2)[0]
        if b and 0x4000 <= a < 0x8000:
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
    for (b, a) in hints.OBJ_LISTS:
        t.parse_obj_list(b, a, b)
    for a in (0x502F, 0x5048, 0x5061, 0x507A, 0x5093, 0x50AC, 0x50C5):  # chained by OBJ_VAR_3B
        t.parse_obj_list(8, a, 8)
    for k in range(1, 17):
        o = off(8, 0x4CA0 + 8 * k + 6)
        t.parse_obj_list(8, rom[o] | rom[o + 1] << 8, 8)
    t.run()
    claim_obj_scripts(t, rom)
    t.run()
    for args in hints.FRAME_STRUCTS:
        t.parse_frame_struct(*args)
    t.scan_frame_tables(hints.FRAME_TABLE_SCAN_BANKS)
    t.scan_anim_tables(hints.FRAME_TABLE_SCAN_BANKS)
    Speculator(t).run(hints.SPECULATE_BANKS)
    # frames loaded with "ld de" and stored into OBJ_FRAME; a load whose
    # value is a frame header in a function that stores frames that way
    # counts too (the store can sit after a branch joins)
    frame_funcs = set()
    for i in t.de_frame_refs:
        if i.imm is not None and off(t.frame_bank, i.imm) in t.frame_headers:
            i.dataref = (t.frame_bank, i.imm)
            frame_funcs.add((i.bank, i.addr >> 6))
    for i in t.de_loads:
        if i.dataref is None and off(t.frame_bank, i.imm) in t.frame_headers and \
                any((i.bank, (i.addr >> 6) + d) in frame_funcs for d in (-1, 0, 1)):
            i.dataref = (t.frame_bank, i.imm)
    # the targets of "jp" table entries are entry points of their own, even
    # where they sit inside a longer routine (the game states in bank $00 and
    # the front-end program's tables)
    for (b, start, count, stride) in hints.JP_TABLES:
        if 0 < b < 0xF0:
            continue
        for k in range(count):
            i = t.insns.get(off(b, start + k * stride))
            if i is not None and i.op == 0xC3 and i.target is not None and i.target < 0x8000:
                to = off(b if i.target >= 0x4000 else 0, i.target)
                if to in t.insns:
                    t.labels[to] = "func"
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
