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

### Unused content

`python3 tools/find_unused.py` lists sprite frames, animation scripts and palettes that nothing decoded so far refers to. It writes a report and images to `unused/`, which is gitignored because the images are the game's graphics. Before calling anything unused, it searches the undecoded bytes of banks `$00`–`$0F` for its address and reports any hits. That search is how the frame and animation pointer tables in banks `$00` and `$08`–`$0A` were found. The tracer now decodes those tables (`FrameTable_…`, `AnimTable_…`), so they count as uses.

### Status

Code banks found so far are `$00`, `$04`, `$05`, `$07`, `$08`, `$09`, `$0A`, `$0D`, `$0F`, `$F0`, `$F1`, `$F2`, `$F5` and `$FE`. Roughly 69 KB of code has been traced, plus 1,114 object initialiser lists, 425 animation scripts, all 1,415 sprite frames, all palettes and the level table, entrances and descriptors. Labels such as `Func_09_4001` (bank `$09`, address `$4001`) and `.jump_44f5` are placeholders waiting for real names.
