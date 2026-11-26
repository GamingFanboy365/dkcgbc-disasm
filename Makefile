# Donkey Kong Country (GBC) disassembly
#
#   make          build dkc.gbc and compare it with the original ROM
#   make check    re-assemble with tools/check_asm.py (no RGBDS needed)
#   make generate regenerate src/ from baserom.gbc with tools/emit.py
#   make extract  write missing frame PNGs (gfx/frames/) from baserom.gbc

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

# Sprite frames: gfx/frames/BB/AAAA.png holds the tiles at BB:AAAA as 8x16
# sprites side by side (see tools/gfx.py). Missing PNGs are extracted from
# the base ROM; existing ones are never overwritten.
%.2bpp: %.png
	$(RGBGFX) -c dmg -Z -o $@ $<

gfx/frames/%.png: | gfx/frames/.extracted ;

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
