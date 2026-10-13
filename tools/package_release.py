#!/usr/bin/env python3
"""Copy only a gate-approved candidate DSK into the user-facing dist folder."""
from pathlib import Path
import argparse, hashlib, json, shutil
from validate_release_evidence import validate, ROOT

def package(evidence, output):
    proof = validate(evidence)
    source = ROOT / proof['candidate']['dsk']
    destination = Path(output)
    destination = destination if destination.is_absolute() else ROOT / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    if digest != proof['candidate']['dsk_sha256']:
        destination.unlink(missing_ok=True)
        raise ValueError('copia destino no coincide con candidato aprobado')
    if destination.parent == ROOT / 'dist':
        launcher = destination.parent / 'Jugar.command'
        launcher.write_text('''#!/bin/sh\n# Lanzador del paquete distribuible desde la carpeta dist.\nPROJECT_ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd) || exit 1\nexec /usr/bin/python3 "$PROJECT_ROOT/tools/run_game.py" "$PROJECT_ROOT/dist/Devuelto-CPC6128.dsk"\n''')
        launcher.chmod(0o755)
        guide = destination.parent / 'LEEME.txt'
        guide.write_text(f'''¡DEVUELTO! — Banterhouse 2\n\nPlataforma objetivo: Amstrad CPC 6128 clásico, 128 KiB.\n\nmacOS: abre Jugar.command. En el menú, pulsa Espacio para empezar.\nCPC real o emulador CPC: carga el DSK y ejecuta RUN"DEVUELTO.BIN".\n\nLa campaña no necesita residir entera en memoria. El disco contiene el programa\nDEVUELTO.BIN y cuatro paquetes AMSDOS independientes (CH01.BIN–CH04.BIN).\nEl juego carga los datos del capítulo al cambiar de capítulo y reutiliza la\nmemoria de cada paquete. Mantén este DSK disponible durante la partida.\n\nControles: cursores mueven/saltan/bajan; Espacio o X devuelve; P pausa;\nR reinicia la arena actual.\n\nSHA-256 DSK: {digest}\nSHA-256 Jugar.command: {hashlib.sha256(launcher.read_bytes()).hexdigest()}\n\nVerificación: ../research/release-validation.json\n''')
        files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (destination, launcher, guide)}
    else:
        files = {destination.name: digest}
    manifest = {'schema_version':2,'files':files,'target':'Amstrad CPC 6128 clásico, 128 KiB','layout':'DEVUELTO.BIN más cuatro activos AMSDOS de capítulo, cargados y reutilizados desde disco entre transiciones.','boot':'macOS: doble clic en Jugar.command; CPC: RUN"DEVUELTO.BIN"','verification':str(Path(evidence).relative_to(ROOT)) if Path(evidence).is_relative_to(ROOT) else str(evidence),'campaign_scope':'24 arenas, dos campañas Caprice32, una campaña 1984, cargas por capítulo verificadas','limitations':['No se ha probado en CPC físico.','La prueba de campaña usa replay determinista; los controles manuales y el reintento se probaron aparte.','El prototipo no implementa todas las escenas narrativas previstas.']}
    (destination.parent/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return destination,digest

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,default=ROOT/'research/release-validation.json');p.add_argument('--output',type=Path,default=ROOT/'dist/Devuelto-CPC6128.dsk');a=p.parse_args()
    try: dest,sha=package(a.evidence,a.output)
    except (ValueError,KeyError,FileNotFoundError,TypeError) as e: raise SystemExit('RELEASE BLOCKED: '+str(e))
    print(f'Packaged {dest} ({dest.stat().st_size} bytes), SHA-256 {sha}')
