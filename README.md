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

Objects are `$40`-byte slots at `$C800 + bc`. `AllocObject` takes a free slot offset from the list at `$C400` (count in `$C440`), clears the slot and returns it in `bc`, with carry set if none are free. Every frame `RunObjects` visits each active object, maps its `OBJ_BANK` and jumps to its `OBJ_HANDLER`. Handlers change behaviour by overwriting their own `OBJ_HANDLER` field.

Objects are set up from initialiser lists, which `ApplyObjInit` (and `InitObject`, which calls it) applies to the object in `bc`. A list is a run of entries ending in a byte of `$81` or above:

| Bytes | Macro | Meaning |
|---|---|---|
| `ff vv` (`ff` < `$40`) | `obj_byte field, value` | set byte field `ff` |
| `$40\|ff, lo, hi` | `obj_word field, value` | set word field `ff` |
| `$80, lo, hi` | `obj_include list` | apply another list, then continue |
| `$81`–`$FF` | `obj_end` | end of list (the game uses `$81`) |

The only fields named so far are `OBJ_FLAGS` (`$00`), `OBJ_BANK` (`$01`) and `OBJ_HANDLER` (`$02`). In the sources these lists are labelled `ObjInit_BB_AAAA`. Code usually loads `hl` with a constant right before calling `ApplyObjInit`, so the tracer reads each list and follows its handler. Bank `$0E` is nothing but 981 consecutive lists (`$4000`–`$79F3`). Those are the ones level data refers to: the level spawner near `$17F0` maps bank `$0E` and calls `InitObject` with a pointer taken from the level's object table in RAM. Following these handlers is what opened up most of banks `$08`–`$0A`.

Code banks found so far are `$00`, `$05`, `$07`, `$08`, `$09`, `$0A`, `$0D`, `$0F`, `$F0`, `$F1`, `$F2`, `$F5` and `$FE`. Roughly 68 KB of code has been traced, plus 1,109 object initialiser lists. Labels such as `Func_09_4001` (bank `$09`, address `$4001`) and `.jump_44f5` are placeholders waiting for real names.
