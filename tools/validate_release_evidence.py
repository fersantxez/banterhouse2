#!/usr/bin/env python3
"""Validate evidence and candidate identity before publishing a CPC release."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from check_game_snapshot import inspect

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'research/release-validation.json'
CAMPAIGNS = ('campaign_caprice_1', 'campaign_caprice_2', 'campaign_1984')
PACKAGE_RUNS = ('package_cold_launch_1', 'package_cold_launch_2', 'package_cold_launch_3')
REQUIRED_CASES = (*CAMPAIGNS, 'stability_30m', 'audio_pcm', 'modular_disk_load', 'manual_controls', *PACKAGE_RUNS)
REQUIRED_CHECKS = {
    **{name: ('cold_boot', 'all_24_arenas', 'terminal_snapshot', 'new_game_or_win_screen', 'cleanup') for name in CAMPAIGNS},
    'stability_30m': ('duration_30m', 'pause_resume', 'reload', 'candidate_image_checkpoints', 'cleanup'),
    'audio_pcm': ('melody_changes', 'bass_changes', 'tempo_stable', 'sfx_coexists', 'pause_silence_resume', 'candidate_identity'),
    'modular_disk_load': ('boot_program', 'chapter_1_load', 'chapter_2_load', 'chapter_3_load', 'chapter_4_load', 'unload_or_reuse', 'disk_integrity'),
    'manual_controls': ('movement', 'jump', 'return_action', 'pause_resume', 'death_retry', 'new_game'),
    **{name: ('cold_boot', 'start_game', 'move_jump_action', 'pause_resume', 'exit_and_cleanup', 'disk_hash_unchanged') for name in PACKAGE_RUNS},
}

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fail(message: str) -> None:
    raise ValueError(message)

def read_json(path: Path):
    try: return json.loads(path.read_text())
    except Exception as exc: fail(f'JSON inválido {path}: {exc}')

def validate(evidence=EVIDENCE, candidate=None):
    evidence = Path(evidence)
    if not evidence.is_file(): fail('Falta manifiesto N09 estructurado')
    proof = read_json(evidence)
    if proof.get('schema_version') != 2: fail('schema_version debe ser 2')
    if proof.get('release_status') != 'candidate_verified': fail('candidato ausente, revocado o no aprobado por gate')
    cand = proof.get('candidate', {})
    for key in ('dsk', 'bin', 'map'):
        rel = cand.get(key)
        expected = cand.get(key + '_sha256')
        if not isinstance(rel, str) or not isinstance(expected, str) or len(expected) != 64:
            fail('Identidad incompleta del candidato: ' + key)
        path = Path(candidate) if candidate and key == 'dsk' else ROOT / rel
        if not path.is_file() or digest(path) != expected: fail('Hash candidato no coincide: ' + key)
    dsk_hash = cand['dsk_sha256']
    evidence_files = proof.get('evidence_files')
    if not isinstance(evidence_files, dict) or not evidence_files: fail('Falta índice de evidencias con hashes')
    for evidence_id, record in evidence_files.items():
        if not isinstance(record, dict) or not isinstance(record.get('path'), str) or not isinstance(record.get('sha256'), str): fail('Evidencia sin ruta/hash: ' + str(evidence_id))
        p = ROOT / record['path']
        if not p.is_file() or digest(p) != record['sha256']: fail('Evidencia falta o fue alterada: ' + str(evidence_id))
    cases = proof.get('cases')
    if not isinstance(cases, list): fail('Faltan casos estructurados')
    by_id = {c.get('case_id'): c for c in cases if isinstance(c, dict)}
    missing = sorted(set(REQUIRED_CASES) - set(by_id))
    if missing: fail('Casos ausentes: ' + ', '.join(missing))
    for cid in REQUIRED_CASES:
        case = by_id[cid]
        if case.get('status') != 'PASS': fail(f'{cid}: estado no PASS')
        if case.get('candidate_dsk_sha256') != dsk_hash: fail(f'{cid}: disco distinto')
        checks = case.get('checks')
        if not isinstance(checks, dict): fail(f'{cid}: faltan resultados por comprobación')
        for check in REQUIRED_CHECKS[cid]:
            item = checks.get(check)
            if not isinstance(item, dict) or item.get('status') != 'PASS': fail(f'{cid}: comprobación pendiente/fallida {check}')
            refs = item.get('evidence')
            if not isinstance(refs, list) or not refs: fail(f'{cid}: comprobación sin evidencia {check}')
            for ref in refs:
                if ref not in evidence_files: fail(f'{cid}: evidencia no indexada {ref}')
        if case.get('active_process_count_after') != 0: fail(f'{cid}: quedaron procesos del emulador')
        if case.get('emulator_processes_after') != []: fail(f'{cid}: inventario ambiguo o con emuladores activos')
        if isinstance(case.get('session_result'), str):
            result = read_json(ROOT / case['session_result'])
            if result.get('status') != 'pass' or result.get('timed_out') or result.get('cleanup', {}).get('process_group_absent') is not True:
                fail(f'{cid}: ejecución bloqueada, agotada o sin cleanup')
    # Campaign reports and snapshots must be actual CPC RAM from this exact linked image.
    for cid in CAMPAIGNS:
        c = by_id[cid]
        snapshot = c.get('snapshot')
        report_path = c.get('campaign_report')
        result_path = c.get('session_result')
        if not all(isinstance(x, str) for x in (snapshot, report_path, result_path)): fail(f'{cid}: metadatos ausentes')
        report = read_json(ROOT / report_path); result = read_json(ROOT / result_path)
        if report.get('candidate_dsk_sha256') != dsk_hash or result.get('status') != 'pass' or result.get('timed_out') or result.get('cleanup', {}).get('process_group_absent') is not True: fail(f'{cid}: sesión/disco no válido')
        if c.get('kind') == '1984':
            inspect(ROOT / snapshot, complete=True, map_path=ROOT / cand['map'], bin_path=ROOT / cand['bin'])
        else:
            inspect(ROOT / snapshot, complete=True, map_path=ROOT / cand['map'], bin_path=ROOT / cand['bin'])
        if report.get('stage') != 24 or report.get('completed') != list(range(1,25)) or report.get('error') != 0: fail(f'{cid}: campaña incompleta')
    stable = by_id['stability_30m']
    stable_result = read_json(ROOT / stable['session_result'])
    if stable_result.get('status') != 'pass' or stable_result.get('timed_out') or stable_result.get('duration_seconds', 0) < 1800 or stable_result.get('cleanup', {}).get('process_group_absent') is not True: fail('estabilidad <30 min, timeout o cleanup pendiente')
    if len(stable.get('snapshots', [])) < 3: fail('faltan checkpoints de estabilidad')
    for snap in stable['snapshots']:
        inspect(ROOT / snap, map_path=ROOT / cand['map'], bin_path=ROOT / cand['bin'], require_demo=False)
    audio = read_json(ROOT / by_id['audio_pcm']['analysis'])
    if audio.get('candidate_dsk_sha256') != dsk_hash: fail('audio PCM no medido con el DSK candidato')
    metrics = audio.get('metrics', {})
    if metrics.get('distinct_melody_bins_10hz', 0) < 8 or metrics.get('distinct_bass_bins_5hz', 0) < 8 or not metrics.get('tempo_stable_near_125_bpm') or not metrics.get('sfx_detected') or not metrics.get('pause_silence_then_resume'):
        fail('PCM no demuestra melodía, bajo, tempo, SFX y pausa/reanudación')
    # The modular image is separately parsed: one boot BIN plus four AMSDOS chapter assets.
    modular = read_json(ROOT / by_id['modular_disk_load']['disk_report'])
    if modular.get('disk_sha256') != dsk_hash or modular.get('chapter_assets_loaded') != 4: fail('informe de activos modulares no coincide')
    for cid in PACKAGE_RUNS:
        case = by_id[cid]
        session_path = case.get('session_json')
        if not isinstance(session_path, str): fail(f'{cid}: falta manifiesto de sesión')
        session = read_json(ROOT / session_path)
        command = session.get('command', [])
        expected_dsk = str((ROOT / 'dist/Devuelto-CPC6128.dsk').resolve())
        if expected_dsk not in command: fail(f'{cid}: no se lanzó el DSK publicado por Jugar.command')
    dist = ROOT / 'dist/Devuelto-CPC6128.dsk'
    if not dist.is_file() or digest(dist) != dsk_hash: fail('dist no contiene exactamente los bytes aprobados')
    return proof

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, default=EVIDENCE)
    p.add_argument('--candidate', type=Path, help='DSK source override used by negative tests')
    a = p.parse_args()
    try: proof = validate(a.evidence, a.candidate)
    except (ValueError, KeyError, FileNotFoundError, TypeError) as e: raise SystemExit('RELEASE BLOCKED: ' + str(e))
    print(f"PASS release gate: {len(proof['cases'])} structured cases, exact DSK {proof['candidate']['dsk_sha256']}")
