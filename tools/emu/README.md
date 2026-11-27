# Emulator checks

Nothing here is part of the build. These scripts run the built ROM in
[mGBA](https://mgba.io/) (headless, scripted in Lua) to check things the code
alone leaves open, and write what they saw into two text files that the other
tools read:

| File | What it holds | Read by |
|---|---|---|
| `observed_palettes.txt` | for each sprite frame, the object palette it was drawn with in the running game | `tools/frame_palettes.py` (previews, `docs/unused.md`) |
| `observed_handlers.txt` | each routine seen as an object's handler: which objects ran it, which handler came before and after | naming work in `tools/names.py` |

Both files are committed, so the rest of the repository works without an
emulator. Run the harvest again only to extend it.

## How the harvest works

`harvest.lua` boots the game to the world map once, saves the state, and then
for each job

1. rewrites one scratch entrance record in bank `$04` (descriptor, position)
   and points every `LevelTable` entry at it,
2. loads the saved state and presses A, so the game enters that area at that
   position,
3. logs all 32 object slots on every frame: handler, touch handler, OAM
   attribute, `OBJ_PALETTE`, frame, animation, spawn index and the object's
   initialiser list, together with the object palette RAM.

`mkjobs.py` writes the job list: every level start plus one point per
256×192 pixel cell that holds objects (1,823 points). A job line may end in
pairs of *touch handler, initialiser list*: the list (bank `$09`) is applied
to the live object with that touch handler, 150 frames in, and the next pair
70 frames later. That is how states no idle run reaches are shown: a boss
being hit and defeated, a sticker pad giving up its sticker.

Inputs are scripted with `MODE` (`idle`, `right`, `left`, `roll`, `slap`,
`up`, `swim`); `KONG=diddy` plays as Diddy Kong.

`analyze.py` turns the logs into the two text files. A frame's palette is the
object's `OBJ_PALETTE` when the colours of its hardware slot match that
palette; otherwise the slot's colours are looked up in the palette table in
bank `$80` and used only when exactly one palette has them.

## Running it

```sh
python3 tools/emu/mkjobs.py > jobs.txt
JOBS=jobs.txt PART=0 PARTS=1 OUT=logs/idle.log RUN=400 MODE=idle \
    mgba-headless --script tools/emu/harvest.lua dkc.gbc
python3 tools/emu/analyze.py logs
```

`PART`/`PARTS` split the job list so several emulators can run side by side.
mGBA has to be built with scripting and the headless front end
(`-DBUILD_HEADLESS=ON -DENABLE_SCRIPTING=ON`).

## What it cannot tell

Only what was on screen is recorded. Frames that never appear in these runs
keep the palette worked out from the code, or none; the previews mark which
is which (`observed`, `object`, `inferred`).
