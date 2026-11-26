# Donkey Kong Country (GBC) disassembly
#
#   make          build dkc.gbc and compare it with the original ROM
#   make check    re-assemble with tools/check_asm.py (no RGBDS needed)
#   make generate regenerate src/ from baserom.gbc with tools/emit.py

ROM     := dkc.gbc
BASEROM := baserom.gbc

RGBDS   ?=
RGBASM  ?= $(RGBDS)rgbasm
RGBLINK ?= $(RGBDS)rgblink
RGBFIX  ?= $(RGBDS)rgbfix
PYTHON  ?= python3

include layout.mk

INCS := $(wildcard include/*.inc)

.PHONY: all compare check generate clean

all: compare

compare: $(ROM)
	sha1sum -c rom.sha1

$(ROM): $(OBJS)
	$(RGBLINK) -n $(ROM:.gbc=.sym) -m $(ROM:.gbc=.map) -o $@ $(OBJS)
	$(RGBFIX) -v $@

%.o: %.asm $(INCS) $(BASEROM)
	$(RGBASM) -o $@ $<

$(BASEROM):
	$(error $(BASEROM) is missing: copy your own dump of the game here (see README.md))

check: $(BASEROM)
	$(PYTHON) tools/check_asm.py $(BASEROM)

generate: $(BASEROM)
	$(PYTHON) tools/emit.py $(BASEROM)

clean:
	rm -f $(ROM) $(ROM:.gbc=.sym) $(ROM:.gbc=.map) $(OBJS)
