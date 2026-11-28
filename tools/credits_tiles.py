"""Where the ending's credit pictures get their tiles from.

For each full screen the ending shows (Flow_Ending in bank $0D), counts the
distinct non-blank 8x8 tiles it uses and how many of them (allowing for
flips) also appear in a level tileset, in the sprite graphics (banks
$21-$3A), in the title pictures or in another full screen. With --mask it
also writes gfx/credits/level_tiles_mask.png: the credit pictures with every
tile that is not in a level tileset dimmed. See docs/trivia.md.

    python3 tools/credits_tiles.py [--mask]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backgrounds as bg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flipx(b):
    return bytes(int("{:08b}".format(x)[::-1], 2) for x in b)


def flipy(b):
    return b"".join(b[2 * r:2 * r + 2] for r in range(7, -1, -1))


def canon(b):
    return min(b, flipx(b), flipy(b), flipx(flipy(b)))


def blank(b):
    lo, hi = b[0::2], b[1::2]
    return len({((hi[r] >> (7 - x)) & 1) << 1 | ((lo[r] >> (7 - x)) & 1)
                for r in range(8) for x in range(8)}) <= 1


class Tiles:
    def __init__(self, rom):
        self.rom = rom

    def raw(self, bank, addr):
        o = bg.off(bank, addr)
        return bytes(self.rom[o:o + 16])

    def tileset(self, bank, addr):
        ts, out = bg.Tileset(self.rom, bank, addr), set()
        for vb in (0, 1):
            for t in range(256):
                a = ts.tile_addr(vb, t)
                if a + 16 <= 0x8000:
                    out.add(canon(self.raw(bank, a)))
        return out

    def screen(self, rec):
        """[(map position, canonical tile or None for blank)]"""
        ts, mo = bg.Tileset(self.rom, rec["bank"], rec["tiles"]), bg.off(rec["bank"], rec["map"])
        out = []
        for i in range(360):
            attr, t = self.rom[mo + i], self.rom[mo + 360 + i]
            b = self.raw(rec["bank"], ts.tile_addr((attr >> 3) & 1, t))
            out.append((i, None if blank(b) else canon(b)))
        return out


def ending_screens():
    """Screen records the ending loads, in order (from the generated source)."""
    src = open(os.path.join(ROOT, "src", "bank_0d.asm")).read()
    part = src[src.index("Flow_Ending::"):src.index("Flow_EndingHoard::")]
    syms = {}
    for ln in open(os.path.join(ROOT, "dkc.sym")):
        m = re.match(r"([0-9a-f]{2}):([0-9a-f]{4}) (\S+)", ln)
        if m:
            syms[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))
    return [syms[n] for n in re.findall(r"flow_load_screen (\w+)", part)]


def main():
    rom = open(os.path.join(ROOT, "baserom.gbc"), "rb").read()
    tl = Tiles(rom)
    level = set()
    for h, _ in bg.map_headers(rom).values():
        level |= tl.tileset(h["ts_bank"], h["ts"])
    sprite = {canon(tl.raw(b, a)) for b in range(0x21, 0x3B) for a in range(0x4000, 0x8000, 16)}
    title = set()
    for tv in bg.titles(rom):
        title |= tl.tileset(tv["ts_bank"], tv["ts"])
    credits = ending_screens()
    others = set()
    for k, rec in bg.screen_records(rom).items():
        if k not in credits:
            others |= {c for _, c in tl.screen(rec) if c}
    print("screen     tiles  level sprite  title  other  any")
    for b, a in credits:
        used = {c for _, c in tl.screen(bg.screen_record(rom, b, a)) if c}
        anyk = used & (level | sprite | title | others)
        print("%02x_%04x  %5d  %5d  %5d  %5d  %5d  %3d (%d%%)" % (
            b, a, len(used), len(used & level), len(used & sprite), len(used & title),
            len(used & others), len(anyk), 100 * len(anyk) // max(1, len(used))))
    if "--mask" in sys.argv:
        from PIL import Image, ImageDraw
        pics = [(b, a) for b, a in credits][:28]
        cols, sc = 6, 2
        rows = (len(pics) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (160 * sc + 8), rows * (144 * sc + 22)), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        for k, (b, a) in enumerate(pics):
            rec = bg.screen_record(rom, b, a)
            canvas = bg.render_screen(rom, rec)
            im = Image.new("RGB", (160, 144))
            im.putdata([p for row in canvas for p in row])
            px = im.load()
            for i, c in tl.screen(rec):
                if c is None or c in level:
                    continue
                for y in range(8):
                    for x in range(8):
                        X, Y = (i % 20) * 8 + x, (i // 20) * 8 + y
                        r_, g_, b_ = px[X, Y]
                        px[X, Y] = (r_ // 4 + 20, g_ // 4 + 20, b_ // 4 + 60)
            x, y = (k % cols) * (160 * sc + 8), (k // cols) * (144 * sc + 22)
            sheet.paste(im.resize((160 * sc, 144 * sc), Image.NEAREST), (x, y + 18))
            d.text((x + 2, y + 3), "%d  %02x_%04x" % (k + 1, b, a), fill=(255, 255, 255))
        out = os.path.join(ROOT, "gfx", "credits")
        os.makedirs(out, exist_ok=True)
        sheet.save(os.path.join(out, "level_tiles_mask.png"))
        print("wrote", os.path.join(out, "level_tiles_mask.png"))


if __name__ == "__main__":
    main()
