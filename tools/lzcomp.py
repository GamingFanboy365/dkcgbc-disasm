#!/usr/bin/env python3
"""The level map compression (unpacked by Decompress).

A stream is a list of control bytes n:

  $00          end of data
  $01-$7F      repeat the next byte n times
  $80-$BF      copy n & $3F literal bytes
  $C0-$FF      copy n & $3F bytes from d bytes back in the output (d is the
               next byte)

`compress` reproduces the game's own packer exactly (all 384 map streams in
the ROM come out byte for byte): at each position it takes the longer of a
run (up to 127 bytes) and the nearest back copy (up to 63 bytes, at most 255
back, never overlapping itself), preferring the run on a tie; runs and copies
must be at least 3 bytes, and anything else goes into literal blocks of up to
63 bytes.

  python3 tools/lzcomp.py in.bin out.lz     compress
  python3 tools/lzcomp.py -d in.lz out.bin  decompress
"""
import sys


def compress(data):
    out, lit = bytearray(), bytearray()
    i, n = 0, len(data)

    def flush():
        nonlocal lit
        while lit:
            chunk, lit = lit[:63], lit[63:]
            out.append(0x80 | len(chunk))
            out.extend(chunk)
    while i < n:
        run = 1
        while i + run < n and data[i + run] == data[i] and run < 127:
            run += 1
        best = dist = 0
        for d in range(1, min(i, 255) + 1):
            k = 0
            while i + k < n and k < 63 and k < d and data[i + k - d] == data[i + k]:
                k += 1
            if k > best:
                best, dist = k, d
        if run >= 3 and run >= best:
            flush()
            out += bytes([run, data[i]])
            i += run
        elif best >= 3:
            flush()
            out += bytes([0xC0 | best, dist])
            i += best
        else:
            lit.append(data[i])
            i += 1
    flush()
    out.append(0)
    return bytes(out)


def decompress(src, start=0):
    """Returns (data, compressed length)."""
    out, o = bytearray(), start
    while True:
        n = src[o]
        o += 1
        if n == 0:
            break
        if n < 0x80:
            out += bytes([src[o]]) * n
            o += 1
        elif n < 0xC0:
            k = n & 0x3F
            out += src[o:o + k]
            o += k
        else:
            k, d = n & 0x3F, src[o]
            o += 1
            for _ in range(k):
                out.append(out[-d])
    return bytes(out), o - start


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "-d":
        open(args[2], "wb").write(decompress(open(args[1], "rb").read())[0])
    elif len(args) == 2:
        open(args[1], "wb").write(compress(open(args[0], "rb").read()))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
