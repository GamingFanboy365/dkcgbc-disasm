"""Object behaviour scripts in bank $0A ($7358-$7AF5).

Several object handlers in bank $0A step through a small byte-code script
whose pointer they keep in an object variable. Every interpreter shares the
same outline (see RunKritterScript):

  read a command byte; 0 = jump to the word that follows (a jump to $0000
  stops the script for the interpreters that check for it); other commands
  either continue with the next command or store the pointer and return
  until the handler calls the interpreter again; an unknown command stops.

The command sets differ per interpreter. Each entry below gives the
argument bytes ("b" byte, "w" word, "o" word naming an object initialiser
list) and a short description.

  python3 tools/objscripts.py [baserom.gbc]   prints the decoded scripts
"""
import sys

BANK, START, END = 0x0A, 0x7358, 0x7AF6

# interpreter -> (object variable holding the pointer, {command: (args, text)})
INTERPRETERS = {
    0x5B56: (0x32, {1: ("b", "wait"), 2: ("b", "walk (Anim_04_4947)"), 3: ("w", "move (Kritter_JumpStart)"),
                    4: ("", "call Player_ReverseX"), 5: ("", "save position"), 6: ("", "restore position")}),
    0x5E65: (0x2E, {1: ("b", "wait"), 2: ("", "animation Anim_04_4a0d"), 3: ("w", "jump (Necky_Throw)")}),
    0x64BA: (0x2E, {1: ("b", "wait"), 2: ("", "animation Anim_04_4ce3"), 3: ("", "animation Anim_04_4cc7"),
                    4: ("ww", "throw: x speed, y speed")}),
    0x6689: (0x2E, {1: ("b", "wait"), 2: ("", "yield"), 3: ("w", "target x speed"), 4: ("w", "target y speed"),
                    5: ("w", "acceleration"), 6: ("", "fall (ObjInit_0a_66f8)"), 7: ("", "end")}),
    0x6992: (0x2E, {1: ("b", "wait (MiniNecky_Hover)"), 2: ("b", "wait (MiniNecky_Swoop)"), 3: ("", "finish (MiniNecky_Spit)")}),
    0x6AEC: (0x2E, {1: ("b", "wait"), 2: ("w", "attack (RunMankyKongScript.jump_6b11)")}),
    0x6C60: (0x2E, {2: ("", "yield (Croctopus_Chase)"), 3: ("w", "target x speed"), 4: ("w", "target y speed"),
                    5: ("", "end"), 6: ("", "yield (Croctopus_WaitForPlayer)")}),
    0x6FC5: (0x2E, {1: ("b", "wait"), 2: ("", "yield"), 3: ("w", "target x speed"), 4: ("w", "target y speed"),
                    5: ("", "yield (Millstone_Despawn)"), 6: ("w", "acceleration"), 7: ("w", "x acceleration"),
                    8: ("w", "y acceleration")}),
    0x713C: (0x31, {1: ("b", "wait"), 2: ("o", "spawn")}),
    0x71EB: (0x31, {2: ("", "animation (ObjInit_0a_727a)"), 3: ("", "animation (ObjInit_0a_726f)"),
                    4: ("b", "animation (ObjInit_0a_7285)"), 5: ("b", "animation (ObjInit_0a_7290)"),
                    6: ("", "set OBJ_VAR_2E bit 7"), 7: ("", "clear OBJ_VAR_2E bit 7"),
                    8: ("", "sound $94"), 9: ("", "sound $9a")}),
}
# the handler an object starts with -> the interpreter it calls
HANDLERS = {0x5C17: 0x5B56, 0x5ED0: 0x5E65, 0x6556: 0x64BA, 0x670A: 0x6689, 0x6744: 0x6689, 0x69F5: 0x6992,
            0x6B9F: 0x6AEC, 0x6CFC: 0x6C60, 0x7055: 0x6FC5, 0x71B1: 0x713C, 0x729B: 0x71EB}
# scripts no object list points at (format from their neighbours)
UNREFERENCED = [(0x7495, 0x5B56), (0x74AC, 0x5B56)]
ENDS = ("end",)


def off(bank, addr):
    return bank * 0x4000 + addr - 0x4000


def parse(rom, starts):
    """starts: {addr: interpreter}. Returns {addr: (interpreter, [(addr, cmd, args, text)])}
    with one entry per run between boundaries (starts and jump targets)."""
    b = lambda a: rom[off(BANK, a)]  # noqa: E731
    seen, todo, cmds, interp = set(), sorted(starts.items()), {}, {}
    bounds = set(starts)
    while todo:
        a, it = todo.pop()
        if a in seen:
            continue
        seen.add(a)
        table = INTERPRETERS[it][1]
        p = a
        while True:
            if p in cmds:  # ran into a script parsed already
                bounds.add(p)
                break
            c = b(p)
            interp[p] = it
            if c == 0:
                tgt = b(p + 1) | b(p + 2) << 8
                cmds[p] = (0, [tgt], "jump" if tgt else "stop")
                if tgt:
                    bounds.add(tgt)
                    todo.append((tgt, it))
                break
            if c not in table:
                cmds[p] = (c, [], "stop")
                break
            args, text = table[c]
            vals, q = [], p + 1
            for x in args:
                if x == "b":
                    vals.append(b(q))
                    q += 1
                else:
                    vals.append(b(q) | b(q + 1) << 8)
                    q += 2
            cmds[p] = (c, vals, text)
            p = q
            if text in ENDS:
                break
    # split into runs at the boundaries
    out, cur = {}, None
    for p in sorted(cmds):
        if p in bounds or cur is None or p != nxt:
            cur = p
            out[cur] = (interp[p], [])
        c, vals, text = cmds[p]
        out[cur][1].append((p, c, vals, text))
        nxt = p + 1 + sum(1 if x == "b" else 2 for x in arg_kinds(interp[p], c, vals))
        if c == 0 or text in ("stop",) + ENDS:
            cur = None
    return out


def arg_kinds(it, c, vals):
    if c == 0:
        return ["w"]
    table = INTERPRETERS[it][1]
    return list(table[c][0]) if c in table else []


def script_starts(t, rom):
    """Pointers set by object initialiser lists, resolved to interpreters by
    the handler each list ends up with (following includes)."""
    lists = {o: v for o, v in t.data.items() if v[0] == "objinit"}

    def fields(o, depth=0):
        _, bank, entries, _ = lists[o]
        f = {}
        for e in entries:
            if e[0] == "byte":
                f[e[1]] = e[2]
            elif e[0] == "word":
                f[e[1]], f[e[1] + 1], f[("w", e[1])] = e[2] & 0xFF, e[2] >> 8, e[2]
            elif e[0] == "include":
                io = off(0 if e[1] < 0x4000 else bank, e[1])
                if io in lists and depth < 10:
                    f.update(fields(io, depth + 1))
        return f
    starts = {}
    for o in lists:
        f = fields(o)
        if f.get(1) != BANK:
            continue
        it = HANDLERS.get(f.get(2, 0) | f.get(3, 0) << 8)
        if it is None:
            continue
        v = f.get(("w", INTERPRETERS[it][0]))
        if v is not None and START <= v < END:
            starts[v] = it
    for a, it in UNREFERENCED:
        starts.setdefault(a, it)
    return starts


def main():
    sys.path.insert(0, "tools")
    from run_trace import make
    rom = open(sys.argv[1] if len(sys.argv) > 1 else "baserom.gbc", "rb").read()
    t = make(rom)
    runs = parse(rom, script_starts(t, rom))
    n = 0
    for a, (it, cs) in sorted(runs.items()):
        print("$%04x  Func_0a_%04x" % (a, it))
        for p, c, vals, text in cs:
            print("   %02x %-20s %s" % (c, text, " ".join("$%x" % v for v in vals)))
            n += 1 + sum(1 if x == "b" else 2 for x in arg_kinds(it, c, vals))
    print("bytes:", n)


if __name__ == "__main__":
    main()
