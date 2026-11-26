"""SM83 (Game Boy CPU) opcode tables used by the disassembler.

Each entry is (template, length, flow). Template placeholders:
  {n8}  immediate byte        {n16} immediate word
  {e8}  relative jump target  {a8}  ldh offset ($FF00+n)
  {s8}  signed byte (sp+e8)
Flow: None (falls through), 'jp', 'jr', 'call', 'ret', 'jphl', 'rst', 'stop'
plus a trailing 'c' for conditional forms (e.g. 'jpc', 'jrc', 'callc', 'retc').
"""

R8 = ["b", "c", "d", "e", "h", "l", "[hl]", "a"]
R16 = ["bc", "de", "hl", "sp"]
R16S = ["bc", "de", "hl", "af"]
CC = ["nz", "z", "nc", "c"]
ALU = ["add a, ", "adc a, ", "sub a, ", "sbc a, ", "and a, ", "xor a, ", "or a, ", "cp a, "]
ALU_SHORT = ["add a, ", "adc a, ", "sub ", "sbc a, ", "and ", "xor ", "or ", "cp "]

OPS = [None] * 256
CB = [None] * 256


def _build():
    o = OPS
    o[0x00] = ("nop", 1, None)
    o[0x08] = ("ld [{n16}], sp", 3, None)
    o[0x10] = ("stop", 2, "stop")
    o[0x18] = ("jr {e8}", 2, "jr")
    for i, c in enumerate(CC):
        o[0x20 + i * 8] = ("jr %s, {e8}" % c, 2, "jrc")
        o[0xC0 + i * 8] = ("ret %s" % c, 1, "retc")
        o[0xC2 + i * 8] = ("jp %s, {n16}" % c, 3, "jpc")
        o[0xC4 + i * 8] = ("call %s, {n16}" % c, 3, "callc")
    for i, r in enumerate(R16):
        o[0x01 + i * 16] = ("ld %s, {n16}" % r, 3, None)
        o[0x03 + i * 16] = ("inc %s" % r, 1, None)
        o[0x09 + i * 16] = ("add hl, %s" % r, 1, None)
        o[0x0B + i * 16] = ("dec %s" % r, 1, None)
    o[0x02] = ("ld [bc], a", 1, None)
    o[0x12] = ("ld [de], a", 1, None)
    o[0x22] = ("ld [hli], a", 1, None)
    o[0x32] = ("ld [hld], a", 1, None)
    o[0x0A] = ("ld a, [bc]", 1, None)
    o[0x1A] = ("ld a, [de]", 1, None)
    o[0x2A] = ("ld a, [hli]", 1, None)
    o[0x3A] = ("ld a, [hld]", 1, None)
    for i, r in enumerate(R8):
        o[0x04 + i * 8] = ("inc %s" % r, 1, None)
        o[0x05 + i * 8] = ("dec %s" % r, 1, None)
        o[0x06 + i * 8] = ("ld %s, {n8}" % r, 2, None)
    for i, m in enumerate(["rlca", "rrca", "rla", "rra", "daa", "cpl", "scf", "ccf"]):
        o[0x07 + i * 8] = (m, 1, None)
    for d in range(8):
        for s in range(8):
            op = 0x40 + d * 8 + s
            if op == 0x76:
                o[op] = ("halt", 1, None)
            else:
                o[op] = ("ld %s, %s" % (R8[d], R8[s]), 1, None)
    for i in range(8):
        for s in range(8):
            o[0x80 + i * 8 + s] = (ALU_SHORT[i] + R8[s], 1, None)
        o[0xC6 + i * 8] = (ALU_SHORT[i] + "{n8}", 2, None)
        o[0xC7 + i * 8] = ("rst ${:02x}".format(i * 8), 1, "rst")
    for i, r in enumerate(R16S):
        o[0xC1 + i * 16] = ("pop %s" % r, 1, None)
        o[0xC5 + i * 16] = ("push %s" % r, 1, None)
    o[0xC3] = ("jp {n16}", 3, "jp")
    o[0xC9] = ("ret", 1, "ret")
    o[0xD9] = ("reti", 1, "ret")
    o[0xCD] = ("call {n16}", 3, "call")
    o[0xE0] = ("ldh [{a8}], a", 2, None)
    o[0xF0] = ("ldh a, [{a8}]", 2, None)
    o[0xE2] = ("ldh [c], a", 1, None)
    o[0xF2] = ("ldh a, [c]", 1, None)
    o[0xEA] = ("ld [{n16}], a", 3, None)
    o[0xFA] = ("ld a, [{n16}]", 3, None)
    o[0xE8] = ("add sp, {s8}", 2, None)
    o[0xF8] = ("ld hl, sp + {s8}", 2, None)
    o[0xE9] = ("jp hl", 1, "jphl")
    o[0xF9] = ("ld sp, hl", 1, None)
    o[0xF3] = ("di", 1, None)
    o[0xFB] = ("ei", 1, None)
    # 0xCB prefix handled separately
    o[0xCB] = ("cb", 2, None)

    for i, m in enumerate(["rlc", "rrc", "rl", "rr", "sla", "sra", "swap", "srl"]):
        for s in range(8):
            CB[i * 8 + s] = "%s %s" % (m, R8[s])
    for i, m in enumerate(["bit", "res", "set"]):
        for b in range(8):
            for s in range(8):
                CB[0x40 + i * 0x40 + b * 8 + s] = "%s %d, %s" % (m, b, R8[s])


_build()
