#!/usr/bin/env python3
"""Comprueba cuotas propuestas de campaña; no inspecciona un DSK ni un linker."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    plan = json.loads((ROOT / 'research/campaign-storage-budget.json').read_text())
    geometry = plan['geometry']
    raw = (geometry['tracks_per_side'] * geometry['sectors_per_track']
           * geometry['sector_bytes'])
    available = raw - geometry['directory_bytes']
    sides = {}
    for name, quotas in plan['sides'].items():
        assert all(isinstance(v, int) and v >= 0 for v in quotas.values())
        total = sum(quotas.values())
        assert total == available, (name, total, available)
        sides[name] = {
            'raw_bytes': raw,
            'after_directory_bytes': available,
            'assigned_including_overheads_bytes': total - quotas['unassigned_reserve'],
            'unassigned_reserve_bytes': quotas['unassigned_reserve'],
            'sum_bytes': total,
        }
    memory = json.loads((ROOT / 'research/memory-budgets.json').read_text())
    banks = memory['architectures']['A']['banks']
    assert sorted(b['bank'] for b in banks) == list(range(8))
    for bank in banks:
        end = 0
        for region in sorted(bank['regions'], key=lambda r: r['offset']):
            assert region['offset'] == end
            end += region['bytes']
        assert end == 16384
    scratch = next(r['bytes'] for b in banks if b['bank'] == 2
                   for r in b['regions'] if r['name'] == 'scratch_foreground')
    assert plan['independent_block_input_max_bytes'] <= scratch
    assert plan['independent_block_output_max_bytes'] <= 16384
    result = {
        'result': 'PASS_arithmetic_only_not_asset_fit_or_hardware_validation',
        'sides': sides,
        'candidate_A_physical_bytes_reserved': 8 * 16384,
        'fixed_staging_bytes_reserved': scratch,
        'illustrative_background_bytes': 256 * 32 + 5 * 20 * 25,
        'illustrative_sprites_six_poses_bytes': 6 * 2 * (8 + 9) * 32 * 2,
        'illustrative_sprites_eight_poses_bytes': 8 * 2 * (8 + 9) * 32 * 2,
        'measured_disk_loads': None,
        'actual_campaign_packed_bytes': None,
    }
    (ROOT / 'research/results/campaign-budget-check.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
