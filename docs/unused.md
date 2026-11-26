# Unused content

This page collects content in Donkey Kong Country (GBC) that the game appears never to use. It is text only: no images from the game are committed. To see the items, run

```bash
python3 tools/find_unused.py baserom.gbc unused
```

That writes a fuller report with images to `unused/`, which git ignores. The tables below come from that report; the notes are written by hand.

## How "unused" is decided

Something counts as unused when nothing the disassembly decodes refers to it. That covers code, object lists, animation scripts, frame and animation tables, level entrances and descriptors, map headers, palette preload lists and the flow script. Before an item is listed, the bytes of banks `$00`–`$0F` that aren't decoded yet are searched for its address, and any hit is reported as a *loose match*: a table there may still use it. That search has already uncovered real tables, which shrank the lists a lot. One blind spot remains: code that computes an address (for example "the frame after this one") leaves no pointer to find, so items right next to used ones deserve extra doubt.

## Sprite frames

89 of the 1,414 sprite frames are never shown by any animation, object or table found so far. The 18 with no loose match anywhere are the strongest finds:

| Frames | What they show |
|---|---|
| `Frame_20_4dda`, `4de6`, `4dec` | "STOP", "ON" and "OFF" signs (next to used frames, so possibly picked by arithmetic) |
| `Frame_20_5674`–`5686` | a mine cart tilting through four angles |
| `Frame_20_57a6`–`57b8`, `581e` | a small creature (four frames plus one related frame) |
| `Frame_20_5992`, `5cce` | a "FUEL" can and an "OIL" drum |
| `Frame_20_5e18`, `5e1e` | a gorilla-like character |
| `Frame_20_5ea8`, `5ec6` | a monkey-like character |

The other 71 have loose matches. They include letter sprites (A–Z, except the letters the game's own titles use), credits headings ("KREDITS", "KODING", "KARACTERS", "KOLORING", "KONCEPT", "KOMMANDER"), the ending caption in five languages ("THE END?", "FIN ?", "DAS ENDE(?)", "FINE…?", "¿FIN?"), a cast list ("KLAP TRAP", "KRUSHA", "KRITTER", "KLUMP", "KING K.ROOL") and rotating barrels. These are probably drawn through text or credits tables that aren't decoded yet.

| Frames | Count | Graphics bank | Loose matches |
|---|---|---|---|
| `Frame_20_4264` | 1 | `$22` | loose match at 00:3820 |
| `Frame_20_4b82`–`4ba0` | 6 | `$28` | loose match at 08:4e70, 08:4e76, 08:4e8e, 08:4eb6 … |
| `Frame_20_4bac`–`4bb8` | 3 | `$28` | loose match at 08:4ed7, 08:4f29, 08:4f3b, 08:4f51 |
| `Frame_20_4bc4`–`4bca` | 2 | `$28` | loose match at 08:4f26, 08:7942, 0b:4da2, 0b:4daa |
| `Frame_20_4bdc`–`4c54` | 21 | `$28` | loose match at 00:386c, 02:4ba2, 02:4ba9, 02:4bb0 … |
| `Frame_20_4c7e`–`4ca2` | 7 | `$28` | loose match at 05:44d6, 0b:477b, 0b:4a1c |
| `Frame_20_4dda` | 1 | `$29` | none |
| `Frame_20_4de6`–`4dec` | 2 | `$29` | none |
| `Frame_20_5032`–`505c` | 8 | `$2A` | loose match at 01:4fc0, 01:6d09, 05:4ced, 05:4ec3 … |
| `Frame_20_5476`–`547c` | 2 | `$31` | loose match at 00:3704 |
| `Frame_20_54d6` | 1 | `$31` | loose match at 0d:5958 |
| `Frame_20_5674`–`5686` | 4 | `$33` | none |
| `Frame_20_56b0` | 1 | `$33` | loose match at 0b:5307, 0b:5867, 0b:5eb0, 0b:5eb8 … |
| `Frame_20_57a6`–`57b8` | 4 | `$34` | none |
| `Frame_20_581e` | 1 | `$34` | none |
| `Frame_20_592c`–`5932` | 2 | `$34` | loose match at 08:583e, 0c:7b7f |
| `Frame_20_5992` | 1 | `$35` | none |
| `Frame_20_5cce` | 1 | `$37` | none |
| `Frame_20_5d46`–`5da0` | 16 | `$37` | loose match at 02:5d57, 02:5d5a, 02:5d5d, 02:5d69 … |
| `Frame_20_5e18`–`5e1e` | 2 | `$38` | none |
| `Frame_20_5ea8` | 1 | `$39` | none |
| `Frame_20_5ec6` | 1 | `$39` | none |
| `Frame_20_5f68` | 1 | `$39` | loose match at 08:4ce0, 08:4d10, 08:4e04 |

Since nothing uses these frames, the ROM doesn't say which palette they would be drawn with. The images `find_unused.py` writes to `unused/frames/` stay gray (or use the palette where one is known). A second set in `unused/frames_guessed_palette/` borrows the palette of the nearest frame in the same graphics bank that has a known palette, and the report lists, for every guess, which palette was used and which frame it came from. Those colors are guesses, not facts from the game.

## Animation scripts

12 scripts in bank `$04` are never started, but every frame they show is used by some other script, so nothing is hidden in them. Four have no loose match at all: `Anim_04_4aab`, `Anim_04_4d21`, `Anim_04_4d5b` and `Anim_04_4d9d`.

## Palettes

Four BG palette sets are used by none of the 128 level descriptors and have no loose match: `BGPaletteSet_0A`, `0D`, `10` and `25`. Set `$25` is nearly black, and its last palette is solid magenta, a common placeholder color. A set could still be loaded as "the level's set plus 64 bytes" (a darkened variant, say), which no pointer search can see. Ten object palettes are used by no object list, preload list or decoded code: IDs `$0D`, `$10`, `$12`, `$18`, `$1C`, `$1D` and `$3B`–`$3E`. That is the weakest claim here, since code can pick a palette from a value the tracer can't follow.

## Level blocks

Levels are built from 32×32-pixel blocks. 1,005 blocks are fully defined in the block banks but placed in no level map. Some may be swapped in by code at run time (breakable walls, switches, animated scenery), so these are candidates. Even so, some groups are clearly whole pieces of scenery. The treetop set (`LevelBlocks_93`) has 147 unplaced blocks, including what fits together as a large treehouse platform with rope bridges that no level contains.

| Block bank | Defined | Never placed | Used by maps |
|---|---|---|---|
| `LevelBlocks_90` | 629 | 24 | `MapHeader_04_65c4`, `MapHeader_04_65d3`, `MapHeader_04_65e8`, `MapHeader_04_65f7` … |
| `LevelBlocks_93` | 655 | 147 | `MapHeader_04_6624`, `MapHeader_04_6633`, `MapHeader_04_6642`, `MapHeader_04_6651` … |
| `LevelBlocks_96` | 974 | 103 | `MapHeader_04_666f`, `MapHeader_04_6684`, `MapHeader_04_6693`, `MapHeader_04_66a2` … |
| `LevelBlocks_99` | 372 | 20 | `MapHeader_04_66c0` |
| `LevelBlocks_9c` | 927 | 24 | `MapHeader_04_66d5`, `MapHeader_04_66e4`, `MapHeader_04_66f3`, `MapHeader_04_6702` … |
| `LevelBlocks_9f` | 90 | 45 | `MapHeader_04_675c`, `MapHeader_04_676b` |
| `LevelBlocks_a5` | 809 | 90 | `MapHeader_04_677a`, `MapHeader_04_6789`, `MapHeader_04_6798`, `MapHeader_04_67ad` … |
| `LevelBlocks_ab` | 586 | 9 | `MapHeader_04_685e`, `MapHeader_04_686d`, `MapHeader_04_687c`, `MapHeader_04_688b` … |
| `LevelBlocks_b1` | 979 | 27 | `MapHeader_04_68b8`, `MapHeader_04_68cd`, `MapHeader_04_68dc`, `MapHeader_04_68eb` … |
| `LevelBlocks_b4` | 416 | 84 | `MapHeader_04_6909` |
| `LevelBlocks_b7` | 1021 | 22 | `MapHeader_04_691e`, `MapHeader_04_692d`, `MapHeader_04_6942`, `MapHeader_04_6951` … |
| `LevelBlocks_bd` | 691 | 87 | `MapHeader_04_6a4d`, `MapHeader_04_6a62`, `MapHeader_04_6a77`, `MapHeader_04_6a8c` … |
| `LevelBlocks_c0` | 911 | 97 | `MapHeader_04_6af5`, `MapHeader_04_6b04`, `MapHeader_04_6b19`, `MapHeader_04_6b2e` … |
| `LevelBlocks_c3` | 216 | 68 | `MapHeader_04_6c2d`, `MapHeader_04_6c3c`, `MapHeader_04_6c4b`, `MapHeader_04_6c5a` … |
| `LevelBlocks_c6` | 233 | 65 | `MapHeader_04_6b88`, `MapHeader_04_6b97`, `MapHeader_04_6ba6` |
| `LevelBlocks_c9` | 228 | 93 | `MapHeader_04_6bb5`, `MapHeader_04_6bc4`, `MapHeader_04_6bd3`, `MapHeader_04_6be2` … |

## Level tiles

Two level tilesets contain tiles that no block uses at all, placed or not: 8 in `BGTiles_84_59f0` and 8 in `BGTiles_89_5e10`.

## World maps

The eight world maps take their BG palettes from 128-byte blocks in bank `$0F`, spaced `$80` apart. Six blocks in that run are used by no map record:

| Block | Contents |
|---|---|
| `$499C`, `$4A1C`, `$4D9C`, `$4E1C` | one pale color throughout: blank filler |
| `$4A9C` | blank except a magenta palette and a pink ramp, typical placeholder colors |
| `$4E9C` | first half blank; second half eight clean color ramps (magenta, yellow, brown, orange, gray, blue, green, red), which looks like a test palette |

Only the first 64 bytes of each block (8 BG palettes) reach the screen, so the colors in `$4E9C`'s second half would never show even if the block were loaded. Three world tilesets have tiles no world map uses: 7 in `BGTiles_18_55c0`, 9 in `BGTiles_19_4000` and 3 in `BGTiles_1b_4000`. These could still appear through the map's own code, for example as level markers.

World map 7 is reached by no location in the location table, but `Func_05_4274` checks for it by number, so code uses it directly. It shows the same island as map 0, with a different list of level markers.

## Checked and found complete

These turned up nothing unused, which is worth knowing too:

| What | Result |
|---|---|
| Level maps | all 112 map headers are used by level descriptors, and every byte of compressed map data in banks `$E0`–`$EC` belongs to a map |
| Level descriptors | all 128 are reached by at least one of the 237 entrance records |
| Full screens | all 39 screen records in their banks are loaded by the flow script, with no unreferenced records next to them |
| Game states | every state in the `$0300` jump table is selected by the flow script or by code |

## Not identified yet

Large parts of these banks aren't claimed by anything decoded so far, so they hold either content not yet understood or unused data: `$01`–`$02`, `$0B`–`$0C`, `$10`–`$14`, `$40`–`$43`, `$45`, `$50`–`$6F` and `$74`. Banks `$18`–`$1B`, listed here before, turned out to be the world map tilesets. Banks `$40` and `$41` hold the world map's sprite tiles and palettes. Nothing in these banks should be called unused until it has been identified.
