"""Prepare and assess the pilot's three-method analyst exercise."""
import csv
import json
from collections import defaultdict
from contextlib import closing
from pathlib import Path
from statistics import median

from .database import connect
from .evaluation_protocol import Reviewer, file_sha, load_bundle
from .ingestion import day
from .research_repository import dossier
from .research_validation import decode_packet
from .retrieval import compare

METHODS = ('manual', 'lexical_b0', 'curated_dossiers')
COLUMNS = ('query_id', 'method', 'analyst_id', 'elapsed_seconds', 'answer', 'evidence_and_search_log',
           'reviewer_id', 'usefulness_grade', 'material_errors', 'review_rationale', 'reviewed_on')
BRIEF = (
    'Identify up to three relevant healthtech references for the project and question. '
    'Describe what each evaluation or deployment source establishes and one material limit. '
    'Give a source and passage locator for each material claim. '
    'If the evidence is insufficient, describe the most important gap and your search.'
)


def export_task_review(output: Path, research_results):
    """Write prompts, frozen method outputs and a blank measurement worksheet."""
    bundle = output / 'lexical-bundle'
    manifest, _, bank = load_bundle(bundle)
    tasks = [task for task in bank.tasks if task.split == 'development' and task.status == 'runnable']
    by_query = {row['query_id']: row['result'] for row in research_results}
    if set(by_query) != {task.query_id for task in tasks} or len(by_query) != len(research_results):
        raise ValueError('Lexical and research task IDs must agree')
    rubric = dict(brief=BRIEF, usefulness={
        '0': 'Unusable answer or unsupported claim central to the decision.',
        '1': 'Relevant lead with a material gap in sourcing, applicability or outcome description.',
        '2': 'A useful sourced result or justified abstention with a concrete next evidence gap.',
        '3': 'A useful sourced result that also makes the applicable workflow, evidence and timing clear.',
    })
    cards = []
    results = []
    with closing(connect(bundle/'corpus.sqlite')) as conn:
        for task in tasks:
            comparison = by_query[task.query_id]
            if comparison['as_of'] != manifest['evidence_as_of']:
                raise ValueError('The dossier and lexical task cutoffs must agree')
            subject = dossier(conn, comparison['subject_id'])['subject']
            cards.append(dict(query_id=task.query_id, project_subject_id=subject['subject_id'],
                project_name=subject['display_name'], project_description=task.query_text,
                question=comparison['question'], focus=task.inclusion_criteria,
                research_cutoff=manifest['evidence_as_of']))
            results.append(dict(query_id=task.query_id,
                result=compare(conn, query=task.query_text, mode=task.mode, policy=manifest['policy'])))
    (output/'task-cards.json').write_text(json.dumps(dict(rubric=rubric, tasks=cards), indent=2)+'\n')
    (output/'lexical-evidence.json').write_text(json.dumps(results, indent=2)+'\n')
    with (output/'task-runs.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(COLUMNS)
        for task in tasks:
            for method in METHODS:
                writer.writerow([task.query_id, method, *([''] * (len(COLUMNS)-2))])
    inputs = ('task-cards.json', 'lexical-evidence.json', 'research-results.json')
    review = {
        'format_version': 'healthtech-task-review:1',
        'research_cutoff': manifest['evidence_as_of'],
        'lexical_manifest_id': manifest['manifest_id'],
        'tasks': [task.query_id for task in tasks],
        'methods': list(METHODS),
        'files': {name:file_sha(output/name) for name in inputs},
        'held_out_pending': [task.query_id for task in bank.tasks if task.status == 'awaiting_evidence'],
    }
    (output/'task-review-inputs.json').write_text(json.dumps(review, indent=2)+'\n')


def _nonnegative_int(value, label):
    if not value.isdecimal():
        raise ValueError(f'{label} must be a nonnegative integer')
    return int(value)


def report_task_review(directory: Path, runs: Path, reviewers_file: Path, as_of: str):
    """Summarise submitted human observations with explicit task denominators."""
    day(as_of)
    inputs = decode_packet((directory/'task-review-inputs.json').read_bytes())
    expected_files = {'task-cards.json','lexical-evidence.json','research-results.json'}
    if inputs['format_version'] != 'healthtech-task-review:1' or set(inputs['files']) != expected_files:
        raise ValueError('Unsupported task review inputs')
    for name, expected in inputs['files'].items():
        if file_sha(directory/name) != expected:
            raise ValueError('Task review inputs changed: '+name)
    registry = [Reviewer.model_validate(d) for d in decode_packet(reviewers_file.read_bytes())]
    reviewers = {r.reviewer_id:r for r in registry}
    if len(registry) != len(reviewers):
        raise ValueError('Duplicate reviewer registration')

    records = {}
    rows_seen = set()
    analysts_seen = set()
    with runs.open(newline='') as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or []) != COLUMNS:
            raise ValueError('Task-run worksheet columns differ from the supplied template')
        for row in reader:
            key = (row['query_id'], row['method'])
            if None in row or None in row.values() or key[0] not in inputs['tasks'] or key[1] not in METHODS or key in rows_seen:
                raise ValueError('Invalid or duplicate task/method row')
            rows_seen.add(key)
            if all(not row[column].strip() for column in COLUMNS[2:]):
                continue
            if any(not row[column].strip() for column in COLUMNS[2:]):
                raise ValueError('Complete the analyst and reviewer fields for '+str(key))
            analyst = reviewers.get(row['analyst_id'])
            reviewer = reviewers.get(row['reviewer_id'])
            if (not analyst or not reviewer or analyst.reviewer_id == reviewer.reviewer_id
                or not reviewer.independent_of_author):
                raise ValueError('A registered analyst and a separate registered independent reviewer are required')
            analyst_task = (analyst.reviewer_id, key[0])
            if analyst_task in analysts_seen:
                raise ValueError('Each analyst can measure one method per task')
            analysts_seen.add(analyst_task)
            elapsed = _nonnegative_int(row['elapsed_seconds'], 'Elapsed seconds')
            grade = _nonnegative_int(row['usefulness_grade'], 'Usefulness grade')
            errors = _nonnegative_int(row['material_errors'], 'Material errors')
            if elapsed == 0 or grade > 3:
                raise ValueError('Enter positive elapsed seconds and usefulness grade 0–3')
            reviewed_on = day(row['reviewed_on'])
            if not inputs['research_cutoff'] <= reviewed_on <= as_of:
                raise ValueError('Review date is outside the validation period')
            records[key] = dict(row, elapsed_seconds=elapsed, usefulness_grade=grade, material_errors=errors)

    by_task = defaultdict(set)
    for task, method in records:
        by_task[task].add(method)
    complete = sorted(task for task, methods in by_task.items() if methods == set(METHODS))
    summary = {}
    for method in METHODS:
        paired = [records[task, method] for task in complete]
        useful = [row for row in paired if row['usefulness_grade'] >= 2 and row['material_errors'] == 0]
        summary[method] = {
            'reviewed_runs': sum(key[1] == method for key in records),
            'runs_on_complete_tasks': len(paired),
            'useful_without_material_error': len(useful),
            'median_seconds_to_useful_answer': median(row['elapsed_seconds'] for row in useful) if useful else None,
            'material_errors_on_complete_tasks': sum(row['material_errors'] for row in paired) if paired else None,
        }
    return dict(format_version='healthtech-task-review-report:1',
        status='human_review_supplied' if records else 'not_evaluated',
        observations=[records[key] for key in sorted(records)],
        complete_task_ids=complete, expected_task_count=len(inputs['tasks']), summary=summary,
        input_sha256s=dict(manifest=file_sha(directory/'task-review-inputs.json'), task_runs=file_sha(runs), reviewers=file_sha(reviewers_file)),
        scope='Descriptive results on complete development tasks using different evidence corpora.',
        held_out_pending=inputs['held_out_pending'])
