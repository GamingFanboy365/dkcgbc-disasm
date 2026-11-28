"""Main-game RAM variables: WRAM, save RAM and HRAM.

Each entry is (address, size in bytes, name, description). An access to
address + k inside a variable is written "name + k". The front-end program
(banks $F0-$FE) and the programs in banks $50+ have their own memory maps
and don't use these names (see hints.SECOND_PROGRAM_BANKS).

Names were chosen from the routines that read and write each address;
"(tentative)" marks those whose purpose is less certain. include/ram.inc
is generated from this list.
"""

WRAM = [
    # sprites are drawn into three layer buffers ($c500, $c600, $c700) and
    # merged into wShadowOAM, front to back (CopyOAMBuffersForward/Backward)
    (0xC000, 0xA0, "wShadowOAM", "sprite attributes, copied to OAM by DMA"),
    (0xC100, 0x80, "wBGPalettes", "8 BG palettes as the level or screen defines them"),
    (0xC180, 0x80, "wOBJPalettes", "8 OBJ palettes (slots handed out by AllocObjPalette)"),
    (0xC200, 0x80, "wBGPalettesOut", "wBGPalettes after brightness, uploaded to the LCD"),
    (0xC280, 0x80, "wOBJPalettesOut", "wOBJPalettes after brightness"),
    (0xC300, 3, "wRandomState", "Random's seed, $ff $ff $f8 at power-on"),
    (0xC303, 2, "wFlowPointer", "next command of the flow script (bank $0d), RunFlowScript"),
    (0xC305, 1, "wFlowArg1", "first argument of the current state: fade flags, song, wait timer (low)"),
    (0xC306, 1, "wFlowArg2", "second argument: fade brightness, wait timer (high)"),
    (0xC307, 1, "wFlowArg3", "third argument"),
    (0xC309, 1, "wSaveFile", "save file in use (0-2; 3 = the system record); its record is at sSaveFile0 + $40 * n"),
    (0xC30A, 1, "wWorld", "current world map (0-7), from the location table at $05:491e"),
    (0xC30B, 1, "wMapLocation", "current location on the world map"),
    (0xC30C, 1, "wLevel", "current level number; also the location type at a shop"),
    (0xC30D, 1, "wLanguage", "language; the text bank is $10 + wLanguage"),
    (0xC30E, 1, "wGameModeBit", "1, 2 or 4: which completion bit of a level's save byte this game sets "
                                "(2 and 4 picked by sOptions bits 0 and 1; tentative)"),
    (0xC30F, 1, "wKongs", "bit 0: Diddy leads (else DK), bit 1: the partner Kong is along, "
                          "bit 3: riding an animal, bits 4-5: which (Rambi, Expresso, Enguarde, Winky)"),
    (0xC310, 1, "wMapFlags", "bit 0: cleared at a level clear, bit 5: set in Cranky's Cabin, "
                             "bit 6: a level was newly cleared, bit 7: the Kong travels at double "
                             "speed with another sprite, as in Funky's Flights (tentative)"),
    (0xC311, 1, "wPaletteUpdate", "bit 0: upload BG, bit 1: upload OBJ, bit 2: fade mode"),
    (0xC312, 1, "wPaletteBrightness", ""),
    (0xC313, 4, "wAnimalTokens", "animal tokens held, one byte per animal; three start an animal bonus"),
    (0xC317, 4, "wAnimalTokensPending", "animal tokens collected in this level, added to wAnimalTokens when it ends"),
    (0xC31B, 1, "wBananas", "banana count (BCD); 100 give an extra life"),
    (0xC31C, 1, "wBananasPending", "bananas collected but still flying to the counter"),
    (0xC31D, 1, "wLives", "lives (BCD); $ff is treated as a special value by State_Level and GiveExtraLife (tentative)"),
    (0xC31E, 1, "wLivesOver99", "extra lives beyond 99"),
    (0xC31F, 1, "wLivesPending", "extra lives collected but not yet added"),
    (0xC320, 1, "wStickers", "stickers found (BCD)"),
    (0xC321, 1, "wMusicTempoCounter", "music tempo accumulator; a carry is a music tick"),
    (0xC322, 1, "wMusicTempo", "added to wMusicTempoCounter every frame (from the song's tempo)"),
    (0xC323, 1, "wMusicTick", "bit 7 set on frames the music advances"),
    (0xC324, 1, "wMusicSweep", "NR10 value for the music (MusCmd_Sweep)"),
    (0xC327, 1, "wMusicBank", "ROM bank of the song playing"),
    (0xC328, 1, "wSong", "song playing; PlaySong ignores a request for it"),
    (0xC329, 4, "wSFXQueue", "sound effect to start on each of the four SFX slots, 0 = none (StartQueuedSFX)"),
    (0xC32D, 3, "wVBlankTrampoline", "jp to the VBlank handler of the current state"),
    (0xC330, 3, "wLCDTrampoline", "jp to the LCD (STAT) handler"),
    (0xC333, 3, "wOldFarCallTrampoline", "jp used by OldFarCall"),
    (0xC336, 2, "wFrameCounter", "counts frames; wraps at $0e00 (one minute) into wPlayTimeMinutes"),
    (0xC338, 1, "wPlayTimeMinutes", "play time minutes (BCD)"),
    (0xC339, 1, "wPlayTimeHours", "play time hours (BCD)"),
    (0xC340, 12, "wFileSummaries", "files 0-2 for the front end: completion (word), hours, minutes "
                                   "(Save_ComputeSummaries)"),
    (0xC380, 0x40, "wMapColumnBuffer", "tile and attribute pairs of the BG column to write (WriteScrollEdges)"),
    (0xC3C0, 0x40, "wMapRowBuffer", "tile and attribute pairs of the BG row to write"),
    (0xC400, 0x40, "wObjectFreeList", "stack of free object slot offsets (words)"),
    (0xC440, 1, "wObjectFreeCount", "number of entries in wObjectFreeList"),
    (0xC441, 1, "wHUDFlags", "bit 0: show the banana counter, bit 1: show lives, "
                             "bit 2: collected items are not counted (tentative)"),
    (0xC442, 1, "wHUDState", "bits set while the HUD counters slide out"),
    (0xC443, 1, "wLevelFlags", "bit 0: paused, bit 1: leave the level, bit 2-3, 6: how it is left, "
                               "bit 4: pausing allowed, bit 5: leaving from the pause screen allowed, "
                               "bit 7: three animal tokens collected"),
    (0xC444, 1, "wEntranceKind", "last byte of the entrance record; low nibble 2 = arrived by mine cart"),
    (0xC445, 1, "wLevelKind", "first byte of the level descriptor; bits 0-2 the level type "
                              "(4 Stop & Go, 5 Loopy Lights, 6 flickering lights, 7 snowflakes), "
                              "bits 4-6 the animal bonus"),
    (0xC446, 2, "wLevelTimer", "per-level counter: Stop & Go and lights timers, mine cart fuel, "
                               "animal bonus tokens"),
    (0xC448, 1, "wItemsInFlight", "collected items still flying to the HUD"),
    (0xC449, 2, "wLevelEntrance", "pointer to the current LevelEntrance record (bank $04)"),
    (0xC44B, 2, "wReturnEntrance", "entrance to go back to when leaving a bonus level"),
    (0xC44D, 1, "wShopExit", "shop result: $ff leave, $fe fly away (Funky's Flights)"),
    (0xC44E, 1, "wShopChoice", "shop's selected option (tentative)"),
    (0xC44F, 1, "wLastRandom", "RandomBelow's last result, so the next differs"),
    (0xC450, 1, "wCameraPlayerX", "where the camera keeps the player across the screen"),
    (0xC451, 1, "wCameraPlayerY", "where the camera keeps the player down the screen"),
    (0xC452, 2, "wCameraShiftX", "extra camera X offset, eased back to 0"),
    (0xC454, 2, "wCameraShiftY", "extra camera Y offset, eased back to 0"),
    (0xC456, 2, "wCameraGroundY", "height of the ground the player last stood on, followed by the camera"),
    (0xC458, 2, "wMapRowDest", "BG map address of the row in wMapRowBuffer"),
    (0xC45A, 1, "wMapColumnDest", "low byte of the BG map address of the column in wMapColumnBuffer; "
                                  "$ff = none"),
    (0xC45C, 16, "wCameraRegion", "camera region record (bank $06): left, right, top, bottom edges; "
                                  "while a map loads, its first word points to the map's regions"),
    (0xC46C, 4, "wSpawnRangeX", "left and right edge of the area objects spawn in"),
    (0xC470, 4, "wSpawnRangeY", "top and bottom edge of the spawn area"),
    (0xC474, 4, "wDespawnRangeX", "left and right edge of the area objects stay alive in"),
    (0xC478, 4, "wDespawnRangeY", "top and bottom edge of that area"),
    (0xC480, 0x80, "wSnowflakes", "snowflake positions (Snowflakes)"),
    (0xC500, 0x100, "wRasterTable", "LYC and scroll values per screen split (world map)"),
]
WRAM += [
    # title screen (Title_Init, Title_UpdatePalettes, RasterLCDHandler)
    (0xCE00, 0x40, "wTitlePalettes", "title BG palettes with the swaps for the current scroll applied"),
    (0xCF00, 0x60, "wTitlePaletteSwaps", "palette swap list (scroll line, source*8, $80 | slot*8), $ff-terminated"),
    (0xCF60, 1, "wTitleScrollY", "title picture scroll, copied to rSCY"),
    (0xCF61, 1, "wTitleTimer", "frames left in the current step"),
    (0xCF62, 1, "wTitleStep", "step of the title sequence: fade in, wait, scroll, fade out..."),
    (0xCF63, 1, "wTitleSwapPos", "next swap RasterLCDHandler applies this frame"),
    (0xCF64, 1, "wTitleSwapStart", "first swap below the top of the screen"),
    (0xCF65, 1, "wTitleBrightness", "fade level of the title"),
    # interrupt trampolines the second programs install (jp nnnn)
    (0xCFF7, 3, "wTimerTrampoline", "jp to the timer interrupt handler"),
    (0xCFFA, 3, "wSerialTrampoline", "jp to the serial interrupt handler"),
    (0xCFFD, 3, "wJoypadTrampoline", "jp to the joypad interrupt handler"),
    # world map ($c600-$c616; in levels $c500-$c7ff hold the sprite layer buffers)
    (0xC600, 1, "wMapKongFlags", "bit 1: the Kong faces left"),
    (0xC601, 1, "wMapScrollX", "world map scroll, in columns"),
    (0xC602, 1, "wMapScrollMax", "rightmost scroll of this world map"),
    (0xC603, 1, "wMapUnused_c603", "copied from the world map record, never read"),
    (0xC604, 2, "wMapNodes", "pointer to the world map's node table (4 bytes a node: x, y, ...)"),
    (0xC606, 1, "wMapColumnToDraw", "next BG column DrawWorldMapColumn draws"),
    (0xC607, 1, "wMapLevelsCleared", "cleared levels counted by WorldMap_SetUpMarkers; picks the sign tiles"),
    (0xC608, 1, "wMapNode", "node the Kong stands at or walks to"),
    (0xC609, 2, "wMapKongXVel", "X step per frame while walking (AddSignedWordTo24 onto wMapKongX)"),
    (0xC60B, 3, "wMapKongX", "Kong's X: fraction, then pixels (word)"),
    (0xC60E, 2, "wMapKongYVel", "Y step per frame while walking"),
    (0xC610, 3, "wMapKongY", "Kong's Y: fraction, then pixels"),
    (0xC613, 2, "wMapPath", "next byte of the path being walked ($ff ends it)"),
    (0xC615, 1, "wMapStepFrames", "frames left in the current step"),
    (0xC616, 1, "wMapNodeSong", "song of the node last entered; $ff after loading the map"),
    # switchable WRAM ($d000-$dfff): the bank is chosen with rSVBK
    (0xD000, 0, "wWRAMX", "start of the switchable WRAM bank: map data (banks 1-3, 5-7), "
                          "sound channels (bank 4), screen maps being loaded"),
    (0xD01F, 1, "wMusicChannelActive", "WRAM bank 4: nonzero while music channel 1 plays; "
                                       "channels 2-4 are $100 apart"),
    (0xD020, 0, "wTextBuffer", "LoadTextString's output"),
    (0xD039, 1, "wMusicSweepActive", "WRAM bank 4: nonzero while channel 1 uses its own sweep"),
    (0xD400, 0x100, "wBonusesFound", "WRAM bank 4: per level two words, bonuses found and their union "
                                     "(compared with LevelBonusMasks)"),
    (0xD500, 0x7E, "wPlatforms", "WRAM bank 4: platforms objects can stand on this frame"),
    (0xD57E, 0x7E, "wPlatformsNext", "WRAM bank 4: platforms registered during this frame"),
    (0xD5FC, 1, "wPlatformsNextSize", "bytes in wPlatformsNext"),
    (0xD5FD, 1, "wPlatformsCount", "entries in wPlatforms"),
    (0xD5FE, 1, "wPlatformsNextCount", "entries in wPlatformsNext"),
    (0xD600, 0x80, "wObjPaletteSlots", "WRAM bank 4: OBJ palette slot of each preloaded palette"),
    (0xD680, 8, "wFreeObjPaletteSlots", "WRAM bank 4: OBJ palette slots not taken by the preload list"),
    (0xD800, 0x400, "wTileAnimBuffer", "WRAM bank 4: the animal bonus mask, tiles of animated objects"),
]

# Other uses of RAM that the lists above name differently; reached through
# high bytes (ld h, $c5) rather than full addresses. Written to ram.inc only.
UNIONS = [
    (0xC500, 0x100, "wSpriteLayer0", "in levels: sprites of layer 0 (front), merged into wShadowOAM"),
    (0xC600, 0x100, "wSpriteLayer1", "in levels: layer 1"),
    (0xC700, 0x100, "wSpriteLayer2", "in levels: layer 2 (back)"),
    (0xC900, 0x100, "wMapNodeData", "on the world map: a byte per node (bits 0-6 its song)"),
]

# Shadow OAM's end, used as a pointer
WRAM_EXTRA = [
    (0xC0A0, 0, "wShadowOAMEnd", "end of wShadowOAM"),
]

# Save RAM. SRAM bank 0: $a000-$afff is work RAM cleared at power-on;
# $b000-$b0ff the save files, with backup copies at $b100, $b200 and $b300.
SRAM = [
    (0xA000, 0x800, "sWorkRAM", "cleared at power-on"),
    (0xA800, 0x800, "sLevelObjects", "the level's object tables, $100 bytes apart (BuildSpawnGrid)"),
    (0xB000, 0x40, "sSaveFile0", "save file 1 (layout: SAVE_* in include/ram.inc)"),
    (0xB040, 0x40, "sSaveFile1", "save file 2"),
    (0xB080, 0x40, "sSaveFile2", "save file 3"),
    (0xB0C0, 1, "sSystemFile", "fourth record: settings shared by the files"),
    (0xB0C1, 1, "sTitlePicture", "title screen picture, advanced at every power-on (0-2)"),
    (0xB0C2, 3, "sStickersFound", "one bit per sticker found in any file"),
    (0xB0C5, 1, "sMostBonusCoins", "most bonus coins in any file; unlocks link modes in the front end"),
    (0xB0C6, 1, "sOptions", "set by the front end: bits 0-1 game mode (see wGameModeBit), "
                            "bit 2: sound effects off"),
    (0xB0C7, 1, "sCrankyUnlock", "Crosshair Cranky unlock level (0-6)"),
    (0xB100, 0x100, "sSaveBackup1", "copies of the four records"),
    (0xB200, 0x100, "sSaveBackup2", ""),
    (0xB300, 0x100, "sSaveBackup3", ""),
]

# Offsets in a save file record
SAVE_FIELDS = [
    (0x00, "SAVE_LEVELS", "a byte per level: bits 0-2 cleared (per wGameModeBit), bit 3 first "
                          "cleared with Diddy leading, bit 4 every bonus found, bit 5 sticker taken; "
                          "bit 6 of the byte numbered by a world: its bonus coin taken"),
    (0x30, "SAVE_HOURS", "play time"),
    (0x31, "SAVE_MINUTES", ""),
    (0x32, "SAVE_WORLD", "world reached, one byte per game mode"),
    (0x35, "SAVE_BONUS_COINS", "bonus coins collected"),
    (0x3E, "SAVE_CHECKSUM", "word over bytes $00-$3d, seeded with $aa55 (Save_Checksum)"),
]

HRAM = [
    (0xFF80, 1, "hJoyHeld", "buttons held (bit 0 A, 1 B, 2 Select, 3 Start, 4-7 Right Left Up Down)"),
    (0xFF81, 1, "hJoyPressed", "buttons pressed this frame"),
    (0xFF82, 1, "hJoyUsed", "buttons the player code has acted on; a bit clears when the button is let go"),
    (0xFF83, 1, "hVBlankDone", "set by DoOAMDMA; the main loop waits for it"),
    (0xFF84, 1, "hGameState", "low byte of the current state's entry in the jump table at $0301"),
    (0xFF85, 1, "hMapBlockBank", "ROM bank of the map's blocks (the next bank holds the rest)"),
    (0xFF86, 1, "hMapTerrainBank", "ROM bank of the map's terrain shapes (GetTerrainUnderObject)"),
    (0xFF87, 1, "hMapBlockRow", "offset of the tile row or column inside a block while drawing"),
    (0xFF88, 1, "hMapFlags", "bit 0: vertical level, bit 1: map has the extra layers in WRAM 5-7, "
                             "bit 7: camera held still"),
    (0xFF89, 2, "hCameraX", "camera position, copied to rSCX"),
    (0xFF8B, 2, "hCameraY", "copied to rSCY"),
    (0xFF8D, 2, "hCameraMinX", "camera region edges (SetCameraRegion)"),
    (0xFF8F, 2, "hCameraMinY", ""),
    (0xFF91, 2, "hCameraMaxX", ""),
    (0xFF93, 2, "hCameraMaxY", ""),
    (0xFF95, 2, "hScratch2", "scratch: HUD item bits, banana bunch positions"),
    (0xFF97, 2, "hSpriteY", "screen position of the sprite frame being drawn"),
    (0xFF99, 2, "hSpriteX", ""),
    (0xFF9B, 1, "hSpriteAttr", "OAM attributes of the frame being drawn; also scratch"),
    (0xFF9C, 1, "hScratch3", "scratch"),
    (0xFF9D, 2, "hSpriteFrame", "frame being drawn"),
    (0xFF9F, 1, "hSpriteLayerPos", "fill position in the sprite layer buffer"),
    (0xFFA0, 1, "hSpriteLayerHigh", "high byte of that buffer ($c5-$c7)"),
    (0xFFA1, 1, "hSpriteBufferPhase", "flips every frame: bit 0 picks the VRAM bank of sprite tiles"),
    (0xFFA2, 3, "hSpriteLayerFill", "bytes used in each sprite layer buffer ($c500, $c600, $c700)"),
    (0xFFA5, 1, "hSpriteTileSpace", "sprite tile space left this frame ($60 at the start; tentative)"),
    (0xFFA6, 1, "hObjectRunMask", "RunObjects runs the objects whose OBJ_FLAGS share a bit with this"),
    (0xFFA7, 1, "hContactFlags", "collision flags of the player's last contact (tentative)"),
    (0xFFA8, 8, "hScratch", "scratch: contact and terrain checks, bonus games"),
    (0xFFB0, 2, "hContactObject", "slot of the object touching the player"),
    (0xFFB2, 2, "hTempX", "scratch position, e.g. where SpawnObjectDigits puts digits"),
    (0xFFB4, 2, "hTempY", ""),
    (0xFFB6, 2, "hTempX2", ""),
    (0xFFB8, 2, "hSavedSlot", "object slot kept across a call"),
    (0xFFBB, 3, "hTerrainTemp", "GetTerrainUnderObject's scratch"),
    (0xFFBF, 1, "hFreeObjPalettes", "OBJ palette slots left (AllocObjPalette)"),
    (0xFFC0, 1, "hSplitTop", "screen line where the shop's text box starts ($ff = none)"),
    (0xFFC1, 1, "hSplitBottom", "line where it ends"),
    (0xFFC2, 1, "hSplitTarget", "line the box slides to"),
    (0xFFC3, 1, "hTextLines", "lines LoadTextString wrote"),
    (0xFFC4, 1, "hSplitSCY", "rSCY inside the text box"),
    (0xFFC5, 1, "hShopTextState", "shop dialogue progress (tentative)"),
    (0xFFC6, 1, "hRasterPos", "next entry of wRasterTable (world map)"),
    (0xFFC7, 1, "hMapSCX", "world map rSCX, set at VBlank"),
    (0xFFC8, 8, "hOAMDMA", "OAMDMARoutine, copied here at power-on; call with a = $c0"),
]


def _off(k):
    return str(k) if k < 10 else "$%02x" % k


def _table(entries):
    """address -> name or "name + k". Where variables overlap (switchable
    WRAM banks, reused buffers) the one starting nearest below wins; an
    earlier entry wins a tie."""
    t, start = {}, {}
    for a, size, name, _ in entries:
        for k in range(max(size, 1)):
            if size == 0 and k == 0 and a in t:
                continue
            if a + k in start and start[a + k] >= a:
                continue
            start[a + k] = a
            t[a + k] = name if k == 0 else "%s + %s" % (name, _off(k))
    return t


_SAVE = {o: n for o, n, _ in SAVE_FIELDS}
MAIN = _table(WRAM + WRAM_EXTRA + HRAM)
SRAM_TABLE = _table(SRAM)
for _a, _n in list(SRAM_TABLE.items()):
    if 0xB000 <= _a < 0xB0C0 and (_a & 0x3F) in _SAVE and (_a & 0x3F):
        SRAM_TABLE[_a] = "sSaveFile%d + %s" % ((_a - 0xB000) >> 6, _SAVE[_a & 0x3F])
    elif 0xB000 <= _a < 0xB0C0 and (_a & 0x3F) >= 0x30:
        base = max(o for o in _SAVE if o <= (_a & 0x3F))
        SRAM_TABLE[_a] = "sSaveFile%d + %s + %s" % ((_a - 0xB000) >> 6, _SAVE[base], _off((_a & 0x3F) - base))


def lookup(v, bank, main=True):
    """Name for RAM address v used in bank, or None. main: code of the main
    game (not the front end or the programs in banks $50+)."""
    if 0xA000 <= v < 0xC000:
        if main or 0xF0 <= bank <= 0xFE:
            return SRAM_TABLE.get(v)
        return None
    if main:
        return MAIN.get(v)
    return None


def write_inc(path):
    out = ["; RAM variables (generated from tools/ramnames.py).\n",
           "; The main game, the front end (banks $F0-$FE) and Funky's Fishing\n",
           "; (banks $50+) each have their own memory map: w/h names are the main\n",
           "; game's, wFE_/hFE_ the front end's and wCranky_/hCranky_ Crosshair\n",
           "; Cranky's. Save RAM (s) means the same to all of them.\n\n",
           "IF !DEF(RAM_INC)\nDEF RAM_INC EQU 1\n"]

    written = set()

    def block(title, entries):
        out.append("\n; %s\n" % title)
        for a, size, name, desc in sorted(entries):
            if name in written:
                continue
            written.add(name)
            note = ("(%d bytes) " % size if size > 1 else "") + desc
            out.append("DEF %-22s EQU $%04x%s\n" % (name, a, (" ; " + note) if note.strip() else ""))

    block("WRAM", [e for e in WRAM + WRAM_EXTRA])
    block("Other uses of the same WRAM (ld h, $c5 and the like)", UNIONS)
    block("Front end (banks $F0-$FE): shared by the menus and Crosshair Cranky", FE_COMMON + FE_COMMON_HRAM)
    block("Front end: the menus (banks $F0-$F4)", FE_MENUS + FE_MENUS_HRAM)
    block("Crosshair Cranky (banks $F5, $FE)", CRANKY + CRANKY_HRAM)
    out.append("\n; Front-end code copied to RAM (FE_RAM_CODE)\n")
    for a, n in sorted(list(FE_RAM_CODE.items()) + list(CRANKY_RAM_CODE.items())):
        out.append("DEF %-22s EQU $%04x\n" % (n, a))
    block("Save RAM (SRAM bank 0)", SRAM)
    out.append("\n; Save file record fields (sSaveFile0-2, $40 bytes each)\n")
    for o, n, d in SAVE_FIELDS:
        out.append("DEF %-22s EQU $%02x%s\n" % (n, o, (" ; " + d) if d else ""))
    block("HRAM", HRAM)
    out.append("\nENDC\n")
    with open(path, "w") as f:
        f.write("".join(out))


# ---------------------------------------------------------------------------
# The front-end program (banks $F0-$FE). It has its own memory map; the
# lists below are used in its banks only. FE_COMMON applies to all of them;
# Crosshair Cranky (banks $F5 and $FE) reuses some of the menus' RAM, so the
# menus ($F0-$F2) and Crosshair Cranky have a list each.
FE_COMMON = [
    (0xC000, 0xA0, "wFE_ShadowOAM", "front end's sprite attributes, copied to OAM by FE_OAMDMA"),
    (0xC340, 12, "wFileSummaries", "left by the main game (Save_ComputeSummaries): per file "
                                   "completion (word; bit 7 of the high byte: file in use), hours, minutes"),
    (0xC800, 1, "wFE_FarBank", "ROM bank FE_FarCopy, FE_FarReadWord/Byte and the HDMA helpers read from"),
    (0xC801, 2, "wFE_SavedSP", "stack pointer kept while FE_UploadPalettes pops colours off the palette buffers"),
    (0xC803, 2, "wFE_GameSP", "the main game's stack pointer, saved by FE_Enter"),
    (0xC805, 1, "wFE_Language", "0 English, 1 German, 2 French, 3 Italian, 4 Spanish"),
    (0xC806, 0x40, "wFE_BGPalettes", "front end's BG palettes as uploaded"),
    (0xC846, 0x40, "wFE_OBJPalettes", "front end's OBJ palettes as uploaded"),
    (0xCFF6, 0, "wFE_StackTop", "the front end's stack (FE_Enter)"),
    (0xDA00, 0x80, "wFE_FadePalettes", "colours being faded (FE_FadePaletteStep); target in another buffer"),
    (0xDF00, 0x80, "wFE_SavedHRAM", "the main game's HRAM, kept while the front end runs (FE_SaveHRAM)"),
]
FE_COMMON_HRAM = [
    (0xFF80, 1, "hFE_VBlankFlag", "set to 1 by the front end's VBlank handlers; loops wait for it"),
    (0xFF81, 1, "hFE_ROMBank", "current ROM bank (far calls push and restore it)"),
    (0xFF82, 5, "hFE_Scratch", "scratch shared by most routines: counts, fade steps, sprite numbers"),
    (0xFF91, 1, "hFE_JoyInput", "buttons newly pressed (FE_ReadJoypadPressed) or held (FE_ReadJoypadHeld)"),
    (0xFF92, 1, "hFE_JoyHeld", "buttons held"),
    (0xFF93, 1, "hFE_JoyPrevious", "buttons held the frame before"),
    (0xFF94, 4, "hFE_RandomState", "FE_Random's state (FE_SeedRandom)"),
    (0xFF98, 2, "hFE_Scratch2", "scratch: sprite position and attributes while placing sprites, box sizes"),
    (0xFF9A, 1, "hFE_FrameCounter", "counts menu frames; seeds FE_Random when a game starts"),
]

FE_MENUS = [
    (0xC960, 1, "wFE_RingSize", "items on the current ring (2-5)"),
    (0xC961, 1, "wFE_RingAngle", "ring rotation while it turns (tentative)"),
    (0xC962, 5, "wFE_RingIcons", "picture of each item"),
    (0xC967, 5, "wFE_RingLabels", "label of each item"),
    (0xC96C, 1, "wFE_RingItem", "item in front"),
    (0xC96D, 1, "wFE_RingHeight", "ring parameter from RingTable, used to place the items (tentative)"),
    (0xC96E, 1, "wFE_Ring", "current ring (RingTable index)"),
    (0xC96F, 1, "wFE_ChosenFile", "save file picked to erase or copy to"),
    (0xC970, 5, "wFE_RingActions", "action byte of each item (see the README)"),
    (0xC975, 1, "wFE_ParentRing", "ring B goes back to"),
    (0xC976, 1, "wFE_LinkGame", "link game chosen (tentative)"),
    (0xC977, 1, "wFE_FileState", "state of the chosen file for the ring rules (1 = finished; tentative)"),
    (0xC978, 1, "wFE_FileState2", "second value the ring rules test (tentative)"),
    (0xC979, 1, "wFE_RingExtra", "picks the extra picture FE_DrawRingExtras draws"),
    (0xC97A, 7, "wFE_FileInfoDigits", "digits shown for a save file: completion and play time (FE_ReadSaveFileStatus)"),
    (0xC981, 1, "wFE_EntryMode", "how the front end was entered (d): 0 main menu, 1 language select, "
                                 "2 Crosshair Cranky, 3 Cranky unlocked message"),
    (0xC982, 1, "wFE_EntryArg", "second entry argument (e)"),
    (0xC983, 1, "wFE_CopySource", "save file copied from"),
    (0xC984, 1, "wFE_CopyDest", "save file copied to"),
    (0xC986, 1, "wFE_SoundTestSong", "song number in the sound test"),
    (0xC988, 1, "wFE_StickerPage", "Sticker Book page; also the menu cursor's page (tentative)"),
    (0xC989, 1, "wFE_MenuChoice", "option chosen in a menu (3 = Are you sure?)"),
    (0xC98A, 4, "wFE_GridMoves", "item reached by up, down, left and right ($ff = none): "
                                 "Sticker Book and Make Flag keyboard"),
    (0xC98E, 2, "wFE_GridCursor", "cursor sprite position (y, x)"),
    (0xC990, 2, "wFE_GridCursorSize", "cursor's height and width"),
    (0xC992, 1, "wFE_Sticker", "sticker selected"),
    (0xC993, 1, "wFE_StickerSlot", "slot of the selected sticker on the page"),
    (0xC994, 1, "wFE_MenuCursor", "highlighted option of a menu or yes/no box"),
    (0xC995, 1, "wFE_MenuSize", "options in that menu"),
    (0xC996, 2, "wFE_MapCell", "tile and attribute read by FE_GetMapCell"),
    (0xC998, 1, "wFE_StickerScroll", "Sticker Book scroll"),
    (0xC999, 1, "wFE_StickerText", "text shown for the sticker"),
    (0xC99A, 3, "wFE_FilesUsed", "nonzero for each save file in use"),
    (0xC99D, 1, "wFE_ViewItem", "item shown in View Items"),
    (0xC99E, 1, "wFE_ViewItemDrawn", "item last drawn"),
    (0xC99F, 1, "wFE_ViewScroll", "View Items scroll position"),
    (0xC9A0, 1, "wFE_FlagKey", "Make Flag keyboard key selected"),
    (0xC9A1, 1, "wFE_FlagLine", "banner line being typed (0 or 1)"),
    (0xC9A2, 2, "wFE_FlagLengths", "characters typed on each line"),
    (0xC9A4, 2, "wFE_FlagLine1Pointer", "printing position in line 1"),
    (0xC9A6, 2, "wFE_FlagLine2Pointer", "printing position in line 2"),
    (0xC9A8, 2, "wFE_BannerLine1", "banner buffer position of line 1"),
    (0xC9AA, 2, "wFE_BannerLine2", "banner buffer position of line 2"),
    (0xC9AC, 1, "wFE_FlagLine1Char", "character being printed on line 1 ($87 = end, $88 = start)"),
    (0xC9AD, 1, "wFE_FlagLine2Char", ""),
    (0xC9AE, 1, "wFE_Choice", "choice on a sideways menu: language, print darkness..."),
    (0xC9B0, 1, "wFE_BannerBorder", "border picked for the banner"),
    (0xC9B1, 0x13, "wFE_FlagText1", "Make Flag line 1, ending in $87"),
    (0xC9C4, 0x13, "wFE_FlagText2", "Make Flag line 2"),
    (0xC9D7, 2, "wFE_Unused_c9d7", "cleared by FE_Main, never read"),
    (0xC9D9, 1, "wFE_VBlankTimerActive", "nonzero while wFE_VBlankTimer counts down"),
    (0xC9DA, 1, "wFE_AttrPass", "VRAM bank FE_WriteScreenAttributes is writing"),
    (0xC9DB, 2, "wFE_AttrSource", ""),
    (0xC9DC, 3, "wFE_Product", "FE_Multiply16's result"),
    (0xC9E0, 2, "wFE_Multiplier", "FE_Multiply16's operand"),
    (0xC9E2, 1, "wFE_ProductSign", "bit 7: negative result"),
    (0xC9E3, 2, "wFE_VBlankTimer", "frames counted down by the VBlank handler"),
    (0xC9E5, 1, "wFE_Letter", "letter shown in Alphabet (0-$33)"),
    (0xC9E6, 0xA, "wFE_PrinterInitPacket", "Game Boy Printer packets, built by FE_Printer_InitPackets"),
    (0xC9F0, 0xE, "wFE_PrinterPrintPacket", ""),
    (0xC9FE, 0xA, "wFE_PrinterStatusPacket", ""),
    (0xCA08, 0xA, "wFE_PrinterDataHeader", "header of a data packet"),
    (0xCA12, 0x280, "wFE_PrinterData", "640 bytes of tile data for one data packet"),
    (0xCC9C, 2, "wFE_PrinterStatus", "the two status bytes the printer answered"),
    (0xCC9E, 1, "wFE_PrinterBusy", "set while a packet is being sent"),
    (0xCC9F, 1, "wFE_PrintPalette", "palette byte of the print command"),
    (0xCCA0, 1, "wFE_PrintDarkness", "exposure byte of the print command (Make Flag darkness menu)"),
    (0xCCA1, 1, "wFE_PrintBands", "bands left to send (2 tile rows each)"),
    (0xCCA2, 2, "wFE_PrintSource", "next picture row to print"),
    (0xCCA5, 3, "wFE_PrintTiles", "bank and address of the tiles being printed"),
    (0xCCA8, 3, "wFE_StickerPageRecord", "sticker page being printed: three bytes of its record"),
    (0xCCAB, 1, "wFE_PrinterRetries", ""),
    (0xCCAC, 1, "wFE_PrinterSending", "nonzero while the serial handler sends a packet"),
    (0xCCAD, 2, "wFE_PrinterPacketPos", "next byte of the packet being sent"),
    (0xCCAF, 2, "wFE_PrinterPacketLeft", "bytes left in it"),
    (0xCCB1, 1, "wFE_PrinterError", "error found in the status (FE_Printer_DecodeStatus)"),
    (0xCCB2, 2, "wFE_PrinterErrorText", "message shown for it"),
    (0xCCB4, 2, "wFE_PrinterErrorText2", ""),
    (0xCCB7, 1, "wFE_PrinterTimeout", "set by the VBlank handler when printing takes too long (tentative)"),
    (0xCCB8, 1, "wFE_PrinterTimedOut", ""),
    (0xCCB9, 1, "wFE_PrintDelay", "frames to wait between bands"),
    (0xCF80, 0, "wFE_LinkResults", "results the two Game Boys exchange after link Funky's Fishing"),
    (0xD000, 0x800, "wFE_ScreenBuffer", "WRAMX: the screen being built (tile numbers, attributes at +$400), "
                                        "banner pieces, score digits"),
    (0xD700, 0x780, "wFE_SavedState", "copy of $c800-$cf7f kept while a game is played (FE_SaveState)"),
    (0xD800, 0x800, "wFE_SavedBGMap", "copy of wFE_ScreenBuffer (FE_SaveBGMap)"),
    (0xDB00, 0x50, "wFE_GradientPalettes", "colours of the menus' line-by-line gradient (tentative)"),
    (0xDB50, 0xC0, "wFE_TargetPalettes", "colours a fade goes to"),
    (0xDC10, 0x78, "wFE_GradientTarget", "gradient colours a fade goes to (tentative)"),
    (0xDC88, 0x80, "wFE_GradientFadeFrom", "(tentative)"),
    (0xDD1E, 1, "wFE_IRRole", "2 when this Game Boy starts the infrared exchange"),
    (0xDD1F, 1, "wFE_IRStatus", "$aa: packet received; other values are errors (FE_IR_SetError)"),
    (0xDD20, 4, "wFE_IRTimings", "pulse lengths measured at start-up for this CPU speed (FE_IR_Init)"),
    (0xDD24, 1, "wFE_IRThreshold", "length that tells a 1 from a 0"),
    (0xDD25, 4, "wFE_IRPacket", "packet received: $37, kind, check bytes"),
    (0xDE29, 5, "wFE_IRHeader", "header of the packet sent: $5a, length, checksum"),
    (0xDE80, 0x80, "wFE_SavedHRAMState", "copy of the front end's own HRAM (FE_SaveState)"),
]
FE_MENUS_HRAM = [
    (0xFF9D, 0xC, "hFE_LinkBuffer", "bytes exchanged by link cable (menu choices, scores)"),
    (0xFFA9, 1, "hFE_LinkPos", "low byte of the next byte to send"),
    (0xFFAA, 1, "hFE_LinkCount", "bytes exchanged so far"),
    (0xFFAB, 1, "hFE_LinkRetries", ""),
    (0xFFAC, 1, "hFE_LinkRole", "$66 or $bb: which side of the link this Game Boy is"),
    (0xFFAD, 1, "hFE_LinkPartnerRole", ""),
    (0xFFAF, 1, "hFE_LinkGotByte", "set by the serial handler when a byte arrives"),
    (0xFFB0, 1, "hFE_SerialDone", "set by the serial handlers when a transfer ends"),
    (0xFFB1, 1, "hFE_LinkPartnerFound", ""),
]

CRANKY = [
    (0xCB00, 0xA0, "wCranky_OAMBuffer", "sprites built during the frame (Cranky_CopyOAMBuffer)"),
    (0xCBA0, 0x10, "wCranky_LinkIn", "state received from the other Game Boy"),
    (0xCBB0, 1, "wCranky_TargetHit", "actor under the crosshair when B fires (from Cranky_Input)"),
    (0xCBB1, 1, "wCranky_Spawned", "actors spawned in this wave"),
    (0xCBB2, 1, "wCranky_RemoteShot", "nonzero when the other player has fired"),
    (0xCBB3, 1, "wCranky_State", "game state: 0 playing, 3 game over, 6 paused..."),
    (0xCBB4, 1, "wCranky_Shots", "shots fired"),
    (0xCBB5, 1, "wCranky_EventActor", "actor of the last event for the link"),
    (0xCBB6, 1, "wCranky_EventKind", "kind of that event"),
    (0xCBB7, 1, "wCranky_Events", "events queued for the link"),
    (0xCBB8, 1, "wCranky_RemoteEvents", "events handled from the other Game Boy"),
    (0xCBB9, 1, "wCranky_NextActorID", "id given to the next actor (wCranky_ActorID)"),
    (0xCBBA, 5, "wCranky_LinkState", "random state and targets sent to the other Game Boy; "
                                     "also the final score digits"),
    (0xCBBF, 1, "wCranky_Game", "0 Buddies Beware, 1 Barrel O'Kremlings, 2 Wanted, 3 Kremling Krackdown, "
                               "4 Kremlings and Kongs, 5 Galleon Gunner"),
    (0xCBC0, 1, "wCranky_CursorX", "crosshair position"),
    (0xCBC1, 1, "wCranky_CursorY", ""),
    (0xCBC2, 1, "wCranky_TileBuffer", "sprite tile buffer in use (double-buffered)"),
    (0xCBC3, 1, "wCranky_AmmoIcon", "ammunition icon of this game"),
    (0xCBC4, 1, "wCranky_Mode", "1 one player, 2 link play"),
    (0xCBC5, 2, "wCranky_SavedSP", "stack pointer to return to when the game ends"),
    (0xCBC7, 1, "wCranky_Time", "time left"),
    (0xCBC8, 1, "wCranky_TimeFrames", "frames to the next time step"),
    (0xCBC9, 1, "wCranky_Barrels", "barrels or waves left (Barrel O'Kremlings, Kremling games)"),
    (0xCBCA, 1, "wCranky_DimLevel", "background dimming while paused"),
    (0xCBCB, 1, "wCranky_Song", "song of the game (Cranky_LoadBackground)"),
    (0xCBCC, 1, "wCranky_ReloadTimer", ""),
    (0xCBCD, 1, "wCranky_SpawnDelay", ""),
    (0xCBCE, 1, "wCranky_PauseItem", "pause menu option highlighted"),
    (0xCBCF, 4, "wCranky_PauseCursorX", "cursor position of each pause option"),
    (0xCBD3, 4, "wCranky_PauseCursorY", ""),
    (0xCBD7, 1, "wCranky_PauseItems", "options on the pause menu"),
    (0xCBD8, 1, "wCranky_KongShown", "a Kong is on screen (Kremlings and Kongs)"),
    (0xCBD9, 1, "wCranky_RepeatTimer", "auto-repeat of left and right"),
    (0xCBDA, 1, "wCranky_ShotMask", "bit per target already hit"),
    (0xCBDB, 1, "wCranky_TargetIcon", ""),
    (0xCBDC, 8, "wCranky_TargetHits", "hits on each target; 4 knocks it down"),
    (0xCBE4, 8, "wCranky_TargetTimers", ""),
    (0xCBEC, 1, "wCranky_SpawnRate", "per-game speed of spawning; raised as the game goes on"),
    (0xCBED, 1, "wCranky_SpawnRate2", "second spawn parameter"),
    (0xCBEE, 1, "wCranky_Ammo", "shots left; B reloads"),
    (0xCBEF, 1, "wCranky_AmmoMax", "a full load"),
    (0xCBF0, 1, "wCranky_ActorsUp", "actors on screen"),
    (0xCBF1, 3, "wCranky_Score", "score, one decimal digit a byte, highest first"),
    (0xCBF4, 3, "wCranky_ScoreFlash", "frames each score digit flashes after a change"),
    (0xCBF7, 1, "wCranky_TargetsUp", "bit per target standing"),
    (0xCBF8, 1, "wCranky_AmmoTile", "first tile of the ammunition icon"),
    (0xCBF9, 1, "wCranky_Result", "value returned to the menus when the game ends"),
    (0xCBFA, 2, "wCranky_BuddyCounts", "Buddies Beware: buddies spawned"),
    (0xCBFC, 0xB, "wCranky_Wanted", "Wanted: the suspect, poster and spawn state"),
    (0xCC07, 1, "wCranky_Ending", "the end effect has started"),
    (0xCC08, 1, "wCranky_WantedRange", "Wanted: how many kinds the random suspects are picked from"),
    (0xCC09, 1, "wCranky_CrosshairBlink", "frames the crosshair blinks after a hit"),
    (0xCC0A, 1, "wCranky_ScreenFlash", "frames the screen flashes"),
    (0xCC0B, 1, "wCranky_ShipsSunk", "Galleon Gunner: ships hit"),
    (0xCC0C, 2, "wCranky_KremlingSpeed", "Kremling games: speed and its fraction"),
    (0xD000, 0x800, "wCranky_ScreenBuffer", "WRAMX: background being built"),
    # actor arrays: 32 actors, one byte each per field; [hCranky_Actor] indexes them
    (0xDB00, 0x20, "wCranky_ActorType", "routine in Cranky_RunActors' table; 0 = free"),
    (0xDB20, 0x20, "wCranky_ActorX", ""),
    (0xDB40, 0x20, "wCranky_ActorY", ""),
    (0xDB60, 0x20, "wCranky_ActorAnimFlags", "bit 1: animation runs backwards"),
    (0xDB80, 0x20, "wCranky_ActorAnimSpeed", "added to wCranky_ActorAnimTimer every frame"),
    (0xDBA0, 0x20, "wCranky_ActorFrames", "frames in the animation"),
    (0xDBC0, 0x20, "wCranky_ActorAnimTimer", "a carry moves to the next frame"),
    (0xDBE0, 0x20, "wCranky_ActorFrame", "current frame"),
    (0xDC00, 0x20, "wCranky_ActorSprite", "first sprite picture of the animation"),
    (0xDC20, 0x20, "wCranky_ActorFlags", "bit 5: shootable (tentative)"),
    (0xDC40, 0x20, "wCranky_ActorSpeed", "added to wCranky_ActorMoveTimer; a carry is one more step"),
    (0xDC60, 0x20, "wCranky_ActorMoveTimer", ""),
    (0xDC80, 0x20, "wCranky_ActorSteps", "whole steps a frame"),
    (0xDCA0, 0x20, "wCranky_ActorDir", "direction of movement (Cranky_MoveActorStep)"),
    (0xDCC0, 0x20, "wCranky_ActorTimer", "frames to wait"),
    (0xDCE0, 0x20, "wCranky_ActorTarget", "target slot the actor stands at"),
    (0xDD00, 0x20, "wCranky_ActorSavedFlags", "wCranky_ActorAnimFlags kept while hit (tentative)"),
    (0xDD20, 0x20, "wCranky_ActorVar", "per-game use (Galleon Gunner)"),
    (0xDD40, 0x20, "wCranky_ActorID", "id shared with the other Game Boy (wCranky_NextActorID)"),
]
CRANKY_HRAM = [
    (0xFF9C, 1, "hCranky_Actor", "actor being run; index into the wCranky_Actor arrays"),
    (0xFF9D, 0x10, "hCranky_LinkOut", "state sent to the other Game Boy"),
    (0xFFAD, 0x10, "hCranky_LinkIn", "state received"),
    (0xFFBD, 0x10, "hCranky_LinkIn2", "second receive buffer"),
    (0xFFCD, 1, "hCranky_LinkPos", "low byte of the next byte to send"),
    (0xFFCE, 1, "hCranky_LinkCount", "bytes left to send"),
    (0xFFCF, 1, "hCranky_LinkTimer", ""),
    (0xFFD0, 1, "hCranky_LinkSending", ""),
    (0xFFD1, 1, "hCranky_LinkGotByte", "set by the serial handler"),
    (0xFFD3, 1, "hCranky_LinkRole", "$66 or $bb"),
    (0xFFD4, 1, "hCranky_LinkMode", "$bb while playing by link"),
    (0xFFD6, 2, "hCranky_LinkReceivePos", "where the next packet goes"),
    (0xFFD8, 1, "hCranky_LinkDelay", ""),
]

FE_MENU_BANKS = range(0xF0, 0xF5)
CRANKY_BANKS = (0xF5, 0xFE)
FE_MENU_TABLE = _table(FE_MENUS + FE_MENUS_HRAM + FE_COMMON + FE_COMMON_HRAM)
CRANKY_TABLE = _table(CRANKY + CRANKY_HRAM + FE_COMMON + FE_COMMON_HRAM)


# Entry points of the front end's code in RAM (hints.RAM_CODE blocks), by
# the RAM address they run at. Defined in ram.inc so every bank can use them.
FE_RAM_CODE = {
    0xCCBA: "FE_VBlank_Menu",             # ei, then FE_VBlank_MenuBody: palette 0 from wFE_GradientPalettes
    0xCCBC: "FE_VBlank_MenuBody",
    0xCCFB: "FE_VBlank_Plain",
    0xCD03: "FE_VBlank_Link",             # also counts wFE_VBlankTimer down
    0xCD47: "FE_STAT_Gradient",           # changes BG colours line by line
    0xCDDA: "FE_STAT_Sound",
    0xCDDF: "FE_Serial_Printer",
    0xCDEF: "FE_Serial_Handshake",
    0xCE2E: "FE_Serial_WaitForPartner",
    0xCE80: "FE_Serial_Flag",
    0xCC0E: "Cranky_SerialHandler",       # copied from $fe:761b by Cranky_InstallLinkRoutines
    0xCE87: "FE_PrinterSerial",           # FE_PrinterSerial_Code, copied by FE_Printer_InitPackets
    0xCEB3: "FE_PrinterSendByte",         # FE_PrinterSendByte_Code
    0xCEF7: "FE_FarCopyBankSwitchingRAM",  # FE_FarCopyBankSwitching_Code
}
# Crosshair Cranky copies other code over part of that RAM
CRANKY_RAM_CODE = {
    0xCCDC: "Cranky_FarCopySprites",      # Cranky_FarCopySprites_Code (Cranky_InstallSpriteCopy)
    0xCC94: "Cranky_LinkPacket",          # Cranky_LinkPacket_Code (Cranky_InstallLinkRoutines)
}


def fe_ram_code(v, bank):
    if bank in CRANKY_BANKS and v in CRANKY_RAM_CODE:
        return CRANKY_RAM_CODE[v]
    return FE_RAM_CODE.get(v)


def fe_lookup(v, bank):
    """Front-end name for RAM address v used in bank $F0-$FE, or None."""
    if bank in CRANKY_BANKS:
        return CRANKY_TABLE.get(v)
    return FE_MENU_TABLE.get(v)
