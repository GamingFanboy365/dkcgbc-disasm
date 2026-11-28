; Object slots (generated from OBJ_FIELD_TABLE in tools/hints.py).
;
; Objects are $40-byte slots starting at wObjects. Slot 0 is the player.
; Every frame RunObjects maps OBJ_BANK and jumps to OBJ_HANDLER for each
; active object, with bc = slot offset. Fields are reached with
;     ld hl, wObjects + OBJ_FIELD
;     add hl, bc
; Fields named OBJ_VAR_xx belong to the object type: their meaning
; depends on the handler.

IF !DEF(OBJECTS_INC)
DEF OBJECTS_INC EQU 1

DEF wObjects EQU $c800
DEF wPlayer  EQU wObjects
DEF OBJ_SIZE EQU $40

DEF OBJ_FLAGS         EQU $00 ; bit 2: counted in a spawn group (see OBJ_VAR_2D); bit 5: flicker
DEF OBJ_BANK          EQU $01 ; ROM bank of OBJ_HANDLER
DEF OBJ_HANDLER       EQU $02 ; (word) code run every frame by RunObjects
DEF OBJ_TOUCH_HANDLER EQU $04 ; (word) routine in bank 9 jumped to when the player touches the object
DEF OBJ_GROUND_Y      EQU $06 ; (word) height of the terrain under the object (GetTerrainUnderObject)
DEF OBJ_TERRAIN_A     EQU $08 ; attribute of the tile under the object (GetTerrainUnderObject)
DEF OBJ_TERRAIN_B     EQU $09 ; second attribute of that tile (GetTerrainUnderObject)
DEF OBJ_VAR_0A        EQU $0a
DEF OBJ_VAR_0B        EQU $0b
DEF OBJ_VAR_0C        EQU $0c
DEF OBJ_TARGET_XVEL   EQU $0d ; (word) X velocity that OBJ_XVEL accelerates towards
DEF OBJ_XACCEL        EQU $0f ; (word) per-frame step from OBJ_XVEL towards OBJ_TARGET_XVEL
DEF OBJ_XVEL          EQU $11 ; (word) X velocity, 1/256 pixel per frame
DEF OBJ_XSUB          EQU $13 ; X position, fraction
DEF OBJ_X             EQU $14 ; (word) X position in pixels
DEF OBJ_TARGET_YVEL   EQU $16 ; (word) Y velocity that OBJ_YVEL accelerates towards (max fall speed)
DEF OBJ_YACCEL        EQU $18 ; (word) per-frame step from OBJ_YVEL towards OBJ_TARGET_YVEL (gravity)
DEF OBJ_YVEL          EQU $1a ; (word) Y velocity, 1/256 pixel per frame
DEF OBJ_YSUB          EQU $1c ; Y position, fraction
DEF OBJ_Y             EQU $1d ; (word) Y position in pixels
DEF OBJ_OAM_ATTR      EQU $1f ; OAM attributes for every sprite of the object (palette, flip)
DEF OBJ_FRAME         EQU $20 ; (word) current sprite frame pointer, set by the animation
DEF OBJ_ANIM          EQU $22 ; (word) animation script pointer (bank $04), run by AnimateObject
DEF OBJ_ANIM_SPEED    EQU $24 ; frames per animation step
DEF OBJ_ANIM_TIMER    EQU $25 ; frames left in the current animation step
DEF OBJ_ANIM_FLAGS    EQU $26 ; bit 7 is cleared by an animation command (tentative)
DEF OBJ_SPAWN_INDEX   EQU $27 ; index into the level object tables at $a8xx-$afxx; 0 = none
DEF OBJ_ANIM_PARAM    EQU $28 ; set by an animation command, read by handlers (tentative)
DEF OBJ_COLLISION     EQU $29 ; collision/interaction flags, cleared on delete (tentative)
DEF OBJ_PALETTE       EQU $2a ; object palette slot, allocated by InitObject
DEF OBJ_LAYER         EQU $2b ; sprite layer used when drawing (DrawObject)
DEF OBJ_VAR_2C        EQU $2c
DEF OBJ_VAR_2D        EQU $2d
DEF OBJ_VAR_2E        EQU $2e
DEF OBJ_VAR_2F        EQU $2f
DEF OBJ_VAR_30        EQU $30
DEF OBJ_VAR_31        EQU $31
DEF OBJ_VAR_32        EQU $32
DEF OBJ_VAR_33        EQU $33
DEF OBJ_VAR_34        EQU $34
DEF OBJ_VAR_35        EQU $35
DEF OBJ_VAR_36        EQU $36
DEF OBJ_VAR_37        EQU $37
DEF OBJ_VAR_38        EQU $38
DEF OBJ_VAR_39        EQU $39
DEF OBJ_VAR_3A        EQU $3a
DEF OBJ_VAR_3B        EQU $3b
DEF OBJ_VAR_3C        EQU $3c
DEF OBJ_VAR_3D        EQU $3d
DEF OBJ_VAR_3E        EQU $3e
DEF OBJ_VAR_3F        EQU $3f

; Front-end routines copied to RAM (FE_RAM_NAMES in tools/hints.py)
DEF FE_FarCopy        EQU $c886
DEF FE_FarReadWord    EQU $c8a3
DEF FE_FarReadByte    EQU $c8b9
DEF FE_HDMA           EQU $c8cd
DEF FE_FarCopySprites EQU $c8e7
DEF FE_UpdateSound    EQU $c930
DEF FE_PlaySong       EQU $c94b
DEF FE_OAMDMA         EQU $ff87

; Funky's Fishing's runtime in RAM (FISHING_RAM_NAMES in tools/hints.py)
DEF Fishing_SerialHandler      EQU $cb00
DEF Fishing_FarJump            EQU $cb99
DEF Fishing_FarReturn          EQU $cba7
DEF Fishing_FarReturnKeepFlags EQU $cbb2
DEF Fishing_CopyBytes          EQU $cbcb
DEF Fishing_CopyBytesShort     EQU $cbd4
DEF Fishing_FillBytes          EQU $cbdb
DEF Fishing_FillBytesShort     EQU $cbe3
DEF Fishing_LinkStoreReceived  EQU $cbe9
DEF Fishing_LinkSendNext       EQU $cbff
DEF Fishing_RestartMainLoop    EQU $cc21
DEF Fishing_ReadWordTable51    EQU $cc32
DEF Fishing_PlaySample         EQU $cc4e
DEF Fishing_PlaySong           EQU $cc91
DEF Fishing_VBlank             EQU $cca5
DEF Fishing_STATScroll         EQU $ccc0
DEF Fishing_SampleTimer        EQU $cce2

ENDC
