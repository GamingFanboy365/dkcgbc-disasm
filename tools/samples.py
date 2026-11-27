#!/usr/bin/env python3
"""Funky's Fishing's digitized sounds, between the ROM and WAV files.

The game plays one byte per two scanlines (72 a frame, about 4300 per
second) by writing it to NR50, the master volume, while every channel holds
a constant tone. Both nibbles of a byte carry the same 3-bit level, so 4 is
silence. A WAV file here is 8-bit mono at 4300 Hz with level v stored as
32 * v (silence = 128); converting back keeps the top three bits, so an edited
or re-recorded sound is simply quantized.

  python3 tools/samples.py wav in.wav out.pcm    WAV -> ROM bytes
  python3 tools/samples.py -d in.pcm out.wav     ROM bytes -> WAV
"""
import struct
import sys
import wave

RATE = 4300


def to_wav(data, path):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(RATE)
        w.writeframes(bytes((b & 7) << 5 for b in data))


def from_wav(path):
    with wave.open(path, "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 1:
            raise SystemExit("%s: expected 8-bit mono" % path)
        frames = w.readframes(w.getnframes())
    return bytes((x >> 5) * 0x11 for x in frames)


def main():
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "-d":
        to_wav(open(a[1], "rb").read(), a[2])
    elif len(a) == 3 and a[0] == "wav":
        open(a[2], "wb").write(from_wav(a[1]))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
