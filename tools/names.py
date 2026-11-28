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
    # --- front-end library, bank $F0
    (0xF0, 0x4000): "FE_InstallRAMRoutines",  # copies FE_HDMA_Code to $c8cd and FE_OAMDMA_Code to $ff87
    (0xF0, 0x4016): "FE_OAMDMA_Code",  # runs at $ff87 (FE_OAMDMA)
    (0xF0, 0x4020): "FE_HDMA_Code",  # runs at $c8cd (FE_HDMA): bank a, source hl, destination bc, d+1 blocks of 16 bytes
    (0xF0, 0x403A): "FE_StartHBlankDMA",
    (0xF0, 0x404C): "FE_HDMAAcrossBanks",  # like FE_HDMA, split in two where the source runs past $7FFF into the next bank
    (0xF0, 0x40D0): "FE_AdvanceFarPointer",  # hl += bc; past $7FFF wraps to $4000 of the next bank ([$c800])
    (0xF0, 0x40E0): "FE_InstallFarCopy",  # copies FE_FarCopy_Code and the two read routines to $c886
    (0xF0, 0x40EB): "FE_FarCopy_Code",  # runs at $c886 (FE_FarCopy)
    (0xF0, 0x4108): "FE_FarReadWord_Code",  # runs at $c8a3
    (0xF0, 0x411E): "FE_FarReadByte_Code",  # runs at $c8b9
    (0xF0, 0x4132): "FE_CopyBytesShort",  # d bytes hl -> bc
    (0xF0, 0x4139): "FE_CopyBytes",  # de bytes hl -> bc
    (0xF0, 0x4145): "FE_SetDoubleSpeed",
    (0xF0, 0x4159): "FE_SaveHRAM",  # $ff80-$fffe -> WRAM bank 6 $df00
    (0xF0, 0x416D): "FE_SaveState",  # $c800-$cf7f -> $d700 and HRAM -> $de80, WRAM bank 6
    (0xF0, 0x418D): "FE_RestoreHRAM",
    (0xF0, 0x41A1): "FE_FillWithBB",  # fills de bytes at bc with $bb (debug)
    (0xF0, 0x41AF): "FE_FillWithBBShort",
    (0xF0, 0x41B8): "FE_RestoreState",
    (0xF0, 0x41DE): "FE_ClearPalettes",
    (0xF0, 0x4201): "FE_FadeToTargetPalettes",  # steps the palettes in $c806 towards $da00 until they match
    (0xF0, 0x4223): "FE_FadeIn",  # from black, brightness rising in steps of 8
    (0xF0, 0x4256): "FE_FadeOut",
    (0xF0, 0x4283): "FE_UnpackPalettes",  # RGB555 words -> one byte per channel
    (0xF0, 0x42AD): "FE_ReadPalettesFromHW",  # BG and OBJ palette RAM -> $c806/$c846
    (0xF0, 0x42E9): "FE_PackColor",
    (0xF0, 0x4306): "FE_StepChannelTowards",
    (0xF0, 0x4326): "FE_FadePaletteStep",
    (0xF0, 0x4394): "FE_ScalePalettes",  # multiplies every channel by the brightness in [$ff82]
    (0xF0, 0x4439): "FE_UploadPalettes",  # $c806 -> BG and OBJ palette RAM
    (0xF0, 0x451A): "FE_ReadJoypadPressed",  # [$ff92] held, [$ff91] newly pressed; A+B+Select+Start resets
    (0xF0, 0x4547): "FE_ReadJoypadPressed_Link",  # the same; the reset first tells the other Game Boy (sends $ef)
    (0xF0, 0x4596): "FE_ReadJoypadHeld_Link",  # [$ff91] held, [$ff93] previous; reset as FE_ReadJoypadPressed_Link
    (0xF0, 0x45BC): "FE_WaitForButton",  # until a newly pressed A, B, Select or Start
    (0xF0, 0x45DA): "FE_ReadJoypadHeld",  # [$ff91] held, [$ff93] previous; A+B+Select+Start resets
    (0xF0, 0x4608): "FE_RandomBelow",  # b = random number below b+1
    (0xF0, 0x4620): "FE_Random",
    (0xF0, 0x4642): "FE_SeedRandom",
    (0xF0, 0x4657): "FE_Multiply",  # hl = b * c
    (0xF0, 0x46A5): "FE_Divide",  # c / b
    (0xF0, 0x46E4): "FE_WaitFrames",  # d frames, reading the joypad
    (0xF0, 0x46F6): "FE_WaitSeconds",  # d times 60 frames
    (0xF0, 0x4707): "FE_InitLineStep",  # sets up a record (at de) that steps along a line by (b, c)
    (0xF0, 0x4761): "FE_LineStep",  # next (dx, dy) step of a FE_InitLineStep record
    (0xF0, 0x47A5): "FE_LoadPictureMap",  # by its kind in PictureMapKinds: 0 plain, 1 UniqueTileMap, 2 attributes in the second half
    (0xF0, 0x47D8): "FE_CopyPictureMap",  # PictureHeights rows of 32 bytes, PictureWidths bytes apart in the source
    (0xF0, 0x4882): "FE_LoadPicture",  # picture b of PictureTable: map, palettes and tiles
    (0xF0, 0x49C3): "FE_SaveBGMap",  # $d000 -> $d800, WRAM bank 2
    (0xF0, 0x49D8): "FE_RestoreBGMap",
    (0xF0, 0x49EC): "FE_UploadBGMap",  # WRAM bank 2 -> $9800 (attributes, then tiles)
    (0xF0, 0x4A16): "FE_UploadBGMap9C00",
    (0xF0, 0x4A40): "FE_GetPictureMapKind",
    (0xF0, 0x4A49): "FE_GetPictureWidth",
    (0xF0, 0x4A52): "FE_GetPictureHeight",
    (0xF0, 0x4A5B): "FE_GetPictureMapPointer",
    (0xF0, 0x4A71): "FE_GetPictureTilesPointer",
    (0xF0, 0x4A87): "FE_GetPicturePalettesPointer",
    (0xF0, 0x4F9D): "FE_InstallSpriteCopy",  # copies FE_FarCopySprites_Code to $c8e7
    (0xF0, 0x4FA8): "FE_DrawSpriteAnim",  # entry d of SpriteAnimTable, variant [$ff82]
    (0xF0, 0x50F7): "FE_PlaceSpritesFixed",  # record types 1 and 3: offsets from the anchor
    (0xF0, 0x513B): "FE_PlaceSpritesStepped",  # type 4: each sprite steps from the last
    (0xF0, 0x517F): "FE_AddSpriteAttributes",  # types 2-4: one attribute byte per sprite
    (0xF0, 0x519A): "FE_PlaceSpritesSteppedFlip",  # types 0 and 2, mirrored as the attributes in [$ff99] ask
    (0xF0, 0x528B): "FE_FarCopySprites_Code",  # runs at $c8e7
    (0xF0, 0x52D4): "FE_ClearOAM",
    (0xF0, 0x52E2): "FE_InstallSoundRoutines",
    (0xF0, 0x52F8): "FE_UpdateSound_Code",  # runs at $c930
    (0xF0, 0x5313): "FE_PlaySong_Code",  # runs at $c94b
    (0xF0, 0x6AD5): "FE_DrawTextFromPointer",
    (0xF0, 0x6B44): "FE_DrawTextOnMap",  # text into the BG map copy in WRAM bank 2
    (0xF0, 0x6BB6): "FE_DrawBox",  # a frame of tiles $7d-... around the text area
    (0xF0, 0x6C60): "FE_DrawTextInBox",
    # --- front end, bank $F1: entry, menus (rings), save files, sound test, printer, sticker book
    (0xF1, 0x4000): "FE_Enter",  # from the main game: saves its stack pointer ($c803) and HRAM, then FE_Main
    (0xF1, 0x4139): "FE_RestoreStateAndReturn",
    (0xF1, 0x4159): "FE_CallF2_6c5a",
    (0xF1, 0x417D): "FE_ReturnToGame",  # restores HRAM and the main game's stack; l = language, d = what to do next
    (0xF1, 0x41D5): "FE_ShowCrankyUnlocked",
    (0xF1, 0x42FC): "FE_LoadGradientColours",  # $659a -> $db00: the colours FE_VBlank_Menu/FE_STAT_Gradient draw down the screen
    (0xF1, 0x430B): "FE_ClearGradientColours",
    (0xF1, 0x4316): "FE_SetGradientColoursWhite",
    (0xF1, 0x4322): "FE_SetBGPalettesWhite",
    (0xF1, 0x432E): "FE_SetOBJPalettesWhite",
    (0xF1, 0x433A): "FE_LoadMenuOBJPalettes",  # $65e8 -> $c846
    (0xF1, 0x4349): "FE_InitMenuState",
    (0xF1, 0x4361): "FE_ReadSaveFilesUsed",  # bit 7 of each file's status byte ($c341/$c345/$c349) -> $c99a-$c99c
    (0xF1, 0x437D): "FE_StickerBook_Reset",
    (0xF1, 0x438B): "FE_MakeFlag_Reset",
    (0xF1, 0x43A1): "FE_Alphabet_Reset",
    (0xF1, 0x43A6): "FE_ClearFirstTile",
    (0xF1, 0x43BE): "FE_LoadMenuFont",  # font tiles from bank $FF
    (0xF1, 0x43E6): "FE_FadeInScreen",  # palettes and gradient up from black, in steps of 8
    (0xF1, 0x4456): "FE_FadeOutScreen",  # down to black, then clears the palettes
    (0xF1, 0x44C5): "FE_FadeOutScreen_NoInput",
    (0xF1, 0x452C): "FE_FadeOutScreenSlow",
    (0xF1, 0x4588): "FE_FadeInScreenSlow",
    (0xF1, 0x45DC): "FE_FadeToWhite",
    (0xF1, 0x464B): "FE_FadeToColours",  # towards the colour list at $db50
    (0xF1, 0x4695): "FE_FadeToColoursWithGradient",
    (0xF1, 0x470D): "FE_FadeToColoursSlow",
    (0xF1, 0x475D): "FE_FadeStepToColour",
    (0xF1, 0x4787): "FE_DrawRingItems",  # each item's sprite around the ring
    (0xF1, 0x480D): "FE_GetRingItemPosition",  # RingAngleLists by item count, rotated by $c96d
    (0xF1, 0x4862): "FE_DrawMenu",  # clears OAM, draws the ring items and the cursor, waits for VBlank, OAM DMA
    (0xF1, 0x48A4): "FE_MenuInput",  # right/left turn the ring, A or Start selects, B goes back
    (0xF1, 0x48D6): "FE_TurnRingRight",
    (0xF1, 0x4926): "FE_IsRingItemHidden",  # by the ring's rule in the table at $67aa; d = 1 when hidden
    (0xF1, 0x4943): "FE_RingRule_SaveFiles",
    (0xF1, 0x4946): "FE_RingRule_UsedFilesOnly",
    (0xF1, 0x4949): "FE_RingRule_EmptyFilesOnly",
    (0xF1, 0x494C): "FE_RingRule_Options",
    (0xF1, 0x494F): "FE_RingRule_Main",
    (0xF1, 0x4952): "FE_RingRule_Ring3",
    (0xF1, 0x4955): "FE_RingRule_LinkCrankyModes",
    (0xF1, 0x4958): "FE_RingRule_Print",
    (0xF1, 0x495B): "FE_HideMakeFlagUntilUnlocked",  # Print ring item 2 while [$b0c7] < 6
    (0xF1, 0x496A): "FE_HideLinkUntilUnlocked",  # main ring item 2 while [$b0c5] = 0
    (0xF1, 0x4978): "FE_HideRing3Items",
    (0xF1, 0x4989): "FE_HideLockedLinkModes",  # items past [$b0c5] - 2
    (0xF1, 0x4997): "FE_HideCopyErase",  # Erase when no file is used; Copy also when all three are
    (0xF1, 0x49A5): "FE_HideIfFileNotFinished",
    (0xF1, 0x49C4): "FE_HideOptionsUntilFinished",  # Options items 2 and 3 need a file with bit 6 of its status set
    (0xF1, 0x49FC): "FE_RingRuleCommon",
    (0xF1, 0x4A66): "FE_HideUnusedFile",
    (0xF1, 0x4A79): "FE_HideUsedFile",
    (0xF1, 0x4A8C): "FE_TurnRingLeft",
    (0xF1, 0x4ADA): "FE_DrawMenuTurning",
    (0xF1, 0x4B96): "FE_SetSaveFileIcons",
    (0xF1, 0x4BBA): "FE_SelectRingItem",  # by the item's action byte: a ring number, or bit 7 action, bit 6 file, bit 5 language, bit 4 option
    (0xF1, 0x4C75): "FE_BackToParentRing",
    (0xF1, 0x4CFA): "FE_Action_StickerBook",  # actions $80-$8d: jp table
    (0xF1, 0x4CFD): "FE_Action_ViewItems",
    (0xF1, 0x4D00): "FE_Action_None",
    (0xF1, 0x4D03): "FE_Action_MakeFlag",
    (0xF1, 0x4D06): "FE_Action_Link",
    (0xF1, 0x4D09): "FE_Action_EraseFile",
    (0xF1, 0x4D0C): "FE_Action_Alphabet",
    (0xF1, 0x4D0F): "FE_Action_CopyFrom",
    (0xF1, 0x4D12): "FE_Action_CopyTo",
    (0xF1, 0x4D15): "FE_Action_FunkysFishing",
    (0xF1, 0x4D18): "FE_Action_StartGame8A",  # no ring item uses action $8a
    (0xF1, 0x4D1B): "FE_Action_SoundTest",
    (0xF1, 0x4D1E): "FE_Action_HiScore",
    (0xF1, 0x4D21): "FE_Action_CrosshairCranky",
    (0xF1, 0x4D24): "FE_ViewItems_Start",
    (0xF1, 0x4D28): "FE_Alphabet_Start",
    (0xF1, 0x4D31): "FE_CrosshairCranky_Start",  # leaves the front end (main game stack) with the game number in d and e
    (0xF1, 0x4D86): "FE_SoundTest",  # left/right pick a song, A plays it, B leaves
    (0xF1, 0x4DC4): "FE_SoundTest_DrawNumber",
    (0xF1, 0x4DE5): "FE_SoundTest_Previous",
    (0xF1, 0x4DF6): "FE_SoundTest_Next",
    (0xF1, 0x4E06): "FE_FunkysFishing_Start",
    (0xF1, 0x4E61): "FE_FunkysFishing_Return",
    (0xF1, 0x4E87): "FE_AfterBonusGame",
    (0xF1, 0x4ECD): "FE_HiScore_Return",
    (0xF1, 0x4EF3): "FE_ReturnToMenu",
    (0xF1, 0x4EFC): "FE_HiScore_Start",
    (0xF1, 0x4F36): "FE_RestoreAndReturnToMenu",
    (0xF1, 0x4F4D): "FE_StartGame8A",
    (0xF1, 0x4FA4): "FE_ReturnToMenuFromLink",
    (0xF1, 0x4FC1): "FE_Link_Start",
    (0xF1, 0x4FCA): "FE_CopyFrom_Start",  # remembers the source file, opens the target ring (12)
    (0xF1, 0x4FF1): "FE_CopyTo_Confirm",  # "Sure?", then copies the 64-byte file block
    (0xF1, 0x5071): "FE_MakeFlag_Start",
    (0xF1, 0x507A): "FE_EraseFile_Confirm",  # "Sure?", then clears the file's 64-byte block
    (0xF1, 0x50F1): "FE_ClearLinkFlags",
    (0xF1, 0x51CC): "FE_ClearBGMap",
    (0xF1, 0x5206): "FE_ReadSaveFileStatus",
    (0xF1, 0x5243): "FE_DrawSaveFileInfo",
    (0xF1, 0x5333): "FE_DrawRingLabelPicture",
    (0xF1, 0x53C9): "FE_AdvanceFarPointer_F1",
    (0xF1, 0x53EC): "FE_HDMAAcrossBanks_F1",
    (0xF1, 0x5411): "FE_LoadLanguageWords",
    (0xF1, 0x5419): "FE_DrawRingExtras",
    (0xF1, 0x5508): "FE_AskSure",  # Yes/No box; [$c994] = answer
    (0xF1, 0x5552): "FE_AskSure_FromF2",
    (0xF1, 0x55F3): "FE_DrawYesNo",
    (0xF1, 0x5675): "FE_YesNoInput",
    (0xF1, 0x569E): "FE_YesNo_Next",
    (0xF1, 0x56B4): "FE_YesNo_Previous",
    (0xF1, 0x56C9): "FE_JP_VBlank_Menu",  # jp templates written into the interrupt slots
    (0xF1, 0x56CC): "FE_JP_VBlank_Plain",
    (0xF1, 0x56CF): "FE_JP_VBlank_Link",
    (0xF1, 0x56D2): "FE_JP_STAT_Gradient",
    (0xF1, 0x56D5): "FE_JP_STAT_Sound",
    (0xF1, 0x56D8): "FE_JP_Serial_Printer",
    (0xF1, 0x56DB): "FE_JP_Serial_Handshake",
    (0xF1, 0x56DE): "FE_JP_Serial_WaitForPartner",
    (0xF1, 0x56E1): "FE_JP_Serial_Flag",
    (0xF1, 0x56E4): "FE_InstallInterruptHandlers",  # copies the handlers at $57f0-$59bc to $ccba-$ce80
    (0xF1, 0x5763): "FE_SetInterrupts_Menu",
    (0xF1, 0x5780): "FE_SetInterrupts_Plain",
    (0xF1, 0x579D): "FE_SetInterrupts_Printer",
    (0xF1, 0x57BA): "FE_SetInterrupts_Handshake",
    (0xF1, 0x57C9): "FE_SetInterrupts_WaitForPartner",
    (0xF1, 0x57D8): "FE_SetInterrupts_SerialFlag",
    (0xF1, 0x57E7): "FE_WriteJumpSlot",
    (0xF1, 0x59BD): "FE_EnableInterrupts_Menu",  # VBlank and per-line STAT (the gradient)
    (0xF1, 0x59CE): "FE_EnableInterrupts_Plain",  # VBlank, STAT at line $64 updates the sound
    (0xF1, 0x59E3): "FE_EnableInterrupts_VBlankOnly",
    (0xF1, 0x59F0): "FE_EnableInterrupts_Printer",
    (0xF1, 0x59FD): "FE_EnableInterrupts_Handshake",
    (0xF1, 0x5A0A): "FE_EnableInterrupts_SerialFlag",
    (0xF1, 0x5A1B): "FE_WaitForLinkPartner",  # sends $ea and waits for the other Game Boy
    (0xF1, 0x5A34): "FE_ViewItems",
    (0xF1, 0x5ADF): "FE_ViewItems_Loop",
    (0xF1, 0x5B02): "FE_LoadViewItemsScreen",
    (0xF1, 0x5B81): "FE_CopyTilesToMap2",
    (0xF1, 0x5B9A): "FE_CopyTileRows",
    (0xF1, 0x5BB3): "FE_ViewItems_ScrollIn",
    (0xF1, 0x5BE0): "FE_ViewItems_ScrollOut",
    (0xF1, 0x5C09): "FE_ViewItems_DrawItems",
    (0xF1, 0x5C69): "FE_ViewItems_DrawItem",
    (0xF1, 0x5CD1): "FE_ViewItems_LoadPalettes",
    (0xF1, 0x5CE0): "FE_Printer_InitPackets",  # packet templates and the serial routine (copied to $ce87)
    (0xF1, 0x5D28): "FE_Printer_InitInitPacket",
    (0xF1, 0x5D35): "FE_Printer_InitStatusPacket",
    (0xF1, 0x5D42): "FE_Printer_InitEmptyDataPacket",
    (0xF1, 0x5D4F): "FE_Printer_BuildPrintPacket",  # $88 $33, command 2: sheets, margins, palette, exposure
    (0xF1, 0x5D79): "FE_Printer_SendInit",  # command 1
    (0xF1, 0x5D96): "FE_Printer_SendPrint",
    (0xF1, 0x5DC3): "FE_Printer_SendPacket",  # byte by byte through the serial port, then reads the status
    (0xF1, 0x5E15): "FE_Printer_DecodeStatus",  # printer status bits -> error number in [$ccb1]
    (0xF1, 0x5E67): "FE_Printer_DecodeStatus2",
    (0xF1, 0x5E80): "FE_Printer_SendData",  # command 4, 640 bytes per packet from WRAM bank 5 on
    (0xF1, 0x5F19): "FE_Printer_SendEmptyData",
    (0xF1, 0x5F29): "FE_Printer_CopyAcrossWRAMBanks",
    (0xF1, 0x5F44): "FE_Printer_BuildDataPacket",
    (0xF1, 0x5F7B): "FE_Printer_Checksum",
    (0xF1, 0x5FAA): "FE_PrinterSerial_Code",  # runs at $ce87, from the serial interrupt
    (0xF1, 0x5FD6): "FE_PrinterSendByte_Code",  # runs at $ceb3
    (0xF1, 0x601A): "FE_FarCopyBankSwitching_Code",  # runs at $cef7
    (0xF1, 0x603A): "FE_FarCopyBankSwitching",
    (0xF1, 0x6047): "FE_SetDoubleSpeed_F1",
    (0xF1, 0x6069): "FE_ToggleCPUSpeed",  # the printer is driven at single speed
    (0xF1, 0x6087): "FE_SetVBlankTimer",
    (0xF1, 0x60A2): "FE_WaitVBlankTimer",
    (0xF1, 0x60B6): "FE_Multiply16",
    (0xF1, 0x6136): "FE_WriteScreenAttributes",
    (0xF1, 0x6179): "FE_OrMapRect",
    (0xF1, 0x61B2): "FE_FillMapRect",
    (0xF1, 0x61E1): "FE_StartHDMA_F1",
    (0xF1, 0x61F1): "FE_HDMAToVRAMBank",
    (0xF1, 0x6206): "FE_IsPointInRect",
    (0xF1, 0x6218): "FE_CopyBytes_F1",  # bc bytes de -> hl
    (0xF1, 0x6221): "FE_FillBytes_F1",  # de bytes of b at hl
    (0xF1, 0x6229): "FE_DelayLoop",  # about bc / 8 iterations
    (0xF1, 0x6240): "FE_BuildPointerList",
    (0xF1, 0x624D): "FE_Printer_Init",  # palette $e4, exposure $24
    (0xF1, 0x625B): "FE_PrintWRAMImage",
    (0xF1, 0x62C4): "FE_PrintPicture",  # a front-end picture, through FE_LoadPictureForPrinter
    (0xF1, 0x635D): "FE_PrintStickerPage",  # by the page's job list at $6586
    (0xF1, 0x6473): "FE_SetPrintDarkness",  # b = 0-2, from the table at $64cb
    (0xF1, 0x6485): "FE_GetPrintDarkness",
    (0xF1, 0x649C): "FE_Printer_ShowError",
    (0xF1, 0x707A): "FE_StickerBook",
    (0xF1, 0x7148): "FE_StickerBook_Input",  # by the screen's state [$c989], jp table at $715e
    (0xF1, 0x715E): "FE_StickerBook_State0",
    (0xF1, 0x7161): "FE_StickerBook_State1",
    (0xF1, 0x7164): "FE_StickerBook_State2",
    (0xF1, 0x7167): "FE_StickerBook_State3",
    (0xF1, 0x716A): "FE_StickerBook_State4",
    (0xF1, 0x716D): "FE_StickerBook_OptionsMenu",
    (0xF1, 0x7187): "FE_StickerBook_DarknessMenu",
    (0xF1, 0x71A7): "FE_StickerBook_SendMenu",
    (0xF1, 0x71C1): "FE_StickerBook_PrintMenu",
    (0xF1, 0x7251): "FE_StickerBook_Browse",  # d-pad moves between stickers through MenuTable links, A opens a menu
    (0xF1, 0x728E): "FE_StickerBook_ReadInput",
    (0xF1, 0x72D4): "FE_MenuCursorNext",
    (0xF1, 0x72F9): "FE_MenuCursorPrevious",
    (0xF1, 0x7357): "FE_StickerBook_ShowPage",
    (0xF1, 0x73AC): "FE_StickerBook_ShowSticker",
    (0xF1, 0x73EF): "FE_StickerBook_SelectSticker",
    (0xF1, 0x745B): "FE_StickerBook_OpenOptions",
    (0xF1, 0x7485): "FE_StickerBook_OpenDarkness",
    (0xF1, 0x74B0): "FE_StickerBook_OpenPrint",
    (0xF1, 0x74DA): "FE_StickerBook_OpenSend",
    (0xF1, 0x7504): "FE_MenuCursorHighlight",
    (0xF1, 0x7524): "FE_MenuCursorUnhighlight",
    (0xF1, 0x7544): "FE_DrawSubMenu",  # from SpriteLists_f1_691a by state
    (0xF1, 0x75B6): "FE_SlideSpritesUp",
    (0xF1, 0x75D7): "FE_SlideSpritesDown",
    (0xF1, 0x75F8): "FE_StickerBook_DrawCursor",
    (0xF1, 0x765A): "FE_StickerBook_MoveUp",
    (0xF1, 0x766F): "FE_StickerBook_MoveDown",
    (0xF1, 0x7684): "FE_StickerBook_MoveLeft",
    (0xF1, 0x7699): "FE_StickerBook_MoveRight",
    (0xF1, 0x76AE): "FE_StickerBook_LoadItem",  # the current MenuTable item -> $c98a-$c991
    (0xF1, 0x76F9): "FE_LoadStickerFrameTile",
    (0xF1, 0x7718): "FE_StickerBook_SendIR",  # sends the sticker through the infrared port
    (0xF1, 0x7791): "FE_StickerBook_ReceiveIR",
    (0xF1, 0x77CF): "FE_StickerBook_IsStickerFound",
    (0xF1, 0x7803): "FE_TestStickerBit",  # bit a of the sticker bitfield at $b0c2
    (0xF1, 0x781A): "FE_StickerBook_UnlockReceived",
    (0xF1, 0x7840): "FE_SetStickerBit",
    (0xF1, 0x7865): "FE_SetBitN",
    (0xF1, 0x787E): "FE_SetBitN_Body",
    (0xF1, 0x78A0): "FE_TestBitN",
    (0xF1, 0x78B8): "FE_TestBitN_Body",
    (0xF1, 0x78D2): "FE_IR_Receive",  # waits for a $aa / $37 packet in $dd1f-$dd28
    (0xF1, 0x7912): "FE_IR_CheckPacket",
    (0xF1, 0x794B): "FE_IR_Send",
    (0xF1, 0x799E): "FE_IR_CheckAck",
    (0xF1, 0x79A8): "FE_StickerBook_DrawStickers",
    (0xF1, 0x79E2): "FE_StickerBook_DrawSticker",
    (0xF1, 0x7A4F): "FE_StickerBook_ScrollWhileSelect",
    (0xF1, 0x7A6F): "FE_StickerBook_ScrollUp",
    (0xF1, 0x7A8D): "FE_StickerBook_ScrollDown",
    (0xF1, 0x7ABB): "FE_StickerBook_LoadRowAbove",
    (0xF1, 0x7AD6): "FE_StickerBook_LoadRowBelow",
    (0xF1, 0x7AF6): "FE_GetMapCell",
    (0xF1, 0x7B15): "FE_LoadPictureRow",
    (0xF1, 0x7B82): "FE_CopyPictureRowTiles",
    (0xF1, 0x7BC5): "FE_CopyPictureRowTiles_A",
    (0xF1, 0x7BF1): "FE_CopyPictureRowTiles_B",
    (0xF1, 0x7C1A): "FE_CopyPictureRowTiles_C",
    (0xF1, 0x7C58): "FE_CopyPictureRowTiles_D",
    (0xF1, 0x7C82): "FE_CopyPictureRowTiles_E",
    (0xF1, 0x7CB9): "FE_LanguageSelect",  # the first screen: ring 6, the five languages
    (0xF1, 0x7CFF): "FE_LanguageSelect_Input",
    (0xF1, 0x7D37): "FE_LanguageSelect_Done",  # back to the main game, l = language, d = 1
    (0xF1, 0x7D58): "FE_LanguageSelect_Draw",
    (0xF0, 0x48FA): "FE_LoadPictureForPrinter",  # tiles of picture b, complemented, into WRAM bank 5 on
    (0xF0, 0x48F4): "FE_LoadPictureForPrinter_Check",
    (0xF1, 0x7870): "FE_SetBitN_0",
    (0xF1, 0x78AA): "FE_TestBitN_0",
    (0xF1, 0x7872): "FE_SetBitN_1",
    (0xF1, 0x78AC): "FE_TestBitN_1",
    (0xF1, 0x7874): "FE_SetBitN_2",
    (0xF1, 0x78AE): "FE_TestBitN_2",
    (0xF1, 0x7876): "FE_SetBitN_3",
    (0xF1, 0x78B0): "FE_TestBitN_3",
    (0xF1, 0x7878): "FE_SetBitN_4",
    (0xF1, 0x78B2): "FE_TestBitN_4",
    (0xF1, 0x787A): "FE_SetBitN_5",
    (0xF1, 0x78B4): "FE_TestBitN_5",
    (0xF1, 0x787C): "FE_SetBitN_6",
    (0xF1, 0x78B6): "FE_TestBitN_6",
    # --- front end, bank $F2: Alphabet, Make Flag, infrared, link play
    (0xF2, 0x4000): "FE_Alphabet",  # Print -> Alphabet: a letter with its character, printed
    (0xF2, 0x4112): "FE_Alphabet_Loop",
    (0xF2, 0x414D): "FE_Alphabet_DrawArrows",
    (0xF2, 0x41A3): "FE_Alphabet_Next",  # 52 pictures, PictureByItem
    (0xF2, 0x41B4): "FE_Alphabet_Previous",
    (0xF2, 0x41C5): "FE_Alphabet_ShowLetter",
    (0xF2, 0x41F9): "FE_Alphabet_OpenMenu",
    (0xF2, 0x4278): "FE_Alphabet_OpenPrintMenu",
    (0xF2, 0x42CE): "FE_Alphabet_Print",  # "Printing...", through FE_PrintPicture
    (0xF2, 0x4350): "FE_ClearBGMap9C00AndTiles",
    (0xF2, 0x4376): "FE_ClearBGMap9C00_Loop",
    (0xF2, 0x43CB): "FE_MakeFlag",  # Print -> Make Flag: type a two-line banner, print it in big letters
    (0xF2, 0x4500): "FE_MakeFlag_Input",
    (0xF2, 0x4544): "FE_MakeFlag_DrawCursor",
    (0xF2, 0x45D4): "FE_MakeFlag_MoveUp",  # through the key links in MenuItemRecords
    (0xF2, 0x45DF): "FE_MakeFlag_MoveDown",
    (0xF2, 0x45EA): "FE_MakeFlag_MoveLeft",
    (0xF2, 0x45F5): "FE_MakeFlag_MoveRight",
    (0xF2, 0x4600): "FE_MakeFlag_LoadKey",  # key [$c9a0] of MenuItemRecords
    (0xF2, 0x4626): "FE_MakeFlag_TypeKey",  # adds the key's character (MenuItemBytes) to the current line
    (0xF2, 0x466E): "FE_MakeFlag_Backspace",
    (0xF2, 0x467E): "FE_MakeFlag_DeleteCharacter",
    (0xF2, 0x46B2): "FE_MakeFlag_DrawLines",
    (0xF2, 0x46EA): "FE_MakeFlag_ClearLines",
    (0xF2, 0x470F): "FE_FillBytesD",
    (0xF2, 0x4714): "FE_MakeFlag_DrawKeyboard",
    (0xF2, 0x47C6): "FE_MakeFlag_Menu",  # the menu after Select: line 1 / line 2 / print
    (0xF2, 0x480A): "FE_MakeFlag_SwitchLine",
    (0xF2, 0x4814): "FE_MakeFlag_MenuInput",
    (0xF2, 0x4842): "FE_MakeFlag_MenuNext",
    (0xF2, 0x4857): "FE_MakeFlag_MenuDraw",
    (0xF2, 0x4864): "FE_MakeFlag_MenuPrevious",
    (0xF2, 0x487B): "FE_PrintMenuInput",
    (0xF2, 0x48B8): "FE_PrintMenuNext",
    (0xF2, 0x48F3): "FE_PrintMenuPrevious",
    (0xF2, 0x490A): "FE_HideMenuCursor",
    (0xF2, 0x4928): "FE_ShowMenuCursor",
    (0xF2, 0x4946): "FE_LoadMenuFrameTiles",
    (0xF2, 0x4965): "FE_SlideSpritesRight",
    (0xF2, 0x4993): "FE_ShiftSpritesX",
    (0xF2, 0x49A4): "FE_MakeFlag_DarknessMenu",
    (0xF2, 0x4A15): "FE_MakeFlag_DarknessInput",
    (0xF2, 0x4A39): "FE_MakeFlag_PrintMenu",
    (0xF2, 0x4B37): "FE_SlideSpritesUpScroll",
    (0xF2, 0x4B64): "FE_SlideSpritesDownScroll",
    (0xF2, 0x4B91): "FE_MakeFlag_OpenDarkness",
    (0xF2, 0x4BDB): "FE_MakeFlag_OpenPrintChoice",
    (0xF2, 0x4C27): "FE_MakeFlag_BorderMenu",  # left/right pick the banner's border
    (0xF2, 0x4C5E): "FE_MakeFlag_DrawBorderChoice",
    (0xF2, 0x4CBA): "FE_MakeFlag_BorderLoop",
    (0xF2, 0x4D7A): "FE_TurnChoiceRight",  # also the language select
    (0xF2, 0x4DC4): "FE_TurnChoiceLeft",
    (0xF2, 0x4FB0): "FE_MakeFlag_PrintBanner",
    (0xF2, 0x501E): "FE_MakeFlag_SetUpLines",
    (0xF2, 0x5074): "FE_ClearBannerBuffer",  # WRAM $d000-$d9ff
    (0xF2, 0x507B): "FE_ClearBytes",
    (0xF2, 0x5084): "FE_ClearBannerTail",
    (0xF2, 0x508F): "FE_ScrollBannerBuffer",
    (0xF2, 0x50A4): "FE_AdvanceBannerLines",
    (0xF2, 0x50CD): "FE_MakeFlag_PrintNextStrip",
    (0xF2, 0x51B8): "FE_MakeFlag_PrintFirstStrip",
    (0xF2, 0x5288): "FE_MakeFlag_SetLine1",
    (0xF2, 0x529C): "FE_MakeFlag_SetLine2",
    (0xF2, 0x52B0): "FE_MakeFlag_GetLine1",
    (0xF2, 0x52C4): "FE_MakeFlag_GetLine2",
    (0xF2, 0x52D8): "FE_DrawBannerText",  # each character as a big letter from LetterPieces
    (0xF2, 0x5300): "FE_BannerHasRoom",
    (0xF2, 0x530F): "FE_AddHLToDE",
    (0xF2, 0x5313): "FE_DrawBigLetter",
    (0xF2, 0x53A8): "FE_DrawBigLetterTile",
    (0xF2, 0x53E2): "FE_DrawBigLetterTile_Copy",
    (0xF2, 0x53F6): "FE_PrintBannerStrip",
    (0xF2, 0x5418): "FE_PrintBannerStripShort",
    (0xF2, 0x543A): "FE_PrintBannerEnd",
    (0xF2, 0x545C): "FE_DrawBannerBorder",
    (0xF2, 0x549A): "FE_CopyFarBytesTwice",
    (0xF2, 0x54AA): "FE_DrawBannerEndPiece",  # one of eight end pieces from $f2:5760, chosen at random
    (0xF2, 0x54EB): "FE_DrawBannerStartPiece",
    (0xF2, 0x552C): "FE_CopyBannerPiece",
    (0xF2, 0x5553): "FE_FarCopyB",
    (0xF2, 0x555D): "FE_CopyBannerPieceRows",
    (0xF2, 0x6760): "FE_IR_Init",  # infrared port on (rRP), waits, sets the timing for single or double speed
    (0xF2, 0x6798): "FE_IR_WaitHigh",
    (0xF2, 0x67A0): "FE_IR_WaitLow",
    (0xF2, 0x67A8): "FE_IR_LightOn",
    (0xF2, 0x67AF): "FE_IR_LightOff",
    (0xF2, 0x67B6): "FE_IR_ReceiveHandshake",
    (0xF2, 0x6802): "FE_IR_SendHandshake",
    (0xF2, 0x6850): "FE_IR_Off",
    (0xF2, 0x6859): "FE_IR_SendPacket",  # $5a, length, data, checksum
    (0xF2, 0x68A5): "FE_IR_SendBytes",
    (0xF2, 0x6920): "FE_IR_SetError",
    (0xF2, 0x6932): "FE_IR_ReceivePacket",
    (0xF2, 0x698D): "FE_IR_ReceiveBytes",
    (0xF2, 0x6A12): "FE_IR_SendPacket_Entry",
    (0xF2, 0x6A17): "FE_IR_ReceivePacket_Entry",
    (0xF2, 0x6A1C): "FE_IR_Nop",
    (0xF2, 0x6A1D): "FE_IR_Delay",
    (0xF2, 0x6A5A): "FE_LinkFishingResults",  # "Player 1 Wins" ... with both scores
    (0xF2, 0x6B67): "FE_BonusGameResults",
    (0xF2, 0x6BF6): "FE_DrawScore",
    (0xF2, 0x6C24): "FE_DrawScore4",
    (0xF2, 0x6C3D): "FE_DrawBCDByte",
    (0xF2, 0x6C5A): "FE_LinkGameResults",  # by result type, jp table at $6caa
    (0xF2, 0x6CAA): "FE_LinkResult_Compare",
    (0xF2, 0x6CAD): "FE_LinkResult_GameOver",
    (0xF2, 0x6CB0): "FE_LinkResult_TwoScores",
    (0xF2, 0x6CB3): "FE_LinkResult_Zero",
    (0xF2, 0x6CB6): "FE_LinkResult_CompareBody",  # "You Win", "You Lose", "You Draw"
    (0xF2, 0x6D43): "FE_LinkResult_GameOverBody",
    (0xF2, 0x6D9C): "FE_LinkResult_TwoScoresBody",
    (0xF2, 0x6E68): "FE_LinkResult_ZeroBody",
    (0xF2, 0x6EDD): "FE_DrawText_YouDraw",
    (0xF2, 0x6EF5): "FE_DrawText_YouWin",
    (0xF2, 0x6F0D): "FE_DrawText_YouLose",
    (0xF2, 0x6F26): "FE_DrawText_GameOver",
    (0xF2, 0x6F3E): "FE_DrawText_Player1Wins",
    (0xF2, 0x6F56): "FE_DrawText_Player1Loses",
    (0xF2, 0x6F6E): "FE_DrawText_Player1Draws",
    (0xF2, 0x6F86): "FE_DrawText_Player2Wins",
    (0xF2, 0x6F9E): "FE_DrawText_Player2Loses",
    (0xF2, 0x6FB6): "FE_DrawText_Player2Draws",
    (0xF2, 0x6FCE): "FE_DrawScorePlayer1",
    (0xF2, 0x6FD5): "FE_DrawScorePlayer1_DE",
    (0xF2, 0x6FE0): "FE_DrawScorePlayer2",
    (0xF2, 0x6FE7): "FE_DrawScorePlayer2_DE",
    (0xF2, 0x6FF2): "FE_DrawBCD3",
    (0xF2, 0x700F): "FE_DrawDigitTile",
    (0xF2, 0x701A): "FE_RestartFrontEnd",  # back to the main menu after a bonus or link game
    (0xF2, 0x70BD): "FE_Link",  # main menu -> Link: connects, then the link ring
    (0xF2, 0x72B1): "FE_LinkFishing1_Return",
    (0xF2, 0x72D7): "FE_LinkFishing1_AfterGame",
    (0xF2, 0x7303): "FE_LinkFishing1_Start",  # Funky's Fishing ($50:4000) over the link cable
    (0xF2, 0x736F): "FE_LinkFishing1_Restore",
    (0xF2, 0x7398): "FE_LinkFishing1_Results",
    (0xF2, 0x73C1): "FE_LinkFishing1_Quit",
    (0xF2, 0x73C9): "FE_Link_ExchangeSettings",
    (0xF2, 0x74DD): "FE_LinkFishing2_Return",
    (0xF2, 0x7503): "FE_LinkFishing2_AfterGame",
    (0xF2, 0x752F): "FE_LinkFishing2_Start",
    (0xF2, 0x7576): "FE_LinkFishing2_Restore",
    (0xF2, 0x759F): "FE_LinkFishing2_Results",
    (0xF2, 0x75C8): "FE_LinkFishing2_Quit",
    (0xF2, 0x75D0): "FE_Link_Nop",
    (0xF2, 0x75D1): "FE_Link_ShowScreen",
    (0xF2, 0x7640): "FE_LinkMenu",
    (0xF2, 0x765F): "FE_LinkMenu_Input",
    (0xF2, 0x769B): "FE_LinkMenu_IgnoreOther",
    (0xF2, 0x76A2): "FE_LinkMenu_Select",
    (0xF2, 0x7742): "FE_LinkMenu_Back",  # from the link ring: tells the other Game Boy ($77)
    (0xF2, 0x77A0): "FE_Link_StartHandshake",  # $bb / $66 exchange
    (0xF2, 0x77C5): "FE_Link_WaitForPartner",
    (0xF2, 0x78AE): "FE_Link_ExchangeByte",
    (0xF2, 0x78FD): "FE_Link_ExchangeChoices",
    (0xF2, 0x7943): "FE_Link_AgreeOnChoices",  # takes each value both Game Boys sent the same, else the first
    (0xF2, 0x7966): "FE_Link_MajorityOfThree",
    (0xF2, 0x7971): "FE_ClearPalette7",
    (0xF2, 0x7987): "FE_RestorePalette7",
    (0xF2, 0x7A1C): "FE_Link_Disconnected",  # back to the main menu
    (0xF2, 0x7A5B): "FE_Padding_F2",
    # --- Crosshair Cranky, bank $F5 (game numbers: 0 Buddies Beware, 1 Barrel O'Kremlings, 2 Wanted,
    #     3 Kremling Krackdown, 4 Kremlings and Kongs, 5 Galleon Gunner)
    (0xF5, 0x4000): "Cranky_LoadPicture",  # as FE_LoadPicture, keeping the sound running
    (0xF5, 0x4082): "Cranky_LoadPictureTiles_8800",
    (0xF5, 0x40AF): "Cranky_LoadPictureTiles_9000",
    (0xF5, 0x40B6): "Cranky_HDMAAcrossBanks",
    (0xF5, 0x4142): "Cranky_UploadBGMap",
    (0xF5, 0x4193): "Cranky_UploadBGMap9C00",
    (0xF5, 0x41E4): "Cranky_InstallSpriteCopy",  # copies Cranky_FarCopySprites_Code to $ccdc
    (0xF5, 0x41F3): "Cranky_ClearPalettes",
    (0xF5, 0x421D): "Cranky_FadeIn",
    (0xF5, 0x425E): "Cranky_FadeOut",
    (0xF5, 0x4291): "Cranky_UploadPalettes",
    (0xF5, 0x42AA): "Cranky_UploadPaletteBytes",
    (0xF5, 0x42B6): "Cranky_CopyOAM",  # 160 bytes to $fe00
    (0xF5, 0x449C): "Cranky_FarCopySprites_Code",  # runs at $ccdc
    (0xF5, 0x44E1): "Cranky_StartHBlankDMA",
    (0xF5, 0x44F3): "Cranky_RestoreBGMap",
    (0xF5, 0x4520): "Cranky_SetWRAMBank1",
    (0xF5, 0x4525): "Cranky_DimForPause",
    (0xF5, 0x4556): "Cranky_UndimAfterPause",
    (0xF5, 0x4588): "Cranky_DimBackground",
    (0xF5, 0x45C1): "Cranky_UndimBackground",
    (0xF5, 0x4613): "Cranky_ResetState",
    (0xF5, 0x46BA): "Cranky_ClearGradient",
    (0xF5, 0x46C5): "Cranky_SetUpLinkGame",  # by game number, jp table at $46d8
    (0xF5, 0x46D8): "Cranky_SetUpLink_BuddiesBeware",
    (0xF5, 0x46DB): "Cranky_SetUpLink_BarrelOKremlings",
    (0xF5, 0x46DE): "Cranky_SetUpLink_Wanted",
    (0xF5, 0x46E1): "Cranky_SetUpLink_KremlingKrackdown",
    (0xF5, 0x46E4): "Cranky_SetUpLink_KremlingsAndKongs",
    (0xF5, 0x46E7): "Cranky_SetUpLink_BuddiesBeware_Body",
    (0xF5, 0x4715): "Cranky_SetUpLink_BarrelOKremlings_Body",
    (0xF5, 0x4731): "Cranky_SetUpLink_Wanted_Body",
    (0xF5, 0x475F): "Cranky_SetUpLink_KremlingKrackdown_Body",
    (0xF5, 0x478A): "Cranky_SetUpLink_KremlingsAndKongs_Body",
    (0xF5, 0x47B3): "Cranky_SetUpGame",  # by game number, jp table at $47c6
    (0xF5, 0x47C6): "Cranky_SetUp_BuddiesBeware",
    (0xF5, 0x47C9): "Cranky_SetUp_BarrelOKremlings",
    (0xF5, 0x47CC): "Cranky_SetUp_Wanted",
    (0xF5, 0x47CF): "Cranky_SetUp_KremlingKrackdown",
    (0xF5, 0x47D2): "Cranky_SetUp_KremlingsAndKongs",
    (0xF5, 0x47D5): "Cranky_SetUp_GalleonGunner",
    (0xF5, 0x47D8): "Cranky_SetUp_BuddiesBeware_Body",
    (0xF5, 0x4806): "Cranky_SetUp_BarrelOKremlings_Body",
    (0xF5, 0x4831): "Cranky_SetUp_Wanted_Body",
    (0xF5, 0x486E): "Cranky_SetUp_KremlingKrackdown_Body",
    (0xF5, 0x48A3): "Cranky_SetUp_KremlingsAndKongs_Body",
    (0xF5, 0x48D6): "Cranky_SetUp_GalleonGunner_Body",
    (0xF5, 0x4950): "Cranky_LoadBackground",  # the game's picture and song from CrankyBackgrounds
    (0xF5, 0x4978): "Cranky_LoadFont",
    (0xF5, 0x49A5): "Cranky_DrawScreen",
    (0xF5, 0x4A3E): "Cranky_GalleonGunner_SetGradient",
    (0xFE, 0x4662): "Cranky_WaitLineAndUpdateSound",  # waits for line $82, then FE_UpdateSound
    (0xFE, 0x77B0): "Cranky_UpdateTileAnims",
    (0xFE, 0x44B9): "Cranky_EndEffect_BuddiesBeware",
    (0xFE, 0x44BC): "Cranky_EndEffect_BarrelOKremlings",
    (0xFE, 0x44BF): "Cranky_EndEffect_Wanted",
    (0xFE, 0x44C2): "Cranky_EndEffect_KremlingKrackdown",
    (0xFE, 0x44C5): "Cranky_EndEffect_KremlingsAndKongs",
    (0xFE, 0x44C8): "Cranky_EndEffect_GalleonGunner",
    (0xFE, 0x4570): "Cranky_EndTally_BuddiesBeware",
    (0xFE, 0x4573): "Cranky_EndTally_BarrelOKremlings",
    (0xFE, 0x4576): "Cranky_EndTally_Wanted",
    (0xFE, 0x4579): "Cranky_EndTally_KremlingKrackdown",
    (0xFE, 0x457C): "Cranky_EndTally_KremlingsAndKongs",
    (0xFE, 0x457F): "Cranky_EndTally_GalleonGunner",
    (0xFE, 0x47FB): "Cranky_Shoot_BuddiesBeware",
    (0xFE, 0x47FE): "Cranky_Shoot_BarrelOKremlings",
    (0xFE, 0x4801): "Cranky_Shoot_Wanted",
    (0xFE, 0x4804): "Cranky_Shoot_KremlingKrackdown",
    (0xFE, 0x4807): "Cranky_Shoot_KremlingsAndKongs",
    (0xFE, 0x480A): "Cranky_Shoot_GalleonGunner",
    (0xFE, 0x4BA7): "Cranky_LinkShoot_BuddiesBeware",
    (0xFE, 0x4BAA): "Cranky_LinkShoot_BarrelOKremlings",
    (0xFE, 0x4BAD): "Cranky_LinkShoot_Wanted",
    (0xFE, 0x4BB0): "Cranky_LinkShoot_KremlingKrackdown",
    (0xFE, 0x4BB3): "Cranky_LinkShoot_KremlingsAndKongs",
    (0xFE, 0x4E38): "Cranky_LinkHit_BuddiesBeware",
    (0xFE, 0x4E3B): "Cranky_LinkHit_BarrelOKremlings",
    (0xFE, 0x4E3E): "Cranky_LinkHit_Wanted",
    (0xFE, 0x4E41): "Cranky_LinkHit_KremlingKrackdown",
    (0xFE, 0x4E44): "Cranky_LinkHit_KremlingsAndKongs",
    (0xFE, 0x4FE4): "Cranky_Reload_BuddiesBeware",
    (0xFE, 0x4FE7): "Cranky_Reload_BarrelOKremlings",
    (0xFE, 0x4FEA): "Cranky_Reload_Wanted",
    (0xFE, 0x4FED): "Cranky_Reload_KremlingKrackdown",
    (0xFE, 0x4FF0): "Cranky_Reload_KremlingsAndKongs",
    (0xFE, 0x4FF3): "Cranky_Reload_GalleonGunner",
    (0xFE, 0x50AC): "Cranky_UpdateTargets_BuddiesBeware",
    (0xFE, 0x50AF): "Cranky_UpdateTargets_BarrelOKremlings",
    (0xFE, 0x50B2): "Cranky_UpdateTargets_Wanted",
    (0xFE, 0x50B5): "Cranky_UpdateTargets_KremlingKrackdown",
    (0xFE, 0x50B8): "Cranky_UpdateTargets_KremlingsAndKongs",
    (0xFE, 0x50BB): "Cranky_UpdateTargets_GalleonGunner",
    (0xFE, 0x55C1): "Cranky_SetAmmoIcon_BuddiesBeware",
    (0xFE, 0x55C3): "Cranky_SetAmmoIcon_BarrelOKremlings",
    (0xFE, 0x55C5): "Cranky_SetAmmoIcon_Wanted",
    (0xFE, 0x55C7): "Cranky_SetAmmoIcon_KremlingKrackdown",
    (0xFE, 0x55C9): "Cranky_SetAmmoIcon_KremlingsAndKongs",
    (0xFE, 0x6946): "Cranky_Spawn_BuddiesBeware",
    (0xFE, 0x6949): "Cranky_Spawn_BarrelOKremlings",
    (0xFE, 0x694C): "Cranky_Spawn_Wanted",
    (0xFE, 0x694F): "Cranky_Spawn_KremlingKrackdown",
    (0xFE, 0x6952): "Cranky_Spawn_KremlingsAndKongs",
    (0xFE, 0x6955): "Cranky_Spawn_GalleonGunner",
    (0xFE, 0x5CD8): "Cranky_ActorType00",
    (0xFE, 0x5CDB): "Cranky_ActorType01",
    (0xFE, 0x5CDE): "Cranky_ActorType02",
    (0xFE, 0x5CE1): "Cranky_ActorType03",
    (0xFE, 0x5CE4): "Cranky_ActorType04",
    (0xFE, 0x5CE7): "Cranky_ActorType05",
    (0xFE, 0x5CEA): "Cranky_ActorType06",
    (0xFE, 0x5CED): "Cranky_ActorType07",
    (0xFE, 0x5CF0): "Cranky_ActorType08",
    (0xFE, 0x5CF3): "Cranky_ActorType09",
    (0xFE, 0x5CF6): "Cranky_ActorType10",
    (0xFE, 0x5CF9): "Cranky_ActorType11",
    (0xFE, 0x5CFC): "Cranky_ActorType12",
    (0xFE, 0x5CFF): "Cranky_ActorType13",
    (0xFE, 0x5D02): "Cranky_ActorType14",
    (0xFE, 0x5D05): "Cranky_ActorType15",
    (0xFE, 0x5D08): "Cranky_ActorType16",
    (0xFE, 0x5D0B): "Cranky_ActorType17",
    (0xFE, 0x5D0E): "Cranky_ActorType18",
    (0xFE, 0x640E): "Cranky_Type18Step00",
    (0xFE, 0x6411): "Cranky_Type18Step01",
    (0xFE, 0x6414): "Cranky_Type18Step02",
    (0xFE, 0x6417): "Cranky_Type18Step03",
    (0xFE, 0x641A): "Cranky_Type18Step04",
    (0xFE, 0x641D): "Cranky_Type18Step05",
    (0xFE, 0x6420): "Cranky_Type18Step06",
    (0xFE, 0x6423): "Cranky_Type18Step07",
    (0xFE, 0x6426): "Cranky_Type18Step08",
    (0xFE, 0x6429): "Cranky_Type18Step09",
    (0xFE, 0x642C): "Cranky_Type18Step10",
    (0xFE, 0x642F): "Cranky_Type18Step11",
    (0xFE, 0x6432): "Cranky_Type18Step12",
    (0xFE, 0x6435): "Cranky_Type18Step13",
    (0xFE, 0x6438): "Cranky_Type18Step14",
    (0xFE, 0x643B): "Cranky_Type18Step15",
    (0xFE, 0x643E): "Cranky_Type18Step16",
    (0xFE, 0x6441): "Cranky_Type18Step17",
    (0xFE, 0x6444): "Cranky_Type18Step18",
    (0xFE, 0x6447): "Cranky_Type18Step19",
    (0xFE, 0x644A): "Cranky_Type18Step20",
    (0xFE, 0x644D): "Cranky_Type18Step21",
    (0xFE, 0x6450): "Cranky_Type18Step22",
    (0xFE, 0x6453): "Cranky_Type18Step23",
    (0xFE, 0x6456): "Cranky_Type18Step24",
    (0xFE, 0x6459): "Cranky_Type18Step25",
    (0xFE, 0x645C): "Cranky_Type18Step26",
    (0xFE, 0x645F): "Cranky_Type18Step27",
    (0xFE, 0x6462): "Cranky_Type18Step28",
    (0xFE, 0x6465): "Cranky_Type18Step29",
    (0xFE, 0x6468): "Cranky_Type18Step30",
    (0xFE, 0x646B): "Cranky_Type18Step31",
    (0xFE, 0x646E): "Cranky_Type18Step32",
    (0xFE, 0x6471): "Cranky_Type18Step33",
    (0xFE, 0x6474): "Cranky_Type18Step34",
    (0xFE, 0x6477): "Cranky_Type18Step35",
    (0xFE, 0x647A): "Cranky_Type18Step36",
    (0xFE, 0x647D): "Cranky_Type18Step37",
    (0xFE, 0x6480): "Cranky_Type18Step38",
    (0xFE, 0x6483): "Cranky_Type18Step39",
    (0xFE, 0x6486): "Cranky_Type18Step40",
    (0xFE, 0x6489): "Cranky_Type18Step41",
    (0xFE, 0x648C): "Cranky_Type18Step42",
    (0xFE, 0x648F): "Cranky_Type18Step43",
    (0xFE, 0x6492): "Cranky_Type18Step44",
    (0xFE, 0x6495): "Cranky_Type18Step45",
    (0xFE, 0x6498): "Cranky_Type18Step46",
    (0xFE, 0x649B): "Cranky_Type18Step47",
    (0xFE, 0x649E): "Cranky_Type18Step48",
    (0xFE, 0x64A1): "Cranky_Type18Step49",
    (0xFE, 0x64A4): "Cranky_Type18Step50",
    (0xFE, 0x64A7): "Cranky_Type18Step51",
    (0xFE, 0x64AA): "Cranky_Type18Step52",
    (0xFE, 0x64AD): "Cranky_Type18Step53",
    (0xFE, 0x64B0): "Cranky_Type18Step54",
    (0xFE, 0x64B3): "Cranky_Type18Step55",
    (0xFE, 0x64B6): "Cranky_Type18Step56",
    (0xFE, 0x682F): "Cranky_MoveActorDir0",
    (0xFE, 0x6831): "Cranky_MoveActorDir1",
    (0xFE, 0x6833): "Cranky_MoveActorDir2",
    (0xFE, 0x6835): "Cranky_MoveActorDir3",
    (0xFE, 0x6837): "Cranky_MoveActorDir4",
    (0xFE, 0x6839): "Cranky_MoveActorDir5",
    (0xFE, 0x683B): "Cranky_MoveActorDir6",
    (0xFE, 0x5112): "Cranky_TestBitN_0",
    (0xFE, 0x514D): "Cranky_ResBitN_0",
    (0xFE, 0x5188): "Cranky_SetBitN_0",
    (0xFE, 0x5114): "Cranky_TestBitN_1",
    (0xFE, 0x514F): "Cranky_ResBitN_1",
    (0xFE, 0x518A): "Cranky_SetBitN_1",
    (0xFE, 0x5116): "Cranky_TestBitN_2",
    (0xFE, 0x5151): "Cranky_ResBitN_2",
    (0xFE, 0x518C): "Cranky_SetBitN_2",
    (0xFE, 0x5118): "Cranky_TestBitN_3",
    (0xFE, 0x5153): "Cranky_ResBitN_3",
    (0xFE, 0x518E): "Cranky_SetBitN_3",
    (0xFE, 0x511A): "Cranky_TestBitN_4",
    (0xFE, 0x5155): "Cranky_ResBitN_4",
    (0xFE, 0x5190): "Cranky_SetBitN_4",
    (0xFE, 0x511C): "Cranky_TestBitN_5",
    (0xFE, 0x5157): "Cranky_ResBitN_5",
    (0xFE, 0x5192): "Cranky_SetBitN_5",
    (0xFE, 0x511E): "Cranky_TestBitN_6",
    (0xFE, 0x5159): "Cranky_ResBitN_6",
    (0xFE, 0x5194): "Cranky_SetBitN_6",
    # --- Crosshair Cranky, bank $FE: the game. Actors are 32 slots of WRAM arrays (type $db00, x $db20,
    #     y $db40, flags $db60 ...); targets are 8 slots ($cbdc state, $cbe4 timer); score is BCD at
    #     $cbf1-$cbf3; shots left $cbee; game number [$cbbf]
    (0xFE, 0x40C4): "Cranky_MainLoop",
    (0xFE, 0x41CB): "Cranky_EndingFrame",  # the frame loop while the game winds down
    (0xFE, 0x4221): "Cranky_GalleonGunner_CheckLost",
    (0xFE, 0x4248): "Cranky_CheckAllTargetsDown",
    (0xFE, 0x42A0): "Cranky_BarrelOKremlings_UseBarrel",
    (0xFE, 0x42AE): "Cranky_CheckGameOver",  # time up: tally, fade out, results
    (0xFE, 0x4486): "Cranky_GetScores",
    (0xFE, 0x44A5): "Cranky_EndEffect",  # by game number, jp table at $44b9
    (0xFE, 0x44CB): "Cranky_GalleonGunner_EndEffectBody",
    (0xFE, 0x455C): "Cranky_EndTally",  # by game number, jp table at $4570
    (0xFE, 0x4582): "Cranky_TallyBonus",  # counts the bonus into the score
    (0xFE, 0x4609): "Cranky_Nop",
    (0xFE, 0x460A): "Cranky_AreActorsGone",
    (0xFE, 0x461B): "Cranky_TallyFrame",
    (0xFE, 0x4646): "Cranky_IsTallyDone",
    (0xFE, 0x466C): "Cranky_Input",  # Start pauses, the d-pad moves between targets, A shoots, B reloads
    (0xFE, 0x46D1): "Cranky_CursorUp",  # to the target's up neighbour (byte 2 of its record)
    (0xFE, 0x46FB): "Cranky_CursorDown",
    (0xFE, 0x4725): "Cranky_CursorLeft",
    (0xFE, 0x4753): "Cranky_CursorRight",
    (0xFE, 0x4781): "Cranky_AutoRepeatLeftRight",
    (0xFE, 0x479C): "Cranky_RepeatLeft",
    (0xFE, 0x47B0): "Cranky_RepeatRight",
    (0xFE, 0x47C7): "Cranky_Shoot",  # A: uses a shot, then the game's hit routine (jp table at $47fb)
    (0xFE, 0x480D): "Cranky_Shoot_BuddiesBeware_Body",
    (0xFE, 0x484B): "Cranky_Shoot_BarrelOKremlings_Body",
    (0xFE, 0x48BE): "Cranky_Shoot_Wanted_Body",
    (0xFE, 0x4946): "Cranky_RemoveActor",
    (0xFE, 0x49C6): "Cranky_Shoot_Kremlings_Body",  # Kremling Krackdown and Kremlings and Kongs
    (0xFE, 0x4A6D): "Cranky_Shoot_GalleonGunner_Body",
    (0xFE, 0x4AEC): "Cranky_SpawnHitEffect",
    (0xFE, 0x4BB6): "Cranky_LinkShoot_BuddiesBeware_Body",
    (0xFE, 0x4BF1): "Cranky_LinkShoot_BarrelOKremlings_Body",
    (0xFE, 0x4C5E): "Cranky_LinkShoot_Wanted_Body",
    (0xFE, 0x4CD7): "Cranky_RemoveActorLink",
    (0xFE, 0x4D57): "Cranky_LinkShoot_Kremlings_Body",
    (0xFE, 0x4DFE): "Cranky_LinkReceiveShot",
    (0xFE, 0x4E47): "Cranky_LinkHit_BuddiesBeware_Body",
    (0xFE, 0x4E6C): "Cranky_LinkHit_BarrelOKremlings_Body",
    (0xFE, 0x4E9C): "Cranky_LinkHit_Wanted_Body",
    (0xFE, 0x4ECE): "Cranky_RemoveActorLinkHit",
    (0xFE, 0x4F4E): "Cranky_LinkHit_Kremlings_Body",
    (0xFE, 0x4FD0): "Cranky_Reload",  # B, by game number (jp table at $4fe4)
    (0xFE, 0x4FF6): "Cranky_Reload_BuddiesBeware_Body",
    (0xFE, 0x5024): "Cranky_ReloadOne",
    (0xFE, 0x5045): "Cranky_ReloadFull",  # four shots
    (0xFE, 0x5065): "Cranky_GetTargetRecord",  # this player's target [$cbc0] in the game's position list ($789b)
    (0xFE, 0x5081): "Cranky_GetOtherTargetRecord",  # the other player's, in link play
    (0xFE, 0x509D): "Cranky_UpdateTargets",  # by game number, jp table at $50ac
    (0xFE, 0x50BE): "Cranky_UpdateTargets_BuddiesBeware_Body",
    (0xFE, 0x5106): "Cranky_UpdateTargets_None",
    (0xFE, 0x5107): "Cranky_TestBitN",
    (0xFE, 0x5120): "Cranky_TestBitN_Body",
    (0xFE, 0x5142): "Cranky_ResBitN",
    (0xFE, 0x515B): "Cranky_ResBitN_Body",
    (0xFE, 0x517D): "Cranky_SetBitN",
    (0xFE, 0x5196): "Cranky_SetBitN_Body",
    (0xFE, 0x51B8): "Cranky_DrawCrosshair",
    (0xFE, 0x51EF): "Cranky_DrawCrosshairBlinking",
    (0xFE, 0x5235): "Cranky_DrawCrosshairAt",
    (0xFE, 0x5289): "Cranky_BeginOAM",
    (0xFE, 0x52A5): "Cranky_SwapTileBuffer",
    (0xFE, 0x52DA): "Cranky_SwapTileBuffer_B",
    (0xFE, 0x530F): "Cranky_SwapTileBuffer_A",
    (0xFE, 0x531A): "Cranky_CopyOAMBuffer",  # $c000 -> $cb00
    (0xFE, 0x5332): "Cranky_ClearOAMTileBank",
    (0xFE, 0x5341): "Cranky_ShiftOAMTiles",
    (0xFE, 0x5354): "Cranky_AnimateBackgroundTiles",  # CrankyTileAnimTable ($79cf)
    (0xFE, 0x541C): "Cranky_DrawAmmo",
    (0xFE, 0x5457): "Cranky_CountTargetsUp",
    (0xFE, 0x5474): "Cranky_FlashScore",
    (0xFE, 0x5494): "Cranky_SubtractPoints",
    (0xFE, 0x54D5): "Cranky_DrawScoreNow",
    (0xFE, 0x54D8): "Cranky_DrawScore",
    (0xFE, 0x5597): "Cranky_DigitBlinkDown",
    (0xFE, 0x55A1): "Cranky_DigitRollUp",
    (0xFE, 0x55B4): "Cranky_SetAmmoIcon",  # by game number, jr table at $55c1
    (0xFE, 0x55CB): "Cranky_SetAmmoIcon_Common",
    (0xFE, 0x55D8): "Cranky_DrawTimer",
    (0xFE, 0x560C): "Cranky_CheckTimeUp",
    (0xFE, 0x5645): "Cranky_CountDownTime",
    (0xFE, 0x566D): "Cranky_ResumeFromPause",
    (0xFE, 0x5703): "Cranky_Pause",  # Start: the pause menu (CrankyPauseText): continue / quit
    (0xFE, 0x580B): "Cranky_PauseLoop",
    (0xFE, 0x582E): "Cranky_PauseNext",
    (0xFE, 0x5844): "Cranky_PausePrevious",
    (0xFE, 0x585A): "Cranky_PauseShowCursor",
    (0xFE, 0x5892): "Cranky_PauseHideCursor",
    (0xFE, 0x58CA): "Cranky_PauseSetItem",
    (0xFE, 0x58DF): "Cranky_DrawPauseText",
    (0xFE, 0x5944): "Cranky_SetPausePalettes",
    (0xFE, 0x595A): "Cranky_ClearPauseScreen",
    (0xFE, 0x599A): "Cranky_UploadPauseScreen",
    (0xFE, 0x59CC): "Cranky_PauseWait",
    (0xFE, 0x59D3): "Cranky_FlashScreen",
    (0xFE, 0x5A11): "Cranky_CheckQuit",
    (0xFE, 0x5A1D): "Cranky_HandleRemoteEvent",  # link play: what the other Game Boy did
    (0xFE, 0x5A3F): "Cranky_RemoteEvent_ActorShot",
    (0xFE, 0x5AB8): "Cranky_RemoteEvent_TargetHit",
    (0xFE, 0x5ADF): "Cranky_DrawTargets",
    (0xFE, 0x5BDA): "Cranky_DrawTarget",
    (0xFE, 0x5C0D): "Cranky_LoadPalettes",  # the game's eight sprite palettes from $7ba9
    (0xFE, 0x5C3D): "Cranky_LoadPauseFont",
    (0xFE, 0x5CB2): "Cranky_RunActors",  # each of the 32 actors by type, jp table at $5cd8
    (0xFE, 0x5CCE): "Cranky_NextActor",
    (0xFE, 0x5D11): "Cranky_Actor_BuddiesBeware_Pop",  # types 1-3
    (0xFE, 0x5D70): "Cranky_Actor_BuddiesBeware_Run",  # type 4
    (0xFE, 0x5DB0): "Cranky_Actor_BuddiesBeware_Shot",
    (0xFE, 0x5E43): "Cranky_Actor_BuddiesBeware_Move",
    (0xFE, 0x5EE7): "Cranky_Actor_BuddiesBeware_AtEdge",
    (0xFE, 0x5F19): "Cranky_Actor_Barrel",  # type 5: Barrel O'Kremlings and Wanted
    (0xFE, 0x5F9D): "Cranky_Actor_Type6",
    (0xFE, 0x5FC4): "Cranky_Actor_Kremling",  # type 8: Kremling Krackdown, Kremlings and Kongs
    (0xFE, 0x6041): "Cranky_Actor_Kremling_Hide",  # type 9
    (0xFE, 0x6104): "Cranky_Actor_Kremling_Appear",  # type 7
    (0xFE, 0x6133): "Cranky_Actor_Kong_Hide",  # type 11: Kremlings and Kongs
    (0xFE, 0x61B3): "Cranky_Actor_Kong",  # type 10
    (0xFE, 0x61D3): "Cranky_Actor_Kong_Appear",  # type 12
    (0xFE, 0x6249): "Cranky_Actor_Galleon13",
    (0xFE, 0x624C): "Cranky_Actor_GalleonShip",  # type 14
    (0xFE, 0x62FC): "Cranky_Actor_Type15",
    (0xFE, 0x62FF): "Cranky_Actor_GalleonSink",  # type 16
    (0xFE, 0x631C): "Cranky_Actor_GalleonSpawnShot",
    (0xFE, 0x63BF): "Cranky_Actor_GalleonCannonball",  # type 17
    (0xFE, 0x63FA): "Cranky_Actor_Type18",  # steps through the jp table at $640e
    (0xFE, 0x64B9): "Cranky_Type18_Remove",
    (0xFE, 0x64C7): "Cranky_Type18_MoveUp",
    (0xFE, 0x64F2): "Cranky_Type18_MoveDown",
    (0xFE, 0x6514): "Cranky_Type18_WaitTurn",
    (0xFE, 0x6554): "Cranky_Type18_Wait",
    (0xFE, 0x656F): "Cranky_Type18_Count",
    (0xFE, 0x658A): "Cranky_Type18_PlaceCentre",
    (0xFE, 0x65E7): "Cranky_Type18_PlaceLeft",
    (0xFE, 0x6644): "Cranky_Type18_PlaceRight",
    (0xFE, 0x66A1): "Cranky_Type18_Pause",
    (0xFE, 0x66FF): "Cranky_Type18_ReachedTop",
    (0xFE, 0x6733): "Cranky_Type18_ReachedBottom",
    (0xFE, 0x676A): "Cranky_Type18_FlipOn",
    (0xFE, 0x677E): "Cranky_Type18_FlipOff",
    (0xFE, 0x6792): "Cranky_AnimateActor",
    (0xFE, 0x67F3): "Cranky_MoveActor",  # by its speed and direction (jr table at $682f)
    (0xFE, 0x681D): "Cranky_MoveActorStep",
    (0xFE, 0x683D): "Cranky_MoveActorDir_Body",
    (0xFE, 0x68B3): "Cranky_DrawActors",
    (0xFE, 0x68D8): "Cranky_DrawActor",
    (0xFE, 0x6910): "Cranky_FindFreeActor",
    (0xFE, 0x6937): "Cranky_Spawn",  # by game number, jp table at $6946
    (0xFE, 0x696A): "Cranky_Spawn_BuddiesBeware_Body",
    (0xFE, 0x6A0E): "Cranky_BuddiesBeware_CountActors",
    (0xFE, 0x6A49): "Cranky_BuddiesBeware_SpawnBuddy",
    (0xFE, 0x6AA8): "Cranky_BuddiesBeware_SpawnKremling",
    (0xFE, 0x6B06): "Cranky_BuddiesBeware_SpawnOther",
    (0xFE, 0x6BDC): "Cranky_InitActor",
    (0xFE, 0x6C5A): "Cranky_Spawn_BarrelOKremlings_Body",
    (0xFE, 0x6CD5): "Cranky_BarrelOKremlings_SpawnBarrel",
    (0xFE, 0x6D97): "Cranky_Spawn_Wanted_Body",
    (0xFE, 0x6ECB): "Cranky_Wanted_ShowPoster",  # the face to look for
    (0xFE, 0x6F6A): "Cranky_Wanted_PosterFrames",
    (0xFE, 0x6F91): "Cranky_Wanted_SpawnSuspect",
    (0xFE, 0x6FA4): "Cranky_Wanted_SpawnWanted",
    (0xFE, 0x6FB0): "Cranky_Wanted_SpawnRandom",
    (0xFE, 0x7084): "Cranky_Spawn_Kremlings_Body",
    (0xFE, 0x71B0): "Cranky_Kremlings_SpeedUp",
    (0xFE, 0x71D9): "Cranky_Kremlings_SpawnWave",
    (0xFE, 0x7303): "Cranky_Spawn_GalleonGunner_Body",
    (0xFE, 0x73A9): "Cranky_GalleonGunner_SpawnShip",
    (0xFE, 0x7498): "Cranky_SaveRandomState",
    (0xFE, 0x74B3): "Cranky_NextWave",
    (0xFE, 0x74C2): "Cranky_LinkPacket_Code",  # copied to $cc94 for link play
    (0xFE, 0x74EA): "Cranky_LinkSendPacket_Code",
    (0xFE, 0x750A): "Cranky_LinkExchangeByte_Code",
    (0xFE, 0x7540): "Cranky_LinkStart_Code",
    (0xFE, 0x755A): "Cranky_InstallLinkRoutines",  # $761b -> $cc0e, $74c2 -> $cc94
    (0xFE, 0x76A4): "Cranky_SetSerialJump",
    (0xFE, 0x76B8): "Cranky_EnableSerial",
    (0xFE, 0x76C4): "Cranky_LinkSendState",
    (0xFE, 0x7740): "Cranky_LinkReceiveState",
    (0xFE, 0x5A39): "Cranky_RemoteEvent0",
    (0xFE, 0x5A3C): "Cranky_RemoteEvent1",
    # --- Funky's Fishing (banks $50-$52). WRAM: joypad held/pressed $dd6f/$dd70; three characters
    #     ($dd81 Funky, $dd8d the rod, $dd99 the hook: anim records of 12 bytes); fish in 8 slots of
    #     16 bytes at $dda8 ([$de28] in use); 8 slots of 12 bytes at $de2c for hooked fish ([$de8c]);
    #     score BCD $de9b-$de9e, points to add $de9f; line meter [$deb1] (0-$4f)
    (0x50, 0x4000): "Fishing_Start",  # far-jumped to from the front end: saves the stack, installs the runtime, loads the screen
    (0x50, 0x4091): "Fishing_LinkGame",  # set-up and loop for two players; with no partner ([$ffc2] = $ff) the one-player loop
    (0x50, 0x41B6): "Fishing_OnePlayerGame",
    (0x50, 0x429C): "Fishing_InstallRuntime",  # FishingRuntime ($51:42f4) -> $cb00
    (0x50, 0x42BE): "Fishing_LinkFrame",
    (0x50, 0x43AC): "Fishing_LinkDrawCharacters",
    (0x50, 0x43DF): "Fishing_LinkFinishOAM",
    (0x50, 0x43EA): "Fishing_OnePlayerFrame",
    (0x50, 0x444F): "Fishing_DrawCharacters",
    (0x50, 0x4463): "Fishing_StartFanfare",
    (0x50, 0x4479): "Fishing_CheckScore500",
    (0x50, 0x44A7): "Fishing_LinkCheckEnd",
    (0x50, 0x44DC): "Fishing_LinkDrainMeter",
    (0x50, 0x4571): "Fishing_InitSound",
    (0x50, 0x45F8): "Fishing_SetSTATHandler",
    (0x50, 0x460A): "Fishing_InitScroll",  # the water drifts
    (0x50, 0x4645): "Fishing_InitCharacters",  # Funky (anim $0d), the rod (9), the hook ($0e)
    (0x50, 0x46B7): "Fishing_ClearCatchList",
    (0x50, 0x46D6): "Fishing_InitFish",
    (0x50, 0x4707): "Fishing_InitLevels",  # score thresholds per level ($defa)
    (0x50, 0x4764): "Fishing_InitWaterAnim",
    (0x50, 0x478D): "Fishing_Init",
    (0x50, 0x492F): "Fishing_LinkSendState",  # score and meter to the other Game Boy
    (0x50, 0x4981): "Fishing_LinkReceiveState",
    (0x50, 0x49B3): "Fishing_LinkApplyReceived",
    (0x50, 0x49F7): "Fishing_LinkCheckPacket",  # checksum of the 14 bytes received
    (0x50, 0x4A24): "Fishing_LinkVBlankWork",
    (0x50, 0x4A67): "Fishing_VBlankWork",  # OAM DMA from the back buffer, HUD rows, water tiles
    (0x50, 0x4AB6): "Fishing_CopyOAM",
    (0x50, 0x4CA5): "Fishing_UploadMeterRow",
    (0x50, 0x4CD5): "Fishing_UploadLinkMeterRow",
    (0x50, 0x4D05): "Fishing_UploadScoreRow",
    (0x50, 0x4D43): "Fishing_LinkUploadScoreRow",
    (0x50, 0x4D6D): "Fishing_UploadComboRow",
    (0x50, 0x4D8E): "Fishing_AnimateAll",
    (0x50, 0x4DAA): "Fishing_MoveRod",
    (0x50, 0x4E01): "Fishing_RodFollowScroll",
    (0x50, 0x4E19): "Fishing_MoveHook",
    (0x50, 0x4E95): "Fishing_HookFollowScroll",
    (0x50, 0x4EAC): "Fishing_ScrollWater",
    (0x50, 0x4F3F): "Fishing_AnimateFish",
    (0x50, 0x4F6A): "Fishing_UpdateHookedFish",
    (0x50, 0x4F97): "Fishing_UpdateHookedOne",
    (0x50, 0x5002): "Fishing_StopRod",
    (0x50, 0x500A): "Fishing_MoveFish",
    (0x50, 0x507A): "Fishing_LinkComboTimer",
    (0x50, 0x509A): "Fishing_LinkStartCombo",
    (0x50, 0x50C2): "Fishing_LinkDrawComboSprite",
    (0x50, 0x50FC): "Fishing_Return50FC",
    (0x50, 0x50FD): "Fishing_DrawFish",
    (0x50, 0x5149): "Fishing_DrawFish_Next",
    (0x50, 0x5157): "Fishing_DrawFunky",
    (0x50, 0x518C): "Fishing_DrawRod",
    (0x50, 0x51C1): "Fishing_Return51C1",
    (0x50, 0x51C2): "Fishing_DrawHook",
    (0x50, 0x51F7): "Fishing_Return51F7",
    (0x50, 0x522A): "Fishing_HookPhysics",
    (0x50, 0x532B): "Fishing_ReelInHookedFish",
    (0x50, 0x5369): "Fishing_ReelInOne",  # a fish on the hook rises with it; at the top it is caught
    (0x50, 0x549F): "Fishing_IsInRect",
    (0x50, 0x54C4): "Fishing_ReelHook",  # the hook moves towards its target depth
    (0x50, 0x55AF): "Fishing_Input",  # A casts (and reels), B the combo attack
    (0x50, 0x56D4): "Fishing_CheckHookOnFish",
    (0x50, 0x5734): "Fishing_HookFish",
    (0x50, 0x57A2): "Fishing_FishHitbox",  # by fish type 1-6
    (0x50, 0x580B): "Fishing_FindFreeFishSlot",
    (0x50, 0x581C): "Fishing_SetFishType",  # speed and animation by type 1-6
    (0x50, 0x5881): "Fishing_SpawnFish",  # random side and depth
    (0x50, 0x58FF): "Fishing_RemoveFish",
    (0x50, 0x5911): "Fishing_CheckNextLevel",  # score against the thresholds at $77f7
    (0x50, 0x59C4): "Fishing_Compare24",
    (0x50, 0x59E3): "Fishing_DrawMeter",  # [$deb1] / 8 full tiles
    (0x50, 0x5A1A): "Fishing_DrawLinkMeter",
    (0x50, 0x5A51): "Fishing_AddBonusPoints",
    (0x50, 0x5AF3): "Fishing_LinkShowCombo",
    (0x50, 0x5B12): "Fishing_ScoreCatch",  # points for the fish caught, combos, meter
    (0x50, 0x5CCF): "Fishing_PointsByType",
    (0x50, 0x5D70): "Fishing_AddToMeter",  # c, clamped to 0-$4f
    (0x50, 0x5D8E): "Fishing_CheckCombo",
    (0x50, 0x5DCA): "Fishing_ComboByCount",
    (0x50, 0x5E17): "Fishing_DrawComboText",
    (0x50, 0x5E90): "Fishing_ComboTextTimer",
    (0x50, 0x5EBA): "Fishing_StartHDMA",
    (0x50, 0x5ECA): "Fishing_PlayMeterSample",  # speech by the meter's level
    (0x50, 0x5F10): "Fishing_CheckEnd",
    (0x50, 0x5F98): "Fishing_AnimateWater",
    (0x50, 0x6010): "Fishing_UploadWaterTiles",
    (0x50, 0x6034): "Fishing_BlinkMessage",
    (0x50, 0x6086): "Fishing_FadeIn",
    (0x50, 0x609C): "Fishing_FadeOut",
    (0x50, 0x60AF): "Fishing_ClearRestOfOAM",
    (0x50, 0x60B9): "Fishing_SetAnim",  # anim b of FishingAnimTable for the record at hl ($52:4000)
    (0x50, 0x60D5): "Fishing_Return60D5",
    (0x50, 0x60D6): "Fishing_SetAnimKeepFrame",  # ($52:404b)
    (0x50, 0x60F2): "Fishing_Return60F2",
    (0x50, 0x60F3): "Fishing_ScaleWord",
    (0x50, 0x611B): "Fishing_ScaleWord2",
    (0x50, 0x614B): "Fishing_ScaleWord3",
    (0x50, 0x617E): "Fishing_ScaleWordRead",
    (0x50, 0x618A): "Fishing_SignedDifference",
    (0x50, 0x6198): "Fishing_ReadJoypad",  # hl = held, de = pressed; A+B+Select+Start resets
    (0x50, 0x61BC): "Fishing_FindButton",
    (0x50, 0x61C9): "Fishing_SetDoubleSpeed",
    (0x50, 0x61EB): "Fishing_ToggleCPUSpeed",
    (0x50, 0x6209): "Fishing_InitLCD",  # also copies the OAM DMA routine to $ff80
    (0x50, 0x6223): "Fishing_ClearWRAM",
    (0x50, 0x6231): "Fishing_ClearVRAM",
    (0x50, 0x6256): "Fishing_ClearHRAM",
    (0x50, 0x6261): "Fishing_ClearOAMBuffer",
    (0x50, 0x626C): "Fishing_OAMDMA_Code",  # runs at $ff80
    (0x50, 0x6276): "Fishing_HighestBitMask",
    (0x50, 0x62B1): "Fishing_RangeMask16",
    (0x50, 0x62C3): "Fishing_InitRandomFromDIV",
    (0x50, 0x62E8): "Fishing_InitRandom",  # the generator's 1 KB state from $7885
    (0x50, 0x630E): "Fishing_InitRandomIndices",
    (0x50, 0x631C): "Fishing_RandomSeedFromDIV",
    (0x50, 0x635B): "Fishing_RandomStep",  # lagged Fibonacci over $d96f, indices $d96d/$d96e
    (0x50, 0x639D): "Fishing_RandomRange",  # b <= result <= c
    (0x50, 0x63D4): "Fishing_RandomRange16",
    (0x50, 0x640A): "Fishing_SignedDifference2",
    (0x50, 0x6418): "Fishing_MultiplySigned",
    (0x50, 0x6498): "Fishing_Multiply16",
    (0x50, 0x64D4): "Fishing_Multiply8",
    (0x50, 0x6523): "Fishing_Divide",
    (0x50, 0x6561): "Fishing_IsWithin",
    (0x50, 0x657A): "Fishing_IsBelow",
    (0x50, 0x6585): "Fishing_CompareBCDE",
    (0x50, 0x658B): "Fishing_CompareBCHL",
    (0x50, 0x6591): "Fishing_CompareDEHL",
    (0x50, 0x6597): "Fishing_AddDEToBC",
    (0x50, 0x659E): "Fishing_SubDEFromBC",
    (0x50, 0x65A5): "Fishing_LoadPalette",
    (0x50, 0x65F2): "Fishing_ReadBGPalettes",
    (0x50, 0x66FC): "Fishing_UploadBGPalettes",
    (0x50, 0x6783): "Fishing_UploadOBJPalettes",
    (0x50, 0x6791): "Fishing_UploadOBJPalettesN",
    (0x50, 0x67A3): "Fishing_UploadBGPalettesN",
    (0x50, 0x67B5): "Fishing_MultiplyFade",
    (0x50, 0x67D8): "Fishing_ScalePalettes",
    (0x50, 0x6828): "Fishing_UnpackPalettes",
    (0x50, 0x6860): "Fishing_FadePalettes",  # from level h to l in b steps
    (0x50, 0x68E1): "Fishing_FadeAllPalettes",
    (0x50, 0x6996): "Fishing_SubClamped",
    (0x50, 0x69AE): "Fishing_AddClamped",
    (0x50, 0x69C5): "Fishing_AnimTimer",
    (0x50, 0x69DE): "Fishing_UpdateAnim",
    (0x50, 0x6A23): "Fishing_Return6A23",
    (0x50, 0x6A24): "Fishing_Animate",  # next frame of an anim record
    (0x50, 0x6B58): "Fishing_DrawPauseWindow",
    (0x50, 0x6BB6): "Fishing_DrawPauseText",
    (0x50, 0x6D19): "Fishing_LinkDrawPauseWindow",
    (0x50, 0x6D77): "Fishing_LinkDrawPauseText",
    (0x50, 0x6F2A): "Fishing_DrawPauseCursor",
    (0x50, 0x6FEB): "Fishing_LinkWaitForPartner",
    (0x50, 0x7061): "Fishing_Pause",  # Start: CONTINUE / QUIT
    (0x50, 0x70C8): "Fishing_LinkPause",
    (0x50, 0x7159): "Fishing_PauseInput",
    (0x50, 0x71C7): "Fishing_LinkPauseInput",
    (0x50, 0x724E): "Fishing_PartnerPaused",
    (0x50, 0x72C4): "Fishing_DimForPause",
    (0x50, 0x72EA): "Fishing_UndimAfterPause",
    (0x50, 0x730B): "Fishing_LinkDimForPause",
    (0x50, 0x7331): "Fishing_LinkUndimAfterPause",
    (0x50, 0x7352): "Fishing_PauseFade",
    (0x50, 0x7379): "Fishing_InitPause",
    (0x50, 0x7396): "Fishing_SetUpPauseText",  # FishingPauseText in the chosen language, through CharTileTable_50
    (0x50, 0x7686): "Fishing_TextToTiles",
    (0x51, 0x4000): "Fishing_LoadScreen",  # one-player screen ($6a90) or the two-player one ($6d60), palettes, box
    (0x51, 0x40AE): "Fishing_UploadScreenMap",
    (0x51, 0x410F): "Fishing_LoadTiles",
    (0x51, 0x41D6): "Fishing_StartHDMA_51",
    (0x51, 0x41E6): "Fishing_UploadBGPalettes_51",
    (0x51, 0x426D): "Fishing_UploadOBJPalettes_51",
    (0x52, 0x4000): "Fishing_SetAnimRecord",  # from FishingAnimTable
    (0x52, 0x404B): "Fishing_SetAnimRecordKeepFrame",
    (0x52, 0x4097): "Fishing_DrawAnimFrame",  # sprites and tiles of the record's current frame
    (0x52, 0x40BD): "Fishing_AllocOAM",
    (0x52, 0x40E9): "Fishing_AllocTileBuffer",
    (0x52, 0x4107): "Fishing_WriteSprites",
    (0x52, 0x413D): "Fishing_CopyFrameTiles",
    (0x52, 0x41A1): "Fishing_BeginFrame",  # resets the OAM and tile buffers (double-buffered by [$c8a4])
    (0x50, 0x5EA8): "Fishing_IsPointInBox",
}
