IF !DEF(MACROS_INC)
DEF MACROS_INC EQU 1

; rst $00 is a far call whose arguments follow the instruction:
; dw address, db bank.
MACRO rst_farcall
	rst $00
	dw \1
	db BANK(\1)
ENDM

; Object initialiser lists, applied to the object in bc by ApplyObjInit.
; Field names are in include/objects.inc.

; obj_byte field, value
MACRO obj_byte
	ASSERT (\1) < $40
	db \1, \2
ENDM

; obj_word field, value
MACRO obj_word
	ASSERT (\1) < $40
	db $40 | (\1)
	dw \2
ENDM

; obj_include list: apply another list, then continue with this one
MACRO obj_include
	db $80
	dw \1
ENDM

; obj_end [byte]: any byte >= $81 ends the list (the game uses $81)
MACRO obj_end
	IF _NARG == 1
		db \1
	ELSE
		db $81
	ENDC
ENDM


; Animation scripts (bank $04), run by AnimateObject once every OBJ_ANIM_SPEED
; frames. Each entry is a word: with bit 15 clear it is a frame to show (it
; goes into OBJ_FRAME and ends the step); otherwise the low byte is an
; argument and bits 8-14 select a command, which runs immediately.

; anim_frame header: show a frame (a header in bank $20) for one step
MACRO anim_frame
	dw \1
ENDM

; anim_jump script: continue at another script (usually a loop)
MACRO anim_jump
	db $00, $80
	dw \1
ENDM

; anim_speed n: set OBJ_ANIM_SPEED (frames per step) for following frames
MACRO anim_speed
	db \1, $81
ENDM

; anim_call routine: call a routine (with bank $04 mapped, bc = object)
MACRO anim_call
	db $00, $82
	dw \1
ENDM

; anim_clear_flag: clear bit 7 of OBJ_ANIM_FLAGS (handlers poll it)
MACRO anim_clear_flag
	db $00, $83
ENDM

; anim_param n: set OBJ_ANIM_PARAM
MACRO anim_param
	db \1, $84
ENDM

; anim_var38 value: set the word OBJ_ANIM_WORD (OBJ_VAR_38 in older notes)
MACRO anim_var38
	db $00, $85
	dw \1
ENDM

; anim_xor_attr mask: toggle OBJ_OAM_ATTR bits (e.g. OAM_XFLIP = $20)
MACRO anim_xor_attr
	db \1, $86
ENDM

; anim_sfx channel, id: play sound effect id on channel 1-4
MACRO anim_sfx
	ASSERT 1 <= (\1) && (\1) <= 4
	db \2, $86 + (\1)
ENDM

; Frame headers (bank $20), drawn by DrawSpriteFrame.
; frame tiles, offsets, count: count 8x8 tiles at tiles are copied to VRAM by
; HDMA, and each pair of tiles becomes one 8x16 sprite. offsets holds a
; signed (dx, dy) byte pair per sprite; each pair moves from the previous
; sprite's position (the first from the object's position), and the pairs
; are mirrored when the object is flipped. Both must be in the same bank.
MACRO frame
	ASSERT BANK(\1) == BANK(\2)
	dw \1, \2
	db \3, BANK(\1)
ENDM

; frame_none: the empty frame (header 0)
MACRO frame_none
	dw 0, 0
	db 0, 0
ENDM


; rgb r, g, b[, r, g, b...]: CGB colors, 0-31 per channel
MACRO rgb
	REPT _NARG / 3
		dw (\1) | (\2) << 5 | (\3) << 10
		SHIFT 3
	ENDR
ENDM

; obj_pal_preload id, ...: object palettes loaded into hardware slots 0, 1, ...
; in order (PreloadObjPalettes), with a count byte first
MACRO obj_pal_preload
	db _NARG
	db \#
ENDM


; Flow script (bank $0d), run by RunFlowScript: each byte is a game state
; (an offset into the jump table at $0300), some followed by arguments.
; Only the states below are named so far; others are written as numbers.
DEF FLOW_LOAD_LEVEL          EQU $01
DEF FLOW_WORLD_MAP_INIT      EQU $0d
DEF FLOW_PLAY_SONG           EQU $19
DEF FLOW_FADE                EQU $1c
DEF FLOW_LOAD_SCREEN         EQU $1f
DEF FLOW_PICK_ENDING_MESSAGE EQU $31
DEF FLOW_WORLD_MAP           EQU $49
DEF FLOW_WAIT                EQU $4c
DEF FLOW_WAIT_MUSIC_END      EQU $4f
DEF FLOW_WAIT_BUTTON         EQU $52
DEF FLOW_SCREEN_MAP          EQU $55
DEF FLOW_SCREEN_PALETTES     EQU $58
DEF FLOW_SCREEN_TILES_0      EQU $5b
DEF FLOW_SCREEN_TILES_1      EQU $5e
DEF FLOW_RUN_SECOND_PROGRAM  EQU $61

; flow_jump script: continue at another script
MACRO flow_jump
	db $00
	dw \1
ENDM

; flow_load_screen record: pick a full screen (record of palettes, tile map,
; tiles); FLOW_SCREEN_PALETTES/_MAP/_TILES_0/_TILES_1 then load its parts
MACRO flow_load_screen
	db FLOW_LOAD_SCREEN
	dw \1
	db BANK(\1)
ENDM

; flow_wait frames
MACRO flow_wait
	db FLOW_WAIT
	dw \1
ENDM

; flow_play_song id
MACRO flow_play_song
	db FLOW_PLAY_SONG, \1
ENDM

; flow_fade flags: bit 0 picks the direction (in/out); bit 3 = OBJ palettes too
MACRO flow_fade
	db FLOW_FADE, \1
ENDM


; picture map, palettes, tiles: a record of the front end's picture table
; (PictureTable, bank $f0); each argument becomes (bank, address)
MACRO picture
	db BANK(\1)
	dw \1
	db BANK(\2)
	dw \2
	db BANK(\3)
	dw \3
ENDM

ENDC
