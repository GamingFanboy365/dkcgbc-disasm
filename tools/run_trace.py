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
    tb, ta = hints.THUMBNAILS["table"]
    rows = []
    for k in range(hints.THUMBNAILS["count"]):
        r = rom[off(tb, ta + 8 * k):off(tb, ta + 8 * k) + 8]
        lab = "BGTiles_%02x_%04x" % (r[3], r[4] | r[5] << 8)
        rows.append(("db", ["$%02x" % r[0], "%d" % r[1], "%d" % r[2], "BANK(%s)" % lab, "LOW(%s)" % lab, "HIGH(%s)" % lab,
                            "%d" % r[6], "%d" % r[7]], "slot, x, y, tiles, width, height" if k == 0 else None))
    t._claim(tb, ta, 8 * len(rows), "rows", rows, "=ThumbnailTable")
    # Crosshair Cranky animated BG tiles (Func_fe_5354): per game type a
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
    # Crosshair Cranky: background picture and song per game type (Func_f5_4950)
    t._claim(0xF5, 0x45FB, 12, "rows", [("dw", [ref(0xF5, rom[off(0xF5, 0x45FB + 2 * g)] | rom[off(0xF5, 0x45FB + 2 * g) + 1] << 8)],
                                         games[g]) for g in range(6)], "=CrankyBackgrounds")
    for g in range(6):
        p = rom[off(0xF5, 0x45FB + 2 * g)] | rom[off(0xF5, 0x45FB + 2 * g) + 1] << 8
        t._claim(0xF5, p, 2, "rows", [("db", ["%d" % rom[off(0xF5, p)], "$%02x" % rom[off(0xF5, p) + 1]],
                                       "picture, song")], "CrankyBackground")
    for a, name in ((0x40BE, "=CrankyModeToGame_UnusedTable"), (0x41C5, "=CrankyModeToGameTable")):
        t._claim(0xFE, a, 6, "rows", [("db", ["%d" % x for x in rom[off(0xFE, a):off(0xFE, a) + 6]], "game type per mode")], name)
    t._claim(0xFE, 0x5934, 16, "palette", 2, "=CrankyObjPalettes")  # Func_fe_5944 writes them to OCPD
    t._claim(0xFE, 0x77E1, 22 * 8, "palette", 22, "=CrankyObjPaletteSet")
    t._claim(0xFE, 0x7BA9, 48, "rows", [("db", ["%d" % x for x in rom[off(0xFE, 0x7BA9 + 8 * g):off(0xFE, 0x7BA9 + 8 * g) + 8]],
                                         games[g]) for g in range(6)], "=CrankyPaletteChoice")  # Func_fe_5c0d
    t._claim(0xFE, 0x794F, 12, "rows", [("db", ["%d" % x for x in rom[off(0xFE, 0x794F + 2 * g):off(0xFE, 0x794F + 2 * g) + 2]],
                                         games[g]) for g in range(6)], "=CrankyCoords")  # Func_fe_5235
    for tab, end, name, sub in ((0x789B, 0x794F, "=CrankyRecordTable", "CrankyRecords"),   # Func_fe_5065/5081, 6 bytes per [$cbc0]
                                (0x795B, 0x79CF, "=CrankyTileAnimSetup", "CrankyTileAnimInit")):  # Func_fe_5adf
        ps = [rom[off(0xFE, tab + 2 * g)] | rom[off(0xFE, tab + 2 * g) + 1] << 8 for g in range(6)]
        t._claim(0xFE, tab, 12, "rows", [("dw", [ref(0xFE, x)], games[g]) for g, x in enumerate(ps)], name)
        cuts = sorted(set(ps))
        for i, x in enumerate(cuts):
            y = cuts[i + 1] if i + 1 < len(cuts) else end
            t._claim(0xFE, x, y - x, "rows", hexrow("db", rom[off(0xFE, x):off(0xFE, y)], 6 if sub == "CrankyRecords" else 8), sub)
    t._claim(0xFE, 0x7891, 10, "incbin", None, "=CrankyData_fe_7891")
    t._claim(0xFE, 0x7BD9, 0x7E88 - 0x7BD9, "incbin", None, "=CrankyData_fe_7bd9")
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
    for b, a in ((0x42, 0x72D0), (0x43, 0x60C0), (0x43, 0x6410)):  # Func_00_2c48 copies 128 bytes
        t._claim(b, a, 64, "palette", 8, "ScreenPalettesTail")
    # bank $03 16-byte blocks that no level object list points to
    for a in range(0x4000, 0x4FF0, 16):
        if not any(off(3, a) + j in t.owner for j in range(16)) and any(rom[off(3, a):off(3, a) + 16]):
            t._claim(3, a, 16, "rows", hexrow("db", rom[off(3, a):off(3, a) + 16]), "LevelObjBlockUnused")
    t._claim(0x0D, 0x4000, 1, "rows", [("db", ["$0d"], "bank number")], "=Bank0D_Number")
    # bytes after a frame's sprite offset list that the draw code (Func_00_1037) never reads
    for b in range(0x21, 0x3B):
        spr = sorted(o for o, (k, bb, pl, ln) in t.data.items() if k == "sprites" and o // 0x4000 == b)
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
            t._claim(b, 0x4000 + i % 0x4000, j - i, "incbin", None, "FrameSpritesTail")
            i = j
    # world map (bank $05): metasprites for Func_05_4001 (4-byte steps: dy, dx, tile, attributes; $80 ends)
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
    # world map movement (Func_00_1dc5 area): per location 4 path pointers, picked by the
    # pressed direction (down, up, left, right); a path lists marker numbers, $ff ends
    mv = [rom[off(5, 0x4AB9 + 2 * k)] | rom[off(5, 0x4AB9 + 2 * k) + 1] << 8 for k in range(4 * 98)]
    t._claim(5, 0x4AB9, 784, "rows", [("dw", [ref(5, x) if x else "0" for x in mv[4 * k:4 * k + 4]],
                                       "location %d: down, up, left, right" % k if k == 0 else "location %d" % k) for k in range(98)],
             "=WorldMapMoves")
    t._claim(5, 0x4DC9, 10, "rows", hexrow("db", rom[off(5, 0x4DC9):off(5, 0x4DD3)]), "=WorldMapMovesTail")
    t._claim(5, 0x4DD3, 78 * 4, "rows", [("db", ["$%02x" % v for v in rom[off(5, 0x4DD3 + 4 * k):off(5, 0x4DD3 + 4 * k) + 4]],
                                          "location %d" % (k + 1)) for k in range(78)], "=WorldMapArrows")  # Func_05_446a
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
    t._claim(7, 0x43FE, 48, "palette", 6, "=TitleObjPalettes")  # Func_07_4001 copies 64 bytes from here to $c1c0
    for a in (0x452E, 0x4CCE, 0x546E):  # second half of each title palette block, read during the title
        t._claim(7, a, 256, "palette", 32, "TitlePalettesExtra")
    # small tables in the object code banks, named by what reads them
    def words(b, a, n):
        return [rom[off(b, a + 2 * k)] | rom[off(b, a + 2 * k) + 1] << 8 for k in range(n)]
    t._claim(0x0A, 0x4248, 40, "rows", [("dw", ["$%04x" % w for w in words(0x0A, 0x4248, 20)[k:k + 4]],
                                         "Y velocity by OBJ_VAR_2E" if k == 0 else None) for k in range(0, 20, 4)], "ObjYVelTable")
    t._claim(0x0A, 0x481D, 16, "rows", [("dw", ["$%04x" % w for w in words(0x0A, 0x481D + 4 * k, 2)],
                                         "target X velocity, ?" if k == 0 else None) for k in range(4)], "ObjXVelTable")  # Func_0a_47fe
    t._claim(0x0A, 0x4CB1, 20, "rows", [("dw", ["$%04x" % w for w in words(0x0A, 0x4CB1, 10)], "by OBJ_VAR_2E")], "ObjWordTable")
    for a in (0x63C6, 0x63D6):  # chosen by [$c445] (Func_09_6390 area), indexed by the terrain attribute
        t._claim(0x09, a, 16, "rows", hexrow("db", rom[off(9, a):off(9, a) + 16]), "TerrainTable")
    t._claim(0x09, 0x7F01, 0x8000 - 0x7F01, "rows", hexrow("db", rom[off(9, 0x7F01):off(9, 0x8000)]), "=RampTable_09_7f01")
    # blocks the front end copies to RAM before use ("ld hl,src / ld bc,dest / ld d,n" loops)
    for b, src, dst, n in ((0xF1, 0x57F0, 0xCCBA, 65), (0xF1, 0x5831, 0xCCFB, 8), (0xF1, 0x5839, 0xCD03, 68),
                           (0xF1, 0x587D, 0xCD47, 147), (0xF1, 0x5910, 0xCDDA, 5), (0xF1, 0x5915, 0xCDDF, 16),
                           (0xF1, 0x5925, 0xCDEF, 63), (0xF1, 0x5964, 0xCE80, 7), (0xF1, 0x596B, 0xCE2E, 82),
                           (0xF1, 0x659A, 0xDB00, 80), (0xFE, 0x761B, 0xCC0E, 134)):
        t._claim(b, src, n, "incbin", None, "=RAMCopy_%02x_%04x_to_%04x" % (b, src, dst))
    # 8 OBJ palettes copied to $c846 from $65e8 (Func_f1_433a); their first 2 bytes are the end of the block above
    t._claim(0xF1, 0x65EA, 62, "rows", hexrow("db", rom[off(0xF1, 0x65EA):off(0xF1, 0x6628)], 8), "=FrontEndObjPalettesRest")
    t._claim(0xF1, 0x5CC1, 16, "palette", 2, "=HiScoreObjPalettes")       # copied to $c846 (Func_f1_5cd1)
    # bank $f2 tables
    t._claim(0xF2, 0x4397, 52, "rows", hexrow("db", rom[off(0xF2, 0x4397):off(0xF2, 0x4397 + 52)], 16),
             "=PictureByItem")  # picture number by [$c9e5] (Func_f2_41c5)
    t._claim(0xF2, 0x4E0C, 360, "rows", [("db", ["$%02x" % v for v in rom[off(0xF2, 0x4E0C + 6 * k):off(0xF2, 0x4E0C + 6 * k) + 6]],
                                          "entry %d" % k) for k in range(60)], "=MenuItemRecords")  # by [$c9a0] (Func_f2_4600)
    t._claim(0xF2, 0x4F74, 60, "rows", hexrow("db", rom[off(0xF2, 0x4F74):off(0xF2, 0x4F74 + 60)], 12), "=MenuItemBytes")  # Func_f2_4626
    t._claim(0xF2, 0x6A22, 56, "rows", [("db", ["%d" % v for v in rom[off(0xF2, 0x6A22 + 4 * k):off(0xF2, 0x6A22 + 4 * k) + 4]],
                                         "picture, type, ?, ?" if k == 0 else None) for k in range(14)], "=PictureScreens")  # Func_f2_6c5a
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
    t._claim(0x50, te, 0x769A + 1515 - te, "incbin", None, "=FishingData_50_7753")
    sine = [rom[off(0x51, 0x44F1 + 2 * k)] | rom[off(0x51, 0x44F1 + 2 * k) + 1] << 8 for k in range(1031)]
    t._claim(0x51, 0x44F1, 2062, "rows", [("dw", ["$%04x" % w for w in sine[j:j + 8]], None) for j in range(0, 1031, 8)],
             "=FishingSineTable")
    # letters drawn from pieces of the alphabet pictures (Func_f2_5313): character -> FontMapC -> record
    t._claim(0xF2, 0x5574, 61 * 8, "rows", [("db", ["%d" % v for v in rom[off(0xF2, 0x5574 + 8 * k):off(0xF2, 0x5574 + 8 * k) + 8]],
                                             "picture, x, y, width, height, ..." if k == 0 else None) for k in range(61)], "=LetterPieces")
    t._claim(0xF2, 0x575C, 4, "rows", hexrow("db", rom[off(0xF2, 0x575C):off(0xF2, 0x5760)]), "=LetterPiecesEnd")
    # font maps: character - $20 -> tile (FE_DrawText's two loops) or letter piece record
    t._claim(0xF0, 0x6CA7, 221, "rows", hexrow("db", rom[off(0xF0, 0x6CA7):off(0xF0, 0x6CA7 + 221)], 16), "=FontMapA")
    t._claim(0xF0, 0x6D84, 221, "rows", hexrow("db", rom[off(0xF0, 0x6D84):off(0xF0, 0x6D84 + 221)], 16), "=FontMapB")
    t._claim(0xF0, 0x6E61, 192, "rows", hexrow("db", rom[off(0xF0, 0x6E61):off(0xF0, 0x6F21)], 16), "=FontMapC")
    # three bytes per front-end picture (Func_f0_4a40, Func_f0_4a49, Func_f0_4a52), 149 each
    for a, name in ((0x5328, "PictureInfoA"), (0x53BD, "PictureInfoB"), (0x5452, "PictureInfoC")):
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
    t._claim(0, 0x33C3, 4, "rows", [("db", ["$ee", "$dd", "$bb", "$77"], "NR51 masks per channel (Func_00_33b4)")], "=ChannelPanMasks")
    t._claim(0, 0x1EFA, 16, "rows", [("dw", ["$%04x" % (rom[0x1EFA + 2 * k] | rom[0x1EFB + 2 * k] << 8) for k in range(8)], None)],
             "=WordTable_00_1efa")
    t._claim(0, 0x20B5, 6, "rows", [("db", ["%d" % v for v in rom[0x20B5:0x20BB]], None)], "=ByteTable_00_20b5")
    # map patches in bank $04: objects keep a pointer in OBJ_VAR_2F/30/32 and
    # pass it to ApplyMapPatch (Func_00_0d74), which writes a block of the level
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
    # bank $08 objects that carry a second object (Func_08_4652 area): indexed
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
    # part groups for Func_08_4344 (pointer in OBJ_VAR_35, count in OBJ_VAR_33):
    # $80 / $81 spawn ObjInit_08_441d / ObjInit_08_442b, anything else is the
    # part's OBJ_VAR_33 followed by its sprite frame
    def obj_refs(field, lo, hi):
        out = set()
        for b in (8, 0x0E):
            seg = rom[off(b, 0x4000):off(b, 0x8000)]
            for i in range(len(seg) - 2):
                v = seg[i + 1] | seg[i + 2] << 8
                if seg[i] == 0x40 | field and lo <= v < hi:
                    out.add(v)
        return out
    starts = obj_refs(0x35, 0x4E6F, 0x4F8F) | {0x4E6F}
    a, cur, rows = 0x4E6F, 0x4E6F, []
    while a <= 0x4F8F:
        if a in starts or a == 0x4F8F:
            if rows:
                t._claim(8, cur, a - cur, "rows", rows, "PartGroup")
                t.obj_ptr_refs[(0x35, cur)] = 8
            cur, rows = a, []
        if a == 0x4F8F:
            break
        if rom[off(8, a)] in (0x80, 0x81):
            rows.append(("db", ["$%02x" % rom[off(8, a)]], "ObjInit_08_441d" if rom[off(8, a)] == 0x80 else "ObjInit_08_442b"))
            a += 1
        else:
            fr = rom[off(8, a + 1)] | rom[off(8, a + 2)] << 8
            rows.append(("db", ["$%02x" % rom[off(8, a)]], None))
            rows.append(("dw", [ref(t.frame_bank, fr)], None))
            a += 3
    # step patterns for Func_08_4581 rows (pointer in OBJ_VAR_33, length in
    # OBJ_VAR_32): frames to wait, then an index into CarrierObjectTable (0 = hidden)
    starts = sorted(obj_refs(0x33, 0x4F8F, 0x502F) | {0x4F8F}) + [0x502F]
    for x, y in zip(starts, starts[1:]):
        d = rom[off(8, x):off(8, y)]
        t._claim(8, x, y - x, "rows", [("db", ["%d" % d[k], "%d" % d[k + 1]], None) for k in range(0, len(d), 2)], "StepPattern")
        t.obj_ptr_refs[(0x33, x)] = 8
    # bank $08 small tables
    w8 = lambda a: rom[off(8, a)] | rom[off(8, a + 1)] << 8  # noqa: E731
    t._claim(8, 0x5AE3, 0xC0, "rows", [("dw", ["$%04x" % w8(a), "$%04x" % w8(a + 2)], None) for a in range(0x5AE3, 0x5BA3, 4)],
             "=SlopeVelocities")  # x and y speed by OBJ_TERRAIN_B slope (Func_08_5aba)
    masks = [w8(0x5D93 + 2 * k) for k in range(4)]
    t._claim(8, 0x5D93, 8, "rows", [("dw", [ref(8, m) for m in masks], "by animal buddy ([$c445] bits 4-6), Func_08_5d4a")],
             "=AnimalMaskTable")
    for m in masks:
        w, h = rom[off(8, m)], rom[off(8, m + 1)]
        rows = [("db", ["%d" % w, "%d" % h], "bytes per row, rows; copied to WRAM 4 $d800, 16 bytes a row")]
        for r in range(h):
            rows.append(("db", ["%" + format(v, "08b") for v in rom[off(8, m + 2 + w * r):off(8, m + 2 + w * (r + 1))]], None))
        t._claim(8, m, 2 + w * h, "rows", rows, "AnimalMask")
    t._claim(8, 0x5F73, 5, "rows", hexrow("db", rom[off(8, 0x5F73):off(8, 0x5F78)]), "=AnimalMask_Unused_08_5f73")
    t._claim(8, 0x614E, 3, "rows", [("db", ["$fc", "$07", "$00"], "block, attribute, terrain (written by Func_00_0d9d)")], "=MapCell_08_614e")
    t._claim(8, 0x615B, 8, "rows", [("dw", ["$%04x" % w8(0x615B + 2 * k) for k in range(4)], "y offset by animal buddy (Func_08_5fe6)")],
             "=AnimalYOffsets")
    t._claim(8, 0x62B6, 20, "rows", [("db", ["%" + format(v, "08b") for v in rom[off(8, a):off(8, a + 5)]], c)
                                      for a, c in zip(range(0x62B6, 0x62CA, 5), ("x", "1", "2", "3"))],
             "=ObjectDigits")  # drawn one object per set bit by Func_08_6246
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
    for (b, a) in hints.OBJ_LISTS:
        t.parse_obj_list(b, a, b)
    for a in (0x502F, 0x5048, 0x5061, 0x507A, 0x5093, 0x50AC, 0x50C5):  # chained by OBJ_VAR_3B
        t.parse_obj_list(8, a, 8)
    for k in range(1, 17):
        o = off(8, 0x4CA0 + 8 * k + 6)
        t.parse_obj_list(8, rom[o] | rom[o + 1] << 8, 8)
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
