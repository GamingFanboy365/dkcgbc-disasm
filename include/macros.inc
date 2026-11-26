IF !DEF(MACROS_INC)
DEF MACROS_INC EQU 1

; rst $00 is a far call whose arguments follow the instruction:
; dw address, db bank.
MACRO rst_farcall
	rst $00
	dw \1
	db BANK(\1)
ENDM

ENDC
