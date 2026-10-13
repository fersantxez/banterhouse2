#!/usr/bin/env python3
"""Valida las reservas propuestas; no valida un mapa real de linker."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    results = {}
    for name, architecture in data['architectures'].items():
        banks = architecture['banks']
        assert sorted(b['bank'] for b in banks) == list(range(8)), name
        total = 0
        for bank in banks:
            expected_base = bank['bank'] * 16384 if bank['bank'] < 4 else 16384
            assert bank['cpu_base'] == expected_base, (name, bank['bank'], 'window')
            end = 0
            for region in sorted(bank['regions'], key=lambda r: r['offset']):
                assert region['bytes'] > 0, (name, region)
                assert region['offset'] == end, (name, bank['bank'], 'overlap or gap', region)
                end += region['bytes']
            assert end == 16384, (name, bank['bank'], end)
            total += end
        assert total == 131072, (name, total)
        assert all(v >= 0 for v in architecture['time_ms'].values())
        work = sum(architecture['time_ms'].values())
        period = architecture['period_ms_nominal']
        assert work + architecture['margin_ms'] == period, name
        assert abs(work / period - .8) < 1e-9, name
        results[name] = {'physical_bytes_reserved': total, 'bank_count': 8,
                         'nominal_work_ms_proposed': work,
                         'nominal_margin_ms_proposed': architecture['margin_ms'],
                         'result': 'PASS_arithmetic_only'}
    return results


if __name__ == '__main__':
    data = json.loads((ROOT / 'research/memory-budgets.json').read_text())
    results = validate(data)
    target = ROOT / 'research/results/budget-check.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))
