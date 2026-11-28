"""Names for local labels from the shape of the code around them.

Every jump target inside a routine used to be called .jump_XXXX. This pass
gives each one a name that says what kind of place it is:

  .return      the label is an unconditional ret/reti
  .done        straight-line code from the label reaches a ret within a few
               instructions (no calls or branches on the way)
  .jp_Name     the label is an unconditional jump to the global label Name
  .loop        some instruction later in the same routine jumps back to it
  .skip        a conditional jump a few instructions back skips to it
  .else        the code just before it never falls through (ends in an
               unconditional jump or ret), so only jumps reach it
  .continue    any other place jumps reach from earlier in the routine
  .entry       nothing jumps to it: reached through a table or a pushed
               return address
  .back        reached only by jumps from after it in other routines

A name used once in a routine is written as it is; when a routine has
several labels of a kind, each gets its address (.loop_44f5, .loop_4502),
which also keeps them easy to find in a debugger. Labels named by hand
(HAND_NAMES below) come first.
"""

DONE_MAX = 6     # instructions from the label to the ret for .done
SKIP_MAX = 6     # instructions a .skip jumps over

BRANCHES = ("jr", "jrc", "jp", "jpc", "call", "callc")

# (bank, address) -> local name (without the dot): the labels other
# routines jump into, which are entry points of a kind, named by hand.
HAND_NAMES = {
    (0x00, 0x041D): "jp_write_save_file",
    (0x00, 0x0CAE): "draw_at_camera",
    (0x00, 0x1778): "pop_and_spawn",
    (0x00, 0x18FE): "delete",
    (0x00, 0x1D55): "from_node",
    (0x00, 0x1DC2): "check_node",
    (0x00, 0x1E0A): "newly_cleared",
    (0x00, 0x2477): "enter",
    (0x00, 0x2BD2): "copy",
    (0x00, 0x2EF2): "write_save_file",
    (0x00, 0x308B): "store_regs",
    (0x00, 0x3255): "play_note",
    (0x00, 0x3257): "save_stream_pos",
    (0x00, 0x325C): "set_period",
    (0x00, 0x332D): "update_effects",
    (0x00, 0x3342): "write_regs",
    (0x00, 0x3347): "copy_regs",
    (0x00, 0x33A0): "set_pan",
    (0x00, 0x33D2): "stop_channel",
    (0x00, 0x33F8): "set_duty_envelope",
    (0x00, 0x345C): "call",
    (0x00, 0x34CB): "ret",
    (0x00, 0x34FA): "set_length",
    (0x00, 0x3546): "set_loop",
    (0x00, 0x3554): "loop_end",
    (0x00, 0x3575): "set_echo",
    (0x00, 0x35BB): "set_volume",
    (0x00, 0x3983): "run_object",
    (0x00, 0x39BF): "apply_y",
    (0x00, 0x39E5): "undo",
    (0x00, 0x3D42): "enter",
    (0x00, 0x3FDC): "far_jump",
    (0x08, 0x4486): "run",
    (0x08, 0x46DD): "stop",
    (0x08, 0x54DB): "swing_back",
    (0x09, 0x44F5): "next_object",
    (0x09, 0x55FF): "bounced",
    (0x09, 0x5CA4): "common_update",
    (0x09, 0x612B): "set_speed",
    (0x09, 0x61C3): "drop",
    (0x09, 0x7200): "bounce",
    (0x09, 0x7213): "no_contact",
    (0x0A, 0x4BB4): "set_anim",
    (0x0A, 0x4D4E): "next_run",
    (0x0A, 0x4EF8): "hop",
    (0x0A, 0x50DE): "animate",
    (0x0A, 0x5179): "start_kredits",
    (0x0A, 0x5E14): "animate",
    (0x0A, 0x6F4B): "spawn",
    (0x50, 0x41FC): "start_game",
    (0x50, 0x43C3): "far_jump",
    (0x50, 0x49B9): "apply",
    (0x50, 0x510C): "draw_slot",
    (0x50, 0x5152): "next_slot",
    (0x50, 0x615D): "scale",
    (0x50, 0x6186): "read",
    (0x55, 0x4123): "finish",
    (0xF0, 0x4572): "wait_lcd",
    (0xF0, 0x4600): "soft_reset",
    (0xF0, 0x4840): "copy_unique_map",
    (0xF0, 0x496D): "load",
    (0xF0, 0x6B02): "next_char",
    (0xF1, 0x425A): "show",
    (0xF1, 0x4A24): "count_files",
    (0xF1, 0x4A51): "check_files",
    (0xF1, 0x4A63): "hide",
    (0xF1, 0x4CEC): "run_action",
    (0xF1, 0x50F9): "choose_file",
    (0xF1, 0x56B0): "highlight",
    (0xF1, 0x5E71): "check_bits",
    (0xF1, 0x71A1): "open_options",
    (0xF1, 0x72E9): "highlight",
    (0xF1, 0x7310): "next_page",
    (0xF1, 0x7334): "previous_page",
    (0xF1, 0x7413): "select",
    (0xF1, 0x78D8): "retry",
    (0xF1, 0x7962): "retry",
    (0xF1, 0x7BC6): "copy",
    (0xF1, 0x7BF2): "copy",
    (0xF1, 0x7C59): "copy",
    (0xF1, 0x7CBA): "show",
    (0xF2, 0x48D2): "highlight",
    (0xF2, 0x4A4F): "check_text",
    (0xF2, 0x4CF8): "darkness",
    (0xF2, 0x519B): "print_strip",
    (0xF2, 0x5229): "print_end",
    (0xF2, 0x5250): "finish",
    (0xF2, 0x691A): "timeout",
    (0xF2, 0x6929): "error_bit2",
    (0xF2, 0x71C7): "start",
    (0xF2, 0x7306): "start",
    (0xF2, 0x7532): "start",
    (0xF2, 0x73EB): "show_menu",
    (0xF2, 0x7831): "leave",
    (0xF2, 0x79A7): "return_to_menu",
    (0xF2, 0x79EA): "signal_partner",
    (0xFE, 0x4115): "start",
    (0xFE, 0x42BD): "game_over",
    (0xFE, 0x42EB): "tally",
    (0xFE, 0x431E): "wait_end",
    (0xFE, 0x436D): "quit",
    (0xFE, 0x43C7): "finish",
    (0xFE, 0x4B7B): "check_fire",
    (0xFE, 0x5212): "blink",
    (0xFE, 0x525F): "draw",
    (0xFE, 0x52E3): "swap",
    (0xFE, 0x54DA): "draw_now",
    (0xFE, 0x55CD): "set",
    (0xFE, 0x5698): "resume",
    (0xFE, 0x5CB5): "run_actor",
    (0xFE, 0x683F): "dir0",
    (0xFE, 0x6849): "dir1",
    (0xFE, 0x685C): "dir2",
    (0xFE, 0x6866): "dir3",
    (0xFE, 0x6879): "dir4",
    (0xFE, 0x6883): "dir5",
    (0xFE, 0x6896): "dir6",
    (0xFE, 0x6B64): "spawn",
    (0xFE, 0x6FCD): "pick",
    (0xFE, 0x6FF1): "spawn",
    (0xFE, 0x7202): "spawn_kremling",
    (0xFE, 0x721B): "find_slot",
    (0xFE, 0x746A): "next_wave",
    (0xF1, 0x7880): "set_bit0",
    (0xF1, 0x7884): "set_bit1",
    (0xF1, 0x7888): "set_bit2",
    (0xF1, 0x788C): "set_bit3",
    (0xF1, 0x7890): "set_bit4",
    (0xF1, 0x7894): "set_bit5",
    (0xF1, 0x7898): "set_bit6",
    (0xF1, 0x78BA): "test_bit0",
    (0xF1, 0x78BD): "test_bit1",
    (0xF1, 0x78C0): "test_bit2",
    (0xF1, 0x78C3): "test_bit3",
    (0xF1, 0x78C6): "test_bit4",
    (0xF1, 0x78C9): "test_bit5",
    (0xF1, 0x78CC): "test_bit6",
    (0xFE, 0x5122): "test_bit0",
    (0xFE, 0x5126): "test_bit1",
    (0xFE, 0x512A): "test_bit2",
    (0xFE, 0x512E): "test_bit3",
    (0xFE, 0x5132): "test_bit4",
    (0xFE, 0x5136): "test_bit5",
    (0xFE, 0x513A): "test_bit6",
    (0xFE, 0x515D): "res_bit0",
    (0xFE, 0x5161): "res_bit1",
    (0xFE, 0x5165): "res_bit2",
    (0xFE, 0x5169): "res_bit3",
    (0xFE, 0x516D): "res_bit4",
    (0xFE, 0x5171): "res_bit5",
    (0xFE, 0x5175): "res_bit6",
    (0xFE, 0x5198): "set_bit0",
    (0xFE, 0x519C): "set_bit1",
    (0xFE, 0x51A0): "set_bit2",
    (0xFE, 0x51A4): "set_bit3",
    (0xFE, 0x51A8): "set_bit4",
    (0xFE, 0x51AC): "set_bit5",
    (0xFE, 0x51B0): "set_bit6",
}


def _target_off(i, o, bank_size, off):
    t = i.target
    if t is None or t >= 0x8000:
        return None
    if t < 0x4000:
        return t
    b = o // bank_size
    if b == 0:
        b = i.ctx or 0
        if not b:
            return None
    return off(b, t)


def name_locals(locals_, names, insns, bank_size, off):
    """locals_: {offset: (scope offset, ".jump_xxxx")}; rewritten in place."""
    import bisect
    refs = {}
    for o, i in insns.items():
        if i.flow in BRANCHES:
            t = _target_off(i, o, bank_size, off)
            if t is not None:
                refs.setdefault(t, []).append(o)
    scopes = {}
    for o, (scope, _) in locals_.items():
        scopes.setdefault(scope, []).append(o)
    starts = {}
    for o in names:
        starts.setdefault(o // bank_size, []).append(o)
    for v in starts.values():
        v.sort()

    def scope_of(o):
        lst = starts.get(o // bank_size, [])
        k = bisect.bisect_right(lst, o) - 1
        best = lst[k] if k >= 0 else None
        # a local label's scope is the global before it
        return best

    def steps(o, n):
        """Up to n instructions from o in straight-line order."""
        out = []
        while len(out) < n and o in insns:
            i = insns[o]
            out.append((o, i))
            if i.flow in ("jp", "jr", "ret", "jphl", "stop") or i.flow is None and i.op in (0xD9,):
                break
            o += i.length
        return out

    prev_of = {o + i.length: o for o, i in insns.items()}

    def kind(o, scope):
        bank = o // bank_size
        addr = (o % bank_size) + (0x4000 if bank else 0)
        if (bank, addr) in HAND_NAMES:
            return HAND_NAMES[(bank, addr)], True
        i = insns.get(o)
        if i is not None and i.op in (0xC9, 0xD9):
            return "return", False
        if i is not None and i.flow in ("jp", "jr"):
            t = _target_off(i, o, bank_size, off)
            if t is not None and t in names and not names[t].startswith("."):
                return "jp_" + names[t], False
        run = steps(o, DONE_MAX + 1)
        if run and run[-1][1].op in (0xC9, 0xD9) and all(
                x.flow not in BRANCHES + ("retc", "rst", "jphl") for _, x in run[:-1]):
            return "done", False
        srcs = refs.get(o, [])
        own = [s for s in srcs if scope_of(s) == scope]
        if any(s > o for s in own):
            return "loop", False
        p = prev_of.get(o)
        falls_in = p is not None and insns[p].flow not in ("jp", "jr", "ret", "jphl") and \
            insns[p].op not in (0xD9,)
        if own and falls_in:
            near = [s for s in own if s < o and insns[s].flow in ("jrc", "jpc")]
            for s in near:
                n, q = 0, s + insns[s].length
                while q < o and q in insns and n <= SKIP_MAX:
                    q += insns[q].length
                    n += 1
                if q == o and n <= SKIP_MAX:
                    return "skip", False
            return "continue", False
        if own:
            return "else", False
        if srcs:
            return "back" if all(s > o for s in srcs) else "continue", False
        return "entry", False

    for scope, offs in scopes.items():
        offs.sort()
        kinds = {}
        for o in offs:
            if not locals_[o][1].startswith(".jump_"):
                continue
            kinds[o] = kind(o, scope)
        count = {}
        for k, hand in kinds.values():
            count[k] = count.get(k, 0) + 1
        for o, (k, hand) in kinds.items():
            addr = (o % bank_size) + (0x4000 if o // bank_size else 0)
            nm = k if hand or count[k] == 1 else "%s_%04x" % (k, addr)
            locals_[o] = (scope, "." + nm)
    import os
    dump = os.environ.get("LOCALS_DUMP")
    if dump:
        with open(dump, "w") as f:
            for o, (scope, nm) in sorted(locals_.items()):
                b = o // bank_size
                f.write("%02x %04x %s%s\n" % (b, (o % bank_size) + (0x4000 if b else 0), names.get(scope, "?"), nm))
