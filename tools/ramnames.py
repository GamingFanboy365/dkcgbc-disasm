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
    t = {}
    for a, size, name, _ in entries:
        if size == 0:
            t.setdefault(a, name)
        for k in range(size):
            t.setdefault(a + k, name if k == 0 else "%s + %s" % (name, _off(k)))
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
    out = ["; Main-game RAM (generated from tools/ramnames.py).\n",
           "; The front end (banks $F0-$FE) and Funky's Fishing (banks $50+) have\n",
           "; their own memory maps; see FE_RAM_NAMES and FISHING_RAM_NAMES.\n\n",
           "IF !DEF(RAM_INC)\nDEF RAM_INC EQU 1\n"]

    def block(title, entries):
        out.append("\n; %s\n" % title)
        for a, size, name, desc in sorted(entries):
            note = ("(%d bytes) " % size if size > 1 else "") + desc
            out.append("DEF %-22s EQU $%04x%s\n" % (name, a, (" ; " + note) if note.strip() else ""))

    block("WRAM", [e for e in WRAM + WRAM_EXTRA])
    block("Other uses of the same WRAM (ld h, $c5 and the like)", UNIONS)
    block("Save RAM (SRAM bank 0)", SRAM)
    out.append("\n; Save file record fields (sSaveFile0-2, $40 bytes each)\n")
    for o, n, d in SAVE_FIELDS:
        out.append("DEF %-22s EQU $%02x%s\n" % (n, o, (" ; " + d) if d else ""))
    block("HRAM", HRAM)
    out.append("\nENDC\n")
    with open(path, "w") as f:
        f.write("".join(out))
