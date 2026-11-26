IF !DEF(MACROS_INC)
DEF MACROS_INC EQU 1

; rst $00 is a far call whose arguments follow the instruction:
; dw address, db bank.
MACRO rst_farcall
	rst $00
	dw \1
	db BANK(\1)
ENDM

; Object initialiser lists, applied to the object in bc by Func_00_188b.
; Objects live at $c800 + bc; the object loop at Func_00_3980 switches to
; OBJ_BANK and jumps to OBJ_HANDLER for every active object.
DEF OBJ_FLAGS   EQU $00
DEF OBJ_BANK    EQU $01
DEF OBJ_HANDLER EQU $02 ; word

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

ENDC
