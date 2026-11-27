"""Names derived from tables in the ROM (manual names in hints.NAMES win).

  MusCmd_*   music command handlers, from the table at $3F0A and the macro
             names in tools/music.py
  SfxCmd_*   sound effect command handlers, from the table at $3F00
  GameState_XX  the stubs of the game-state jump table at $0300 (the state
             number is the offset from $0300)
"""
from music import MUSIC_CMDS, SFX_CMDS


def camel(macro, prefix):
    parts = macro[len(prefix):].split("_")
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def auto_names(rom):
    w = lambda a: rom[a] | rom[a + 1] << 8  # noqa: E731
    names = {}
    for op in sorted(MUSIC_CMDS):
        macro, args = MUSIC_CMDS[op]
        a = w(0x3F0A + 2 * op)
        if a == 0 or (0, a) in names:
            continue
        n = "MusCmd_" + camel(macro, "mus_")
        if args.startswith("="):
            n += args[1:].rstrip("bw")
        names[(0, a)] = n
    for op, (macro, _) in SFX_CMDS.items():
        names[(0, w(0x3F00 + op))] = "SfxCmd_" + camel(macro, "sfx_")
    for a in range(0x0301, 0x0364, 3):
        if rom[a] == 0xC3:
            names[(0, a)] = "GameState_%02X" % (a - 0x0300)
    return names
