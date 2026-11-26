"""Manually-identified code entry points and tables (bank, address)."""

CODE = [
    # Code banks begin with their own bank number followed by code.
    (5, 0x4001), (7, 0x4001), (8, 0x4001), (9, 0x4001), (10, 0x4001), (15, 0x4001),
    (0, 0x0000), (0, 0x004B), (0, 0x0286), (0, 0x3FD5), (0, 0x00BC),
    (0, 0x0616), (0, 0x1CC2), (0, 0x2400),  # interrupt handlers installed at runtime
    (0, 0x3995),
    (0x50, 0x4000),  # extra program, far-jumped to from bank $f2 ($736a, $7571)
    (0, 0x36A7),  # sound hardware reset falling into Func_00_36b8; no caller found
    (0x55, 0x4000),  # Hi-Score screen, far-jumped to from bank $f1 ($4ec8, $4f31)
    (0, 0x1CEC), (0, 0x241D),  # interrupt handlers (push af/hl, read LY), installed at runtime
    # object handlers set by init lists the tracer doesn't parse yet, or by byte stores
    (9, 0x6A7E), (9, 0x6CCC), (9, 0x6EF8), (9, 0x72F4), (9, 0x7532), (9, 0x7A3E), (0xA, 0x5141),
    (0, 0x001B), (0, 0x0023), (0, 0x002C), (0, 0x0040), (0, 0x0048),
    (0, 0x0050), (0, 0x0058), (0, 0x0060), (0, 0x0063), (0, 0x00A1), (0, 0x0100),
]

# (bank, first entry, count, stride) of tables made of "jp nnnn" instructions
JP_TABLES = [
    (0, 0x0301, 33, 3),  # game state handlers, dispatched by the main loop
    # front end and Crosshair Cranky: "ld b,a / add a,a / add a,b / ld hl,X / ... / jp hl",
    # mostly indexed by the Crosshair Cranky game type [$cbbf]
    (0xF1, 0x4943, 8, 3), (0xF5, 0x46D8, 5, 3), (0xF5, 0x47C6, 6, 3),
    (0xFE, 0x44B9, 6, 3), (0xFE, 0x4570, 6, 3), (0xFE, 0x47FB, 6, 3), (0xFE, 0x4BA7, 5, 3),
    (0xFE, 0x4E38, 5, 3), (0xFE, 0x4FE4, 6, 3), (0xFE, 0x50AC, 6, 3), (0xFE, 0x5A39, 2, 3),
    (0xFE, 0x5CD8, 19, 3), (0xFE, 0x640E, 57, 3), (0xFE, 0x6946, 6, 3),
    # "add a,a / ld hl,X / ... / jp hl" into tables of "jr" instructions
    (0xFE, 0x5112, 8, 2), (0xFE, 0x514D, 8, 2), (0xFE, 0x5188, 8, 2), (0xFE, 0x55C1, 6, 2), (0xFE, 0x682F, 8, 2),
]

# (bank, start, count) of tables of 16-bit code pointers
PTR_TABLES = [
    (0, 0x3F00, 87),  # music sequence command handlers (UpdateMusicChannel indexes from $3F0A)
]

# Bank-0 routines that call a = bank, hl = address in another bank
FARCALL_HL_A = [0x3FC0]

# Human-chosen names for code labels: (bank, address) -> name
NAMES = {
    (0, 0x0000): "OldFarCall",       # rst $00 far call with inline args (appears unused)
    (0, 0x001A): "CallHL",           # "call CallHL" = call [hl]
    (0, 0x001B): "OAMDMARoutine",    # copied to HRAM at $ffc8
    (0, 0x0023): "CopyBytes",        # copy bc bytes from de to hl
    (0, 0x002C): "FillMemory",       # fill bc bytes at hl with a
    (0, 0x0038): "Rst38",
    (0, 0x0040): "VBlankInterrupt",  # jumps to a RAM trampoline at $c32d
    (0, 0x0048): "LCDInterrupt",     # jumps to a RAM trampoline at $c330
    (0, 0x0050): "TimerInterrupt",
    (0, 0x0058): "SerialInterrupt",
    (0, 0x0060): "JoypadInterrupt",
    (0, 0x0063): "ReadJoypad",
    (0, 0x0100): "Start",
    (0, 0x0150): "Init",
    (0, 0x028C): "NotGBC",           # shows the "GBC only" screen on DMG
    (0, 0x3FC0): "FarCall_A_HL",     # call a:hl, used by the banks $f0+ program
    (0, 0x167D): "InitObjectSlots",  # puts slots 1-31 on the free list
    (0, 0x182F): "InitObject",       # ApplyObjInit, then sets flags from field $2a
    (0, 0x188B): "ApplyObjInit",     # apply the initialiser list at hl to object bc
    (0, 0x18C0): "AllocObject",      # bc = free $40-byte slot offset; carry if full
    (0, 0x3980): "RunObjects",       # call OBJ_HANDLER (in OBJ_BANK) of each object
    (0, 0x3995): "NextObject",       # handlers jump here when done; runs the next slot
    (0, 0x30F1): "PlaySong",         # a = song id
    (0, 0x3167): "UpdateSound",
    (0, 0x31B7): "UpdateMusic",      # steps the four channels at $d000-$d3ff
    (0, 0x3220): "UpdateMusicChannel",
    (0, 0x2CA6): "PreloadObjPalettes",   # hl = preload list (bank $80)
    (0, 0x2CFB): "AllocObjPalette",      # a = palette ID -> a = hardware slot
    (0, 0x2D5A): "FreeObjPalette",       # a = palette ID
    (0, 0x2D78): "UpdatePalettes",       # apply brightness, upload what changed
    (0, 0x2DAB): "LoadBGPalettesHL",
    (0, 0x2DBA): "UploadBGPalettes",
    (0, 0x2DDF): "LoadOBJPalettesHL",
    (0, 0x2DED): "UploadOBJPalettes",
    (0, 0x2E12): "FadePalettesToBlack",  # a = brightness; wBG/OBJPalettes -> ...Out
    (0, 0x2E44): "FadePalettesToWhite",  # same, towards white
    # Front end (banks $F0-$FF)
    (0xF0, 0x6ADA): "FE_DrawText",           # b = text table, c = entry (table at $F0:6F21), de = position
    (0xF0, 0x6C80): "FE_GetTextPointer",     # [$c805] = language; -> [$c800] = bank, hl = text
    (0xF1, 0x4019): "FE_Main",               # d -> [$c981] (what to run), e -> [$c982] (its argument)
    (0xF1, 0x41BF): "FE_RaiseCrankyUnlock",  # [$b0c7] = max([$b0c7], l)
    (0xF1, 0x4B19): "FE_LoadRing",           # ring [$c96e] from the table at $F1:67BF
    (0xF1, 0x5162): "FE_DrawRingLabel",      # label id [$c967 + cursor], (sheet, row) from text table 0
    # Crosshair Cranky (bank $FE)
    (0xFE, 0x4000): "CrosshairCranky",       # h = island node 1-6 (single player)
    (0xFE, 0x4003): "CrosshairCrankyLink",   # h = mode 0-4 (link play)
    (0xFE, 0x40AE): "CrankyModeToGame_Unused",  # older remap table {3,4,1,2,0,5}; nothing calls it
    (0xFE, 0x41B5): "CrankyModeToGame",      # [$cbbf] = {4,1,3,0,2,5}[[$cbbf]]
    (0xFE, 0x440D): "CrankyShowInstructions",  # text table 5 entry [$cbbf]; none for 5 (Galleon Gunner)
}

# Generated source files that have been edited by hand and must not be
# regenerated by tools/emit.py (paths relative to the repo root).
KEEP = set()

# Banks where unreached gaps may be traced speculatively (see tracer.Speculator).
SPECULATE_BANKS = [0, 4, 5, 7, 8, 9, 10, 15] + list(range(0x50, 0x57)) + list(range(0xF0, 0xFF))

# Bank-0 routines that apply an object initialiser list at hl to the object
# in bc (see Func_00_188b).
OBJ_INIT_FUNCS = [0x188B, 0x182F]

# Runs of consecutive object initialiser lists: (bank, start, end).
# Bank $0e holds the lists that level data refers to (spawned by Func_00_17xx
# via Func_00_182f with bank $0e mapped).
OBJ_LIST_RUNS = [
    (0x0E, 0x4000, 0x79F4),
]

# Tables of pointers to object initialiser lists: (bank, start, count)
OBJ_LIST_TABLES = [
    (0x0A, 0x443C, 4),
    (0x08, 0x583A, 13),  # picked by Func_08_5814 and InitObject
    (0x0A, 0x4A47, 10),  # spawned objects, indexed by a counter (Func_0a_4a2c area)
]

# Single object initialiser lists the tracer misses (applied after a branch)
OBJ_LISTS = [(0x09, 0x485E)]

# Object slot layout. Objects are $40-byte slots at wObjects ($c800) + bc;
# slot 0 is the player (wPlayer). offset -> (name, size, description).
# Offsets not listed here are written as OBJ_VAR_xx: per-object-type
# variables whose meaning depends on the handler.
OBJ_FIELD_TABLE = {
    0x00: ("OBJ_FLAGS", 1, "bit 2: counted in a spawn group (see OBJ_VAR_2D); bit 5: flicker"),
    0x01: ("OBJ_BANK", 1, "ROM bank of OBJ_HANDLER and OBJ_TOUCH_HANDLER"),
    0x02: ("OBJ_HANDLER", 2, "code run every frame by RunObjects"),
    0x04: ("OBJ_TOUCH_HANDLER", 2, "jumped to when the player comes within range (tentative)"),
    0x06: ("OBJ_GROUND_Y", 2, "height of the terrain under the object (Func_00_2214)"),
    0x08: ("OBJ_TERRAIN_A", 1, "attribute of the tile under the object (Func_00_2214)"),
    0x09: ("OBJ_TERRAIN_B", 1, "second attribute of that tile (Func_00_2214)"),
    0x0D: ("OBJ_TARGET_XVEL", 2, "X velocity that OBJ_XVEL accelerates towards"),
    0x0F: ("OBJ_XACCEL", 2, "per-frame step from OBJ_XVEL towards OBJ_TARGET_XVEL"),
    0x11: ("OBJ_XVEL", 2, "X velocity, 1/256 pixel per frame"),
    0x13: ("OBJ_XSUB", 1, "X position, fraction"),
    0x14: ("OBJ_X", 2, "X position in pixels"),
    0x16: ("OBJ_TARGET_YVEL", 2, "Y velocity that OBJ_YVEL accelerates towards (max fall speed)"),
    0x18: ("OBJ_YACCEL", 2, "per-frame step from OBJ_YVEL towards OBJ_TARGET_YVEL (gravity)"),
    0x1A: ("OBJ_YVEL", 2, "Y velocity, 1/256 pixel per frame"),
    0x1C: ("OBJ_YSUB", 1, "Y position, fraction"),
    0x1D: ("OBJ_Y", 2, "Y position in pixels"),
    0x1F: ("OBJ_OAM_ATTR", 1, "OAM attributes for every sprite of the object (palette, flip)"),
    0x20: ("OBJ_FRAME", 2, "current sprite frame pointer, set by the animation"),
    0x22: ("OBJ_ANIM", 2, "animation script pointer (bank $04), run by Func_00_127d"),
    0x24: ("OBJ_ANIM_SPEED", 1, "frames per animation step"),
    0x25: ("OBJ_ANIM_TIMER", 1, "frames left in the current animation step"),
    0x26: ("OBJ_ANIM_FLAGS", 1, "bit 7 is cleared by an animation command (tentative)"),
    0x27: ("OBJ_SPAWN_INDEX", 1, "index into the level object tables at $a8xx-$afxx; 0 = none"),
    0x28: ("OBJ_ANIM_PARAM", 1, "set by an animation command, read by handlers (tentative)"),
    0x29: ("OBJ_COLLISION", 1, "collision/interaction flags, cleared on delete (tentative)"),
    0x2A: ("OBJ_PALETTE", 1, "object palette slot, allocated by InitObject"),
    0x2B: ("OBJ_LAYER", 1, "sprite layer used when drawing (Func_00_1341)"),
}

# Banks of the separate program that has its own memory map (stack at
# $cff6, different HRAM and WRAM use), so main-game RAM names don't apply.
SECOND_PROGRAM_BANKS = set(range(0xF0, 0xFF)) | set(range(0x50, 0x70))

# Main-game RAM variables (not used for SECOND_PROGRAM_BANKS): address -> name
RAM_NAMES = {
    0xC400: "wObjectFreeList",   # stack of free slot offsets (words)
    0xC440: "wObjectFreeCount",  # number of entries in wObjectFreeList
    0xC100: "wBGPalettes",        # 8 BG palettes as the level/screen defines them
    0xC180: "wOBJPalettes",       # 8 OBJ palettes (slots handed out by AllocObjPalette)
    0xC200: "wBGPalettesOut",     # wBGPalettes after brightness, uploaded to the LCD
    0xC280: "wOBJPalettesOut",
    0xC311: "wPaletteUpdate",     # bit 0: upload BG, bit 1: upload OBJ, bit 2: fade mode
    0xC312: "wPaletteBrightness",
    0xC449: "wLevelEntrance",     # pointer to the current LevelEntrance record
}

# Animation scripts (see Func_00_127d): runs of consecutive entries
# (bank, start, end).
ANIM_RUNS = [
    (0x04, 0x4001, 0x5747),
]

# Frame header tables (see Func_00_1037): (bank, start, count)
FRAME_TABLES = [
    (0x20, 0x4000, 1415),
]

# Palettes (bank $80). Object palette p (OBJ_PALETTE) is 4 colors at
# $4000 + 8p; InitObject copies colors 1-3 into a free hardware slot.
# BG palette sets are 8 palettes each, picked by the level descriptor.
# Preload lists (count, then palette IDs) fill the OBJ slots in order
# (Func_00_2ca6).
PALETTES = {
    "bank": 0x80,
    "obj_palettes": (0x4000, 64),
    "preload_lists": (0x4200, 0x4257),
    "bg_palette_sets": (0x4257, 55),
}
PRELOAD_FUNCS = [0x2CA6]

# Levels (bank $04): LevelTable has two entrance-record pointers per level
# number ([$c30c]); records point to 12-byte level descriptors.
LEVELS = {
    "table": (0x04, 0x57B4, 42),
    "entrances": (0x585C, 0x5FC4),    # 237 records; the table reaches 75 (others via warps)
    "descriptors": (0x5FC4, 0x65C4),  # 128 descriptors, all reached by some record
}

# Banks searched for tables of frame header pointers (tracer.scan_frame_tables)
FRAME_TABLE_SCAN_BANKS = list(range(0x00, 0x10))

# Records that mix frame pointers with other words:
# (bank, start, count, words per record, columns that are frames)
FRAME_STRUCTS = [
    (0x0A, 0x60E7, 32, 4, (0, 2, 3)),  # rotating object: frame by angle; column 1 is a curve
]

# Flow script (bank $0d, Func_00_38cd): entry points set by code
# (ld de, X / call Func_00_38c7) and the per-world table at $3976.
FLOW_ENTRIES = [0x5F58, 0x5F90, 0x5F92, 0x5F96, 0x5F9C, 0x5FA5, 0x5FB7, 0x5FBE, 0x5FC1,
                0x618F, 0x619A, 0x61A5, 0x61B0, 0x61BB, 0x6184]

# Routines that start the flow script at de (bank $0d)
FLOW_FUNCS = [0x38C7]

# World map records: (bank, pointer table, count). The table is indexed by
# [$c30a], which comes from the per-location table at $05:491e.
WORLD_MAPS = (0x05, 0x4AA9, 8)

# Far jump used by the extra programs: push the return address ($3fd5) and
# the target address a byte at a time ("ld a, n / push af / inc sp"), put
# the bank in a and jump here; it switches banks and returns into the target.
FARJUMP_STACK = [0x3FDC]

# Far jump of the program in banks $50+: its runtime (copied from $51:42f4
# to $cb00) jumps through $cb99 with the bank in a and the target pushed
# last (return address, bank and the cleanup routine $cba7 pushed before).
FARJUMP_HL_STACK = [0xCB99]

# Funky's Fishing (bank $51), loaded by Func_51_410f (tiles, HDMA) and
# Func_51_4000 (palettes, screens, box). Tile pieces: (start, tiles,
# VRAM bank, destination).
FISHING = {
    "bank": 0x51,
    "tiles": [(0x4D00, 0x7E, 0, 0x8000), (0x54E0, 0x80, 0, 0x9000), (0x5CE0, 0x78, 0, 0x8800),
              (0x6460, 0x02, 1, 0x9000), (0x6480, 0x36, 1, 0x8CA0), (0x67E0, 0x2B, 1, 0x8800)],
    "screens": [0x6A90, 0x6D60],   # one player; link play
    "box": 0x7030,                 # 12x4: 48 attributes, then 48 tiles, drawn at $98b4
    "bg_palettes": 0x7090,
    "obj_palettes": 0x70D0,
}

# Title screen pictures (bank $07, Func_07_4001). [$b0c1] & 3 picks one of
# four slots; slot 3 repeats slot 2, so there are three pictures. Tables:
# map pointers, palette pointers (256 bytes = 32 palettes), tilesets (bank,
# address) and palette-swap lists ((scroll line, source palette*8, $80 |
# slot*8), ending with $ff; Func_07_4195 applies them as the title scrolls).
TITLES = {"bank": 0x07, "maps": 0x4117, "palettes": 0x411F, "tilesets": 0x4127, "lists": 0x4133, "count": 4}

# The front end's picture table (bank $f0): 149 records of (map, palettes,
# tiles), each a (bank, address) pair, indexed by number. Maps of the
# first records are 720 bytes (360 attributes, then 360 tile numbers);
# the rest are 360 tile numbers with attribute 0. Tiles are laid out in
# VRAM like a level tileset (see backgrounds.Tileset); tile data runs on
# across bank boundaries.
PICTURES = {"bank": 0xF0, "table": 0x54E7, "count": 149, "full_maps": 6}

# Sound driver tables (bank 0) and data (see tools/banks.py)
SOUND = {
    "songs": 35,
    "song_banks": 0x30CE,    # db bank per song (PlaySong)
    "tempos": 0x3789,        # db per song -> $c322
    "song_table": 0x37AC,    # 4 channel stream pointers per song
    "note_periods": (0x3607, 63),   # dw frequency register values
    "table_3685": (0x3685, 17),     # dw, purpose unknown (follows the periods)
    "wave_patterns": (0x36F8, 9),   # 16-byte wave RAM patterns (Func_00_36b8)
    "sfx_table": (0x02, 0x70E4),    # dw per effect, indexed by id & $fe (Func_00_2f5a)
}

CAMERA_BANK = 0x06   # camera regions, pointed to by map headers ($c45c)

# Funky's Fishing digitized samples, played through NR50 by its timer interrupt
SAMPLES = {"bank": 0x52, "table": 0x41C2, "count": 11}

# Full screens loaded by code rather than the flow script (Func_00_2c48 with
# the bank in b): the world map's shops, picked by location type [$c30c]
EXTRA_SCREENS = [
    ((0x43, 0x6720), "Candy's Challenge"),   # Func_0f_4001, type 2
    ((0x43, 0x6726), "Cranky's Cabin"),      # Func_0f_40a9, types 0 and 3
    ((0x42, 0x75E0), "Funky's Flights"),     # Func_0f_412e, type 1
    ((0x74, 0x5490), "DK's banana hoard"),  # Func_0f_41c2, type 4, song $09
]

# Tile data found by what loads it, outside the level/screen/picture tables:
# (bank, address, tile count, what it is)
EXTRA_TILES = [
    (0x40, 0x4000, 128, "dialogue font for the shops and maps (Func_0f_4001 etc., VRAM bank 1)"),
    (0x40, 0x4800, 9, "world map arrows and icons"),
    (0x40, 0x4A28, 256, "the DMG 'needs a Game Boy Color' screen (NotGBC copies $1000 bytes)"),
    (0x41, 0x4000, 312, "world map sprites (8x16 objects)"),
    (0x0D, 0x4010, 16, "Rare logo: rounded corner sprites"),
    (0x0D, 0x5980, 88, "Rare logo tiles (Func_0d_4216 copies $580 bytes)"),
    (0xFF, 0x6B30, 250, "front-end fonts"),
    # Crosshair Cranky animated background tiles (frames listed by $fe:79cf)
    (0xF5, 0x4AF0, 48, "Crosshair Cranky: Buddies Beware tile animation frames"),
    (0xF5, 0x4FF0, 320, "Crosshair Cranky: Kremlings and Kongs tile animation frames"),
    (0xF5, 0x63F0, 320, "Crosshair Cranky: Kremling Krackdown tile animation frames"),
    (0xF5, 0x77F0, 44, "Crosshair Cranky: Galleon Gunner tile animation frames"),
    (0xF5, 0x4DF0, 32, "Crosshair Cranky: tiles copied by Func_fe_541c"),
    (0x07, 0x6000, 12, "title screen sprite tiles (copied to VRAM $81c0)"),
    (0x08, 0x7800, 128, "animal buddy icons (Rambi, Expresso, Enguarde, Winky), 8x16 sprites"),
]

# Front-end text in bank $ff that the text tables don't reach: per language
# the Winner/Loser lines, menu words read by address and length ("PAUSED",
# "CONTINUE", ...), $87-separated label lists and the closing message.
FE_TEXT_RUNS = [(0x4669, 631), (0x4C06, 14), (0x4EF3, 737), (0x586E, 699), (0x5E77, 22),
                (0x615B, 705), (0x677C, 22), (0x6A99, 128)]

# Framed thumbnails in bank $f3, listed by an 18-record table in bank $f1
# (slot, x, y, bank, tiles little-endian, width, height in tiles); read while
# browsing stickers
THUMBNAILS = {"table": (0xF1, 0x693A), "count": 18}
