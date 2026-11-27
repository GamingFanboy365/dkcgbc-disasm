#!/usr/bin/env python3
"""Code that the game copies from ROM to RAM and runs there.

Each block is disassembled at the address it runs from. Its labels are
constants with RAM addresses (DEF ... EQU, listed before the block, and shown
as comments where they fall), and relative jumps are written as @ + offset,
so the bytes stay where they are in the ROM. (An RGBDS LOAD block would be
nicer, but the fishing program and the front end copy different code to
overlapping RAM, which the linker refuses.) Code is followed from entry points: the start of the block,
plus every address in its range that traced ROM code calls, jumps to or loads
into a register pair (return addresses pushed for the far-call trampolines).
Bytes no path reaches stay as db.

  python3 tools/ramcode.py [baserom.gbc]   prints each block
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sm83 import OPS, CB  # noqa: E402

FLOW_END = ("jp", "jr", "ret", "jphl", "stop")


def decode_at(buf, base, addr):
    """(text template, length, flow, imm, target) for the instruction at addr."""
    i = addr - base
    op = buf[i]
    if op == 0xCB:
        if i + 1 >= len(buf):
            return None
        return (CB[buf[i + 1]], 2, None, None, None)
    ent = OPS[op]
    if ent is None:
        return None
    tmpl, length, flow = ent
    if i + length > len(buf):
        return None
    if op == 0x10 and buf[i + 1] != 0:
        return None
    imm = target = None
    if "{n16}" in tmpl:
        imm = buf[i + 1] | buf[i + 2] << 8
        if flow in ("jp", "jpc", "call", "callc"):
            target = imm
    elif "{e8}" in tmpl:
        e = buf[i + 1]
        target = addr + 2 + (e - 256 if e >= 128 else e)
    elif "{n8}" in tmpl or "{a8}" in tmpl or "{s8}" in tmpl:
        imm = buf[i + 1]
    if flow == "rst":
        target = op & 0x38
    return tmpl, length, flow, imm, target


def trace(buf, base, entries):
    """Returns ({addr: decoded}, set of label addresses)."""
    insns, labels, todo = {}, set(), [e for e in entries if base <= e < base + len(buf)]
    labels.update(todo)
    while todo:
        a = todo.pop()
        while base <= a < base + len(buf) and a not in insns:
            d = decode_at(buf, base, a)
            if d is None:
                break
            if any(x in insns for x in range(a + 1, a + d[1])):
                break
            insns[a] = d
            tmpl, length, flow, imm, target = d
            if target is not None and flow not in ("rst",) and base <= target < base + len(buf):
                labels.add(target)
                todo.append(target)
            if flow in FLOW_END:
                break
            a += length
    return insns, labels


def lines(buf, base, entries, name_of, ext_name=None):
    """(label constants, assembly lines) for the block."""
    insns, labels = trace(buf, base, entries)
    out, a, end = [], base, base + len(buf)
    pending = []

    def flush():
        while pending:
            chunk = pending[:8]
            del pending[:8]
            out.append("\tdb " + ", ".join("$%02x" % v for v in chunk))
    while a < end:
        if a in labels:
            flush()
            out.append("; %s:" % name_of(a))
        if a in insns:
            flush()
            tmpl, length, flow, imm, target = insns[a]
            t = tmpl
            if "{n16}" in t:
                txt = None
                if target is not None and base <= target < end:
                    txt = name_of(target)
                elif ext_name:
                    txt = ext_name(imm, tmpl)
                t = t.replace("{n16}", txt or "$%04x" % imm)
            elif "{e8}" in t:
                t = t.replace("{e8}", "@ %+d" % (target - a) + (" ; %s" % name_of(target) if base <= target < end else ""))
            elif "{a8}" in t:
                t = t.replace("{a8}", (ext_name(0xFF00 | imm, "ldh") if ext_name else None) or "$ff%02x" % imm)
            elif "{n8}" in t:
                t = t.replace("{n8}", "$%02x" % imm)
            elif "{s8}" in t:
                t = t.replace("{s8}", "%d" % (imm - 256 if imm >= 128 else imm))
            out.append("\t" + t)
            if flow in FLOW_END:
                out.append("")
            a += length
        else:
            pending.append(buf[a - base])
            a += 1
    flush()
    return [(name_of(a), a) for a in sorted(labels)], out


def entries_from(t, rom, base, n):
    """Entry points into [base, base + n) from traced ROM code: jump and call
    targets, and addresses loaded into a register pair that is pushed next."""
    from tracer import off  # noqa: F401
    ents = {base}
    push_of = {0x01: 0xC5, 0x11: 0xD5, 0x21: 0xE5}
    for o, i in t.insns.items():
        if i.flow in ("jp", "jpc", "call", "callc") and i.target is not None and base <= i.target < base + n:
            ents.add(i.target)
        elif i.op in push_of and i.imm is not None and base <= i.imm < base + n:
            if o + 3 < len(rom) and rom[o + 3] == push_of[i.op]:
                ents.add(i.imm)
    return ents
