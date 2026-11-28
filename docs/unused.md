# Unused content

This page collects content in Donkey Kong Country (GBC) that the game appears never to use. It is text only: no images from the game are committed. To see the items, run

```bash
python3 tools/find_unused.py baserom.gbc unused
```

That writes a fuller report with images to `unused/`, which git ignores. The tables below come from that report; the notes are written by hand.

## How "unused" is decided

Something counts as unused when nothing the disassembly decodes refers to it. That covers code, object lists, animation scripts, frame and animation tables, level entrances and descriptors, map headers, palette preload lists and the flow script. Before an item is listed, the bytes of banks `$00`–`$0F` that aren't decoded yet are searched for its address, and any hit is reported as a *loose match*: a table there may still use it. That search has already uncovered real tables, which shrank the lists a lot. One blind spot remains: code that computes an address (for example "the frame after this one") leaves no pointer to find, so items right next to used ones deserve extra doubt.

## Sprite frames

104 of the 1,414 sprite frames are never shown by any animation, object, table or script found so far. Now that every byte of the main game's banks is identified, none of them has even a loose match left (its address turning up in undecoded bytes), so these are firm finds as far as the disassembly can tell.

| Frames | What they show |
|---|---|
| `Frame_20_4bac`, `4bb8`, `4bc4`, `4be2`, `4c00`, `4c18` | letter blocks H, J, L, Q, V and Z, the six letters none of the letter-block words uses (see Object data below) |
| `Frame_20_4c1e`–`4c54` | a barrel turning, ten frames |
| `Frame_20_5032`–`505c` | a DK barrel turning, eight frames |
| `Frame_20_4c7e`–`4ca2` | character pictures, among them Donkey Kong, seven frames |
| `Frame_20_5476`, `547c`, `54d6` | Rambi in two poses and a fish (probably Enguarde) |
| `Frame_20_5674`–`5686`, `56b0` | a mine cart tilting through four angles, and one more cart |
| `Frame_20_57a6`–`57b8`, `581e` | a small creature (four frames plus one related frame) |
| `Frame_20_592c`, `5932` | two thin vertical strips |
| `Frame_20_5992`, `5cce` | a "FUEL" can and an "OIL" drum |
| `Frame_20_5e18`, `5e1e` | a gorilla-like character |
| `Frame_20_5ea8`, `5ec6` | a monkey-like character |
| `Frame_20_4264` | a small cloud or splash |
| `Frame_20_4b58`–`4b7c`, `4f8a`–`4fae`, `44f8`–`451c`, `44c2`–`44e6` | the Rambi, Winky, Expresso and Enguarde animal tokens turning, seven frames each; the heads-up display shows only each token's first frame, as a still picture (`HUD_Items_Hidden`) |
| `Frame_20_60ac`–`60ee` | a coin turning, twelve frames |
| `Frame_20_4a3e`–`4a5c`, `4a62` | Croctopus: six frames of curling tentacles and a single pose, filed with his other frames |
| `Frame_20_4e10`, `5446`, `51d6`, `5278` | one more pose each for Enguarde, Rambi, Expresso and Winky, filed after each animal's other frames |

The last four groups (51 frames) were found when the finder stopped counting an animation script as used just because the script's own loop jumps back into it. Their scripts (`Anim_04_473b`, `47d9`, `4883`, `491b`, `4dc3`, `4dcf`, `4def`, `572b`, and the token scripts `4e39`, `4e4f`, `4e65`, `4e7b`) are started by nothing: no code, initialiser list or table points at them or at the `anim_speed` line just before them. Searching the whole ROM for their addresses as raw bytes turns up only coincidences (tile maps, world map markers, a list in bank `$08` that happens to sit at `$4E37`, and code in the separate front-end program). Neither emulator harvest ever showed one of their frames.

The "STOP", "ON" and "OFF" barrel signs (`Frame_20_4dda`, `4de6`, `4dec`) were on this list too, but the Stop/Go and On/Off barrels (`StopGoBarrel`, `OnOffBarrel`) load them with `ld de`, which the finder now follows. Earlier versions of this list had 89 frames. The rest turned out to be used once the tables in banks `$08` and `$0A` were decoded: the letter blocks A–Y that spell words, the credits headings ("KREDITS", "KODING", "KARACTERS", "KOLORING", "KONCEPT", "KOMMANDER"), the cast names ("KLAP TRAP", "KRUSHA", "KRITTER", "KLUMP", "KING K.ROOL") and "THE END?" in all five languages, all of which the ending draws from `CreditsCaptions` (`$0A:53BF`), and one frame in `CarrierObjectTable`.



Since nothing uses these frames, the ROM doesn't say which palette they would be drawn with. The images `find_unused.py` writes to `unused/frames/` stay gray (or use the palette where one is known). A second set in `unused/frames_guessed_palette/` borrows the palette of the nearest frame in the same graphics bank that has a known palette, and the report lists, for every guess, which palette was used and which frame it came from. Those colors are guesses, not facts from the game.

## Animation scripts

13 scripts in bank `$04` are never started (counting a script as started only when code, an initialiser list or a table points at it, or a started script jumps to it). Twelve of them hold the unused frames listed above. The thirteenth, `Anim_04_479f`, shows six Rambi frames that other scripts use, so nothing is hidden in it. An earlier version of this list named `Anim_04_4aab`, `4d21`, `4d5b` and `4d9d`; the touch handlers start those, now that the finder follows code that loads a script's address.

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

Bank `$05` also has two well-formed lists of level markers that no world map record points to (`WorldMapMarkersUnused`). One at `$45D6` has ten points ending at locations `$2D`, `$2E`, `$2F` and `$3C`; the other at `$48CA` has a single point (location `$3B`) and sits right after the end marker of the previous list. Map 0 (DK Isle) uses the eight points just before the first one, so it may once have continued with these.

World map 7 is reached by no location in the location table, but `Func_05_4274` checks for it by number, so code uses it directly. It shows the same island as map 0, with a different list of level markers.

## Title screen

The title picks one of four slots with `[$B0C1] & 3`, but slot 3 is an exact copy of slot 2 (same map, palettes and tileset). So the game shows only three title pictures. One of its four selections simply repeats the jungle picture, which could be filler or a placeholder for a fourth picture that was never made.

## Front-end picture table

`PictureTable` (149 records) ends with four placeholders, records 145–148. They point at a "map" inside the palette block and at tiles past the end of bank `$6F`'s data, so they hold no picture. The table also repeats some records back to back: the English and French main-menu text appear 7 and 8 times. That's more likely one picture reused for several menu states than unused content.

Two of the pictures are still unexplained: picture 97, Funky floating in a rubber ring among the barrels, and picture 131 (repeated as 132), Funky in his boat full of bananas. They look like the losing and winning screens of Funky's Fishing. No code found loads them: no constant picture number, no table entry and no direct reference to their maps, palettes or tiles. Single-player fishing never reached a final screen in testing, and Link-up fishing can't be tested without a second Game Boy. So whether players ever see them is still open.

### Candy Klash and Funky Bomber

These two names belong to the Bonus menu, but the game never shows them there. The evidence, from the code, the data and running the game in an emulator:

| Check | Result |
|---|---|
| The Bonus ring as played | four entries: Funky Fishing, View Items, Hi-Score, Crosshair Cranky |
| The Bonus ring with every unlock bit at `$B0C2`–`$B0C5` set | the same four entries (only the main ring changes, gaining Link-up) |
| Which label pictures the ring reads | record 28 for Crosshair Cranky and View Items. That sheet's other words are "CANDY KLASH", "FUNKY BOMBER", "STICKER BOOK", "ALPHABET", "MAKE BANNER" and "SFX"; the first two never appear on screen. The labels for Funky Fishing and Hi-Score come from a different sheet, record 122, which belongs to the fishing game. |
| The plain-text label lists in bank `$FF` (French, German, Spanish, Italian) | the Bonus ring's slots read "Candy Clash, Funky Bomber, Crosshair Cranky, View Items" in every language |
| Instructions | bank `$FF` has instructions for Funky's Fishing and for every Crosshair Cranky mode, and none for either name |
| Code | no program or code path for either has been found; the bonus programs identified are Funky's Fishing (`$50`–`$52`), the Hi-Score screen (`$55`) and Crosshair Cranky (front end) |

So Candy Klash and Funky Bomber are not reachable in single-player play. They look like the Bonus menu's original first two entries, replaced by Funky Fishing and Hi-Score late enough that the old label graphics and text lists were left in. Funky Bomber may simply be an earlier name for the fishing game: its own instructions describe a "combo attack". One path is still untested: the Link-up menu, which only continues once a second Game Boy is connected.

#### Title sprites and "COMING SOON Q3"

The two games also have large title words drawn as sprites, in the outlined style of the front end, with versions per language. They sit in bank `$F6` (8×16 sprites), and the front end's sprite animation table (`$F0:5A24`, run by `Func_f0_4fa8`) has entries for them:

| Animation | Tiles | Words, by language |
|---|---|---|
| 2 (`SpriteAnim02_FunkyBomberTitle`) | `FunkyBomberTitle` (`$F6:54E0`), `FunkyBomberTitle_French` (`$58A0`) | "FUNKY BOMBER" in English, German, Italian and Spanish, "BOMBES FUNKY" in French |
| 3 (`SpriteAnim03_CandyKlashTitle`) | `CandyKlashTitle` (`$5620`), `_German` (`$59E0`), `_French` (`$5760`), `_Italian` (`$5B20`) | "CANDY KLASH" in English and Spanish, "CANDY'S CLASH" in German, "CLASH CANDY" in French, "SCONTRO DI CANDY" (two lines) in Italian |
| 7 (`SpriteAnim07_ComingSoon`) | `ComingSoonQ3` (`$5D00`, 40 sprites) | "COMING / SOON" over a large "Q3", one version for all languages, laid out at fixed screen positions |

Each language's entry gives the sprite count, the tiles and a layout in bank `$F0` (`SpriteLayout_f0_…`): steps of (dx, dy) from sprite to sprite for the words, and absolute positions for "COMING SOON Q3". Nothing starts these three animations. Every call of `Func_f0_4fa8` with a constant number uses others, and the two that pass a number from a list (`$F1:5C89` for the Hi-Score screen, `$FE:6909` for Crosshair Cranky) don't use 2, 3 or 7. None of these tiles was read in any emulator session either. The animations get their palette from the caller (`[$ff82]`), so their colours are unknown: any coloured picture of them is a guess, and the gray tiles are the real data.

The rest of the table is all in use as far as the data goes, with one small leftover: the 2-sprite layout at `$F0:5C7E` is followed by four more layout steps (`SpriteLayoutUnused_f0_5c82`) that no record uses, as if it once described a 6-sprite picture.

"Q3" reads like a release quarter. Next to the two cut games' titles, the screen looks like a placeholder for Bonus entries that weren't finished yet, perhaps for a preview or demo build. (The "coming soon" graphic was noted before on The Cutting Room Floor.)

### Crosshair Cranky: Baddy Generator and Galleon Gunner

Label sheet 30 (English; sheets 83, 87, 91 and 95 in the other languages) holds eight menu words: BADDY GENERATOR, BARREL 'O KREMLINGS, WANTED, BUDDIES BEWARE, GALLEON GUNNER, ARE YOU SURE?, COPY FROM and COPY TO. The menus draw a word by label id. Text table 0 of each language (`$F0:6F21`) turns that id into a (sheet, row) pair, and the ring table at `$F1:67BF` lists each ring's label ids. Checking every ring and every direct label store gives this:

| Label | Id | Used by |
|---|---|---|
| BADDY GENERATOR | 31 | nothing |
| BARREL 'O KREMLINGS | 32 | ring 15 (Link-up Crosshair Cranky modes) |
| WANTED | 33 | ring 15 |
| BUDDIES BEWARE | 34 | ring 15 |
| GALLEON GUNNER | 35 | nothing |
| ARE YOU SURE? | 36 | the erase confirmation (`$F1:553A`) |
| COPY FROM / COPY TO | 37, 38 | rings 11 and 12 (copying a save file) |
| CANDY KLASH / FUNKY BOMBER | 10, 11 | nothing |

Ring 15 is the Link-up mode list. It reads Kremlings and Kongs, Barrel O'Kremlings, Kremling Krackdown, Buddies Beware, Wanted, the same order as the instruction texts in bank `$FF`. Its first and third words come from a newer sheet, record 122 (rows KREMLING KRACKDOWN and KREMLINGS AND KONGS, after RESTART GAME, HI-SCORE and FUNKY FISHING). So two of sheet 30's five mode words were replaced. BADDY GENERATOR is never shown, and no mode, text or code uses that name. It is most likely the old name of Kremling Krackdown or of Kremlings and Kongs, but nothing in the ROM says which.

Galleon Gunner, on the other hand, is a real mode, but a secret one. In single-player, Crosshair Cranky is played from a map of DK Isle (`CrosshairCranky`, bank `$FE`, entered with the island node number 1–6 in `h`). Running the game in PyBoy and setting the SRAM bytes involved shows how the nodes open:

| Node | Name on the banner | Opens when |
|---|---|---|
| Cranky's hut | Crosshair Cranky | always (the starting point) |
| 1 | Kremlings and Kongs | always |
| 2–5 | Barrel O'Kremlings, Kremling Krackdown, Buddies Beware, Wanted | one by one, as `[$B0C7]` rises (`FE_RaiseCrankyUnlock` raises it after a game) |
| 6 | Galleon Gunner | a galleon appears by Cranky's hut once any save file has bits 0–2 set in its byte for level `$29`. That byte is at file offset `$29` (`$B029`, `$B069` or `$B0A9`), and level `$29` is Gang-Plank Galleon (its map is the ship's deck). The check is at `$05:43F2`. |

Choosing the galleon starts a shooting gallery on the side of a ship, with targets in the hull's portholes. It works and ends with the usual "You Win/You Lose" box. It is the only mode with no instruction screen: `CrankyShowInstructions` skips mode 5, and bank `$FF` has no text for it. The banner name comes from the level-name list in bank `$10` ("Galleon Gunner" is its last entry, after "Return to island map"). Link play doesn't offer it, so its menu label (id 35) is never drawn either. Galleon Gunner is a hidden reward for finishing the adventure, easy to miss and undocumented in the game, but not cut.

One more leftover sits in bank `$FE`. Each mode number is turned into an internal game number through a six-entry table. `CrankyModeToGame` uses `{4,1,3,0,2,5}`. Right before it, `CrankyModeToGame_Unused` (`$FE:40AE`) holds a different order, `{3,4,1,2,0,5}`, and nothing calls it. Read the same way, it describes a menu ordered Kremling Krackdown, Kremlings and Kongs, Barrel O'Kremlings, Wanted, Buddies Beware, Galleon Gunner, probably an earlier layout.

## Text

The English text bank has one line no pointer reaches: "I'm going for a nap." (`UnusedText_10_62f1`). It belongs to Cranky's line "All this game play / is too much for me." In French, Italian and Spanish the matching string has a third line saying the same thing ("Je vais me coucher.", "Farò un pisolino.", "Me voy a echar una siestecita."). In English the second line ends with a 0 instead of a new line, so the string stops early and the nap line becomes a separate string nobody points to. The German text has no nap line at all ("…Ich bin reif fürs Affenhaus!"). All other strings, in all five banks, are reached.

### A missing end marker in the Spanish front-end text

The front end's text records in bank `$FF` each end with a `$87` byte. The Spanish instructions for Crosshair Cranky ("Mirilla Cranky", `FEText_ff_601a`) end with a new-line byte instead, so the text runs straight on into the next record, the Spanish Funky's Fishing instructions, including that record's four header bytes. The other four languages end the same text properly. `FE_DrawText` reads until it meets a `$87`, so in Spanish this screen would print the fishing instructions as well, with the header bytes drawn as stray characters. These general Crosshair Cranky instructions (text table 5, entry 5) are drawn when `FE_Main` runs with `[$c981]` = 3 (`$F1:425A`). No emulator session has reached that screen yet, so how it looks in play is unconfirmed.

## Music

`tools/music.py` follows every channel of every song through its jumps and calls and decodes whatever it reaches. That leaves 393 bytes no song reaches; in the sources they're labelled `MusUnused_BB_XXXX` or commented "never reached":

| What | Where | Size |
|---|---|---|
| An alternate arrangement of a section of song `$18`, the ice levels' music (Snow Barrel Blast, Ice Age Alley). On channel 2 a subroutine (`MusUnused_01_4fa9`) plays section A, a passage nothing else uses (`MusUnused_01_50e2`, 30 notes of a D/A pattern), section A again and section B. The song itself only ever plays A then B. Channel 3 has a matching unused subroutine (`MusUnused_01_5560` and the two after it). | bank `$01`: `$4FA9`–`$515B` and `$5560`–`$55A8` | 169 bytes |
| Short pieces that no jump or call reaches, up to 14 notes each (one only sets registers) | songs `$02`, `$0F`, `$10`, `$12`, `$14`, `$15`, `$16` | 181 bytes |
| An end byte after a channel's final loop jump, never reached because the loop never ends | 43 streams | 43 bytes |

The short phrases are probably leftovers of edits to those songs. The song `$18` passage is the only unused piece of real length. Rendering it as audio would need a player for this driver, which doesn't exist yet.

## Code

`Func_00_36a7` resets the sound hardware (NR52, NR51, NR50, the wave channel) and falls into `Func_00_36b8`, which loads wave pattern 1. Nothing in the ROM calls or jumps to `$36A7`; the game uses `Func_00_36b8` directly. It's a small leftover, probably an older entry point of the sound driver.

The routines at `$F0:4707`–`$47A4` have no callers either. They step a point along a line: they take the absolute values of dx and dy and pick the direction. No call, jump, far call or table in the ROM reaches them.

A few more pieces of code in the main game's banks can't be reached:

| Where | What |
|---|---|
| `Func_09_487a` | an object handler (it checks `[$ffb0]`, then spawns objects from `ObjInit_09_4918`, `$4934` or `ObjInit_09_4927`). No list, table or code points to it |
| `Func_00_2f09` | `rst_farcall Func_0f_4815` and `ret`, right after another `ret`, with no caller |
| `Func_0a_48b8` | a lone `jp NextObject` after an initialiser list, with no caller |
| `$09:4DFC` | the same `jp NextObject`, sharing its first byte (`$C3`) with the end byte of the list before it |
| `$09:71F3` (`.unreached_71f3`) | 13 bytes inside `Func_09_71e4` that the `jr` before them always skips. They repeat the lines above them with different values (they test bit 7 of the player's y speed and set it to `$FD00` instead of `$0300`), so they look like an older version left in place |
| `$00:03F5`, `$00:1DB5` | a `jr` and a `ret` that nothing reaches, at the end of other code |
| `$F2:4A38`, `$F2:4A4D`, `$F2:6F25`, `$FE:4E37`, `$FE:6E52` | a `ret` (or `add a, $18`) right after a `ret`, `jr` or `jp`, in the front-end program |

## Front-end data

Funky's Fishing's sprite animations 10 and 11 each have one more frame's data after their last frame: a 9-sprite layout and its tiles (`FishingLayout_52_54f0` with `FishingTiles_52_5528`, and `FishingLayout_52_58a8` with `FishingTiles_52_58e0`). The animation headers stop one frame short, and no pointer anywhere reaches them (the two byte matches in banks `$50` and `$55` are an instruction and unrelated data). Put together, each looks like the animation's regular 3-sprite figure stacked three times.


`Unused_f1_678a` (32 bytes at `$F1:678A`, between `RingCircle` and a table read by `Func_f1_4926`) wasn't read in any emulator session, and no pointer anywhere in the ROM leads to it. It holds 10 bytes, a two-entry pointer table and the two 9-byte records it points to, so it was probably a small table of the menu code that lost its user.

The two `LanguageWordTiles` pointers per language name two 8-tile words, but `LoadLanguageWordTiles` only copies the first of each pair. The second words (at `$F1:6AC0`, `$6BC0`, `$6CC0`, `$6DC0` and `$6EC0`) may be loaded somewhere not found yet.

## Object data

Bank `$08` holds words spelled in letter blocks (`SpellWord_08_…`, used by `SpellBonus`): DONKEY, KONG, COUNTRY, NINTENDO, RARE, EXPRESSO, ENGUARDE, RAMBI, WINKY, DIDDY, CANDY, FUNKY and CRANKY. Right after KONG comes RAREWARE (`SpellWord_08_4eb2`), which no object spawns. The only object that uses the KONG list (`ObjInit_0e_4019`) stops after its 8 entries (four letters and four blocks), so the eight RAREWARE letters are never reached.

8 of the 92 map patches in bank `$04` have no pointer to them (`MapPatch_04_6dcd`, `6e02`, `6e16`, `6f8e`, `6f9e`, `6fae`, `6fbe`, `6ffd`). The four at `$6F8E`–`$6FBE` are the same 2×2 patch with different positions. Two movement scripts in bank `$0A` (`ObjScript_0a_7495` and `ObjScript_0a_74ac`) have no pointer either. All of these could still be picked by code arithmetic, but no such code has turned up.

Bank `$31` ends with 31 sparkle sprite tiles (8×16, at `$31:5CA0`) after the last frame's tiles, which no frame points to.

## Sprite offset lists

An earlier version of this file listed 2.3 KB of bytes after sprite offset lists as never read. That was wrong. When an object's OAM attributes have bit 4 set, `DrawSpriteFrame` (`Func_00_1037`, path `.jump_11ce`) reads 3 bytes per sprite instead of 2: dx, dy and a value added to that sprite's attributes, which gives each sprite its own palette. The bosses and other large objects are drawn this way. 167 of the 1,414 frames use these 3-byte lists, and the "leftover" bytes were their third bytes. The frame headers don't say which layout a list uses; `tools/gfx.py` (`sprite_layouts`) counts a list as 3-byte when the room before the next list, or the padding at the end of the bank, is exactly 3 bytes per sprite.

What remains after that are 15 short runs that nothing reads (`FrameSpritesTail_…`): one after a list in bank `$31` and fourteen 2-byte runs after lists in bank `$37`.
## Level object blocks

Bank `$03` has 16-byte blocks that no level object list points to (`LevelObjBlockUnused_…`), between the ones that are used.

## Checked and found complete

These turned up nothing unused, which is worth knowing too:

| What | Result |
|---|---|
| Level maps | all 112 map headers are used by level descriptors, and every byte of compressed map data in banks `$E0`–`$EC` belongs to a map |
| Level descriptors | all 128 are reached by at least one of the 237 entrance records |
| Full screens | all 39 screen records in their banks are loaded by the flow script, with no unreferenced records next to them |
| Game states | every state in the `$0300` jump table is selected by the flow script or by code |

## Open questions

Every byte of the ROM is now identified, so this list holds things whose kind is known but whose use isn't yet. The 256 tiles at `$F2:5760` (after the letter piece records) and the four tiles at `$F7:7F60` (after the front-end sprites) have no known loader. They need more emulator runs (Link-up, Print, the credits) before they can be called unused. A few small front-end tables are decoded by size and reader but not by meaning: `Defaults_f1_5d0a` (copied to `$C9E6`, `$C9FE` and `$CA08`), `Pairs_f1_6fe0` (written relative to the RAM address `$C329` kept in ROM at `$00F6`), `Triples_fe_6958` and `ByteTable_fe_6cce`. The 11th Funky's Fishing sample, which fills bank `$56`, wasn't heard in any session, but it's in the sample table, so it isn't unused on that evidence.

A few names in the gameplay banks are still guesses and are marked as tentative where they are defined in `tools/names.py`: `Entrance_BananaHoard` (the doorway at the very start of Jungle Hijinxs, whose destination changes once the save file has cleared levels), `Player_Carry` and `Player_AfterThrow`, and `HUD_PartnerIcon`. Two routines seen running in the emulator have no name yet (`Func_08_5d4a`, which copies a small grid of bytes into WRAM bank 4, and `Func_09_4dff`). Every sprite frame the game uses now has a palette; the 70 frames still drawn gray are all among the unused ones above.
