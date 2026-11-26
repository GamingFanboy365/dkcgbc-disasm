# Donkey Kong Country (Game Boy Color) disassembly

This is a work-in-progress disassembly of **Donkey Kong Country** for the Game Boy Color (USA/Europe, En/Fr/De/Es/It). The goal is source that RGBDS can assemble back into a byte-for-byte copy of the original ROM:

| Field | Value |
|---|---|
| Title / game code | `DK COUNTRY` / `CGB-BDDE` |
| Cartridge | MBC5 + SRAM + battery, 4 MiB ROM (256 banks), 8 KiB SRAM |
| CGB flag | `$C0` (Game Boy Color only) |
| SHA-1 | `32522dfce902d564e69348541348afc054307f65` |

## Building

You need [RGBDS](https://rgbds.gbdev.io) (tested with 1.0.4), GNU Make and Python 3. The repository contains no ROM data. Put your own dump of the game in the repository root and name it `baserom.gbc`. Any part of the game that has not been disassembled yet is taken from that file with `INCBIN`, so the build needs it until the disassembly is complete. Then run:

```bash
make
```

The ROM is built as `dkc.gbc` and checked against `rom.sha1`. Set `RGBDS=/path/to/rgbds/` if the tools are not on your `PATH`.

You can also check the sources without RGBDS. `make check` re-assembles every file with a small Python assembler (`tools/check_asm.py`) and compares the result with `baserom.gbc` byte by byte. It only understands the syntax the generator writes, so it catches layout and label mistakes; it is no substitute for a real RGBDS build.

## How the sources are produced

The first pass is automatic. `tools/emit.py` (run it with `make generate`) traces the code from known entry points and writes one `src/bank_XX.asm` per bank in which it found code. Every bank with no traced code goes into `src/data_banks.asm`. The tracer starts from the reset and interrupt vectors, the entry point, the game-state jump table at `$0300`, the music command table at `$3F00`, the object initialiser lists and the start of each code bank. It follows calls and jumps across banks by watching for writes to the MBC5 bank register and calls to the game's far-call routines. Gaps it cannot reach get one cautious speculative pass: a gap is kept as code only if the whole path decodes cleanly and doesn't collide with code that is already known. Everything else stays as data, either short `db` runs or `INCBIN` slices of the base ROM.

All the manual knowledge lives in `tools/hints.py`. That file holds the extra entry points, the jump and pointer tables, and the names given to routines. When you identify something, add it there and regenerate. Once a generated file has been edited by hand, list it in `hints.KEEP` so the generator won't overwrite it.

## What is known so far

Bank 0 (home) holds start-up, the main loop, interrupt trampolines and the shared helpers. Boot code checks for a Game Boy Color and jumps to `NotGBC` on other hardware. It then clears memory, copies the OAM DMA routine (`OAMDMARoutine`) to `$FFC8`, and installs RAM trampolines for the VBlank (`$C32D`) and LCD (`$C330`) interrupts. The main loop waits on `$FF83` (set by VBlank), then uses `$FF84` as an index into the jump table at `$0300`.

The game switches banks in two ways. Code in bank 0 often writes the bank number straight to `rROMB0` and restores it afterwards. Code banks store their own bank number at `$4000`, which lets `ld a, [$4000]` read the active bank. `rst $00` is a far call with inline arguments (`dw address`, `db bank`), wrapped by the `rst_farcall` macro.

Banks `$F0`–`$FE` hold a second, largely self-contained program with its own stack (`$CFF6`), its own HRAM layout (`$FF81` is its current-bank variable) and its own far-call routine, `FarCall_A_HL` at `$3FC0` (bank in `a`, address in `hl`). HRAM names therefore differ between the two programs, which is why HRAM addresses are still written as raw numbers.

The music engine lives in bank 0 too. `PlaySong` resets four channel blocks at `$D000`–`$D3FF`, and every frame `UpdateMusic` steps each channel with `UpdateMusicChannel`. That routine reads the channel's sequence: bytes from `$80` up are notes, and lower bytes are commands dispatched through the pointer table at `$3F0A`.

### Objects

Objects are `$40`-byte slots at `wObjects` (`$C800`) `+ bc`. Slot 0 is the player (`wPlayer`), and `InitObjectSlots` puts the other 31 slots on the free list at `wObjectFreeList`. `AllocObject` takes a slot from that list, clears it and returns its offset in `bc`, with carry set if none are free. Every frame `RunObjects` visits each active object, maps its `OBJ_BANK` and jumps to its `OBJ_HANDLER`. Handlers change behaviour by overwriting their own `OBJ_HANDLER` field.

The slot layout is in `include/objects.inc`, which `tools/emit.py` generates from `OBJ_FIELD_TABLE` in `tools/hints.py`. The generator writes object accesses symbolically, as `ld hl, wObjects + OBJ_X` followed by `add hl, bc`, or `[wPlayer + OBJ_X]` for the player. These fields are understood so far:

| Offset | Field | Meaning |
|---|---|---|
| `$00` | `OBJ_FLAGS` | flags (bit 2: counted in a spawn group, bit 5: flicker) |
| `$01` | `OBJ_BANK` | bank of the handlers |
| `$02` | `OBJ_HANDLER` | per-frame code |
| `$04` | `OBJ_TOUCH_HANDLER` | jumped to when the player is in range (tentative) |
| `$06`–`$09` | `OBJ_GROUND_Y`, `OBJ_TERRAIN_A/B` | what the terrain lookup found under the object |
| `$0D`–`$15` | `OBJ_TARGET_XVEL`, `OBJ_XACCEL`, `OBJ_XVEL`, `OBJ_XSUB`, `OBJ_X` | horizontal motion |
| `$16`–`$1E` | `OBJ_TARGET_YVEL`, `OBJ_YACCEL`, `OBJ_YVEL`, `OBJ_YSUB`, `OBJ_Y` | vertical motion |
| `$1F` | `OBJ_OAM_ATTR` | sprite attributes |
| `$20`–`$26` | `OBJ_FRAME`, `OBJ_ANIM`, `OBJ_ANIM_SPEED`, `OBJ_ANIM_TIMER`, `OBJ_ANIM_FLAGS` | animation state |
| `$27` | `OBJ_SPAWN_INDEX` | entry in the level's object tables at `$A8xx`–`$AFxx` |
| `$28`, `$29` | `OBJ_ANIM_PARAM`, `OBJ_COLLISION` | tentative |
| `$2A`, `$2B` | `OBJ_PALETTE`, `OBJ_LAYER` | palette slot and sprite layer |

Positions are 24-bit fixed point (a fraction byte plus a pixel word), and velocities are in 1/256 pixel per frame. Each frame `Func_00_39fa` moves each velocity towards its target by the matching acceleration. The init lists show how that's used: falling objects start with `OBJ_TARGET_YVEL = $07FF` as their top fall speed and `OBJ_YACCEL = $0050` as gravity. The remaining offsets (`OBJ_VAR_0A`–`$0C` and `OBJ_VAR_2C`–`$3F`) belong to each object type, and what they mean depends on the handler.

Objects are set up from initialiser lists, which `ApplyObjInit` (and `InitObject`, which calls it) applies to the object in `bc`. A list is a run of entries ending in a byte of `$81` or above:

| Bytes | Macro | Meaning |
|---|---|---|
| `ff vv` (`ff` < `$40`) | `obj_byte field, value` | set byte field `ff` |
| `$40\|ff, lo, hi` | `obj_word field, value` | set word field `ff` |
| `$80, lo, hi` | `obj_include list` | apply another list, then continue |
| `$81`–`$FF` | `obj_end` | end of list (the game uses `$81`) |

In the sources these lists are labelled `ObjInit_BB_AAAA`. Code usually loads `hl` with a constant right before calling `ApplyObjInit`, so the tracer reads each list and follows its handler. Bank `$0E` is nothing but 981 consecutive lists (`$4000`–`$79F3`). Those are the ones level data refers to: the level spawner near `$17F0` maps bank `$0E` and calls `InitObject` with a pointer taken from the level's object table in RAM. Following these handlers is what opened up most of banks `$08`–`$0A`.

### Animation

Objects that animate call `Func_00_127d` every frame. It counts `OBJ_ANIM_TIMER` down, and when the timer runs out it runs the script at `OBJ_ANIM` (bank `$04`, `$4001`–`$5746`) until it reaches a frame. Each script entry is a word. With bit 15 clear the word points to a frame header: it goes into `OBJ_FRAME`, the timer is reloaded from `OBJ_ANIM_SPEED`, and the step ends. Otherwise the low byte is an argument and bits 8–14 pick a command, which runs straight away:

| Word | Macro | Effect |
|---|---|---|
| `$8000`, `dw` | `anim_jump script` | continue at another script (how loops are made) |
| `$81nn` | `anim_speed n` | frames per step from now on |
| `$8200`, `dw` | `anim_call routine` | call a routine, with bank `$04` mapped |
| `$8300` | `anim_clear_flag` | clear bit 7 of `OBJ_ANIM_FLAGS`, which handlers poll |
| `$84nn` | `anim_param n` | set `OBJ_ANIM_PARAM` |
| `$8500`, `dw` | `anim_var38 value` | set the word `OBJ_VAR_38` |
| `$86nn` | `anim_xor_attr mask` | toggle `OBJ_OAM_ATTR` bits |
| `$87nn`–`$8Ann` | `anim_sfx channel, id` | play a sound effect on channel 1–4 |

Frames are 6-byte headers in bank `$20`: 1,415 of them, the first one empty (`frame_none`). `frame tiles, offsets, count` names the frame's graphics (`count` 8×8 tiles) and its sprite offset list, which are both in the bank stored in the header's last byte (`$21`–`$3A`). `Func_00_1037` copies the tiles to VRAM with HDMA and draws one 8×16 sprite per pair of tiles. Each sprite is placed by a signed `(dx, dy)` pair relative to the sprite before it, starting from the object's screen position. The draw code mirrors the offsets when the object is flipped. Each graphics bank holds its frames' tiles from `$4000` up, followed by all of its offset lists. In the sources these are `Anim_04_XXXX`, `Frame_20_XXXX`, `FrameTiles_BB_XXXX` (see Graphics below) and `FrameSprites_BB_XXXX`. Code that stores a constant into `OBJ_ANIM` or `OBJ_FRAME` is written with `LOW()`/`HIGH()` of the label.

### Graphics

Every sprite frame's tiles are a PNG at `gfx/frames/BB/AAAA.png`, named after the bank and address of the tiles. Each image is 16 pixels tall and holds the frame's 8×16 sprites side by side, in drawing order. The four grays, from white to black, are color indexes 0–3, and white (0) is transparent. The build turns each PNG into a `.2bpp` file with `rgbgfx -c dmg -Z`, and the bank sources `INCBIN` that file. Edit a PNG and the next `make` puts the change in the ROM. Keep the image size the same: the frame header's tile count and the offset list depend on it.

The PNGs are created from `baserom.gbc` by `make extract`, which the build also runs automatically when they're missing, and existing files are never overwritten. They are not committed yet, so the repository still holds no graphics from the game. `python3 tools/gfx.py preview` assembles every frame from its sprites and offsets into `gfx/preview/`, which makes them easier to recognise. Those images are for looking at only and aren't used by the build. The colors are placeholders until the game's palettes are decoded.

### Palettes

All colors live in bank `$80`, written with `rgb r, g, b` (0–31 per channel).

| Range | Contents |
|---|---|
| `$4000`–`$41FF` | `ObjPalette_00`–`3F`: 64 object palettes of 4 colors |
| `$4200`–`$4256` | 11 preload lists (`obj_pal_preload id, …`) |
| `$4257`–`$5016` | `BGPaletteSet_00`–`36`: 55 sets of 8 BG palettes |

At run time `wBGPalettes` and `wOBJPalettes` (`$C100`/`$C180`) hold the palettes as defined. `UpdatePalettes` scales them by `wPaletteBrightness` towards black or white (`FadePalettesToBlack`/`ToWhite`) into `wBGPalettesOut`/`wOBJPalettesOut`, then uploads whatever `wPaletteUpdate` marks as changed.

Object palettes are shared and reference-counted. An object's `OBJ_PALETTE` is a palette ID. `AllocObjPalette` gives the first object with that ID a free hardware slot (0–7) and copies colors 1–3 into it. Color 0 is transparent and never copied. Later objects with the same ID reuse the slot. `InitObject` ORs the slot into `OBJ_OAM_ATTR`, and `FreeObjPalette` releases it when the last user is deleted. `PreloadObjPalettes` fills slots 0, 1, 2… from a preload list. Levels call it, and so do a few screens set up directly by code at `$05A8`.

Levels are described in bank `$04`. `LevelTable` has two entrance pointers per level number. Entrance records (`LevelEntrance_04_XXXX`) are 8 bytes, and there are 237 of them: the table reaches 75, and warps such as bonus rooms reach the rest. Each record points to one of 128 level descriptors (`LevelDesc_04_XXXX`, 12 bytes). A descriptor names the BG palette set, the OBJ preload list and the level's other data.

`tools/frame_palettes.py` works out which palette each sprite frame is drawn with, by following objects from their init lists through their handlers to the animations they play. `tools/gfx.py preview` uses that to color the previews. Frames reached only through code the tracer doesn't follow yet stay gray, and `gfx/preview/index.csv` lists which palettes are certain and which are inferred.

### Backgrounds

**Levels.** A level descriptor points to a map header in bank `$04` (`MapHeader_04_XXXX`, 112 of them). The header names a block bank, a terrain bank, flags (bit 0: vertical level, bit 1: twice the size), a tileset and the map data. A level map is a grid of 32×32-pixel blocks: 16 rows × 256 columns for horizontal levels and 64 × 64 for vertical ones, doubled when flag bit 1 is set. Three compressed layers are unpacked by `Func_00_03e4` into WRAM banks 1–3 (plus 5–7 for the second half). They hold each cell's block number, its block attribute and its terrain. Each control byte n of the compression is one of these:

| n | Meaning |
|---|---|
| `$00` | end of data |
| `$01`–`$7F` | repeat the next byte n times |
| `$80`–`$BF` | copy `n & $3F` literal bytes |
| `$C0`–`$FF` | copy `n & $3F` bytes from d bytes back in the output (d is the next byte) |

Blocks are 4×4 tiles defined in a pair of block banks (`LevelBlocks_XX`), stored as 16 planes of `$400` bytes. Bit 2 of the block attribute picks the second bank. Even entries are tile numbers and odd entries are CGB tile attributes. `Func_00_0c24` (horizontal) and `Func_00_0ce4` (vertical) draw blocks into the BG map as the camera moves. The terrain layer works on the same 32-pixel grid, and `Func_00_2214` reads it through height tables in the terrain bank (`LevelTerrain_XX`).

**Full screens.** Title, credits, ending and similar screens are 20×18 tile maps. A screen record (`Screen_BB_XXXX`) points to 8 BG palettes, the tile map (360 attribute bytes, then 360 tile numbers) and the tiles. The loader copies 128 bytes of palettes, so the "OBJ palettes" it also loads are whatever bytes follow. That's harmless, since these screens have no sprites.

**Tiles.** A tileset is 8 KB copied by HDMA into VRAM: tiles 0–127 at `$9000`, 128–255 at `$8800`, then the same in VRAM bank 1. Some tilesets overlap the next one, so each tile bank is split at every start address. Each piece is a PNG in `gfx/bgtiles/BB/AAAA.png`, 16 tiles per row (plus `AAAA_end.png` for a partial last row). PNGs are extracted from the base ROM and built with `rgbgfx -c dmg`, like the sprite frames, and are not committed.

**World maps.** The eight world maps (state `$0D`, `$1A58`) are listed in `WorldMapTable` in bank `$05`, indexed by a per-location table at `$05:491E`. A record (`WorldMap_05_XXXX`) points to the tile map and BG palettes in bank `$0F` and to a regular 8 KB tileset in banks `$18`–`$1B`. The tile map (`WorldTileMap_0F_XXXX`) is a width byte n, then n columns of 18 tile numbers followed by their 18 attributes. `Func_00_1f8a` copies it to WRAM, and `Func_00_1f0a` draws it as the map scrolls. The map's sprites (Kongs, level markers) get their tiles from banks `$40`–`$41` and their palettes from `$41:5380`.

**Flow script.** The game's overall sequence (boot, title, menus, level entry, credits) is a script in bank `$0D` (`Flow_0D_XXXX`), run by `Func_00_38cd`. Each byte is a game state, an offset into the jump table at `$0300`, and a few take arguments (`flow_load_screen`, `flow_wait`, `flow_play_song`, `flow_fade`, `flow_jump`). State `$61` hands control to the separate program in banks `$F0`–`$FE`.

`python3 tools/backgrounds.py` renders every level map, world map and full screen to `gfx/backgrounds/` (gitignored). Each map is drawn with the BG palettes of its first descriptor, as stored in the ROM. Some levels change palettes while playing, so a render can differ from what's on screen.

### The bonus and front-end programs

Besides the adventure itself, the cartridge holds two more programs, each with its own stack, HRAM and WRAM use. They are therefore excluded from the main game's RAM names (`hints.SECOND_PROGRAM_BANKS`).

**Banks `$F0`–`$FF`: the front end and bonus system.** The flow script enters it with state `$61` (`Func_00_3d28` calls `$F1:4000`). Its text is in bank `$FF`, in five languages, and shows what it covers:

| Area | Contents |
|---|---|
| Main menu | Adventure, Bonus, Link, Print, Options |
| Save files | three files, with copy and erase |
| Options | sound test, view items, alphabet, make flag, language, and toggles such as "DK barrels on/off", "Neckys on/off" and "normal tyres" |
| Bonus games | *Crosshair Cranky*, with its modes "Kremling Krackdown", "Kremlings and Kongs", "Barrel O'Kremlings", "Wanted" and "Buddies Beware" (instructions included), and *Funky's Fishing* |
| Link play | link-cable two-player messages |
| Game Boy Printer | printer support, with status messages, a picture album and unlockable print features |

Code in these banks calls across banks in two ways. `FarCall_A_HL` (`$3FC0`) takes the bank in `a` and the target in `hl`. The other way pushes the return address `$3FD5` and the target a byte at a time (`ld a, n / push af / inc sp`), puts the bank in `a` and jumps to `$3FDC`.

**Banks `$50`–`$6F`: Funky's Fishing, plus graphics shared with the front end.** Running the game in an emulator confirms it: choosing Bonus → Funky's Fishing enters `$50:4000`, which bank `$F2` far-jumps to (`Func_f2_72d7` and one other place). The game installs its own runtime in RAM: `$C800` copies `$51:42F4`–`$44F0` to `$CB00`. Its far calls push the return address, the bank, the cleanup routine `$CBA7` and the target, then jump to `$CB99` with the bank in `a`. The game draws its scenery from raw 20×18 screens in bank `$51` (360 attribute bytes, then 360 tile numbers, the same layout as the main game's full screens). `Func_51_4000` loads the one-player screen at `$51:6A90` or the second version at `$51:6D60`, the palettes at `$51:7090`/`$70D0` and a 12×4 box from `$51:7030`. Every frame, its main loop also streams a 4 KB buffer from WRAM into VRAM by HDMA, which animates its sprites (fish tiles come from bank `$52`). Its pause menu ("CONTINUE", "QUIT?") is in bank `$50` in five languages. Banks `$53`–`$6F` are graphics and layout data, used by the fishing game (banks `$51`, `$5C`) and by the front end's title screen and menus (banks `$5B`, `$5C`, `$61`, `$66`).

### Unused content

`python3 tools/find_unused.py` lists sprite frames, animation scripts, palettes, level blocks and tiles that nothing decoded so far refers to. The findings, as text, are in [`docs/unused.md`](docs/unused.md). It writes a report and images to `unused/`, which is gitignored because the images are the game's graphics. Before calling anything unused, it searches the undecoded bytes of banks `$00`–`$0F` for its address and reports any hits. That search is how the frame and animation pointer tables in banks `$00` and `$08`–`$0A` were found. The tracer now decodes those tables (`FrameTable_…`, `AnimTable_…`), so they count as uses.

## Status

The ROM rebuilds byte for byte, but that alone doesn't mean it's disassembled: anything not yet understood is taken from `baserom.gbc` unchanged. `python3 tools/coverage.py` measures where things stand. As of the last update:

| Category | Size | Share of non-empty ROM |
|---|---|---|
| Code disassembled into readable instructions | 91 KB | 3.4% |
| Data decoded into readable structures | 102 KB | 3.8% |
| Graphics converted to editable PNGs | 612 KB | 23.1% |
| Located and labelled, format known, still raw bytes | 1114 KB | 42.0% |
| Not identified yet | 734 KB | 27.7% |

The remaining 1.4 MB is empty padding and isn't counted. Measured by understanding rather than bytes, the project is much earlier: the code is traced, but only a few dozen of its roughly 8,000 labels have real names. Placeholders such as `Func_09_4001` (bank `$09`, address `$4001`) and `.jump_44f5` are waiting for names.

Code banks found so far are `$00`, `$04`, `$05`, `$07`, `$08`, `$09`, `$0A`, `$0D`, `$0F`, `$50`–`$52`, `$F0`, `$F1`, `$F2`, `$F5` and `$FE`. Decoded so far:

| Content | Coverage |
|---|---|
| Object initialiser lists | 1,114 |
| Animation scripts | 425 |
| Sprite frames | all 1,415 |
| Palettes | all |
| Level table, entrances and descriptors | all |
| Level maps, world maps and full screens | all |
| Flow script | all |

### Plan

The retail ROM comes first: the goal is a complete (100%) disassembly, with every byte identified and decoded and every routine named. Only after that does work start on the earlier demo build (`Donkey Kong Country (U) [demo]`) and the comparison between the two. The order of work:

1. Identify what's left: banks `$50`–`$6F`, `$01`–`$02`, `$0B`–`$0C`, `$10`–`$14`, `$40`–`$45` and the undecoded parts of the code banks.
2. Convert the located raw data (block banks, terrain, compressed maps) into readable or editable form.
3. Name and document the code, system by system, including the separate program in banks `$F0`–`$FE`.
4. Then the demo.

Running the ROM in an emulator (PyBoy, used only locally and never in the build) has become part of the method. It identifies what each part of the ROM is and shows which code and data the game really touches at run time, which catches what static tracing misses and settles whether content is truly unused.

Later, and kept apart from the disassembly, a `wiki/` folder may hold AI-written articles about the game's subjects, drawing on this research and on public sources. Nothing in it feeds back into the sources or documentation of the disassembly.
