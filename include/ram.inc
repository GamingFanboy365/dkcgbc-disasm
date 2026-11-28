; Main-game RAM (generated from tools/ramnames.py).
; The front end (banks $F0-$FE) and Funky's Fishing (banks $50+) have
; their own memory maps; see FE_RAM_NAMES and FISHING_RAM_NAMES.

IF !DEF(RAM_INC)
DEF RAM_INC EQU 1

; WRAM
DEF wShadowOAM             EQU $c000 ; (160 bytes) sprite attributes, copied to OAM by DMA
DEF wShadowOAMEnd          EQU $c0a0 ; end of wShadowOAM
DEF wBGPalettes            EQU $c100 ; (128 bytes) 8 BG palettes as the level or screen defines them
DEF wOBJPalettes           EQU $c180 ; (128 bytes) 8 OBJ palettes (slots handed out by AllocObjPalette)
DEF wBGPalettesOut         EQU $c200 ; (128 bytes) wBGPalettes after brightness, uploaded to the LCD
DEF wOBJPalettesOut        EQU $c280 ; (128 bytes) wOBJPalettes after brightness
DEF wRandomState           EQU $c300 ; (3 bytes) Random's seed, $ff $ff $f8 at power-on
DEF wFlowPointer           EQU $c303 ; (2 bytes) next command of the flow script (bank $0d), RunFlowScript
DEF wFlowArg1              EQU $c305 ; first argument of the current state: fade flags, song, wait timer (low)
DEF wFlowArg2              EQU $c306 ; second argument: fade brightness, wait timer (high)
DEF wFlowArg3              EQU $c307 ; third argument
DEF wSaveFile              EQU $c309 ; save file in use (0-2; 3 = the system record); its record is at sSaveFile0 + $40 * n
DEF wWorld                 EQU $c30a ; current world map (0-7), from the location table at $05:491e
DEF wMapLocation           EQU $c30b ; current location on the world map
DEF wLevel                 EQU $c30c ; current level number; also the location type at a shop
DEF wLanguage              EQU $c30d ; language; the text bank is $10 + wLanguage
DEF wGameModeBit           EQU $c30e ; 1, 2 or 4: which completion bit of a level's save byte this game sets (2 and 4 picked by sOptions bits 0 and 1; tentative)
DEF wKongs                 EQU $c30f ; bit 0: Diddy leads (else DK), bit 1: the partner Kong is along, bit 3: riding an animal, bits 4-5: which (Rambi, Expresso, Enguarde, Winky)
DEF wMapFlags              EQU $c310 ; bit 0: cleared at a level clear, bit 5: set in Cranky's Cabin, bit 6: a level was newly cleared, bit 7: the Kong travels at double speed with another sprite, as in Funky's Flights (tentative)
DEF wPaletteUpdate         EQU $c311 ; bit 0: upload BG, bit 1: upload OBJ, bit 2: fade mode
DEF wPaletteBrightness     EQU $c312
DEF wAnimalTokens          EQU $c313 ; (4 bytes) animal tokens held, one byte per animal; three start an animal bonus
DEF wAnimalTokensPending   EQU $c317 ; (4 bytes) animal tokens collected in this level, added to wAnimalTokens when it ends
DEF wBananas               EQU $c31b ; banana count (BCD); 100 give an extra life
DEF wBananasPending        EQU $c31c ; bananas collected but still flying to the counter
DEF wLives                 EQU $c31d ; lives (BCD); $ff is treated as a special value by State_Level and GiveExtraLife (tentative)
DEF wLivesOver99           EQU $c31e ; extra lives beyond 99
DEF wLivesPending          EQU $c31f ; extra lives collected but not yet added
DEF wStickers              EQU $c320 ; stickers found (BCD)
DEF wMusicTempoCounter     EQU $c321 ; music tempo accumulator; a carry is a music tick
DEF wMusicTempo            EQU $c322 ; added to wMusicTempoCounter every frame (from the song's tempo)
DEF wMusicTick             EQU $c323 ; bit 7 set on frames the music advances
DEF wMusicSweep            EQU $c324 ; NR10 value for the music (MusCmd_Sweep)
DEF wMusicBank             EQU $c327 ; ROM bank of the song playing
DEF wSong                  EQU $c328 ; song playing; PlaySong ignores a request for it
DEF wSFXQueue              EQU $c329 ; (4 bytes) sound effect to start on each of the four SFX slots, 0 = none (StartQueuedSFX)
DEF wVBlankTrampoline      EQU $c32d ; (3 bytes) jp to the VBlank handler of the current state
DEF wLCDTrampoline         EQU $c330 ; (3 bytes) jp to the LCD (STAT) handler
DEF wOldFarCallTrampoline  EQU $c333 ; (3 bytes) jp used by OldFarCall
DEF wFrameCounter          EQU $c336 ; (2 bytes) counts frames; wraps at $0e00 (one minute) into wPlayTimeMinutes
DEF wPlayTimeMinutes       EQU $c338 ; play time minutes (BCD)
DEF wPlayTimeHours         EQU $c339 ; play time hours (BCD)
DEF wFileSummaries         EQU $c340 ; (12 bytes) files 0-2 for the front end: completion (word), hours, minutes (Save_ComputeSummaries)
DEF wMapColumnBuffer       EQU $c380 ; (64 bytes) tile and attribute pairs of the BG column to write (WriteScrollEdges)
DEF wMapRowBuffer          EQU $c3c0 ; (64 bytes) tile and attribute pairs of the BG row to write
DEF wObjectFreeList        EQU $c400 ; (64 bytes) stack of free object slot offsets (words)
DEF wObjectFreeCount       EQU $c440 ; number of entries in wObjectFreeList
DEF wHUDFlags              EQU $c441 ; bit 0: show the banana counter, bit 1: show lives, bit 2: collected items are not counted (tentative)
DEF wHUDState              EQU $c442 ; bits set while the HUD counters slide out
DEF wLevelFlags            EQU $c443 ; bit 0: paused, bit 1: leave the level, bit 2-3, 6: how it is left, bit 4: pausing allowed, bit 5: leaving from the pause screen allowed, bit 7: three animal tokens collected
DEF wEntranceKind          EQU $c444 ; last byte of the entrance record; low nibble 2 = arrived by mine cart
DEF wLevelKind             EQU $c445 ; first byte of the level descriptor; bits 0-2 the level type (4 Stop & Go, 5 Loopy Lights, 6 flickering lights, 7 snowflakes), bits 4-6 the animal bonus
DEF wLevelTimer            EQU $c446 ; (2 bytes) per-level counter: Stop & Go and lights timers, mine cart fuel, animal bonus tokens
DEF wItemsInFlight         EQU $c448 ; collected items still flying to the HUD
DEF wLevelEntrance         EQU $c449 ; (2 bytes) pointer to the current LevelEntrance record (bank $04)
DEF wReturnEntrance        EQU $c44b ; (2 bytes) entrance to go back to when leaving a bonus level
DEF wShopExit              EQU $c44d ; shop result: $ff leave, $fe fly away (Funky's Flights)
DEF wShopChoice            EQU $c44e ; shop's selected option (tentative)
DEF wLastRandom            EQU $c44f ; RandomBelow's last result, so the next differs
DEF wCameraPlayerX         EQU $c450 ; where the camera keeps the player across the screen
DEF wCameraPlayerY         EQU $c451 ; where the camera keeps the player down the screen
DEF wCameraShiftX          EQU $c452 ; (2 bytes) extra camera X offset, eased back to 0
DEF wCameraShiftY          EQU $c454 ; (2 bytes) extra camera Y offset, eased back to 0
DEF wCameraGroundY         EQU $c456 ; (2 bytes) height of the ground the player last stood on, followed by the camera
DEF wMapRowDest            EQU $c458 ; (2 bytes) BG map address of the row in wMapRowBuffer
DEF wMapColumnDest         EQU $c45a ; low byte of the BG map address of the column in wMapColumnBuffer; $ff = none
DEF wCameraRegion          EQU $c45c ; (16 bytes) camera region record (bank $06): left, right, top, bottom edges; while a map loads, its first word points to the map's regions
DEF wSpawnRangeX           EQU $c46c ; (4 bytes) left and right edge of the area objects spawn in
DEF wSpawnRangeY           EQU $c470 ; (4 bytes) top and bottom edge of the spawn area
DEF wDespawnRangeX         EQU $c474 ; (4 bytes) left and right edge of the area objects stay alive in
DEF wDespawnRangeY         EQU $c478 ; (4 bytes) top and bottom edge of that area
DEF wSnowflakes            EQU $c480 ; (128 bytes) snowflake positions (Snowflakes)
DEF wRasterTable           EQU $c500 ; (256 bytes) LYC and scroll values per screen split (world map)
DEF wMapKongFlags          EQU $c600 ; bit 1: the Kong faces left
DEF wMapScrollX            EQU $c601 ; world map scroll, in columns
DEF wMapScrollMax          EQU $c602 ; rightmost scroll of this world map
DEF wMapUnused_c603        EQU $c603 ; copied from the world map record, never read
DEF wMapNodes              EQU $c604 ; (2 bytes) pointer to the world map's node table (4 bytes a node: x, y, ...)
DEF wMapColumnToDraw       EQU $c606 ; next BG column DrawWorldMapColumn draws
DEF wMapLevelsCleared      EQU $c607 ; cleared levels counted by WorldMap_SetUpMarkers; picks the sign tiles
DEF wMapNode               EQU $c608 ; node the Kong stands at or walks to
DEF wMapKongXVel           EQU $c609 ; (2 bytes) X step per frame while walking (AddSignedWordTo24 onto wMapKongX)
DEF wMapKongX              EQU $c60b ; (3 bytes) Kong's X: fraction, then pixels (word)
DEF wMapKongYVel           EQU $c60e ; (2 bytes) Y step per frame while walking
DEF wMapKongY              EQU $c610 ; (3 bytes) Kong's Y: fraction, then pixels
DEF wMapPath               EQU $c613 ; (2 bytes) next byte of the path being walked ($ff ends it)
DEF wMapStepFrames         EQU $c615 ; frames left in the current step
DEF wMapNodeSong           EQU $c616 ; song of the node last entered; $ff after loading the map
DEF wTitlePalettes         EQU $ce00 ; (64 bytes) title BG palettes with the swaps for the current scroll applied
DEF wTitlePaletteSwaps     EQU $cf00 ; (96 bytes) palette swap list (scroll line, source*8, $80 | slot*8), $ff-terminated
DEF wTitleScrollY          EQU $cf60 ; title picture scroll, copied to rSCY
DEF wTitleTimer            EQU $cf61 ; frames left in the current step
DEF wTitleStep             EQU $cf62 ; step of the title sequence: fade in, wait, scroll, fade out...
DEF wTitleSwapPos          EQU $cf63 ; next swap RasterLCDHandler applies this frame
DEF wTitleSwapStart        EQU $cf64 ; first swap below the top of the screen
DEF wTitleBrightness       EQU $cf65 ; fade level of the title
DEF wTimerTrampoline       EQU $cff7 ; (3 bytes) jp to the timer interrupt handler
DEF wSerialTrampoline      EQU $cffa ; (3 bytes) jp to the serial interrupt handler
DEF wJoypadTrampoline      EQU $cffd ; (3 bytes) jp to the joypad interrupt handler
DEF wWRAMX                 EQU $d000 ; start of the switchable WRAM bank: map data (banks 1-3, 5-7), sound channels (bank 4), screen maps being loaded
DEF wMusicChannelActive    EQU $d01f ; WRAM bank 4: nonzero while music channel 1 plays; channels 2-4 are $100 apart
DEF wTextBuffer            EQU $d020 ; LoadTextString's output
DEF wMusicSweepActive      EQU $d039 ; WRAM bank 4: nonzero while channel 1 uses its own sweep
DEF wBonusesFound          EQU $d400 ; (256 bytes) WRAM bank 4: per level two words, bonuses found and their union (compared with LevelBonusMasks)
DEF wPlatforms             EQU $d500 ; (126 bytes) WRAM bank 4: platforms objects can stand on this frame
DEF wPlatformsNext         EQU $d57e ; (126 bytes) WRAM bank 4: platforms registered during this frame
DEF wPlatformsNextSize     EQU $d5fc ; bytes in wPlatformsNext
DEF wPlatformsCount        EQU $d5fd ; entries in wPlatforms
DEF wPlatformsNextCount    EQU $d5fe ; entries in wPlatformsNext
DEF wObjPaletteSlots       EQU $d600 ; (128 bytes) WRAM bank 4: OBJ palette slot of each preloaded palette
DEF wFreeObjPaletteSlots   EQU $d680 ; (8 bytes) WRAM bank 4: OBJ palette slots not taken by the preload list
DEF wTileAnimBuffer        EQU $d800 ; (1024 bytes) WRAM bank 4: the animal bonus mask, tiles of animated objects

; Other uses of the same WRAM (ld h, $c5 and the like)
DEF wSpriteLayer0          EQU $c500 ; (256 bytes) in levels: sprites of layer 0 (front), merged into wShadowOAM
DEF wSpriteLayer1          EQU $c600 ; (256 bytes) in levels: layer 1
DEF wSpriteLayer2          EQU $c700 ; (256 bytes) in levels: layer 2 (back)
DEF wMapNodeData           EQU $c900 ; (256 bytes) on the world map: a byte per node (bits 0-6 its song)

; Save RAM (SRAM bank 0)
DEF sWorkRAM               EQU $a000 ; (2048 bytes) cleared at power-on
DEF sLevelObjects          EQU $a800 ; (2048 bytes) the level's object tables, $100 bytes apart (BuildSpawnGrid)
DEF sSaveFile0             EQU $b000 ; (64 bytes) save file 1 (layout: SAVE_* in include/ram.inc)
DEF sSaveFile1             EQU $b040 ; (64 bytes) save file 2
DEF sSaveFile2             EQU $b080 ; (64 bytes) save file 3
DEF sSystemFile            EQU $b0c0 ; fourth record: settings shared by the files
DEF sTitlePicture          EQU $b0c1 ; title screen picture, advanced at every power-on (0-2)
DEF sStickersFound         EQU $b0c2 ; (3 bytes) one bit per sticker found in any file
DEF sMostBonusCoins        EQU $b0c5 ; most bonus coins in any file; unlocks link modes in the front end
DEF sOptions               EQU $b0c6 ; set by the front end: bits 0-1 game mode (see wGameModeBit), bit 2: sound effects off
DEF sCrankyUnlock          EQU $b0c7 ; Crosshair Cranky unlock level (0-6)
DEF sSaveBackup1           EQU $b100 ; (256 bytes) copies of the four records
DEF sSaveBackup2           EQU $b200 ; (256 bytes) 
DEF sSaveBackup3           EQU $b300 ; (256 bytes) 

; Save file record fields (sSaveFile0-2, $40 bytes each)
DEF SAVE_LEVELS            EQU $00 ; a byte per level: bits 0-2 cleared (per wGameModeBit), bit 3 first cleared with Diddy leading, bit 4 every bonus found, bit 5 sticker taken; bit 6 of the byte numbered by a world: its bonus coin taken
DEF SAVE_HOURS             EQU $30 ; play time
DEF SAVE_MINUTES           EQU $31
DEF SAVE_WORLD             EQU $32 ; world reached, one byte per game mode
DEF SAVE_BONUS_COINS       EQU $35 ; bonus coins collected
DEF SAVE_CHECKSUM          EQU $3e ; word over bytes $00-$3d, seeded with $aa55 (Save_Checksum)

; HRAM
DEF hJoyHeld               EQU $ff80 ; buttons held (bit 0 A, 1 B, 2 Select, 3 Start, 4-7 Right Left Up Down)
DEF hJoyPressed            EQU $ff81 ; buttons pressed this frame
DEF hJoyUsed               EQU $ff82 ; buttons the player code has acted on; a bit clears when the button is let go
DEF hVBlankDone            EQU $ff83 ; set by DoOAMDMA; the main loop waits for it
DEF hGameState             EQU $ff84 ; low byte of the current state's entry in the jump table at $0301
DEF hMapBlockBank          EQU $ff85 ; ROM bank of the map's blocks (the next bank holds the rest)
DEF hMapTerrainBank        EQU $ff86 ; ROM bank of the map's terrain shapes (GetTerrainUnderObject)
DEF hMapBlockRow           EQU $ff87 ; offset of the tile row or column inside a block while drawing
DEF hMapFlags              EQU $ff88 ; bit 0: vertical level, bit 1: map has the extra layers in WRAM 5-7, bit 7: camera held still
DEF hCameraX               EQU $ff89 ; (2 bytes) camera position, copied to rSCX
DEF hCameraY               EQU $ff8b ; (2 bytes) copied to rSCY
DEF hCameraMinX            EQU $ff8d ; (2 bytes) camera region edges (SetCameraRegion)
DEF hCameraMinY            EQU $ff8f ; (2 bytes) 
DEF hCameraMaxX            EQU $ff91 ; (2 bytes) 
DEF hCameraMaxY            EQU $ff93 ; (2 bytes) 
DEF hScratch2              EQU $ff95 ; (2 bytes) scratch: HUD item bits, banana bunch positions
DEF hSpriteY               EQU $ff97 ; (2 bytes) screen position of the sprite frame being drawn
DEF hSpriteX               EQU $ff99 ; (2 bytes) 
DEF hSpriteAttr            EQU $ff9b ; OAM attributes of the frame being drawn; also scratch
DEF hScratch3              EQU $ff9c ; scratch
DEF hSpriteFrame           EQU $ff9d ; (2 bytes) frame being drawn
DEF hSpriteLayerPos        EQU $ff9f ; fill position in the sprite layer buffer
DEF hSpriteLayerHigh       EQU $ffa0 ; high byte of that buffer ($c5-$c7)
DEF hSpriteBufferPhase     EQU $ffa1 ; flips every frame: bit 0 picks the VRAM bank of sprite tiles
DEF hSpriteLayerFill       EQU $ffa2 ; (3 bytes) bytes used in each sprite layer buffer ($c500, $c600, $c700)
DEF hSpriteTileSpace       EQU $ffa5 ; sprite tile space left this frame ($60 at the start; tentative)
DEF hObjectRunMask         EQU $ffa6 ; RunObjects runs the objects whose OBJ_FLAGS share a bit with this
DEF hContactFlags          EQU $ffa7 ; collision flags of the player's last contact (tentative)
DEF hScratch               EQU $ffa8 ; (8 bytes) scratch: contact and terrain checks, bonus games
DEF hContactObject         EQU $ffb0 ; (2 bytes) slot of the object touching the player
DEF hTempX                 EQU $ffb2 ; (2 bytes) scratch position, e.g. where SpawnObjectDigits puts digits
DEF hTempY                 EQU $ffb4 ; (2 bytes) 
DEF hTempX2                EQU $ffb6 ; (2 bytes) 
DEF hSavedSlot             EQU $ffb8 ; (2 bytes) object slot kept across a call
DEF hTerrainTemp           EQU $ffbb ; (3 bytes) GetTerrainUnderObject's scratch
DEF hFreeObjPalettes       EQU $ffbf ; OBJ palette slots left (AllocObjPalette)
DEF hSplitTop              EQU $ffc0 ; screen line where the shop's text box starts ($ff = none)
DEF hSplitBottom           EQU $ffc1 ; line where it ends
DEF hSplitTarget           EQU $ffc2 ; line the box slides to
DEF hTextLines             EQU $ffc3 ; lines LoadTextString wrote
DEF hSplitSCY              EQU $ffc4 ; rSCY inside the text box
DEF hShopTextState         EQU $ffc5 ; shop dialogue progress (tentative)
DEF hRasterPos             EQU $ffc6 ; next entry of wRasterTable (world map)
DEF hMapSCX                EQU $ffc7 ; world map rSCX, set at VBlank
DEF hOAMDMA                EQU $ffc8 ; (8 bytes) OAMDMARoutine, copied here at power-on; call with a = $c0

ENDC
