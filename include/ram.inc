; RAM variables (generated from tools/ramnames.py).
; The main game, the front end (banks $F0-$FE) and Funky's Fishing
; (banks $50+) each have their own memory map: w/h names are the main
; game's, wFE_/hFE_ the front end's, wCranky_/hCranky_ Crosshair
; Cranky's and wFishing_/hFishing_ Funky's Fishing's. Save RAM (s)
; means the same to all of them.

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

; Front end (banks $F0-$FE): shared by the menus and Crosshair Cranky
DEF wFE_ShadowOAM          EQU $c000 ; (160 bytes) front end's sprite attributes, copied to OAM by FE_OAMDMA
DEF wFE_FarBank            EQU $c800 ; ROM bank FE_FarCopy, FE_FarReadWord/Byte and the HDMA helpers read from
DEF wFE_SavedSP            EQU $c801 ; (2 bytes) stack pointer kept while FE_UploadPalettes pops colours off the palette buffers
DEF wFE_GameSP             EQU $c803 ; (2 bytes) the main game's stack pointer, saved by FE_Enter
DEF wFE_Language           EQU $c805 ; 0 English, 1 German, 2 French, 3 Italian, 4 Spanish
DEF wFE_BGPalettes         EQU $c806 ; (64 bytes) front end's BG palettes as uploaded
DEF wFE_OBJPalettes        EQU $c846 ; (64 bytes) front end's OBJ palettes as uploaded
DEF wFE_StackTop           EQU $cff6 ; the front end's stack (FE_Enter)
DEF wFE_FadePalettes       EQU $da00 ; (128 bytes) colours being faded (FE_FadePaletteStep); target in another buffer
DEF wFE_SavedHRAM          EQU $df00 ; (128 bytes) the main game's HRAM, kept while the front end runs (FE_SaveHRAM)
DEF hFE_VBlankFlag         EQU $ff80 ; set to 1 by the front end's VBlank handlers; loops wait for it
DEF hFE_ROMBank            EQU $ff81 ; current ROM bank (far calls push and restore it)
DEF hFE_Scratch            EQU $ff82 ; (5 bytes) scratch shared by most routines: counts, fade steps, sprite numbers
DEF hFE_JoyInput           EQU $ff91 ; buttons newly pressed (FE_ReadJoypadPressed) or held (FE_ReadJoypadHeld)
DEF hFE_JoyHeld            EQU $ff92 ; buttons held
DEF hFE_JoyPrevious        EQU $ff93 ; buttons held the frame before
DEF hFE_RandomState        EQU $ff94 ; (4 bytes) FE_Random's state (FE_SeedRandom)
DEF hFE_Scratch2           EQU $ff98 ; (2 bytes) scratch: sprite position and attributes while placing sprites, box sizes
DEF hFE_FrameCounter       EQU $ff9a ; counts menu frames; seeds FE_Random when a game starts

; Front end: the menus (banks $F0-$F4)
DEF wFE_RingSize           EQU $c960 ; items on the current ring (2-5)
DEF wFE_RingAngle          EQU $c961 ; ring rotation while it turns (tentative)
DEF wFE_RingIcons          EQU $c962 ; (5 bytes) picture of each item
DEF wFE_RingLabels         EQU $c967 ; (5 bytes) label of each item
DEF wFE_RingItem           EQU $c96c ; item in front
DEF wFE_RingHeight         EQU $c96d ; ring parameter from RingTable, used to place the items (tentative)
DEF wFE_Ring               EQU $c96e ; current ring (RingTable index)
DEF wFE_ChosenFile         EQU $c96f ; save file picked to erase or copy to
DEF wFE_RingActions        EQU $c970 ; (5 bytes) action byte of each item (see the README)
DEF wFE_ParentRing         EQU $c975 ; ring B goes back to
DEF wFE_LinkGame           EQU $c976 ; link game chosen (tentative)
DEF wFE_FileState          EQU $c977 ; state of the chosen file for the ring rules (1 = finished; tentative)
DEF wFE_FileState2         EQU $c978 ; second value the ring rules test (tentative)
DEF wFE_RingExtra          EQU $c979 ; picks the extra picture FE_DrawRingExtras draws
DEF wFE_FileInfoDigits     EQU $c97a ; (7 bytes) digits shown for a save file: completion and play time (FE_ReadSaveFileStatus)
DEF wFE_EntryMode          EQU $c981 ; how the front end was entered (d): 0 main menu, 1 language select, 2 Crosshair Cranky, 3 Cranky unlocked message
DEF wFE_EntryArg           EQU $c982 ; second entry argument (e)
DEF wFE_CopySource         EQU $c983 ; save file copied from
DEF wFE_CopyDest           EQU $c984 ; save file copied to
DEF wFE_SoundTestSong      EQU $c986 ; song number in the sound test
DEF wFE_StickerPage        EQU $c988 ; Sticker Book page; also the menu cursor's page (tentative)
DEF wFE_MenuChoice         EQU $c989 ; option chosen in a menu (3 = Are you sure?)
DEF wFE_GridMoves          EQU $c98a ; (4 bytes) item reached by up, down, left and right ($ff = none): Sticker Book and Make Flag keyboard
DEF wFE_GridCursor         EQU $c98e ; (2 bytes) cursor sprite position (y, x)
DEF wFE_GridCursorSize     EQU $c990 ; (2 bytes) cursor's height and width
DEF wFE_Sticker            EQU $c992 ; sticker selected
DEF wFE_StickerSlot        EQU $c993 ; slot of the selected sticker on the page
DEF wFE_MenuCursor         EQU $c994 ; highlighted option of a menu or yes/no box
DEF wFE_MenuSize           EQU $c995 ; options in that menu
DEF wFE_MapCell            EQU $c996 ; (2 bytes) tile and attribute read by FE_GetMapCell
DEF wFE_StickerScroll      EQU $c998 ; Sticker Book scroll
DEF wFE_StickerText        EQU $c999 ; text shown for the sticker
DEF wFE_FilesUsed          EQU $c99a ; (3 bytes) nonzero for each save file in use
DEF wFE_ViewItem           EQU $c99d ; item shown in View Items
DEF wFE_ViewItemDrawn      EQU $c99e ; item last drawn
DEF wFE_ViewScroll         EQU $c99f ; View Items scroll position
DEF wFE_FlagKey            EQU $c9a0 ; Make Flag keyboard key selected
DEF wFE_FlagLine           EQU $c9a1 ; banner line being typed (0 or 1)
DEF wFE_FlagLengths        EQU $c9a2 ; (2 bytes) characters typed on each line
DEF wFE_FlagLine1Pointer   EQU $c9a4 ; (2 bytes) printing position in line 1
DEF wFE_FlagLine2Pointer   EQU $c9a6 ; (2 bytes) printing position in line 2
DEF wFE_BannerLine1        EQU $c9a8 ; (2 bytes) banner buffer position of line 1
DEF wFE_BannerLine2        EQU $c9aa ; (2 bytes) banner buffer position of line 2
DEF wFE_FlagLine1Char      EQU $c9ac ; character being printed on line 1 ($87 = end, $88 = start)
DEF wFE_FlagLine2Char      EQU $c9ad
DEF wFE_Choice             EQU $c9ae ; choice on a sideways menu: language, print darkness...
DEF wFE_BannerBorder       EQU $c9b0 ; border picked for the banner
DEF wFE_FlagText1          EQU $c9b1 ; (19 bytes) Make Flag line 1, ending in $87
DEF wFE_FlagText2          EQU $c9c4 ; (19 bytes) Make Flag line 2
DEF wFE_Unused_c9d7        EQU $c9d7 ; (2 bytes) cleared by FE_Main, never read
DEF wFE_VBlankTimerActive  EQU $c9d9 ; nonzero while wFE_VBlankTimer counts down
DEF wFE_AttrPass           EQU $c9da ; VRAM bank FE_WriteScreenAttributes is writing
DEF wFE_AttrSource         EQU $c9db ; (2 bytes) 
DEF wFE_Product            EQU $c9dc ; (3 bytes) FE_Multiply16's result
DEF wFE_Multiplier         EQU $c9e0 ; (2 bytes) FE_Multiply16's operand
DEF wFE_ProductSign        EQU $c9e2 ; bit 7: negative result
DEF wFE_VBlankTimer        EQU $c9e3 ; (2 bytes) frames counted down by the VBlank handler
DEF wFE_Letter             EQU $c9e5 ; letter shown in Alphabet (0-$33)
DEF wFE_PrinterInitPacket  EQU $c9e6 ; (10 bytes) Game Boy Printer packets, built by FE_Printer_InitPackets
DEF wFE_PrinterPrintPacket EQU $c9f0 ; (14 bytes) 
DEF wFE_PrinterStatusPacket EQU $c9fe ; (10 bytes) 
DEF wFE_PrinterDataHeader  EQU $ca08 ; (10 bytes) header of a data packet
DEF wFE_PrinterData        EQU $ca12 ; (640 bytes) 640 bytes of tile data for one data packet
DEF wFE_PrinterStatus      EQU $cc9c ; (2 bytes) the two status bytes the printer answered
DEF wFE_PrinterBusy        EQU $cc9e ; set while a packet is being sent
DEF wFE_PrintPalette       EQU $cc9f ; palette byte of the print command
DEF wFE_PrintDarkness      EQU $cca0 ; exposure byte of the print command (Make Flag darkness menu)
DEF wFE_PrintBands         EQU $cca1 ; bands left to send (2 tile rows each)
DEF wFE_PrintSource        EQU $cca2 ; (2 bytes) next picture row to print
DEF wFE_PrintTiles         EQU $cca5 ; (3 bytes) bank and address of the tiles being printed
DEF wFE_StickerPageRecord  EQU $cca8 ; (3 bytes) sticker page being printed: three bytes of its record
DEF wFE_PrinterRetries     EQU $ccab
DEF wFE_PrinterSending     EQU $ccac ; nonzero while the serial handler sends a packet
DEF wFE_PrinterPacketPos   EQU $ccad ; (2 bytes) next byte of the packet being sent
DEF wFE_PrinterPacketLeft  EQU $ccaf ; (2 bytes) bytes left in it
DEF wFE_PrinterError       EQU $ccb1 ; error found in the status (FE_Printer_DecodeStatus)
DEF wFE_PrinterErrorText   EQU $ccb2 ; (2 bytes) message shown for it
DEF wFE_PrinterErrorText2  EQU $ccb4 ; (2 bytes) 
DEF wFE_PrinterTimeout     EQU $ccb7 ; set by the VBlank handler when printing takes too long (tentative)
DEF wFE_PrinterTimedOut    EQU $ccb8
DEF wFE_PrintDelay         EQU $ccb9 ; frames to wait between bands
DEF wFE_LinkResults        EQU $cf80 ; results the two Game Boys exchange after link Funky's Fishing
DEF wFE_ScreenBuffer       EQU $d000 ; (2048 bytes) WRAMX: the screen being built (tile numbers, attributes at +$400), banner pieces, score digits
DEF wFE_SavedState         EQU $d700 ; (1920 bytes) copy of $c800-$cf7f kept while a game is played (FE_SaveState)
DEF wFE_SavedBGMap         EQU $d800 ; (2048 bytes) copy of wFE_ScreenBuffer (FE_SaveBGMap)
DEF wFE_GradientPalettes   EQU $db00 ; (80 bytes) colours of the menus' line-by-line gradient (tentative)
DEF wFE_TargetPalettes     EQU $db50 ; (192 bytes) colours a fade goes to
DEF wFE_GradientTarget     EQU $dc10 ; (120 bytes) gradient colours a fade goes to (tentative)
DEF wFE_GradientFadeFrom   EQU $dc88 ; (128 bytes) (tentative)
DEF wFE_IRRole             EQU $dd1e ; 2 when this Game Boy starts the infrared exchange
DEF wFE_IRStatus           EQU $dd1f ; $aa: packet received; other values are errors (FE_IR_SetError)
DEF wFE_IRTimings          EQU $dd20 ; (4 bytes) pulse lengths measured at start-up for this CPU speed (FE_IR_Init)
DEF wFE_IRThreshold        EQU $dd24 ; length that tells a 1 from a 0
DEF wFE_IRPacket           EQU $dd25 ; (4 bytes) packet received: $37, kind, check bytes
DEF wFE_IRHeader           EQU $de29 ; (5 bytes) header of the packet sent: $5a, length, checksum
DEF wFE_SavedHRAMState     EQU $de80 ; (128 bytes) copy of the front end's own HRAM (FE_SaveState)
DEF hFE_LinkBuffer         EQU $ff9d ; (12 bytes) bytes exchanged by link cable (menu choices, scores)
DEF hFE_LinkPos            EQU $ffa9 ; low byte of the next byte to send
DEF hFE_LinkCount          EQU $ffaa ; bytes exchanged so far
DEF hFE_LinkRetries        EQU $ffab
DEF hFE_LinkRole           EQU $ffac ; $66 or $bb: which side of the link this Game Boy is
DEF hFE_LinkPartnerRole    EQU $ffad
DEF hFE_LinkGotByte        EQU $ffaf ; set by the serial handler when a byte arrives
DEF hFE_SerialDone         EQU $ffb0 ; set by the serial handlers when a transfer ends
DEF hFE_LinkPartnerFound   EQU $ffb1

; Crosshair Cranky (banks $F5, $FE)
DEF wCranky_OAMBuffer      EQU $cb00 ; (160 bytes) sprites built during the frame (Cranky_CopyOAMBuffer)
DEF wCranky_LinkIn         EQU $cba0 ; (16 bytes) state received from the other Game Boy
DEF wCranky_TargetHit      EQU $cbb0 ; actor under the crosshair when B fires (from Cranky_Input)
DEF wCranky_Spawned        EQU $cbb1 ; actors spawned in this wave
DEF wCranky_RemoteShot     EQU $cbb2 ; nonzero when the other player has fired
DEF wCranky_State          EQU $cbb3 ; game state: 0 playing, 3 game over, 6 paused...
DEF wCranky_Shots          EQU $cbb4 ; shots fired
DEF wCranky_EventActor     EQU $cbb5 ; actor of the last event for the link
DEF wCranky_EventKind      EQU $cbb6 ; kind of that event
DEF wCranky_Events         EQU $cbb7 ; events queued for the link
DEF wCranky_RemoteEvents   EQU $cbb8 ; events handled from the other Game Boy
DEF wCranky_NextActorID    EQU $cbb9 ; id given to the next actor (wCranky_ActorID)
DEF wCranky_LinkState      EQU $cbba ; (5 bytes) random state and targets sent to the other Game Boy; also the final score digits
DEF wCranky_Game           EQU $cbbf ; 0 Buddies Beware, 1 Barrel O'Kremlings, 2 Wanted, 3 Kremling Krackdown, 4 Kremlings and Kongs, 5 Galleon Gunner
DEF wCranky_CursorX        EQU $cbc0 ; crosshair position
DEF wCranky_CursorY        EQU $cbc1
DEF wCranky_TileBuffer     EQU $cbc2 ; sprite tile buffer in use (double-buffered)
DEF wCranky_AmmoIcon       EQU $cbc3 ; ammunition icon of this game
DEF wCranky_Mode           EQU $cbc4 ; 1 one player, 2 link play
DEF wCranky_SavedSP        EQU $cbc5 ; (2 bytes) stack pointer to return to when the game ends
DEF wCranky_Time           EQU $cbc7 ; time left
DEF wCranky_TimeFrames     EQU $cbc8 ; frames to the next time step
DEF wCranky_Barrels        EQU $cbc9 ; barrels or waves left (Barrel O'Kremlings, Kremling games)
DEF wCranky_DimLevel       EQU $cbca ; background dimming while paused
DEF wCranky_Song           EQU $cbcb ; song of the game (Cranky_LoadBackground)
DEF wCranky_ReloadTimer    EQU $cbcc
DEF wCranky_SpawnDelay     EQU $cbcd
DEF wCranky_PauseItem      EQU $cbce ; pause menu option highlighted
DEF wCranky_PauseCursorX   EQU $cbcf ; (4 bytes) cursor position of each pause option
DEF wCranky_PauseCursorY   EQU $cbd3 ; (4 bytes) 
DEF wCranky_PauseItems     EQU $cbd7 ; options on the pause menu
DEF wCranky_KongShown      EQU $cbd8 ; a Kong is on screen (Kremlings and Kongs)
DEF wCranky_RepeatTimer    EQU $cbd9 ; auto-repeat of left and right
DEF wCranky_ShotMask       EQU $cbda ; bit per target already hit
DEF wCranky_TargetIcon     EQU $cbdb
DEF wCranky_TargetHits     EQU $cbdc ; (8 bytes) hits on each target; 4 knocks it down
DEF wCranky_TargetTimers   EQU $cbe4 ; (8 bytes) 
DEF wCranky_SpawnRate      EQU $cbec ; per-game speed of spawning; raised as the game goes on
DEF wCranky_SpawnRate2     EQU $cbed ; second spawn parameter
DEF wCranky_Ammo           EQU $cbee ; shots left; B reloads
DEF wCranky_AmmoMax        EQU $cbef ; a full load
DEF wCranky_ActorsUp       EQU $cbf0 ; actors on screen
DEF wCranky_Score          EQU $cbf1 ; (3 bytes) score, one decimal digit a byte, highest first
DEF wCranky_ScoreFlash     EQU $cbf4 ; (3 bytes) frames each score digit flashes after a change
DEF wCranky_TargetsUp      EQU $cbf7 ; bit per target standing
DEF wCranky_AmmoTile       EQU $cbf8 ; first tile of the ammunition icon
DEF wCranky_Result         EQU $cbf9 ; value returned to the menus when the game ends
DEF wCranky_BuddyCounts    EQU $cbfa ; (2 bytes) Buddies Beware: buddies spawned
DEF wCranky_Wanted         EQU $cbfc ; (11 bytes) Wanted: the suspect, poster and spawn state
DEF wCranky_Ending         EQU $cc07 ; the end effect has started
DEF wCranky_WantedRange    EQU $cc08 ; Wanted: how many kinds the random suspects are picked from
DEF wCranky_CrosshairBlink EQU $cc09 ; frames the crosshair blinks after a hit
DEF wCranky_ScreenFlash    EQU $cc0a ; frames the screen flashes
DEF wCranky_ShipsSunk      EQU $cc0b ; Galleon Gunner: ships hit
DEF wCranky_KremlingSpeed  EQU $cc0c ; (2 bytes) Kremling games: speed and its fraction
DEF wCranky_ScreenBuffer   EQU $d000 ; (2048 bytes) WRAMX: background being built
DEF wCranky_ActorType      EQU $db00 ; (32 bytes) routine in Cranky_RunActors' table; 0 = free
DEF wCranky_ActorX         EQU $db20 ; (32 bytes) 
DEF wCranky_ActorY         EQU $db40 ; (32 bytes) 
DEF wCranky_ActorAnimFlags EQU $db60 ; (32 bytes) bit 1: animation runs backwards
DEF wCranky_ActorAnimSpeed EQU $db80 ; (32 bytes) added to wCranky_ActorAnimTimer every frame
DEF wCranky_ActorFrames    EQU $dba0 ; (32 bytes) frames in the animation
DEF wCranky_ActorAnimTimer EQU $dbc0 ; (32 bytes) a carry moves to the next frame
DEF wCranky_ActorFrame     EQU $dbe0 ; (32 bytes) current frame
DEF wCranky_ActorSprite    EQU $dc00 ; (32 bytes) first sprite picture of the animation
DEF wCranky_ActorFlags     EQU $dc20 ; (32 bytes) bit 5: shootable (tentative)
DEF wCranky_ActorSpeed     EQU $dc40 ; (32 bytes) added to wCranky_ActorMoveTimer; a carry is one more step
DEF wCranky_ActorMoveTimer EQU $dc60 ; (32 bytes) 
DEF wCranky_ActorSteps     EQU $dc80 ; (32 bytes) whole steps a frame
DEF wCranky_ActorDir       EQU $dca0 ; (32 bytes) direction of movement (Cranky_MoveActorStep)
DEF wCranky_ActorTimer     EQU $dcc0 ; (32 bytes) frames to wait
DEF wCranky_ActorTarget    EQU $dce0 ; (32 bytes) target slot the actor stands at
DEF wCranky_ActorSavedFlags EQU $dd00 ; (32 bytes) wCranky_ActorAnimFlags kept while hit (tentative)
DEF wCranky_ActorVar       EQU $dd20 ; (32 bytes) per-game use (Galleon Gunner)
DEF wCranky_ActorID        EQU $dd40 ; (32 bytes) id shared with the other Game Boy (wCranky_NextActorID)
DEF hCranky_Actor          EQU $ff9c ; actor being run; index into the wCranky_Actor arrays
DEF hCranky_LinkOut        EQU $ff9d ; (16 bytes) state sent to the other Game Boy
DEF hCranky_LinkIn         EQU $ffad ; (16 bytes) state received
DEF hCranky_LinkIn2        EQU $ffbd ; (16 bytes) second receive buffer
DEF hCranky_LinkPos        EQU $ffcd ; low byte of the next byte to send
DEF hCranky_LinkCount      EQU $ffce ; bytes left to send
DEF hCranky_LinkTimer      EQU $ffcf
DEF hCranky_LinkSending    EQU $ffd0
DEF hCranky_LinkGotByte    EQU $ffd1 ; set by the serial handler
DEF hCranky_LinkRole       EQU $ffd3 ; $66 or $bb
DEF hCranky_LinkMode       EQU $ffd4 ; $bb while playing by link
DEF hCranky_LinkReceivePos EQU $ffd6 ; (2 bytes) where the next packet goes
DEF hCranky_LinkDelay      EQU $ffd8

; Funky's Fishing (banks $50-$52)
DEF wFishing_OAMBuffer     EQU $c800 ; (160 bytes) sprites built during the frame (Fishing_CopyOAM)
DEF wFishing_LinkFrameIn   EQU $c8a0 ; frame number in the last packet from the other Game Boy
DEF wFishing_LinkFrameOut  EQU $c8a1 ; frame number sent
DEF wFishing_LinkTimeout   EQU $c8a2 ; frames left to wait for the other Game Boy ($1e)
DEF wFishing_PartnerFlags  EQU $c8a3 ; flags received from the other Game Boy (tentative)
DEF wFishing_TileBufferHalf EQU $c8a4 ; which half of the sprite tile buffer is streamed to VRAM by HDMA
DEF wFishing_PauseCursor   EQU $c8a5 ; pause menu option (CONTINUE, QUIT?)
DEF wFishing_PauseConfirm  EQU $c8a6 ; QUIT? answer
DEF wFishing_PartnerPaused EQU $c8a9 ; the other player has paused
DEF wFishing_FrameReady    EQU $c8aa ; set when a frame's VBlank work is done (tentative)
DEF wFishing_Palettes      EQU $c9a0 ; (96 bytes) palettes being faded (Fishing_FadePalettes)
DEF wFishing_LinkBuffer    EQU $ca00 ; (256 bytes) link packets (tentative)
DEF wFishing_StackTop      EQU $cffb
DEF wFishing_BGPalettes    EQU $d800 ; (128 bytes) palettes a fade goes to: BG, then OBJ at $d880
DEF wFishing_OBJPalettes   EQU $d880 ; (128 bytes) 
DEF wFishing_FadeWork      EQU $d900 ; (96 bytes) (tentative)
DEF wFishing_InitArg       EQU $d960 ; (2 bytes) bc given to Fishing_Init
DEF wFishing_StartArg      EQU $d962 ; (2 bytes) de given to Fishing_Start (tentative)
DEF wFishing_Product       EQU $d964 ; (4 bytes) Fishing_MultiplySigned and Fishing_Multiply16's result
DEF wFishing_Multiplier    EQU $d968 ; (2 bytes) 
DEF wFishing_ProductSign   EQU $d96a ; bit 7: negative
DEF wFishing_FrameCounter  EQU $d96c
DEF wFishing_RandomState   EQU $d96d ; (3 bytes) Fishing_RandomRange's state
DEF wFishing_JoyHeld       EQU $dd6f ; buttons held (Fishing_ReadJoypad)
DEF wFishing_JoyPressed    EQU $dd70 ; buttons newly pressed
DEF wFishing_Unused_dd73   EQU $dd73 ; (2 bytes) cleared by Fishing_Init, never read
DEF wFishing_RodX          EQU $dd75 ; tip of the rod
DEF wFishing_RodY          EQU $dd76
DEF wFishing_HookX         EQU $dd77
DEF wFishing_HookY         EQU $dd78
DEF wFishing_HookTargetX   EQU $dd79 ; where the line is reeled in to
DEF wFishing_HookXSpeed    EQU $dd7a ; (2 bytes) 
DEF wFishing_HookYSpeed    EQU $dd7c ; (2 bytes) 
DEF wFishing_Reeling       EQU $dd7e ; set while the hook is reeled in
DEF wFishing_HookInWater   EQU $dd7f
DEF wFishing_HookState     EQU $dd80 ; 0: on the rod (tentative)
DEF wFishing_FunkyAnim     EQU $dd81 ; (12 bytes) Funky's animation (Fishing_SetAnim): +8 x, +$a y
DEF wFishing_RodAnim       EQU $dd8d ; (12 bytes) the rod's animation
DEF wFishing_HookAnim      EQU $dd99 ; (12 bytes) the hook's animation
DEF wFishing_CastState     EQU $dda5 ; (3 bytes) casting: power and direction (tentative)
DEF wFishing_Fish          EQU $dda8 ; (128 bytes) eight fish slots of 16 bytes (Fishing_SpawnFish, Fishing_MoveFish)
DEF wFishing_FishCount     EQU $de28 ; fish swimming
DEF wFishing_LineState     EQU $de29 ; (3 bytes) line and hook flags (tentative)
DEF wFishing_Hooked        EQU $de2c ; (96 bytes) fish on the hook, rising with the line; $ff = empty
DEF wFishing_HookedCount   EQU $de8c
DEF wFishing_Catch         EQU $de8d ; (8 bytes) kinds of the fish in this catch; $ff = none
DEF wFishing_CatchCount    EQU $de95
DEF wFishing_CatchByKind   EQU $de96 ; (5 bytes) fish of each kind in this catch, for combos
DEF wFishing_Score         EQU $de9b ; (4 bytes) score, highest byte first (Fishing_CheckScore500 compares its low three bytes with 500)
DEF wFishing_ScoreDigits   EQU $de9f ; (4 bytes) score digits being drawn
DEF wFishing_PointsToAdd   EQU $dea3
DEF wFishing_PartnerScore  EQU $dea4 ; (5 bytes) link play: the other player's score (and a flag before it)
DEF wFishing_ScoreRow      EQU $dea9 ; (8 bytes) tiles of the score row, uploaded by Fishing_UploadScoreRow
DEF wFishing_Meter         EQU $deb1 ; line meter; it rises with catches and falls over time
DEF wFishing_PartnerMeter  EQU $deb2 ; link play: the other player's meter
DEF wFishing_MeterStart    EQU $deb3 ; the meter's value at the start of the level
DEF wFishing_MeterRow      EQU $deb4 ; (10 bytes) tiles of the meter
DEF wFishing_PartnerMeterRow EQU $debe ; (10 bytes) 
DEF wFishing_WaterScroll   EQU $dec8 ; (6 bytes) water scroll positions and speeds (Fishing_ScrollWater)
DEF wFishing_LinkPacketIn  EQU $dece ; set when a packet has arrived
DEF wFishing_PauseFade     EQU $ded0
DEF wFishing_PauseTextPos  EQU $ded1 ; (2 bytes) 
DEF wFishing_Unused_ded3   EQU $ded3 ; (2 bytes) set by Fishing_InitPause, never read
DEF wFishing_MeterTimer    EQU $ded5
DEF wFishing_LevelMeter    EQU $ded6 ; meter value the level starts with
DEF wFishing_PointsByKind  EQU $ded7 ; (5 bytes) points for each fish kind
DEF wFishing_HookedKind    EQU $dedc ; kind of the fish being scored (tentative)
DEF wFishing_HookTimer     EQU $dedd
DEF wFishing_SampleMeter   EQU $dede ; meter level the last speech sample was played for
DEF wFishing_Combo         EQU $dedf ; combo picked by Fishing_ComboByCount
DEF wFishing_ComboKind     EQU $dee0
DEF wFishing_ComboTextTimer EQU $dee1 ; frames the combo text stays
DEF wFishing_ComboText     EQU $dee2 ; (5 bytes) combo text tiles
DEF wFishing_LinkCombo     EQU $dee7 ; (5 bytes) link play: the combo shown to the other player
DEF wFishing_MessagePointer EQU $deec ; (2 bytes) message that blinks between levels
DEF wFishing_MessageTimers EQU $deee ; (4 bytes) 
DEF wFishing_MessageTiles  EQU $def2 ; (8 bytes) 
DEF wFishing_Level         EQU $defa
DEF wFishing_LevelMeters   EQU $defb ; (9 bytes) meter start of each level ($46, $41, ..., $1e)
DEF wFishing_LinkComboSprite EQU $df04 ; (12 bytes) link play: the combo sprite
DEF wFishing_EndState      EQU $df10 ; (5 bytes) end of the game: who finished, and the meter drain in link play
DEF wFishing_WaterAnim     EQU $df15 ; (9 bytes) water tile animation (Fishing_AnimateWater)
DEF wFishing_PauseWindow   EQU $df1e ; (12 bytes) pause window size and position
DEF wFishing_PauseText     EQU $df2a ; (66 bytes) the pause menu's lines, $0b bytes each
DEF wFishing_PauseCursorPos EQU $df6c ; (2 bytes) 
DEF wFishing_PauseTextInfo EQU $df6e ; (6 bytes) 
DEF wFishing_Unused_df74   EQU $df74 ; (2 bytes) cleared by Fishing_Init, never read
DEF wFishing_Fanfare       EQU $df76 ; a fanfare is playing (Fishing_StartFanfare)
DEF wFishing_Reached500    EQU $df77 ; the score has passed 500
DEF wFishing_SpawnTimer    EQU $df78 ; (3 bytes) frames to the next fish, and how many may swim
DEF wFishing_PartnerState  EQU $df7b ; link play: the other player's state
DEF hFishing_LinkOut       EQU $ff8a ; (16 bytes) packet sent to the other Game Boy
DEF hFishing_LinkInA       EQU $ff9a ; (16 bytes) packet received; checksum in its last word
DEF hFishing_LinkInB       EQU $ffaa ; (16 bytes) second receive buffer
DEF hFishing_LinkLength    EQU $ffba ; bytes in a packet ($10)
DEF hFishing_LinkPos       EQU $ffbb ; low byte of the next byte to send
DEF hFishing_LinkLeft      EQU $ffbc ; bytes left
DEF hFishing_LinkRetries   EQU $ffbd
DEF hFishing_LinkFlags     EQU $ffbe
DEF hFishing_LinkBuffer    EQU $ffbf ; receive buffer in use (0 or 1)
DEF hFishing_SerialDone    EQU $ffc0 ; set by Fishing_SerialHandler
DEF hFishing_LinkRole      EQU $ffc2 ; b given to Fishing_Start: $ff one player, else the link side
DEF hFishing_LinkRole2     EQU $ffc3 ; $bb on one side of the link
DEF hFishing_PacketOK      EQU $ffc4 ; Fishing_LinkCheckPacket's result
DEF hFishing_ROMBank       EQU $ffc5 ; current ROM bank (Fishing_FarJump keeps it)
DEF hFishing_VRAMBank      EQU $ffc6 ; rVBK as last set
DEF hFishing_VBlankDone    EQU $ffc7
DEF hFishing_Scratch       EQU $ffc8 ; (6 bytes) scratch: numbers being compared, fish records, text
DEF hFishing_FarA          EQU $ffcf ; a kept across a far jump: Fishing_FarJump reloads it, the far returns keep a in it
DEF hFishing_FarHL         EQU $ffd0 ; (2 bytes) hl kept across a far jump (Fishing_FarJump reloads it)
DEF hFishing_RuntimeTemp   EQU $ffd2
DEF hFishing_OAMPos        EQU $ffd3 ; (2 bytes) next free entry in wFishing_OAMBuffer
DEF hFishing_TileCount     EQU $ffd5 ; sprite tiles to stream this frame
DEF hFishing_TileBufferPos EQU $ffd6 ; (2 bytes) next free byte in the sprite tile buffer ($d000)
DEF hFishing_SavedSP       EQU $ffd8 ; (2 bytes) stack pointer at Fishing_Start, restored by Fishing_RestartMainLoop
DEF hFishing_LinkSynced    EQU $ffda ; the serial handler skips the handshake while it is set (tentative)
DEF hFishing_Language      EQU $ffdb ; c given to Fishing_Start
DEF hFishing_SampleFrames  EQU $ffdc ; frames the sample still plays; at 0 the VBlank work stops it
DEF hFishing_SampleBank    EQU $ffdd ; bank of SampleTable
DEF hFishing_SampleTable   EQU $ffde ; (2 bytes) 
DEF hFishing_Scroll        EQU $ffe0 ; (9 bytes) scroll positions and speeds of the water layers (Fishing_InitScroll)
DEF hFishing_FinalScore    EQU $ffe9 ; (4 bytes) link play: this player's score at the end
DEF hFishing_FinalPartnerScore EQU $ffed ; (4 bytes) and the other player's

; The Hi-Score screen (bank $55; it also uses Funky's Fishing's HRAM, joypad and palettes)
DEF wHiScore_Loader        EQU $c800 ; (34 bytes) HiScore_InstallRuntime_Code is copied here and run: it installs the runtime
DEF wHiScoreRecord         EQU $dd75 ; (39 bytes) the table as saved: signature $48 $08, five entries of three letters and a 4-byte score, then the checksum (sum of the first $25 bytes)
DEF wHiScoreNames          EQU $dd9c ; (15 bytes) the five names, three letters each
DEF wHiScoreScores         EQU $ddab ; (20 bytes) the five scores, four bytes each, best first
DEF wHiScoreMoveBuffer     EQU $ddbf ; (15 bytes) entries moved down by HiScore_InsertScore
DEF wHiScoreDigits         EQU $ddce ; (40 bytes) the scores as digit tiles (HiScore_ScoresToTiles)
DEF wHiScoreNewName        EQU $ddf6 ; (3 bytes) name being entered ($fd = blank)
DEF wHiScoreNewRank        EQU $ddf9 ; place of the new score
DEF wHiScoreLetter         EQU $ddfa ; letter of the name being entered (0-2)

; Front-end code copied to RAM (FE_RAM_CODE)
DEF Cranky_SerialHandler   EQU $cc0e
DEF Cranky_LinkPacket      EQU $cc94
DEF FE_VBlank_Menu         EQU $ccba
DEF FE_VBlank_MenuBody     EQU $ccbc
DEF Cranky_FarCopySprites  EQU $ccdc
DEF FE_VBlank_Plain        EQU $ccfb
DEF FE_VBlank_Link         EQU $cd03
DEF FE_STAT_Gradient       EQU $cd47
DEF FE_STAT_Sound          EQU $cdda
DEF FE_Serial_Printer      EQU $cddf
DEF FE_Serial_Handshake    EQU $cdef
DEF FE_Serial_WaitForPartner EQU $ce2e
DEF FE_Serial_Flag         EQU $ce80
DEF FE_PrinterSerial       EQU $ce87
DEF FE_PrinterSendByte     EQU $ceb3
DEF FE_FarCopyBankSwitchingRAM EQU $cef7

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
DEF sHiScoreTable1         EQU $b400 ; (39 bytes) the Hi-Score table (layout of wHiScoreRecord), kept in three copies
DEF sHiScoreTable2         EQU $b427 ; (39 bytes) 
DEF sHiScoreTable3         EQU $b44e ; (39 bytes) 

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
