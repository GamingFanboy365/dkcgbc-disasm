"""Routine names (step 3 of the plan). (bank, address) -> name.

Added bank by bank after reading each routine; hints.NAMES (older names)
and the names tools/autonames.py derives from ROM tables are merged with
these by tools/emit.py (hints.NAMES wins, then this file).
"""

NAMES = {
    # bank $00
    (0x00, 0x004B): "EmptyInterrupt",
    (0x00, 0x00A1): "SetDoubleSpeed",
    (0x00, 0x00BC): "SetNormalSpeed",
    (0x00, 0x00F0): "Vector_UpdateSound",
    (0x00, 0x00F3): "Vector_PlaySong",
    (0x00, 0x00F8): "Vector_00f8",
    (0x00, 0x025D): "InstallInterruptTrampolines",
    (0x00, 0x027C): "DoOAMDMA",
    (0x00, 0x0286): "SimpleVBlankHandler",
    (0x00, 0x0364): "Random",
    (0x00, 0x0391): "FarHDMACopy",
    (0x00, 0x03A1): "HDMACopy",
    (0x00, 0x03BE): "GetBitMask",
    (0x00, 0x03E4): "Decompress",
    (0x00, 0x0616): "LCDSplitHandler",
    (0x00, 0x0682): "RandomBelow",
    (0x00, 0x06A3): "LoadTextString",
    (0x00, 0x0718): "WriteScrollEdges",
    (0x00, 0x0780): "UpdateMapScroll",
    (0x00, 0x07C1): "LoadMapColumn",
    (0x00, 0x0891): "LoadMapRow",
    (0x00, 0x097E): "LoadMapColumn_Vertical",
    (0x00, 0x0A69): "LoadMapRow_Vertical",
    (0x00, 0x0B4F): "LoadMap",
    (0x00, 0x0BE4): "DrawMapScreen",
    (0x00, 0x0C24): "DrawMapArea",
    (0x00, 0x0CE4): "DrawMapArea_Vertical",
    (0x00, 0x0D9D): "SetMapCell",
    (0x00, 0x0E91): "LoadCommonSpriteTiles",
    (0x00, 0x0EE2): "ResetOAMBuffers",
    (0x00, 0x0EEE): "ClearOAM",
    (0x00, 0x0F02): "BuildOAM",
    (0x00, 0x0F21): "AnimateSpriteTiles",
    (0x00, 0x0F52): "CopyOAMBuffersForward",
    (0x00, 0x0FBB): "CopyOAMBuffersBackward",
    (0x00, 0x1037): "DrawSpriteFrame",
    (0x00, 0x127D): "AnimateObject",
    (0x00, 0x1341): "DrawObject",
    (0x00, 0x1598): "CheckObjectOnScreen",
    (0x00, 0x162C): "GetObjectScreenPos",
    (0x00, 0x1635): "GetObjectScreenPos_Camera",
    (0x00, 0x1664): "GetObjectScreenPos_Fixed",
    (0x00, 0x1715): "LoadLevelObjects",
    (0x00, 0x1761): "GetLevelObjStringSlot",
    (0x00, 0x1779): "SpawnLevelObjects",
    (0x00, 0x18E4): "MarkObjectSpawnDone",
    (0x00, 0x18F0): "DeleteObjectForGood",
    (0x00, 0x18F5): "DeleteObject",
    (0x00, 0x1933): "UpdateSpawnWindow",
    (0x00, 0x19E7): "SpawnObjectsOnScroll",
    (0x00, 0x1C9D): "AddSignedWordTo24",
    (0x00, 0x1CB1): "WorldMapFrameTasks",
    (0x00, 0x1CC2): "WorldMapVBlankHandler",
    (0x00, 0x1CEC): "WorldMapLCDHandler",
    (0x00, 0x1E3B): "DrawWorldMapColumn",
    (0x00, 0x1E83): "GetWorldMapColumnToDraw",
    (0x00, 0x1EA4): "InitWorldMapGraphics",
    (0x00, 0x1EBC): "AnimateWorldMapTiles",
    (0x00, 0x1F0A): "DrawWorldMapScreen",
    (0x00, 0x1F8A): "CopyWorldTileMap",
    (0x00, 0x1FA7): "GetWorldMapScrollTarget",
    (0x00, 0x1FC9): "UpdateWorldMapScroll",
    (0x00, 0x20BB): "UpdateWorldMapSprites",
    (0x00, 0x20DD): "UpdateCameraRegion",
    (0x00, 0x21AD): "GetCameraRegionEdge",
    (0x00, 0x21BF): "SetCameraRegion",
    (0x00, 0x2214): "GetTerrainUnderObject",
    (0x00, 0x2400): "RasterVBlankHandler",
    (0x00, 0x241D): "RasterLCDHandler",
    (0x00, 0x2766): "InitPlayerObject",
    (0x00, 0x28B5): "UpdateCamera",
    (0x00, 0x29A3): "InitCamera",
    (0x00, 0x29C4): "GetCameraTargetX",
    (0x00, 0x29F5): "GetCameraTargetY",
    (0x00, 0x2AAE): "RequestOBJPaletteUpdate",
    (0x00, 0x2BFB): "CopyScreenTileMap",
    (0x00, 0x2B5F): "GetFlowRecord",
    (0x00, 0x2C0E): "LoadTileset",
    (0x00, 0x2C48): "LoadScreen",
    (0x00, 0x2DF0): "LoadOBJPalettesInHBlank",
    (0x00, 0x2F0E): "InitSound",
    (0x00, 0x2F3D): "IsMusicPlaying",
    (0x00, 0x2F4D): "CheckChannelSFX",
    (0x00, 0x2F5A): "StartSFX",
    (0x00, 0x2F88): "UpdateSFXChannel",
    (0x00, 0x3172): "StartQueuedSFX",
    (0x00, 0x33B4): "GetChannelPanMask",
    (0x00, 0x36A7): "ResetSoundHardware",
    (0x00, 0x36B8): "LoadWavePattern",
    (0x00, 0x38C7): "SetFlowPointer",
    (0x00, 0x38CD): "RunFlowScript",
    (0x00, 0x39AB): "NegateObjectWord",
    (0x00, 0x39B4): "ApplyVelocity",
    (0x00, 0x39BA): "ApplyXVelocity",
    (0x00, 0x39D7): "UndoVelocity",
    (0x00, 0x39DD): "UndoXVelocity",
    (0x00, 0x39E2): "UndoYVelocity",
    (0x00, 0x39FA): "UpdateVelocity",
    (0x00, 0x3AB5): "DespawnIfOutOfRange",
    (0x00, 0x3B39): "GetOffsetFromSpawnX",
    (0x00, 0x3B54): "GetOffsetFromSpawnY",
    (0x00, 0x3B6F): "CheckRangeLimit",
    (0x00, 0x3B85): "TurnAtRangeLimit",
    (0x00, 0x3BA7): "TurnAtRangeLimitX",
    (0x00, 0x3BB6): "GetPlayerDistanceX",
    (0x00, 0x3BCF): "MoveTowardsX",
    (0x00, 0x3BF5): "MoveTowardsY",
    (0x00, 0x3CE1): "LoadBGPaletteSet",
    (0x00, 0x3FD5): "RestoreBankAndReturn",
    # most-called helpers in the object banks
    (0x09, 0x43EA): "CheckPlayerContact",      # object vs player, using Hitboxes; result in [$ffa7]
    (0x08, 0x40E1): "CollideWithTerrain",      # GetTerrainUnderObject, then land on or slide along it
    (0x09, 0x68E7): "SetPlayerAnimation",      # a = animation number (+1 entry for the second Kong, [$c30f] bit 0)
    (0x0A, 0x4063): "SaveObjectPosition",      # x, y and two terrain bytes to [$ffb2]-[$ffb7]
    (0x0A, 0x4086): "MoveObjectToSavedPosition",
    (0x09, 0x5DBB): "HurtPlayer",              # the touch handlers of harmful objects end here
    # objects (banks $08-$0A): start handlers named after the object, identified
    # from their sprites; states by what the code does
    (0x08, 0x4028): "Obj_Idle",
    (0x08, 0x402E): "Obj_Animate",
    (0x08, 0x4034): "Obj_AnimateAndDespawn",
    (0x08, 0x403D): "Obj_MoveAndAnimate",
    (0x08, 0x4046): "Obj_FallThenIdle",
    (0x08, 0x4067): "Obj_FallThenAnimate",
    (0x08, 0x5156): "Obj_Patrol",
    (0x08, 0x5CA6): "Squawks",
    (0x09, 0x5058): "PlayerRambi",
    (0x09, 0x521D): "PlayerExpresso",
    (0x09, 0x53DC): "PlayerEnguarde",
    (0x09, 0x54BF): "PlayerWinky",
    (0x0A, 0x4192): "VeryGnawty",              # also Really Gnawty (ReallyGnawty_Init)
    (0x0A, 0x47CF): "BossDefeated",            # a beaten boss falls; then the giant banana
    (0x0A, 0x4401): "MasterNecky",             # also Master Necky Snr (MasterNeckySnr_Init)
    (0x0A, 0x4674): "QueenB",
    (0x0A, 0x4881): "DumbDrum",
    (0x0A, 0x4B87): "KingKRool",
    (0x0A, 0x57E2): "KongLetter",
    (0x0A, 0x5989): "DKBarrel",
    (0x0A, 0x59A0): "DKBarrel_Wait",
    (0x0A, 0x59D4): "DKBarrel2",
    (0x0A, 0x5B56): "RunKritterScript",
    (0x0A, 0x5C17): "Kritter_Walk",
    (0x0A, 0x5CFE): "Kritter_Jump",
    (0x0A, 0x5D2E): "Kritter_Jump_Loop",
    (0x0A, 0x5D73): "Zinger_Move",
    (0x0A, 0x5D97): "Zinger_Move_Loop",
    (0x0A, 0x5DAF): "Zinger_Move2",
    (0x0A, 0x5DD3): "Zinger_Move2_Loop",
    (0x0A, 0x5E0B): "Zinger_Patrol",
    (0x0A, 0x5E65): "RunNeckyScript",
    (0x0A, 0x5ED0): "Necky_ThrowNuts",
    (0x0A, 0x5EEE): "Necky_Throw",
    (0x0A, 0x656D): "Necky_Fly",
    (0x0A, 0x6579): "Necky_FlyPatrol",
    (0x0A, 0x627A): "Army",
    (0x0A, 0x6397): "Bitesize",
    (0x0A, 0x63B3): "Bitesize_Swim",
    (0x0A, 0x63A5): "Bitesize_Wave",
    (0x0A, 0x63C3): "Bitesize_Wave_Loop",
    (0x0A, 0x63F4): "Chomps",
    (0x0A, 0x6401): "Chomps_Swim",
    (0x0A, 0x6420): "ChompsJr",
    (0x0A, 0x642D): "ChompsJr_Swim",
    (0x0A, 0x64BA): "RunClamboScript",
    (0x0A, 0x6556): "Clambo",
    (0x0A, 0x6AEC): "RunMankyKongScript",
    (0x0A, 0x6B9F): "MankyKong",
    (0x0A, 0x6C60): "RunCroctopusScript",
    (0x0A, 0x6CFC): "Croctopus",
    (0x0A, 0x6F42): "Millstone",
    (0x0A, 0x6F71): "Millstone_Roll",
    (0x0A, 0x6F89): "Millstone_UpdateRider",
    (0x0A, 0x6FC5): "RunMillstoneScript",
    (0x0A, 0x7055): "Millstone_Scripted",
    (0x0A, 0x7061): "Millstone_Wait",
    (0x0A, 0x7090): "Millstone_Move",
    (0x0A, 0x72C1): "ExtraLifeBalloon",
    # bosses: the shared routines are named after the first fight that uses
    # them; each fight's initialiser list (spawned by its level) sets the
    # palette and how many hits are already counted
    (0x0E, 0x470F): "VeryGnawty_Init",
    (0x0E, 0x471B): "ReallyGnawty_Init",
    (0x0E, 0x4727): "QueenB_Init",
    (0x0E, 0x475D): "MasterNecky_Init",
    (0x0E, 0x4769): "MasterNeckySnr_Init",
    (0x0E, 0x4775): "DumbDrum_Init",
    (0x0E, 0x4799): "KingKRool_Init",
    (0x0A, 0x42DD): "VeryGnawty_Hit",
    (0x0A, 0x45B9): "MasterNecky_Defeated",
    (0x0A, 0x5232): "BossDefeated_Banana",
    (0x0A, 0x5285): "GiantBanana",
    (0x09, 0x4712): "StompBoss_Touch",          # beaver and Necky bosses: counts stomps to 5 or 10
    (0x09, 0x47EF): "QueenB_Touch",              # counts barrel hits
    (0x09, 0x487A): "KingKRool_Touch",
    # identified with a set of labelled DKC GBC sprites
    (0x09, 0x400D): "Gnawty_Red",
    (0x09, 0x4026): "Gnawty",
    (0x09, 0x75F9): "Rockkroc",
    (0x0A, 0x5E1D): "Krusha",
    (0x0A, 0x6940): "Klump",
    (0x0A, 0x6963): "Klump2",
    (0x0A, 0x658F): "Klaptrap",
    (0x0A, 0x6477): "Squidge",
    (0x0A, 0x69F5): "MiniNecky",
    (0x0A, 0x6BA8): "Mincer",
    (0x0A, 0x71B1): "BlackDrum",               # spawns enemies (ObjScript, Func_0a_713c)
    (0x08, 0x55FA): "StarBarrel",                # the checkpoint; a per-level bit remembers it
    (0x08, 0x5C2E): "AnimalCrate",
    (0x08, 0x4088): "Coconut",
    (0x0A, 0x65D1): "Elevator",
    # object states
    (0x0A, 0x713C): "RunBlackDrumScript",
    (0x0A, 0x71C3): "BlackDrum_Wait",            # runs the spawn script once enemies are gone and the player is near
    (0x09, 0x401A): "Gnawty_Red_Walk",
    (0x0A, 0x4BCC): "KingKRool_Wait",
    (0x0A, 0x4BF4): "KingKRool_Throw",
    (0x0A, 0x4CC5): "KingKRool_WaitForCrown",
    (0x0A, 0x4CEE): "KingKRool_Animate",
    (0x0A, 0x5198): "Crownerang",                # flies out, then back (Crownerang_Return)
    (0x0A, 0x51B3): "Crownerang_Return",
    (0x0A, 0x50F8): "KingKRool_Defeated",        # falls; plays song $09 when he lands
    (0x0A, 0x65A5): "Klaptrap_Walk",             # jumps when the player presses A
    (0x0A, 0x447E): "MasterNecky_Enter",
    (0x0A, 0x6C3F): "Mincer_Fall",
    (0x09, 0x619D): "PlayerEnguarde_UpDown",
    (0x0A, 0x46AE): "QueenB_Fly",
    (0x0A, 0x47FE): "QueenB_SetSpeed",           # from ObjXVelTable_0a_481d
    (0x0A, 0x46E9): "QueenB_Hit",
    (0x0A, 0x4729): "QueenB_HitRise",
    (0x0A, 0x485C): "QueenB_CycleColour",        # flashes through Cycle_0a_4871
    (0x0A, 0x4849): "QueenB_SetHitColour",
    (0x09, 0x60EC): "BouncePlayerOffBoss",
    (0x0A, 0x42B9): "VeryGnawty_Recoil",
    (0x0A, 0x45E9): "MasterNecky_Recoil",
    (0x08, 0x5168): "BarrelCannon",              # 16 directions (OBJ_VAR_38); OBJ_VAR_3C bit 3: blast barrel frames
    (0x08, 0x5183): "BarrelCannon_Idle",
    (0x08, 0x54FE): "BarrelCannon_SetFrame",     # FrameTable_08_5522
    (0x08, 0x5562): "BarrelCannon_Move",
    (0x0A, 0x6D65): "StopGoBarrel",              # STOP or GO frame and palette by the timer at $c446
    (0x0A, 0x6DCC): "OnOffBarrel",               # ON or OFF frame by the same timer
    (0x08, 0x50DE): "Tire",
    (0x08, 0x44BC): "GreenBanana",
    (0x09, 0x740D): "ClamboPearl",               # thrown by Clambo's script (ObjInit_0a_6542)
    (0x0A, 0x51C6): "Cannonball",
    (0x08, 0x4344): "LetterWord",                # spawns a LetterWord_08_... row of letter blocks
    (0x08, 0x4581): "StepRow",                   # a row of parts stepping through a StepPattern
    (0x09, 0x68A5): "SetPlayerPalette",          # a = palette number (1 DK, 2 Diddy, 3 Rambi, $0d Expresso, $12 Enguarde, $10 Winky)
    # states named with the emulator harvest (tools/emu/observed_handlers.txt gives the order)
    (0x0A, 0x41C8): "VeryGnawty_Hop",  # waits, then jumps (height from ObjYVelTable by hits taken)
    (0x0A, 0x4270): "VeryGnawty_Land",
    (0x0A, 0x4319): "VeryGnawty_AngryHop",  # after a hit: hops towards the player
    (0x0A, 0x438C): "VeryGnawty_AngryLand",
    (0x0A, 0x44A3): "MasterNecky_Spit",  # throws a nut
    (0x0A, 0x4533): "MasterNecky_AfterSpit",
    (0x0A, 0x4582): "MasterNecky_Pause",
    (0x0A, 0x459A): "MasterNecky_Withdraw",  # the head pulls back (after spitting or being hit)
    (0x0A, 0x4742): "QueenB_Charge",  # after a hit: flies at the player
    (0x0A, 0x4894): "DumbDrum_BeginRound",  # drops to make = rounds done + 1
    (0x0A, 0x48BB): "DumbDrum_AimAtPlayer",
    (0x0A, 0x48E7): "DumbDrum_Hover",
    (0x0A, 0x4917): "DumbDrum_Pause",
    (0x0A, 0x492D): "DumbDrum_Drop",
    (0x0A, 0x4957): "DumbDrum_Rise",  # back to AimAtPlayer until the drops are done
    (0x0A, 0x497C): "DumbDrum_BeginSpawn",
    (0x0A, 0x49A1): "DumbDrum_Descend",
    (0x0A, 0x49C3): "DumbDrum_SpawnEnemies",  # from ObjInitTable_0a_4a47
    (0x0A, 0x4B25): "DumbDrum_Leave",
    (0x0A, 0x4B3B): "DumbDrum_WaitForEnemies",  # next round when they are beaten; destroyed after the fifth
    (0x0A, 0x4D00): "KingKRool_BeginRuns",  # after a hit: number of runs by hits taken
    (0x0A, 0x4D66): "KingKRool_RunPause",
    (0x0A, 0x4D88): "KingKRool_Run",  # speeds from WordTable_0a_4e04
    (0x0A, 0x5090): "KingKRool_FakeDefeat",  # starts the fake "KREDITS"
    (0x0A, 0x5141): "KingKRool_FakeKredits",  # waits for them to end, then plays the boss song again
    (0x08, 0x5195): "BarrelCannon_Loaded",  # the player is inside: count down, then pick the next state by type
    (0x08, 0x51C8): "BarrelCannon_TurnToAim",  # towards the direction in OBJ_VAR_32's low nibble
    (0x08, 0x5227): "BarrelCannon_Fire",
    (0x08, 0x5375): "BarrelCannon_AfterFire",
    (0x08, 0x53A1): "BarrelCannon_Cooldown",
    (0x08, 0x53C1): "BarrelCannon_TurnBack",  # to the rest direction (OBJ_VAR_32's high nibble)
    (0x08, 0x5400): "BarrelCannon_AutoRotate",  # OBJ_VAR_3C bit 5: keeps turning with the player inside
    (0x08, 0x5458): "BarrelCannon_SwingForward",  # OBJ_VAR_3C bit 6: swings until A is pressed
    (0x08, 0x5499): "BarrelCannon_SwingBack",
    (0x08, 0x4617): "StepRow_Idle",
    (0x09, 0x760F): "Rockkroc_Run",  # while the Stop/Go timer runs, curls up
    (0x09, 0x763C): "Rockkroc_CurledUp",
    (0x09, 0x7670): "Rockkroc_Uncurl",
    (0x0A, 0x5810): "KongLetter_FlyUp",
    (0x0A, 0x5826): "KongLetter_Collected",
    (0x0A, 0x5A61): "DKBarrel_Open",
    (0x0A, 0x5C38): "Kritter_WalkTimed",  # script command 2
    (0x0A, 0x5C4D): "Kritter_JumpStart",  # script command 3
    (0x0A, 0x5CAB): "Kritter_Jumping",
    (0x0A, 0x62F0): "Army_Idle",
    (0x0A, 0x6346): "Army_Roll",
    (0x0A, 0x6956): "Klump_Walk",
    (0x0A, 0x6A0A): "MiniNecky_Hover",
    (0x0A, 0x6A8B): "MiniNecky_Swoop",
    (0x0A, 0x6A2A): "MiniNecky_Spit",
    (0x0A, 0x6D25): "Croctopus_WaitForPlayer",
    (0x0A, 0x6D16): "Croctopus_Chase",
    (0x0A, 0x6D0D): "Croctopus_Stopped",
    (0x0A, 0x7308): "ExtraLifeBalloon_FlyUp",
    (0x0A, 0x732C): "ExtraLifeBalloon_Count",
    # the player's states (handler of object slot 0), checked with scripted input in mGBA
    (0x09, 0x4956): "Player_EnterLevel",
    (0x09, 0x4AFF): "Player_OnGround",  # stand, walk; A jumps, B rolls, Down crouches
    (0x09, 0x4CFF): "Player_InAir",
    (0x09, 0x4E29): "Player_Roll",  # B; keeps rolling while B and a direction are held
    (0x09, 0x4EF8): "Player_Carry",  # holding a barrel
    (0x09, 0x4F5F): "Player_AfterThrow",
    (0x09, 0x4FAB): "Player_Swim",
    (0x09, 0x56C3): "Player_Launched",  # shot from a barrel cannon; levels also start in this state
    (0x09, 0x5BCC): "Player_InBarrelCannon",  # follows the cannon object in OBJ_VAR_33
    (0x09, 0x59B0): "Player_OnRope",
    (0x09, 0x63E6): "Player_InMineCart",
    (0x09, 0x64A6): "Player_MineCartJump",
    (0x09, 0x564C): "Player_Defeated_Fall",  # waits to land and for the jingle to end
    (0x09, 0x566D): "Player_Defeated_Begin",
    (0x09, 0x5690): "Player_Defeated_Wait",
    (0x09, 0x56A8): "Player_Defeated_Exit",  # the other Kong takes over, or the level ends
    (0x09, 0x6728): "Player_ExitAfterJingle",  # warps to the entrance in [$c44b]
    (0x09, 0x670D): "Player_ExitWait",
    (0x0A, 0x6F10): "Player_ExitFade",
    (0x09, 0x5183): "PlayerRambi_InAir",
    (0x09, 0x5325): "PlayerExpresso_InAir",
    (0x09, 0x536C): "PlayerExpresso_Flap",
    (0x09, 0x55C7): "PlayerWinky_InAir",
    (0x09, 0x4D4D): "Player_Crouch",  # Down
    (0x09, 0x4D94): "Player_HandSlap",  # Down + B
    (0x09, 0x4E0F): "Player_HandSlapEnd",
}
