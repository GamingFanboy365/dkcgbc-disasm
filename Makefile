# Donkey Kong Country (GBC) disassembly
#
#   make          build dkc.gbc and compare it with the original ROM
#   make check    re-assemble with tools/check_asm.py (no RGBDS needed)
#   make generate regenerate src/ from baserom.gbc with tools/emit.py
#   make extract  write missing PNGs (gfx/) and level data (data/) from baserom.gbc

ROM     := dkc.gbc
BASEROM := baserom.gbc

RGBDS   ?=
RGBASM  ?= $(RGBDS)rgbasm
RGBLINK ?= $(RGBDS)rgblink
RGBFIX  ?= $(RGBDS)rgbfix
RGBGFX  ?= $(RGBDS)rgbgfx
PYTHON  ?= python3

.DEFAULT_GOAL := all
include layout.mk

INCS := $(wildcard include/*.inc)

.PHONY: all compare check generate extract clean

# Never delete intermediate files (extracted or hand-edited PNGs in particular).
.SECONDARY:

all: compare

compare: $(ROM)
	sha1sum -c rom.sha1

$(ROM): $(OBJS)
	$(RGBLINK) -n $(ROM:.gbc=.sym) -m $(ROM:.gbc=.map) -o $@ $(OBJS)
	$(RGBFIX) -v $@

%.o: %.asm $(INCS) $(BASEROM)
	$(RGBASM) -o $@ $<

# Graphics: gfx/frames/BB/AAAA.png holds a sprite frame's tiles as 8x16
# sprites side by side; gfx/bgtiles/BB/AAAA.png holds BG tiles 16 to a row
# (see tools/gfx.py). Missing PNGs are extracted from the base ROM (the
# stamp file covers both); existing ones are never overwritten.
gfx/frames/%.2bpp: gfx/frames/%.png
	$(RGBGFX) -c dmg -Z -o $@ $<

# BG tiles (level tilesets, full screens): plain 8x8 tiles, row by row
gfx/bgtiles/%.2bpp: gfx/bgtiles/%.png
	$(RGBGFX) -c dmg -o $@ $<

# Level map layers: data/maps/*.bin hold them decompressed; the build packs
# them with the game's own compression (tools/lzcomp.py).
data/maps/%.lz: data/maps/%.bin
	$(PYTHON) tools/lzcomp.py $< $@

# Level block and terrain banks: data/blocks/*.bin and data/terrain/*.bin hold
# them in natural order (one block or terrain type after another); the build
# converts them to the ROM's interleaved layout (tools/leveldata.py).
data/blocks/%.planar: data/blocks/%.bin
	$(PYTHON) tools/leveldata.py blocks $< $@

data/terrain/%.planar: data/terrain/%.bin
	$(PYTHON) tools/leveldata.py terrain $< $@

data/maps/%.bin: | gfx/frames/.extracted ;
data/blocks/%.bin: | gfx/frames/.extracted ;
data/terrain/%.bin: | gfx/frames/.extracted ;
gfx/frames/%.png: | gfx/frames/.extracted ;
gfx/bgtiles/%.png: | gfx/frames/.extracted ;

gfx/frames/.extracted: | $(BASEROM)
	$(PYTHON) tools/gfx.py extract $(BASEROM)
	@touch $@

extract: $(BASEROM)
	$(PYTHON) tools/gfx.py extract $(BASEROM)
	@touch gfx/frames/.extracted

$(BASEROM):
	$(error $(BASEROM) is missing: copy your own dump of the game here (see README.md))

check: $(BASEROM) | gfx/frames/.extracted
	$(PYTHON) tools/check_asm.py $(BASEROM)

generate: $(BASEROM)
	$(PYTHON) tools/emit.py $(BASEROM)

clean:
	rm -f $(ROM) $(ROM:.gbc=.sym) $(ROM:.gbc=.map) $(OBJS) $(GFX)
