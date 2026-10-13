#!/usr/bin/env python3
"""Convert the approved portrait cover to classic CPC Mode 0, without redraws."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

import build_cpc_screen_studies as cpc

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/loading'
SOURCE = ART / 'banterhouse2-portada-vazquez.png'


def main():
    # A 4:3 CPC display has 5:3 Mode 0 pixels. An 80x200 portrait region
    # therefore displays at 2:3, the original 1024x1536 cover's aspect ratio.
    raw = subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(SOURCE),
        '-vf', 'scale=80:200:flags=area,eq=contrast=1.12:saturation=1.15',
        '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1',
    ], check=True, stdout=subprocess.PIPE).stdout
    if len(raw) != 80 * 200 * 3:
        raise SystemExit('Unexpected image dimensions')
    colors = [tuple(cpc.rgb(i)) for i in range(27)]

    def nearest(pixel, palette):
        return min(palette, key=lambda code: sum(
            weight * (a-b)**2 for weight, a, b in zip((2, 4, 1), pixel, colors[code])))

    samples = [raw[i:i+3] for i in range(0, len(raw), 3)]
    counts = Counter(nearest(p, range(27)) for p in samples)
    # Black, white, yellow and red also serve the restrained loading labels.
    palette = [0, 26, 24, 6]
    palette += [code for code, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
                if code not in palette][:12]
    if len(palette) != 16:
        raise SystemExit('Expected sixteen classic CPC inks')
    canvas = cpc.Canvas()
    for y in range(200):
        for x in range(80):
            canvas.dot(x + 40, y, palette.index(nearest(samples[y*80+x], palette)))
    # Side gutters retain the full composition and readable CPC lettering.
    canvas.rect(36, 0, 1, 200, 2)
    canvas.rect(123, 0, 1, 200, 2)
    canvas.text(4, 82, 'CPC', 2, 2, 2)
    canvas.text(4, 99, '6128', 1)
    canvas.text(4, 111, '128K', 1)
    canvas.text(128, 91, 'UN SELLO', 2)
    canvas.text(128, 102, 'Y PUNTO!', 1)
    canvas.text(126, 177, 'CARGANDO', 2)
    for x in (136, 140, 144):
        canvas.rect(x, 188, 1, 2, 1)
    frame = bytes(canvas.p)
    screen = cpc.to_scr(frame)
    assert cpc.from_scr(screen) == frame
    (ART / 'banterhouse2-loading.scr').write_bytes(screen)
    (ART / 'banterhouse2-loading.fwpal').write_bytes(bytes(palette))
    (ART / 'banterhouse2-loading.hwpal').write_bytes(bytes(0x40 | cpc.HW[p] for p in palette))
    cpc.png(ART / 'banterhouse2-loading.native.png', frame, palette)
    cpc.png(ART / 'banterhouse2-loading-preview.png', frame, palette, 5, 3)
    (ART / 'loading-manifest.json').write_text(json.dumps({
        'source': SOURCE.name, 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'screen_sha256': hashlib.sha256(screen).hexdigest(), 'mode': 0,
        'dimensions': [160, 200], 'screen_bytes': len(screen), 'firmware_palette': palette,
        'image_region': [40, 0, 80, 200], 'display_pixel_aspect': '5:3',
        'full_source_preserved': True, 'dithering': False,
        'conversion': 'ffmpeg area scale; contrast 1.12, saturation 1.15; nearest classic CPC inks',
    }, indent=2) + '\n')
    print(f'Converted approved cover: 160x200 Mode 0, 16 inks, {len(screen)} bytes')


if __name__ == '__main__':
    main()
