#!/usr/bin/env python3
"""Comprueba documentos y seguimiento; nunca compila ni ejecuta el CPC."""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/implementation'


def validate_graph(tasks):
    ids = [t['id'] for t in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError('ID de tarea duplicado')
    by_id = {t['id']: t for t in tasks}
    for task in tasks:
        if task['status'] not in {'pending', 'in_progress', 'blocked', 'done'}:
            raise ValueError(f"Estado inválido: {task['id']}")
        deps = task['depends_on']
        if len(deps) != len(set(deps)):
            raise ValueError(f"Dependencia duplicada: {task['id']}")
        for dep in deps:
            if dep not in by_id:
                raise ValueError(f"Dependencia ausente: {task['id']} -> {dep}")
        if task['status'] == 'done':
            if not task['evidence']:
                raise ValueError(f"Tarea done sin evidencia: {task['id']}")
            if any(by_id[d]['status'] != 'done' for d in deps):
                raise ValueError(f"Tarea done con dependencia sin cerrar: {task['id']}")
    visiting, visited = set(), set()

    def walk(id_):
        if id_ in visiting:
            raise ValueError(f'Ciclo de dependencias: {id_}')
        if id_ in visited:
            return
        visiting.add(id_)
        for dep in by_id[id_]['depends_on']:
            walk(dep)
        visiting.remove(id_)
        visited.add(id_)

    for id_ in ids:
        walk(id_)
    return by_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Informe nuevo; no sobrescribe uno anterior')
    args = parser.parse_args()
    state = json.loads((DOC / 'STATUS.json').read_text())
    tasks = state['tasks']
    by_id = validate_graph(tasks)
    expected = {f'T{i:02}' for i in range(1, 36)} | {f'O{i:02}' for i in range(17)}
    if set(by_id) != expected:
        raise ValueError('Inventario de tareas distinto de T01–T35 y O00–O16')
    headings = {}
    for name in ('TASKS.md', 'OPTIMIZATION_TASKS.md'):
        content = (DOC / name).read_text()
        sections = re.split(r'^## ([TO]\d{2}) (.+)$', content, flags=re.M)
        for index in range(1, len(sections), 3):
            id_, title, body = sections[index:index+3]
            if id_ in headings:
                raise ValueError(f'Ficha duplicada: {id_}')
            headings[id_] = title.strip()
            match = re.search(r'^\*\*Depende de:\*\* ([^.]+)\.', body, re.M)
            if not match:
                raise ValueError(f'Ficha sin dependencias explícitas: {id_}')
            deps = re.findall(r'\b[TO]\d{2}\b', match.group(1))
            if deps != by_id[id_]['depends_on']:
                raise ValueError(f'Dependencias ficha/STATUS difieren: {id_}: {deps}')
            if headings[id_] != by_id[id_]['title']:
                raise ValueError(f'Título ficha/STATUS difiere: {id_}')
    if set(headings) != expected:
        raise ValueError('Faltan fichas de tareas')
    delivery = json.loads((DOC / 'DELIVERY_STATUS.json').read_text())
    delivery_by_id = validate_graph(delivery['tasks'])
    if set(delivery_by_id) != {f'E{i:02}' for i in range(5)}:
        raise ValueError('Faltan tareas E00–E04 de reparación de entrega')
    delivery_doc = (DOC / 'DELIVERY_REPAIR_PLAN.md').read_text()
    if set(re.findall(r'^## (E\d{2}) ', delivery_doc, re.M)) != set(delivery_by_id):
        raise ValueError('Fichas de entrega incompletas')
    autonomous = json.loads((DOC / 'AUTONOMOUS_STATUS.json').read_text())
    autonomous_by_id = validate_graph(autonomous['tasks'])
    if set(autonomous_by_id) != {f'N{i:02}' for i in range(11)}:
        raise ValueError('Faltan tareas N00–N10 de reparación autónoma')
    autonomous_doc = (DOC / 'AUTONOMOUS_REPAIR_PLAN.md').read_text()
    sections = re.split(r'^## (N\d{2}) (.+)$', autonomous_doc, flags=re.M)
    autonomous_headings = {}
    for index in range(1, len(sections), 3):
        id_, title, body = sections[index:index+3]
        if id_ in autonomous_headings:
            raise ValueError('Ficha autónoma duplicada: ' + id_)
        autonomous_headings[id_] = title.strip()
        match = re.search(r'^\*\*Depende de:\*\* ([^.]+)\.', body, re.M)
        if not match or re.findall(r'\bN\d{2}\b', match.group(1)) != autonomous_by_id[id_]['depends_on']:
            raise ValueError('Dependencias autónomas distintas: ' + id_)
        if '**Archivos:**' not in body or '**Cierre:**' not in body:
            raise ValueError('Ficha autónoma sin archivos/cierre: ' + id_)
    if autonomous_headings != {t['id']: t['title'] for t in autonomous['tasks']}:
        raise ValueError('Títulos autónomos distintos del estado')
    physics = json.loads((DOC / 'PHYSICS_STATUS.json').read_text())
    physics_by_id = validate_graph(physics['tasks'])
    physics_expected = {f'F{i:02}' for i in range(9)}
    if set(physics_by_id) != physics_expected:
        raise ValueError('Inventario de física distinto de F00–F08')
    physics_doc = (DOC / 'PHYSICS_REPAIR_PLAN.md').read_text()
    physics_headings = {}
    for match in re.finditer(r'^## (F\d{2}) (.+)$', physics_doc, re.M):
        if match.group(1) in physics_headings:
            raise ValueError(f"Ficha de física duplicada: {match.group(1)}")
        physics_headings[match.group(1)] = match.group(2).strip()
    if physics_headings != {t['id']: t['title'] for t in physics['tasks']}:
        raise ValueError('Títulos del plan y PHYSICS_STATUS difieren')
    test_text = (DOC / 'OPTIMIZATION_TESTS.md').read_text()
    test_ids = re.findall(r'^## (OP\d{2}) ', test_text, re.M)
    if len(test_ids) != 20 or set(test_ids) != {f'OP{i:02}' for i in range(1, 21)}:
        raise ValueError('Pruebas OP duplicadas o ausentes')
    paths = [ROOT / 'README.md', ROOT / 'docs/IMPLEMENTATION_PLAN.md',
             ROOT / 'docs/PROTOTYPE_PLAN.md'] + [DOC / n for n in (
                 'EXECUTOR_PROMPT.md', 'TASKS.md', 'CONTRACTS.md', 'TESTS.md',
                 'OPTIMIZATION_PLAN.md', 'OPTIMIZATION_TASKS.md', 'OPTIMIZATION_TESTS.md',
                 'PHYSICS_REPAIR_PLAN.md', 'AUTONOMOUS_REPAIR_PLAN.md',
                 'AUTONOMOUS_EXECUTOR.md')]
    local_links = 0
    for path in paths:
        content = path.read_text()
        if path.name.startswith('OPTIMIZATION'):
            refs = set(re.findall(r'\bOP\d{2}\b', content))
            if refs - set(test_ids):
                raise ValueError(f'Prueba OP desconocida en {path.name}')
        for target in re.findall(r'\[[^\]\n]+\]\(([^)]+)\)', content):
            if '://' in target or target.startswith('#'):
                continue
            filename = target.split('#', 1)[0]
            if not (path.parent / filename).exists():
                raise ValueError(f'Enlace local inexistente: {path.name}: {target}')
            local_links += 1
    # Negativos en memoria: no modifican STATUS ni el proyecto original.
    negatives = []
    for kind in ('duplicate', 'missing_dependency', 'cycle', 'done_without_evidence'):
        bad = copy.deepcopy(tasks)
        if kind == 'duplicate':
            bad.append(copy.deepcopy(bad[0]))
        elif kind == 'missing_dependency':
            bad[0]['depends_on'] = ['T99']
        elif kind == 'cycle':
            bad[0]['depends_on'] = ['T01']
        else:
            bad[0]['status'] = 'done'
            bad[0]['evidence'] = []
        try:
            validate_graph(bad)
        except ValueError:
            negatives.append(kind)
        else:
            raise ValueError(f'Negativo no rechazado: {kind}')
    enabled = [t['id'] for t in tasks if t['status'] == 'pending'
               and all(by_id[d]['status'] == 'done' for d in t['depends_on'])]
    resumable = [t['id'] for t in tasks if t['status'] == 'in_progress'
                 and all(by_id[d]['status'] == 'done' for d in t['depends_on'])]
    # H2 no bloquea la medición; producción sí. Hardware sigue separado.
    if 'T18' not in by_id['T21']['depends_on'] or 'T20' not in by_id['T21']['depends_on']:
        raise ValueError('T21 perdió gate humano/técnico')
    if 'O16' not in by_id['T34']['depends_on'] or 'O16' not in by_id['T35']['depends_on']:
        raise ValueError('Candidato sin gate de rendimiento final')
    def ancestors(id_):
        found = set()
        for dep in by_id[id_]['depends_on']:
            found.add(dep)
            found.update(ancestors(dep))
        return found
    if 'T18' in ancestors('O14'):
        raise ValueError('H2 no debe impedir la investigación de rendimiento')
    if 'T18' not in ancestors('T21') or 'T34' in ancestors('T35'):
        raise ValueError('Gate de producción/hardware incoherente')
    first_active = resumable[0] if resumable else (enabled[0] if enabled else None)
    if all(t['status'] == 'pending' for t in tasks) and enabled[0] != state['first_task']:
        raise ValueError('first_task no coincide con primera tarea habilitada')
    if state['hardware_verified'] and (by_id['T34']['status'] != 'done' or not by_id['T34']['evidence']):
        raise ValueError('Hardware sin tarea/evidencia')
    result = {
        'scope': 'Documentation validation only; no game build or CPC execution',
        'plan_version': state['plan_version'], 'task_count': len(tasks),
        'optimization_tasks': 17, 'optimization_test_cases': len(test_ids),
        'all_tasks_pending': all(t['status'] == 'pending' for t in tasks),
        'dependency_graph_acyclic': True, 'titles_and_dependencies_match': True,
        'local_links_checked': local_links, 'negative_cases_rejected': negatives,
        'first_enabled_task': first_active,
        'autonomous_task_count': len(autonomous_by_id),
        'autonomous_acceptance': autonomous['acceptance'],
        'autonomous_execution_started': autonomous['execution_started'],
        'autonomous_first_enabled_task': next((t['id'] for t in autonomous['tasks']
            if t['status'] in ('pending', 'in_progress') and all(
                autonomous_by_id[d]['status'] == 'done' for d in t['depends_on'])), None),
        'delivery_first_enabled_task': next((t['id'] for t in delivery['tasks']
            if t['status'] in ('pending','in_progress') and all(delivery_by_id[d]['status']=='done' for d in t['depends_on'])), None),
        'physics_task_count': len(physics_by_id),
        'physics_first_enabled_task': next((t['id'] for t in physics['tasks']
            if t['status'] == 'in_progress' and all(physics_by_id[d]['status'] == 'done'
                for d in t['depends_on'])), next((t['id'] for t in physics['tasks']
            if t['status'] == 'pending' and all(physics_by_id[d]['status'] == 'done'
                for d in t['depends_on'])), None)),
        'human_gate_and_hardware_dependencies_checked': True,
        'hardware_verified': state['hardware_verified'],
    }
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as handle:
            handle.write(output)
    print(output, end='')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(f'FAIL documentación: {error}')
