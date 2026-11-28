"""Derive names for object lists, animations and sprite frames from their users.

Routines all have names now, so data that was named by kind and address
(ObjInit_0e_4397, Anim_04_4a33, Frame_20_4f60, ...) can take its name from
what uses it:

  ObjInit_<handler>        an initialiser list, after the OBJ_HANDLER it sets
                           (or its touch handler without "_Touch", or the
                           list it includes, or the routine that loads it)
  Anim_<user>              an animation script, after the routine that sets
                           it, else the object list, else the script that
                           jumps to it; a label a script falls into gets the
                           name of the script it belongs to
  Frame_<anim>             a sprite frame, after the first animation showing
                           it (or the routine or table that uses it)
  FrameTiles_<frame>,      a frame's graphics and sprite layout, after the
  FrameSprites_<frame>     frame

Where several items get the same name they are numbered in address order
(Frame_Zinger_Patrol_1, _2, ...). Names in tools/names.py and tools/hints.py
take precedence. The result is written to tools/datanames.py, which
tools/emit.py reads; run this after `make generate` and then generate again:

    python3 tools/autodatanames.py && make generate
"""
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KINDS = ("ObjInit", "Anim", "Frame", "FrameTiles", "FrameSprites")
PH = re.compile(r"^([A-Za-z]\w*?)_([0-9a-f]{2})_([0-9a-f]{4})$")      # any label named by kind and address
STREAMS = ("Mus", "MusUnused", "ObjScript", "Flow")
CODE_WORDS = set("ld ldh jp jr call ret reti push pop inc dec add adc sub sbc and or xor cp bit set res rl rr "
                 "rlc rrc sla sra srl swap di ei halt nop stop daa cpl scf ccf rla rra rlca rrca rst "
                 "rst_farcall".split())                  # code-like data that runs on
LANGUAGES = {0x10: "English", 0x11: "German", 0x12: "French", 0x13: "Italian", 0x14: "Spanish"}
REF = re.compile(r"\b([A-Za-z]\w*_[0-9a-f]{2}_[0-9a-f]{4})\b")   # any label named by address
PLACEHOLDER = re.compile(r"_[0-9a-f]{2}_[0-9a-f]{4}$")


def load_sources():
    """labels: name -> (file, order); bodies: name -> lines; order list"""
    import glob
    bodies, order, files = {}, [], {}
    for f in sorted(glob.glob(os.path.join(ROOT, "src", "*.asm"))):
        cur = None
        for ln in open(f):
            m = re.match(r"^([A-Za-z_]\w*)::?\s*$", ln)
            if m:
                cur = m.group(1)
                bodies[cur] = []
                order.append(cur)
                files[cur] = f
                continue
            if cur:
                bodies[cur].append(ln.split(";")[0].rstrip())
    return bodies, order, files


def symbols():
    out = {}
    for ln in open(os.path.join(ROOT, "dkc.sym")):
        m = re.match(r"([0-9a-f]{2}):([0-9a-f]{4}) (\S+)", ln)
        if m and "." not in m.group(3):
            out[m.group(3)] = (int(m.group(1), 16), int(m.group(2), 16))
    return out


def unused_items():
    """(bank, address) of the frames and scripts tools/find_unused.py reports
    as unused (from unused/README.md, which it writes)."""
    path = os.path.join(ROOT, "unused", "README.md")
    out = set()
    if not os.path.exists(path):
        return out
    for ln in open(path):
        m = re.match(r"\| `(Frame|Anim)_([0-9a-f]{2})_([0-9a-f]{4})`(?:–`([0-9a-f]{4})`)? \|", ln)
        if not m:
            continue
        b, a = int(m.group(2), 16), int(m.group(3), 16)
        end = int(m.group(4), 16) if m.group(4) else a
        step = 6 if m.group(1) == "Frame" else 1
        for x in range(a, end + 1, step):
            out.add((b, x))
    return out


def good(name):
    return name is not None and not PLACEHOLDER.search(name) and not name.startswith("Func_")


def main():
    bodies, order, files = load_sources()
    syms = symbols()
    users = defaultdict(list)          # placeholder label -> [(user label, line)]
    for lab in order:
        for ln in bodies[lab]:
            for r in REF.findall(ln):
                if r != lab:
                    users[r].append((lab, ln.strip()))
    prev = {order[k]: order[k - 1] for k in range(1, len(order))
            if files[order[k]] == files[order[k - 1]]}

    def falls_through(a):
        """a's body doesn't end in a jump or end: the next label continues it."""
        lines = [x.strip() for x in bodies[a] if x.strip()]
        return lines and not lines[-1].startswith(("anim_jump", "anim_end", "anim_stop", "anim_loop", "obj_end",
                                                  "mus_end", "mus_jump", "mus_ret", "mus_sub_ret", "flow_jump",
                                                  "dw", "db", "ds", "INCBIN", "jp", "ret", "jr"))

    base = {}
    GENERIC = ("Obj_", "Touch_")
    letters = {}
    import glob
    for f in sorted(glob.glob(os.path.join(ROOT, "src", "*.asm"))):
        for m in re.finditer(r"dw (Frame_\w+) ; letter (\w)", open(f).read()):
            letters.setdefault(m.group(1), "Letter_" + m.group(2))
    unused = unused_items()
    raw_comment = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "src", "*.asm"))):
        cur = None
        for ln in open(f):
            m = re.match(r"^([A-Za-z_]\w*)::?\s*$", ln)
            if m:
                cur = m.group(1)
            elif cur and ";" in ln and cur not in raw_comment:
                raw_comment[cur] = ln.split(";", 1)[1]
    import hints

    def camel(text, count=4):
        ws = re.findall(r"[A-Za-z0-9]+", re.split(r"[(:;]", text.replace("'", ""))[0])
        return "".join(w[:1].upper() + w[1:] for w in ws[:count]) or None

    hint_names = {}
    for (b, a), desc in hints.EXTRA_SCREENS:
        hint_names[(b, a)] = camel(desc)
    for b, a, _, desc in hints.EXTRA_TILES:
        hint_names.setdefault((b, a), camel(desc))

    def kind(n):
        m = PH.match(n)
        return m.group(1) if m else None

    all_kinds = {PH.match(n).group(1) for n in order if PH.match(n)} | {"LevelDesc", "LevelEntrance"} | set(KINDS)
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import datanames as _old
        all_kinds |= {v.split("_", 1)[0] for v in _old.NAMES.values()}
    except ImportError:
        pass

    def is_code(n):
        first = next((x.split()[0] for x in bodies.get(n, []) if x.strip()), "")
        return first in CODE_WORDS

    def strip_kind(n):
        k = n.split("_", 1)[0]
        return n.split("_", 1)[1] if k in all_kinds and "_" in n and not is_code(n) else n

    def first_word(n):
        m = re.match(r"[A-Z][a-z0-9]*", n)
        return m.group(0) if m else n

    def table_name(n, k):
        """n listed by one data table: k_<index>, its position among that
        table's entries of this kind"""
        us = {u for u, _ in users[n] if u != n}
        if len(us) != 1:
            return None
        t = us.pop()
        if is_code(t) or kind(t) in KINDS:
            return None
        entries = []
        for ln in bodies.get(t, []):
            for r in REF.findall(ln):
                if kind(r) == k and r not in entries:
                    entries.append(r)
        if len(entries) < 4 or n not in entries:
            return None
        if kind(t):
            r = resolve(t)
            if isinstance(r, tuple) and r[0] == "FULL":
                r = r[1].split("_", 1)[1] if r[1] and "_" in r[1] else None
            tb = r if isinstance(r, str) else k
        else:
            tb = strip_kind(t)
        tb = tb.replace("Table", "") or k
        width = len(str(len(entries) - 1))
        idx = "%0*d" % (width, entries.index(n))
        if k.startswith(tb):
            return ("FULL", "%s_%s" % (k, idx))
        if first_word(tb) == first_word(k):
            tb = tb[len(first_word(tb)):]
        sep = "_" if tb[-1:].isdigit() else ""
        return ("FULL", "%s_%s%s%s" % (k, tb, sep, idx) if tb else "%s_%s" % (k, idx))

    def words(n, count=4):
        text = " ".join(re.findall(r'"([^"]*)"', "\n".join(bodies.get(n, []))))
        ws = re.findall(r"[A-Za-z0-9]+", text.replace("'", ""))
        return "".join(w[:1].upper() + w[1:].lower() for w in ws[:count])[:32] or None

    # the same text in each language: entry e of group g in banks $10-$14
    text_pos, text_at, group_index = {}, {}, {}
    for b in LANGUAGES:
        groups = sorted((n for n in order if PH.match(n) and PH.match(n).group(1) == "TextGroup"
                         and int(PH.match(n).group(2), 16) == b), key=lambda x: syms.get(x, (0, 0)))
        for gi, g in enumerate(groups):
            group_index[g] = (b, gi)
            for ei, ln in enumerate(x for x in bodies[g] if x.strip().startswith("dw")):
                t = ln.split()[1]
                text_pos.setdefault(t, (b, gi, ei))
                text_at[(b, gi, ei)] = t

    def generic(n):
        return n.startswith(GENERIC)

    def routine_before(n):
        """the named routine a table follows in the source (its likely user)"""
        p = prev.get(n)
        while p is not None:
            if good(p) and not kind(p) and not p.startswith(tuple(k + "_" for k in all_kinds)):
                return p
            p = prev.get(p)
        return None

    def code_users(n, seen=()):
        """named routines that use n, directly or through a table of n's"""
        out = []
        for u, _ in users[n]:
            if kind(u) in KINDS:
                continue
            if good(u):
                out.append(u)
            elif PLACEHOLDER.search(u) and u not in seen:
                found = code_users(u, seen + (n,))
                if not found and not users[u]:
                    r = routine_before(u)
                    found = [r] if r else []
                out += found
        return out

    def pick(cands):
        if not cands:
            return None
        specific = [c for c in cands if not generic(c)]
        return Counter(specific or cands).most_common(1)[0][0]

    # consecutive animation labels that fall into one another form one script
    group = {}
    for n in order:
        if kind(n) != "Anim":
            continue
        p = prev.get(n)
        group[n] = group[p] if p in group and falls_through(p) else n
    members = defaultdict(list)
    for n, g in group.items():
        members[g].append(n)

    def resolve(n, depth=0):
        """base name for placeholder label n, or None"""
        if n in base:
            return base[n]
        base[n] = None
        if depth > 12:
            return None
        k = kind(n)
        b = None
        body = bodies.get(n, [])
        if syms.get(n) in hint_names and hint_names[syms[n]]:
            base[n] = hint_names[syms[n]]
            return base[n]
        if k == "ObjScript" and "no object list points here" in raw_comment.get(n, ""):
            m = re.search(r"-- Run(\w+?)Script", raw_comment[n])
            base[n] = (m.group(1) if m else "Object") + "_Unused"
            return base[n]
        if k == "ObjInit":
            fields = {}
            for ln in body:
                m = re.match(r"\s*obj_word (OBJ_HANDLER|OBJ_TOUCH_HANDLER), (\S+)", ln)
                if m:
                    fields[m.group(1)] = m.group(2)
                m = re.match(r"\s*obj_include (\S+)", ln)
                if m:
                    fields["include"] = m.group(1)
            h, t = fields.get("OBJ_HANDLER"), fields.get("OBJ_TOUCH_HANDLER")
            t = re.sub(r"_Touch$", "", t) if good(t) else None
            if good(h) and not generic(h):
                b = h
            elif t and not generic(t):
                b = t
            elif "include" in fields:
                inc = fields["include"]
                b = resolve(inc, depth + 1) if kind(inc) else (inc if good(inc) else None)
            if b is None:
                b = (h if good(h) else None) or t or pick(code_users(n))
            if b is None:
                incl = [u for u, ln in users[n] if kind(u) == "ObjInit" and "obj_include" in ln]
                found = [resolve(u, depth + 1) for u in incl]
                found = [f for f in found if f and not f.endswith("_Common")]
                if found:
                    b = Counter(found).most_common(1)[0][0] + "_Common"
            if b is None and not users[n] and [x.strip() for x in body if x.strip()][:1] == ["obj_end"]:
                b = "Empty"
        elif k == "Anim":
            mates = members.get(group.get(n, n), [n])
            cands, lists, anims = [], [], []
            for m in mates:
                cands += code_users(m)
                lists += [u for u, _ in users[m] if kind(u) == "ObjInit"]
                anims += [u for u, _ in users[m] if kind(u) == "Anim" and group.get(u) != group.get(n)]
            b = pick([c for c in cands if not generic(c)])
            for u in lists + anims:
                if b:
                    break
                r = resolve(u, depth + 1)
                b = r if r and not generic(r) else b
            if b is None:
                b = pick(cands)
            for u in lists + anims:
                if b:
                    break
                b = resolve(u, depth + 1)
            if b is None and any(syms.get(m) in unused for m in mates):
                b = "Unused"
        elif k == "Frame":
            if n in letters:
                b = letters[n]
            anims = [u for u, _ in users[n] if kind(u) == "Anim"]
            lists = [u for u, _ in users[n] if kind(u) == "ObjInit"]
            found = [resolve(a, depth + 1) for a in anims]
            found = [f for f in found if f]
            if b is None and found:
                b = next((f for f in found if f != "Unused"), found[0])
            if b is None or b == "Unused":
                b = pick(code_users(n)) or b
            for u in lists:
                if b:
                    break
                b = resolve(u, depth + 1)
            if b is None and syms.get(n) in unused:
                b = "Unused"
        elif k in ("FrameTiles", "FrameSprites"):
            frames = [u for u, _ in users[n] if kind(u) == "Frame"]
            if frames:
                b = ("F", frames[0])   # named after the frame's final name
        elif k == "Text":
            pos = text_pos.get(n)
            eng = text_at.get((0x10,) + pos[1:]) if pos else None
            lang = LANGUAGES.get(pos[0]) if pos else None
            w = words(eng or n)
            if w:
                b = w + ("_" + lang if lang and lang != "English" else "")
        elif k == "TextGroup" and n in group_index:
            bb, gi = group_index[n]
            b = "%s_%02d" % (LANGUAGES[bb], gi)
        if b is None and k in ("FEText", "CrankyPauseString", "FEWords"):
            b = words(n)
        if b is None and k not in KINDS and k not in ("Text", "TextGroup"):
            p = prev.get(n)
            if k in STREAMS and p is not None and falls_through(p):
                b = resolve(p, depth + 1) if kind(p) else (strip_kind(p) if good(p) else None)
            if b is None and k not in STREAMS:
                b = table_name(n, k)
            if b is None:
                found, from_stream = [], False
                for u, _ in users[n]:
                    if u == n:
                        continue
                    from_stream = from_stream or not is_code(u)
                    if kind(u):
                        r = resolve(u, depth + 1)
                        if isinstance(r, tuple) and r[0] == "FULL":
                            r = r[1].split("_", 1)[1] if r[1] and "_" in r[1] else None
                        if r and not isinstance(r, tuple):
                            found.append(r)
                    elif good(u):
                        found.append(strip_kind(u))
                b = pick(found)
                if b and k in STREAMS and from_stream:
                    b += "_Sub"     # called from another stream, not continuing it
            if b is None and not users[n]:
                p = prev.get(n)
                if k.endswith("Tail") and p is not None and p.startswith(k[:-4] + "_"):
                    b = p[len(k) - 3:]                # the rest of the item before it
                elif k in STREAMS and p is not None and (kind(p) == k or p.startswith(k + "_")):
                    r = resolve(p, depth + 1) if kind(p) else p[len(k) + 1:]
                    b = r + "_Part" if isinstance(r, str) else None
                elif k == "BGTiles" and syms.get(n, (0, 0))[1] == 0x4000:
                    pb = syms[n][0] - 1               # tile data runs on from the previous bank
                    cands = [x for x in order if x.startswith("BGTiles_") and syms.get(x, (0, 0))[0] == pb]
                    if cands:
                        last = max(cands, key=lambda x: syms[x])
                        r = resolve(last, depth + 1) if kind(last) else last[len("BGTiles_"):]
                        if isinstance(r, tuple) and r[0] == "FULL" and r[1]:
                            r = r[1].split("_", 1)[1]
                        b = r + "_Cont" if isinstance(r, str) else None
                elif k.endswith("Unused") or k == "Padding":
                    pass                              # numbered below
                elif k not in STREAMS:
                    b = routine_before(n)
            if b is None and not users[n] and k.endswith("Unused"):
                b = ("FULL", None)
        base[n] = b
        return b

    placeholders = [n for n in order if kind(n)]
    for n in placeholders:
        resolve(n)

    # numbering, kind by kind (frames before their tiles)
    final = {}

    def assign(k):
        groups = defaultdict(list)
        for n in placeholders:
            if kind(n) != k or base.get(n) is None:
                continue
            b = base[n]
            if isinstance(b, tuple) and b[0] == "FULL" and b[1] is None:
                groups["\0"].append(n)
                continue
            if isinstance(b, tuple) and b[0] == "FULL":
                final[n] = b[1]
                continue
            if isinstance(b, tuple):
                fr = b[1]
                b = strip_kind(final.get(fr, fr)) if fr in final else None
                if b is None:
                    continue
            groups[b].append(n)
        for b, ns in groups.items():
            ns.sort(key=lambda x: syms.get(x, (0, 0)))
            if b == "\0":
                for i, n in enumerate(ns):
                    final[n] = "%s_%02d" % (k, i + 1)
                continue
            for i, n in enumerate(ns):
                final[n] = "%s_%s" % (k, b) if len(ns) == 1 else "%s_%s_%d" % (k, b, i + 1)

    for k in list(KINDS) + sorted({kind(n) for n in placeholders} - set(KINDS)):
        assign(k)

    taken = set(order) - set(final)
    result = {}
    # names given on an earlier run, which the sources now carry
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import datanames as old
        for (b, a), nm in old.NAMES.items():
            if syms.get(nm) == (b, a):
                result[(b, a)] = nm
    except ImportError:
        pass
    for n, new in sorted(final.items(), key=lambda kv: syms.get(kv[0], (0, 0))):
        if n not in syms:
            continue
        if new in taken:
            k = 2
            while "%s_%d" % (new, k) in taken:
                k += 1
            new = "%s_%d" % (new, k)
        taken.add(new)
        result[syms[n]] = new
    lines = ["    (0x%02X, 0x%04X): \"%s\",\n" % (b, a, nm) for (b, a), nm in sorted(result.items())]
    out = os.path.join(ROOT, "tools", "datanames.py")
    with open(out, "w") as f:
        f.write('"""Names for data labels, derived from what uses them (or, for text, from\n'
                'the words). Generated by tools/autodatanames.py; do not edit by hand (put\n'
                'hand-made names in tools/names.py, which takes precedence)."""\n\n')
        f.write("NAMES = {\n" + "".join(lines) + "}\n")
    total = Counter(kind(n) for n in placeholders)
    done = Counter(kind(n) for n in final)
    for k, t in total.most_common():
        print("%-22s %5d of %5d named" % (k, done[k], t))
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
