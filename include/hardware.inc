; Game Boy / Game Boy Color hardware definitions used by this disassembly.
; (Register names follow the community hardware.inc conventions.)

IF !DEF(HARDWARE_INC)
DEF HARDWARE_INC EQU 1

; I/O registers
DEF rP1      EQU $ff00
DEF rSB      EQU $ff01
DEF rSC      EQU $ff02
DEF rDIV     EQU $ff04
DEF rTIMA    EQU $ff05
DEF rTMA     EQU $ff06
DEF rTAC     EQU $ff07
DEF rIF      EQU $ff0f
DEF rNR10    EQU $ff10
DEF rNR11    EQU $ff11
DEF rNR12    EQU $ff12
DEF rNR13    EQU $ff13
DEF rNR14    EQU $ff14
DEF rNR21    EQU $ff16
DEF rNR22    EQU $ff17
DEF rNR23    EQU $ff18
DEF rNR24    EQU $ff19
DEF rNR30    EQU $ff1a
DEF rNR31    EQU $ff1b
DEF rNR32    EQU $ff1c
DEF rNR33    EQU $ff1d
DEF rNR34    EQU $ff1e
DEF rNR41    EQU $ff20
DEF rNR42    EQU $ff21
DEF rNR43    EQU $ff22
DEF rNR44    EQU $ff23
DEF rNR50    EQU $ff24
DEF rNR51    EQU $ff25
DEF rNR52    EQU $ff26
DEF rLCDC    EQU $ff40
DEF rSTAT    EQU $ff41
DEF rSCY     EQU $ff42
DEF rSCX     EQU $ff43
DEF rLY      EQU $ff44
DEF rLYC     EQU $ff45
DEF rDMA     EQU $ff46
DEF rBGP     EQU $ff47
DEF rOBP0    EQU $ff48
DEF rOBP1    EQU $ff49
DEF rWY      EQU $ff4a
DEF rWX      EQU $ff4b
DEF rKEY1    EQU $ff4d
DEF rVBK     EQU $ff4f
DEF rHDMA1   EQU $ff51
DEF rHDMA2   EQU $ff52
DEF rHDMA3   EQU $ff53
DEF rHDMA4   EQU $ff54
DEF rHDMA5   EQU $ff55
DEF rRP      EQU $ff56
DEF rBCPS    EQU $ff68
DEF rBCPD    EQU $ff69
DEF rOCPS    EQU $ff6a
DEF rOCPD    EQU $ff6b
DEF rSVBK    EQU $ff70
DEF rIE      EQU $ffff

; Memory map
DEF _VRAM    EQU $8000
DEF _SCRN0   EQU $9800
DEF _SCRN1   EQU $9c00
DEF _SRAM    EQU $a000
DEF _RAM     EQU $c000
DEF _RAMBANK EQU $d000
DEF _OAMRAM  EQU $fe00
DEF _AUD3WAVERAM EQU $ff30
DEF _HRAM    EQU $ff80

; MBC5 registers
DEF rRAMG    EQU $0000 ; SRAM enable ($0a = on)
DEF rROMB0   EQU $2000 ; ROM bank, low 8 bits
DEF rROMB1   EQU $3000 ; ROM bank, bit 8
DEF rRAMB    EQU $4000 ; SRAM bank

; Cartridge header values
DEF CART_COMPATIBLE_GBC_ONLY EQU $c0
DEF CART_ROM_MBC5_RAM_BAT    EQU $1b
DEF CART_ROM_4096KB          EQU $07
DEF CART_SRAM_8KB            EQU $02
DEF CART_DEST_NON_JAPANESE   EQU $01

ENDC
