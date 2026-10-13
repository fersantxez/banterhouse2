#!/usr/bin/env python3
"""N09 negative cases: prove bad evidence is rejected before dist changes."""
from __future__ import annotations
import copy, hashlib, json, tempfile
from pathlib import Path
from validate_release_evidence import EVIDENCE, ROOT, validate

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def reject(label, proof, candidate=None):
    with tempfile.NamedTemporaryFile('w', suffix='.json', dir=ROOT/'research/runs/20261013T-N09-package', delete=False) as f:
        json.dump(proof, f); path=Path(f.name)
    try:
        try: validate(path,candidate)
        except (ValueError,KeyError,FileNotFoundError,TypeError): print('PASS reject '+label)
        else: raise AssertionError(label+' was accepted')
    finally: path.unlink(missing_ok=True)

original=validate(EVIDENCE)
dist=ROOT/'dist/Devuelto-CPC6128.dsk'; before=digest(dist)
# Snapshot from a previous binary cannot prove this candidate's linked image.
p=copy.deepcopy(original); p['cases'][0]['snapshot']='snapshot_20261013_134610.sna'; reject('snapshot from another build',p)
# Even a self-consistent old disk file cannot be substituted for the approved candidate.
old=ROOT/'research/runs/20261013T-N09-package/prior-dist/Devuelto-CPC6128.dsk'
p=copy.deepcopy(original); reject('old disk image',p,old)
# A child exit code is insufficient when the run timed out or failed.
p=copy.deepcopy(original); p['cases'][0]['session_result']='research/runs/20261013T-N09-audio-sfx/sessions/20261013T201356Z-session-04af997f/result.json'; reject('incomplete/timeout run',p)
p=copy.deepcopy(original); next(c for c in p['cases'] if c['case_id']=='stability_30m')['snapshots']=[]; reject('omitted stability checkpoints',p)
p=copy.deepcopy(original); next(c for c in p['cases'] if c['case_id']=='package_cold_launch_1')['emulator_processes_after']=['cap32','cap32']; reject('ambiguous multiple emulator processes',p)
# A low-quality audio report is made as a temporary, hash-indexed evidence item.
with tempfile.TemporaryDirectory(prefix='gate-audio-',dir=ROOT/'research/runs/20261013T-N09-package') as td:
    poor=Path(td)/'audio.json'; obj=json.loads((ROOT/original['cases'][4]['analysis']).read_text()); obj['metrics']['distinct_melody_bins_10hz']=1; poor.write_text(json.dumps(obj))
    p=copy.deepcopy(original); c=next(c for c in p['cases'] if c['case_id']=='audio_pcm'); c['analysis']=str(poor.relative_to(ROOT)); p['evidence_files']['audio_report']={'path':str(poor.relative_to(ROOT)),'sha256':digest(poor)}; reject('audio without melody',p)
p=copy.deepcopy(original); next(c for c in p['cases'] if c['case_id']=='stability_30m')['active_process_count_after']=1; reject('cleanup pending',p)
p=copy.deepcopy(original); p['evidence_files']['music_wav']['sha256']='0'*64; reject('tampered evidence manifest',p)
if digest(dist)!=before: raise AssertionError('negative gate tests touched dist')
validate(EVIDENCE)
print('PASS original gate remains valid; dist unchanged at '+before)
