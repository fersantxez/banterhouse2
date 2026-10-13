#!/usr/bin/env python3
"""Decode 2CDT CPC records; verify CRCs, load/entry and exact game bytes."""
import binascii
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def check(tape, binary, mapping):
    raw = Path(tape).read_bytes()
    assert raw[:8] == b'ZXTape!\x1a', 'Invalid CDT signature'
    entry = int(re.search(r'^\s*([0-9A-F]{8})\s+_main\s', Path(mapping).read_text(), re.M)[1], 16)
    data = Path(binary).read_bytes()
    cursor, payload, header, blocks = 10, bytearray(), None, 0
    while cursor < len(raw):
        kind = raw[cursor]
        cursor += 1
        if kind == 0x20:
            cursor += 2
            continue
        assert kind == 0x11, f'Unsupported CDT record {kind:02x}'
        size = int.from_bytes(raw[cursor+15:cursor+18], 'little')
        cursor += 18
        record = raw[cursor:cursor+size]
        cursor += size
        assert len(record) == size and (size-5) % 258 == 0
        decoded = bytearray()
        for offset in range(1, size-4, 258):
            chunk = record[offset:offset+256]
            crc = int.from_bytes(record[offset+256:offset+258], 'big')
            assert crc == (binascii.crc_hqx(chunk, 0xffff) ^ 0xffff), 'CPC tape CRC mismatch'
            decoded.extend(chunk)
        if record[0] == 0x2c:
            assert header is None
            header = decoded
            blocks += 1
            assert header[16] == blocks and header[18] == 2
            assert int.from_bytes(header[21:23], 'little') == 0x100 + len(payload), 'Tape LOAD differs from binary'
            assert int.from_bytes(header[26:28], 'little') == entry, 'Tape EXEC differs from map'
            assert int.from_bytes(header[24:26], 'little') == len(data)
            assert header[23] == (255 if blocks == 1 else 0), 'Invalid first block flag'
        else:
            assert record[0] == 0x16 and header is not None
            size = int.from_bytes(header[19:21], 'little')
            payload.extend(decoded[:size])
            assert header[17] == (255 if len(payload) == len(data) else 0), 'Invalid last block flag'
            header = None
    assert header is None and payload == data, 'Tape payload differs from binary'
    return blocks, entry


if __name__ == '__main__':
    blocks, entry = check(ROOT/'build/DEVUELTO.cdt', ROOT/'build/DEVUELTO.bin', ROOT/'build/DEVUELTO.map')
    print(f'PASS CDT: {blocks} blocks, all CRCs valid, exact BIN, LOAD &0100, EXEC &{entry:04X}')
