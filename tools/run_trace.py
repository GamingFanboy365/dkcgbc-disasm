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
            pr = ref(b, p) if kind == 0x10 else ref(3, p) if kind == 0 else "$%04x" % p
            rows.append(("db", ["$%02x" % i, "$%02x" % fl], None))
            rows.append(("dw", ["$%04x" % x, "$%04x" % y, pr], "x, y, %s" % {0: "block in bank $03", 0x10: "string",
                                                                              0x30: "value"}.get(kind, "?")))
        rows.append(("db", ["0"], "end"))
        t._claim(b, a, 8 * len(recs) + 1, "rows", rows, "LevelObjects")
    blocks = sorted(set(p for recs in lists.values() for (i, fl, x, y, p) in recs if fl & 0x30 == 0))
    for p in blocks:  # copied to $d800 + 16 * id (Func_00_1715)
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
    t._claim(0x51, 0x42F4, 0x44F1 - 0x42F4, "incbin", None, "=FishingRuntime")  # copied to $cb00 and run there
    t._claim(0x52, 0x41EE, 0x8000 - 0x41EE, "incbin", None, "=FishingSpriteTiles")  # streamed to VRAM each frame
    # Rare logo (flow state $10; Func_0d_4130, Func_0d_4216, Func_0d_4266)
    t._claim(0x0D, 0x4110, 32, "rows", [("db", ["$%02x" % x for x in rom[off(0x0D, 0x4110 + 4 * k):off(0x0D, 0x4110 + 4 * k) + 4]],
                                         "y, x, tile, attributes" if k == 0 else None) for k in range(8)], "=RareLogoCornerOAM")
    t._claim(0x0D, 0x42A9, 64, "palette", 8, "=RareLogoPalettes")
    t._claim(0x0D, 0x42E9, 0x5980 - 0x42E9, "incbin", None, "=RareLogoAnimation")  # frames of (n, n bytes) / ($80|n skip), 0 ends a frame
    t._claim(0x0D, 0x5F00, 88, "rows", hexrow("db", rom[off(0x0D, 0x5F00):off(0x0D, 0x5F00) + 88], 8), "=RareLogoAttributes")
    t._claim(0x55, 0x4840, 0x6100 - 0x4840, "incbin", None, "=HiScoreGraphics")  # font, scene tiles and tile maps
    t._claim(0x55, 0x6100, 0x30, "palette", 6, "=HiScorePalettes")
    # Front-end sprite animations ($f0:5a24, Func_f0_4fa8; tools/feanim.py)
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
