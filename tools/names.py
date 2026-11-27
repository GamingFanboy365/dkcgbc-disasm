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
    (0x09, 0x740D): "ClamboPearl",               # thrown by Clambo's script (ObjInit_0a_6542)
    (0x0A, 0x51C6): "Cannonball",
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
    (0x09, 0x4EF8): "Player_Carry",  # tentative
    (0x09, 0x4F5F): "Player_AfterThrow",  # tentative
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
    # --- bonus room games (bank 8) and their touch handlers (bank 9)
    (0x08, 0x4439): "SpellBonus_Main",
    (0x08, 0x44F0): "SpellBonus_Item_Circle",
    (0x08, 0x4537): "SpellBonus_Item_WinPause",
    (0x08, 0x4555): "SpellBonus_Item_Gather",  # back to the centre, then removed
    (0x09, 0x4503): "SpellBonus_CheckTouch",
    (0x09, 0x451D): "SpellBonus_Letter_Touch",
    (0x09, 0x455E): "SpellBonus_BlueBanana_Touch",  # reverses the direction of the circle
    (0x09, 0x4571): "SpellBonus_GreenBanana_Touch",  # speeds the circle up
    (0x08, 0x464F): "MatchBonus_Item_Cycle",
    (0x08, 0x46CA): "MatchBonus_Item_Stopped",
    (0x08, 0x471B): "MatchBonus_Item_FlyTogether",
    (0x09, 0x458B): "MatchBonus_Item_Touch",
    (0x08, 0x473A): "ShuffleBonus",  # the prize jumps between four spots; pick the one it stopped on
    (0x08, 0x47FC): "ShuffleBonus_Shuffle",
    (0x08, 0x482C): "ShuffleBonus_WaitForChoice",
    (0x08, 0x4872): "ShuffleBonus_Spot",
    (0x08, 0x48D5): "ShuffleBonus_Spot_Reveal",
    (0x09, 0x4623): "ShuffleBonus_Spot_Touch",
    (0x08, 0x4914): "StompBonus",  # stomp the Klaptraps and collect ten of the banana bunches they drop
    (0x08, 0x49B3): "StompBonus_Main",
    (0x08, 0x49F3): "StompBonus_Klaptrap_Walk",
    (0x08, 0x4A6C): "StompBonus_Klaptrap_Stomped",
    (0x08, 0x4B3C): "StompBonus_Bananas",
    (0x09, 0x4669): "StompBonus_Klaptrap_Touch",
    (0x09, 0x46BB): "StompBonus_Bananas_Touch",
    (0x08, 0x4B6C): "BonusPrize_WaitCollected",
    (0x08, 0x4BA8): "SetObjectPalette",
    (0x08, 0x4BCD): "Bonus_ShowPrize",
    (0x08, 0x4C45): "BonusCoin_FlyToHUD",
    (0x08, 0x4C6C): "BonusCoin_Count",
    (0x09, 0x46DA): "BonusCoin_Touch",
    # --- walls, entrances and exits
    (0x08, 0x556C): "OpenedWall",  # applies its map patch when the level flag in OBJ_VAR_35 is set
    (0x08, 0x55A0): "BreakableWall",  # opened by a thrown barrel; then an Entrance
    (0x09, 0x746E): "BreakableWall_Touch",
    (0x08, 0x55FA): "Entrance",  # doorway to another area (OBJ_VAR_2E-31: entrance to use)
    (0x08, 0x5648): "Entrance_WaitForSound",
    (0x08, 0x5665): "Entrance_BananaHoard",  # start of the first level; leads elsewhere once the save has cleared levels (tentative)
    (0x09, 0x74C6): "Entrance_Touch",
    (0x09, 0x7532): "Entrance_Blast_Touch",  # barrel that shoots the player to another area
    (0x09, 0x4049): "LevelExit_Touch",
    (0x09, 0x406D): "ReturnExit_Touch",  # back to the entrance the player came from
    (0x08, 0x568C): "WinLine",  # the player walking past it wins (victory jingle, leave)
    (0x08, 0x56A2): "LoseLine",
    (0x08, 0x57C0): "SetLevelFlag",
    # --- stickers
    (0x08, 0x56B8): "StickerBananaBunch",  # banana bunch, green while the sticker of this place is not found
    (0x08, 0x56E1): "StickerPad",
    (0x08, 0x56FD): "Sticker_Appear",
    (0x08, 0x5718): "Sticker_FlyToHUD",
    (0x08, 0x573F): "Sticker_Count",
    (0x08, 0x577C): "IsStickerAvailable",
    (0x09, 0x756B): "StickerPad_Touch",
    (0x09, 0x7586): "Sticker_Touch",
    # --- mine carts
    (0x08, 0x59B8): "MineCart",
    (0x08, 0x59D7): "MineCart_Ridden",
    (0x08, 0x5A40): "MineCart_RollAway",
    (0x08, 0x5959): "MineCartKrash_Parked",  # Krash sitting in a standing cart
    (0x08, 0x5AA0): "MineCartKrash_Parked_Main",
    (0x08, 0x598E): "MineCartKrash",  # Krash riding towards the player
    (0x08, 0x5A63): "MineCartKrash_Main",
    (0x08, 0x5ABA): "MineCart_SetSlopeVelocity",
    (0x08, 0x5BA3): "MineCart_SetSlopeAnim",
    (0x08, 0x5BF5): "MineCartKrash_SetSlopeFrame",
    (0x09, 0x7930): "MineCart_Touch",
    (0x09, 0x7905): "MineCartKrash_Parked_Touch",
    (0x09, 0x78F9): "MineCartKrash_Touch",
    # --- Squawks, animal tokens
    (0x08, 0x5C58): "SquawksCrate",
    (0x08, 0x5C71): "SquawksCrate_Open",
    (0x09, 0x7995): "SquawksCrate_Touch",
    (0x08, 0x61F9): "MiniAnimalToken",  # animal bonus levels
    (0x08, 0x61A4): "MiniAnimalToken_Collected",
    (0x09, 0x7B84): "MiniAnimalToken_Touch",
    (0x08, 0x61CB): "BigAnimalToken_Count",
    (0x09, 0x7B4C): "BigAnimalToken_Touch",
    (0x0A, 0x5855): "AnimalToken_FlyToHUD",
    (0x0A, 0x586E): "AnimalToken_Count",  # three of a kind: off to that animal's bonus level
    (0x09, 0x6A05): "AnimalToken_Touch",
    # --- common touch handlers and helpers (bank 9)
    (0x09, 0x4001): "Touch_Hurt",
    (0x09, 0x4007): "Touch_Enemy",
    (0x09, 0x4179): "Enemy_HandleContact",  # carry set: the enemy was defeated
    (0x09, 0x40D8): "SetOrbitPosition",
    (0x09, 0x4095): "GiveExtraLife",
    (0x09, 0x41CD): "DefeatObject",
    (0x09, 0x41FD): "Obj_FallOffScreen",
    (0x09, 0x4243): "Obj_MoveOnTerrain",
    (0x09, 0x424E): "Obj_TurnAround",
    (0x09, 0x5CD1): "CheckPlayerAttack",  # carry set: the player's stomp or roll beats the object; else the player is hurt
    (0x09, 0x5FEB): "BouncePlayer",
    (0x09, 0x61BA): "Player_DropCarried",
    (0x09, 0x590C): "Player_ThrowCarried",
    (0x09, 0x5976): "Player_PickUp",
    (0x09, 0x6638): "Player_WinAndExit",
    (0x09, 0x6687): "Player_LoseAndExit",
    (0x09, 0x66D6): "Player_ExitToEntrance",
    (0x09, 0x66E4): "Player_BeginExit",
    (0x09, 0x6994): "KongLetter_Touch",
    (0x09, 0x6A7E): "Bananas_Touch",
    (0x0A, 0x58C8): "Bananas",
    (0x09, 0x6B2E): "BananaBunch_Touch",
    (0x09, 0x6B6C): "BananaBunch_Count",
    (0x09, 0x6BFC): "Obj_ToScreenCoords",
    (0x09, 0x6C35): "SpawnCollectedBanana",
    (0x09, 0x6BA1): "CollectedBanana_Fly",
    (0x09, 0x6CCC): "Barrel_Touch",  # picked up with B
    (0x09, 0x6D5C): "Barrel_Carried",
    (0x09, 0x6E97): "DKBarrel_Touch",
    (0x09, 0x6F16): "BreakBarrel",
    (0x09, 0x6FE2): "SpawnBarrelDebris",
    (0x09, 0x70F5): "Gnawty_Touch",
    (0x09, 0x7150): "BouncingCoconut_Touch",
    (0x09, 0x71A8): "TireHalf_Touch",
    (0x09, 0x71E4): "Tire_PushDown_Touch",
    (0x09, 0x71F3): "Tire_SmallBounce_Touch",
    (0x09, 0x7216): "Tire_Touch",
    (0x09, 0x7272): "Tire_Top_Touch",
    (0x09, 0x72B2): "Tire_BouncePlayer",
    (0x09, 0x72F4): "BarrelCannon_Touch",
    (0x09, 0x733F): "Army_Touch",
    (0x09, 0x739E): "Squidge_Touch",
    (0x09, 0x73AF): "Chomps_Touch",
    (0x09, 0x73C0): "ChompsJr_Touch",
    (0x09, 0x73E2): "Fish_HandleContact",
    (0x09, 0x75BD): "Klaptrap_Touch",
    (0x09, 0x769D): "Platform_Touch",
    (0x09, 0x76C6): "BlackDrum_Touch",
    (0x09, 0x7808): "Klump_Touch",
    (0x09, 0x7882): "Nut_Touch",
    (0x09, 0x78A3): "Nut",
    (0x09, 0x78AF): "MankyKong_Touch",
    (0x09, 0x78CD): "MankyBarrel_Touch",
    (0x09, 0x79CD): "AnimalCrate_Touch",
    (0x09, 0x7A3E): "AnimalCrate_Open",
    (0x09, 0x7AD5): "SwitchBarrel_Touch",
    (0x09, 0x7B05): "ExtraLifeBalloon_Touch",
    (0x00, 0x3C1B): "SwingingRope_Touch",
    # --- player
    (0x09, 0x4AA8): "Player_EnterLevel_Walk",
    (0x09, 0x5753): "Player_Hurt",
    (0x09, 0x5C02): "Player_OnSwingingRope",
    (0x09, 0x5C49): "HurtKong_RunAway",  # the Kong that was hit leaves; then the other takes over
    # --- bank $0A objects
    (0x0A, 0x4621): "MasterNecky_Nut",
    (0x0A, 0x4774): "QueenB_Wave",
    (0x0A, 0x5F4A): "BouncingCoconut_Bounce",
    (0x0A, 0x5F6D): "BouncingCoconut_Fall",
    (0x0A, 0x5A9A): "StarBarrel",  # one per level; a DK barrel when OBJ_VAR_2E is 0
    (0x0A, 0x5978): "StarBarrel_Sparkle",
    (0x0A, 0x59F0): "BarrelSupply",  # puts a new barrel down a while after the last was used (boss rooms)
    (0x0A, 0x5A43): "BarrelSupply_Wait",
    (0x0A, 0x5FD9): "Rope",
    (0x0A, 0x5FBA): "Rope_Held",
    (0x0A, 0x6088): "Rope_Released",
    (0x0A, 0x61E7): "SwingingRope",
    (0x0A, 0x61F9): "SwingingRope_Held",
    (0x0A, 0x6245): "SwingingRope_Released",
    (0x0A, 0x6EED): "LevelFadeIn",
    (0x0A, 0x6E7E): "LightsTimer",  # Loopy Lights: the lights go out when the count runs down
    (0x0A, 0x6E23): "StopGoTimer",  # Stop & Go Station
    (0x0A, 0x6EDA): "SetBrightness",
    (0x0A, 0x5440): "HUD_Bananas_Hidden",
    (0x0A, 0x5462): "HUD_Bananas_SlideIn",
    (0x0A, 0x547C): "HUD_Bananas_Shown",
    (0x0A, 0x54A0): "HUD_Bananas_SlideOut",
    (0x0A, 0x54BF): "HUD_Lives_Hidden",
    (0x0A, 0x54F0): "HUD_Lives_SlideIn",
    (0x0A, 0x550A): "HUD_Lives_Shown",
    (0x0A, 0x552E): "HUD_Lives_SlideOut",
    (0x0A, 0x5578): "HUD_Items_Hidden",
    (0x0A, 0x5601): "HUD_Items_SlideIn",
    (0x0A, 0x561D): "HUD_Items_Shown",
    (0x0A, 0x5680): "HUD_Items_SlideOut",
    (0x0A, 0x6C18): "MankyKong_Throw",
    (0x0A, 0x729B): "OilDrum",
    (0x0A, 0x729E): "OilDrum_Wait",
    (0x0A, 0x72AF): "OilDrum_Burn",
    (0x08, 0x4344): "SpellBonus",  # letters circle a centre; touch them in order to spell the word (SpellWord_08_... rows)
    (0x08, 0x44BC): "SpellBonus_Item_Spread",  # letters and bananas move out from the centre
    (0x08, 0x4581): "MatchBonus",  # a row of items that each cycle through pictures (MatchPattern_08_...); stop them all on the same one
    (0x08, 0x4617): "MatchBonus_Main",
    (0x09, 0x6EF8): "FuelBarrel_Touch",  # Tanked Up Trouble: adds OBJ_VAR_2E to the fuel count
    (0x0A, 0x6744): "FuelPlatform_Wait",  # Tanked Up Trouble
    (0x0A, 0x6764): "FuelPlatform_Move",
    (0x0A, 0x67D5): "FuelPlatform_Refuel",
    (0x0A, 0x670A): "TrackPlatform_Wait",  # Trick Track Trek: starts when stood on, then follows its script
    (0x0A, 0x6727): "TrackPlatform_Move",
    (0x0A, 0x6689): "Platform_RunScript",
    (0x0A, 0x68F8): "Platform_Register",  # adds the platform to the list the player is checked against
    (0x0A, 0x68B4): "ArrowPlatform_Wait",  # Platform Perils
    (0x09, 0x77DC): "ArrowPlatform_Move",
    (0x0A, 0x68E9): "ArrowPlatform_Fall",
    (0x0A, 0x65E3): "LoopElevator",  # Elevator Antics: wraps around between two heights
    (0x0A, 0x70D3): "Snowflakes_Init",
    (0x0A, 0x70EC): "Snowflakes",
    (0x0A, 0x70AB): "Snowflake_Randomise",
    (0x0A, 0x52A0): "KingKRool_AfterKredits",  # the camera scrolls back and the fight goes on
    (0x0A, 0x71EB): "OilDrum_RunScript",
    (0x0A, 0x40AD): "Obj_MoveToTarget",
    (0x08, 0x4001): "Obj_ReleaseSpawnGroup",
    (0x08, 0x40D4): "Obj_SetIdle",
    (0x08, 0x54F3): "BarrelCannon_SnapAngle",
    (0x08, 0x57E3): "InitKongLetter",  # the collected version if this level's flag for the letter is set
    (0x08, 0x5FE6): "TileAnimator",  # copies the next frame of a tile animation into VRAM
    (0x08, 0x6163): "AnimalBonus_CountTokens",  # counts the tokens down; an extra life for every 100
    (0x08, 0x6205): "BigAnimalToken_SpawnDigits",
    (0x08, 0x6246): "SpawnObjectDigits",
    (0x08, 0x62CA): "MiniAnimalToken_Draw",
    (0x08, 0x6302): "AnimalBonus_DrawCount",
    (0x0A, 0x448F): "VeryGnawty_ApplyHitList",
    (0x0A, 0x482D): "QueenB_PaletteColour",
    (0x0A, 0x4852): "QueenB_SetYellow",
    (0x0A, 0x5201): "KingKRool_AimCamera",
    (0x0A, 0x57DC): "Obj_Move",
    (0x0A, 0x59CE): "Obj_Remove",
    (0x0A, 0x5D66): "Player_ReverseX",
    (0x0A, 0x6063): "Rope_Slide",
    (0x0A, 0x60B7): "SwingingRope_SetFrame",
    (0x0A, 0x6268): "SwingingRope_Advance",
    (0x0A, 0x6365): "Army_StopRolling",
    (0x0A, 0x6ACF): "Obj_FacePlayer",
    (0x0A, 0x6C2E): "MankyKong_RemoveBarrel",
    (0x0A, 0x6F2F): "LevelFadeIn_SetBrightness",
    (0x0A, 0x56A1): "HUD_Items_Draw",
    (0x0A, 0x56F4): "HUD_Items_Reward",  # all KONG letters, a set of animal tokens...: the prize
    (0x0A, 0x5C27): "Kritter_Scripted",
    (0x09, 0x40B6): "LoseLife",
    (0x09, 0x4212): "Obj_FaceMovement",
    (0x09, 0x4227): "Obj_PatrolOnTerrain",
    (0x09, 0x4294): "SineLookup",
    (0x09, 0x49A5): "Player_EnterLevel_Begin",
    (0x09, 0x4ABB): "Player_SetKongOnLand",
    (0x09, 0x4F7C): "Player_SetKongSwimming",
    (0x09, 0x502D): "Player_SetRambi",
    (0x09, 0x51EF): "Player_SetExpresso",
    (0x09, 0x53A8): "Player_SetEnguarde",
    (0x09, 0x5491): "Player_SetWinky",
    (0x09, 0x546A): "PlayerEnguarde_Stab",
    (0x09, 0x5626): "Player_LeaveAnimal",
    (0x09, 0x5765): "Player_HoldBarrel",
    (0x09, 0x5863): "Player_HoldBarrel_InAir",
    (0x09, 0x58B7): "Player_LiftBarrel",
    (0x09, 0x58EC): "Player_ThrowBarrel",
    (0x09, 0x5953): "Player_PutDownBarrel",
    (0x09, 0x599F): "Player_BeginThrow",
    (0x09, 0x5B60): "Player_LetGoOfRope",
    (0x09, 0x5B86): "Player_GrabRope",
    (0x09, 0x5CC0): "Player_UpdateBlink",
    (0x09, 0x6094): "Player_Jump",
    (0x09, 0x616C): "Player_SteerX",
    (0x09, 0x61D9): "Player_SetGravity",  # lower while A is held
    (0x09, 0x61EC): "Player_SwapKongs",
    (0x09, 0x632C): "Obj_MoveForTime",
    (0x09, 0x64D5): "Player_SetMineCartFrame",
    (0x09, 0x6538): "Player_DrawMineCart",
    (0x09, 0x6746): "Player_EnterInBarrel",
    (0x09, 0x676A): "Player_ClampToLevel",
    (0x09, 0x6986): "Player_Move",
    (0x09, 0x6C1D): "AddBanana",  # 100 bananas: an extra life
    (0x09, 0x6D67): "Barrel_PutDown",
    (0x09, 0x6DA5): "Barrel_Thrown",
    (0x09, 0x6E36): "Barrel_Rolling",
    (0x09, 0x703D): "InitBarrelDebris",
    (0x09, 0x7075): "Barrel_BreakAfterDelay",
    (0x09, 0x708A): "Zinger_Touch",
    (0x09, 0x73D1): "Bitesize_Touch",
    (0x0A, 0x5555): "HUD_PartnerIcon",  # drawn while both Kongs are there (bit 1 of $c30f); tentative
}
