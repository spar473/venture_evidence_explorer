"""Frozen, label-gated evaluation-workbench:1. No synthetic empirical results."""

import csv
import hashlib
import json
import math
import platform
import random
import shutil
import sqlite3
import statistics
import time
from pathlib import Path
from collections import defaultdict
from contextlib import closing
from typing import Literal
from unittest.mock import patch
from pydantic import StrictBool, model_validator
from .database import ROOT, connect
from .ingestion import StrictModel, Text, day
from .research_validation import decode_packet
from .repository import corpus_documents
from .retrieval import METHOD, compare
from .comparison_runs import canonical, digest, result_signature

VERSION = 'evaluation-workbench:1'
SOURCE_FILES = [
    'backend/retrieval.py',
    'backend/evidence_policy.py',
    'backend/repository.py',
    'backend/comparison_runs.py',
    'backend/evaluation_protocol.py',
]


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Task(StrictModel):
    query_id: Text
    split: Literal['development', 'held_out']
    group_id: Text
    identity_group_ids: list[Text]
    status: Literal['runnable', 'awaiting_evidence']
    query_text: str | None
    mode: Literal['product_customer', 'commercialisation', 'stage_milestone']
    inclusion_criteria: Text
    possible_closer_cases: list[Text]
    plausible_distractors: list[Text]
    evidence_gaps: list[Text]
    selection_is_relevance_judgment: StrictBool

    @model_validator(mode='after')
    def complete(self):
        if len(set(self.identity_group_ids)) != len(self.identity_group_ids):
            raise ValueError('Duplicate identity group ID')
        if self.selection_is_relevance_judgment:
            raise ValueError('Candidate selection is not a relevance grade')
        if self.status == 'runnable' and (not self.query_text or not self.identity_group_ids):
            raise ValueError('Runnable tasks need a query and declared identity cohort')
        if self.status == 'awaiting_evidence' and not self.evidence_gaps:
            raise ValueError('Pending tasks need explicit gaps')
        return self


class TaskBank(StrictModel):
    format_version: Literal['evaluation-tasks:1']
    tasks: list[Task]


class Reviewer(StrictModel):
    reviewer_id: Text
    role: Literal['owner', 'independent_reviewer', 'analyst', 'adjudicator']
    independent_of_author: StrictBool
    is_human: StrictBool

    @model_validator(mode='after')
    def human(self):
        if not self.is_human:
            raise ValueError('Human relevance judgments require an actual human reviewer declaration')
        if self.role == 'independent_reviewer' and not self.independent_of_author:
            raise ValueError('Reviewer independence declaration conflicts with role')
        return self


def task_bank(path, venture_ids):
    bank = TaskBank.model_validate(decode_packet(Path(path).read_bytes()))
    ids = set()
    groups = {}
    cohorts = {}
    for t in bank.tasks:
        if t.query_id in ids:
            raise ValueError('Duplicate task ID')
        ids.add(t.query_id)
        if t.group_id in groups and groups[t.group_id] != t.split:
            raise ValueError('Query group leaks across development/held-out splits')
        groups[t.group_id] = t.split
        for identity in t.identity_group_ids:
            if identity in cohorts and cohorts[identity] != t.split:
                raise ValueError('Related venture identity leaks across splits')
            cohorts[identity] = t.split
        for identity in [*t.possible_closer_cases, *t.plausible_distractors, *t.identity_group_ids]:
            if identity not in venture_ids:
                raise ValueError('Unknown task candidate identity: ' + identity)
    return bank


def freeze(db, output, tasks=ROOT / 'evaluation/protocol-v1/tasks.json', policy='exploration', as_of='2026-11-18'):
    day(as_of)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Frozen bundle output must be new/empty; never replace an experiment')
    output.mkdir(parents=True, exist_ok=True)
    with closing(connect(db)) as source, closing(sqlite3.connect(output / 'corpus.sqlite')) as target:
        source.backup(target)
    with closing(connect(output / 'corpus.sqlite')) as conn:
        documents = corpus_documents(conn, policy=policy)
        bank = task_bank(tasks, {r['venture_id'] for r in documents})
        if any(o['retrieved_at'] > as_of for v in documents for o in v['observations']):
            raise ValueError('Frozen evidence cutoff predates inspected sources')
        latest_review = conn.execute('SELECT MAX(substr(reviewed_at,1,10)) FROM review_events').fetchone()[0]
        if latest_review and latest_review > as_of:
            raise ValueError('Frozen evidence cutoff predates review state')
        migrations = [list(r) for r in conn.execute('SELECT * FROM schema_migrations ORDER BY version')]
    (output / 'corpus.json').write_text(canonical(documents) + '\n')
    shutil.copy2(tasks, output / 'tasks.json')
    for name in ('reviewers.json', 'judgments.csv', 'task_observations.csv', 'factual_audit.csv'):
        shutil.copy2(ROOT / 'evaluation/protocol-v1' / name, output / name)
    manifest = {
        'protocol_version': VERSION,
        'method': METHOD,
        'policy': policy,
        'evidence_policy_version': 'evidence-selection-1.0',
        'evidence_as_of': as_of,
        'cutoff_semantics': 'Frozen present-day exploration snapshot; not a historical availability backtest',
        'files': {name: file_sha(output / name) for name in ('corpus.sqlite', 'corpus.json', 'tasks.json')},
        'source_hashes': {name: file_sha(ROOT / name) for name in SOURCE_FILES},
        'migrations': migrations,
        'splits': {
            split: [t.query_id for t in bank.tasks if t.split == split] for split in ('development', 'held_out')
        },
        'tasks_pending': [t.query_id for t in bank.tasks if t.status != 'runnable'],
        'corpus_counts': {
            'identities': len(documents),
            'selected_observations': sum(len(d['observations']) for d in documents),
        },
        'limits': [
            'Candidate pools and distractor suggestions are protocol hypotheses, not relevance judgments',
            'Held-out cohort is explicitly pending independent sourced evidence',
            'No exhaustive recall is reported',
        ],
    }
    manifest['manifest_id'] = digest(manifest)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def load_bundle(bundle):
    manifest = decode_packet((bundle / 'manifest.json').read_bytes())
    body = dict(manifest)
    mid = body.pop('manifest_id')
    if digest(body) != mid or manifest['protocol_version'] != VERSION:
        raise ValueError('Frozen manifest checksum/version mismatch')
    for name, expected in manifest['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or file_sha(bundle / name) != expected:
            raise ValueError('Frozen input drift: ' + name)
    for name, expected in manifest['source_hashes'].items():
        if name not in SOURCE_FILES or file_sha(ROOT / name) != expected:
            raise ValueError('Method/software drift: ' + name)
    if set(manifest['files']) != {'corpus.sqlite', 'corpus.json', 'tasks.json'} or set(
        manifest['source_hashes']
    ) != set(SOURCE_FILES):
        raise ValueError('Incomplete frozen input/method manifest')
    if manifest['method'] != METHOD:
        raise ValueError('Unsupported frozen method parameters')
    corpus = decode_packet((bundle / 'corpus.json').read_bytes())
    with closing(connect(bundle / 'corpus.sqlite')) as conn:
        if canonical(corpus_documents(conn, policy=manifest['policy'])) != canonical(corpus):
            raise ValueError('Frozen corpus projection disagrees with database/policy')
        if [list(r) for r in conn.execute('SELECT * FROM schema_migrations ORDER BY version')] != manifest[
            'migrations'
        ]:
            raise ValueError('Frozen migration history mismatch')
    ids = {v['venture_id'] for v in corpus}
    bank = task_bank(bundle / 'tasks.json', ids)
    return manifest, corpus, bank


def review_materials(bundle, output):
    manifest, corpus, bank = load_bundle(bundle)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Review output must be new/empty; never overwrite human work')
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'review_sheet.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                'query_id',
                'venture_id',
                'reviewer_id',
                'relevance_grade',
                'rationale',
                'supporting_observation_ids',
                'reviewed_on',
            ]
        )
        for t in bank.tasks:
            if t.status == 'runnable':
                for v in corpus:
                    writer.writerow([t.query_id, v['venture_id'], '', '', '', '', ''])
    criteria = []
    for t in bank.tasks:
        criteria.append(t.model_dump())
    (output / 'criteria_and_evidence_gaps.json').write_text(
        json.dumps(
            {
                'manifest_id': manifest['manifest_id'],
                'purpose': 'Inspection candidates, never positive/negative labels',
                'tasks': criteria,
            },
            indent=2,
        )
        + '\n'
    )
    for name in ('reviewers.json', 'task_observations.csv', 'factual_audit.csv'):
        # Blank files are never populated with synthetic people or observations.
        shutil.copy2(ROOT / 'evaluation/protocol-v1' / name, output / name)
    (output / 'adjudication_sheet.csv').write_text(
        'query_id,venture_id,adjudicator_id,grade,rationale,reviewed_on,prior_reviewer_ids\n'
    )
    return {
        'manifest_id': manifest['manifest_id'],
        'review_rows': sum(t.status == 'runnable' for t in bank.tasks) * len(corpus),
        'held_out_pending': [t.query_id for t in bank.tasks if t.status != 'runnable'],
    }


def read_labels(path, reviewers_path, bank, corpus, as_of):
    registry = [Reviewer.model_validate(r) for r in decode_packet(Path(reviewers_path).read_bytes())]
    if len({r.reviewer_id for r in registry}) != len(registry):
        raise ValueError('Duplicate reviewer ID')
    reviewers = {r.reviewer_id: r.model_dump() for r in registry}
    tasks = {t.query_id: t for t in bank.tasks}
    ids = {v['venture_id'] for v in corpus}
    observations = {o['observation_id']: o for v in corpus for o in v['observations']}
    labels = {}
    pending = 0
    columns = {
        'query_id',
        'venture_id',
        'reviewer_id',
        'relevance_grade',
        'rationale',
        'supporting_observation_ids',
        'reviewed_on',
    }
    with Path(path).open(newline='') as f:
        reader = csv.DictReader(f)
        if set(reader.fieldnames or []) != columns:
            raise ValueError('Judgment CSV columns do not match evaluation-workbench:1')
        for row in reader:
            if None in row:
                raise ValueError('Extra judgment columns')
            qid, vid = row['query_id'], row['venture_id']
            grade = row['relevance_grade'].strip()
            if qid not in tasks or vid not in ids:
                raise ValueError('Unknown task/venture in judgment sheet')
            if not grade:
                pending += 1
                continue
            if tasks[qid].status != 'runnable':
                raise ValueError('Cannot judge a task awaiting evidence')
            reviewer = row['reviewer_id']
            if reviewer not in reviewers:
                raise ValueError('Unknown reviewer; supply actual role/independence declaration')
            if grade not in ('0', '1', '2', '3') or not row['rationale'].strip():
                raise ValueError('Judgments need grade 0–3 and an evidence-based rationale')
            day(row['reviewed_on'])
            if row['reviewed_on'] > as_of:
                raise ValueError('Judgment after external validation date')
            refs = [r.strip() for r in row['supporting_observation_ids'].split(';') if r.strip()]
            if not refs or any(r not in observations or observations[r]['venture_id'] != vid for r in refs):
                raise ValueError('Judgment evidence is unselected, unknown or belongs to a different venture')
            if any(observations[r]['retrieved_at'] > row['reviewed_on'] for r in refs):
                raise ValueError('Judgment predates inspected source')
            key = (qid, vid, reviewer)
            if key in labels:
                raise ValueError('Duplicate reviewer/task/venture judgment')
            labels[key] = {
                **row,
                'relevance_grade': int(grade),
                'supporting_observation_ids': refs,
                'reviewer': reviewers[reviewer],
            }
    return labels, pending, reviewers


def read_factual_audit(path, bank, corpus, reviewers, as_of):
    observations = {o['observation_id']: o for v in corpus for o in v['observations']}
    tasks = {t.query_id: t for t in bank.tasks}
    seen = set()
    records = []
    columns = {
        'query_id',
        'venture_id',
        'observation_id',
        'reviewer_id',
        'entailment_status',
        'rationale',
        'reviewed_on',
    }
    with Path(path).open(newline='') as f:
        reader = csv.DictReader(f)
        if set(reader.fieldnames or []) != columns:
            raise ValueError('Factual audit columns mismatch')
        for row in reader:
            if not row['entailment_status'].strip():
                continue
            if row['entailment_status'] not in ('supported', 'contradicted', 'insufficient'):
                raise ValueError('Unknown factual audit status')
            observation = observations.get(row['observation_id'])
            if (
                row['query_id'] not in tasks
                or tasks[row['query_id']].status != 'runnable'
                or not observation
                or observation['venture_id'] != row['venture_id']
            ):
                raise ValueError('Factual audit target/evidence mismatch')
            if row['reviewer_id'] not in reviewers or not row['rationale'].strip():
                raise ValueError('Factual audit needs an actual registered reviewer and rationale')
            day(row['reviewed_on'])
            if not observation['retrieved_at'] <= row['reviewed_on'] <= as_of:
                raise ValueError('Factual audit date outside chronology')
            key = tuple(row[k] for k in ('query_id', 'venture_id', 'observation_id', 'reviewer_id'))
            if key in seen:
                raise ValueError('Duplicate factual audit')
            seen.add(key)
            records.append(dict(row, reviewer=reviewers[row['reviewer_id']]))
    return records


def query_metrics(qid, ranked, eligible, labels):
    reviewers = sorted({r for q, v, r in labels if q == qid})
    result = []
    for reviewer in reviewers:
        grades = {v: row['relevance_grade'] for (q, v, r), row in labels.items() if q == qid and r == reviewer}
        complete_results = bool(ranked) and all(v in grades for v in ranked)
        complete_corpus = all(v in grades for v in eligible)
        precision = sum(grades[v] >= 1 for v in ranked) / len(ranked) if complete_results else None
        ndcg = None
        reason = 'judgments_incomplete'
        if complete_results and complete_corpus:
            dcg = lambda values: sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(values))
            ideal = dcg(sorted((grades[v] for v in eligible), reverse=True)[:3])
            if ideal:
                ndcg = dcg([grades[v] for v in ranked]) / ideal
                reason = None
            else:
                reason = 'zero_ideal_gain'
        elif not ranked:
            reason = 'abstention_no_relevance_score'
        result.append(
            dict(
                reviewer_id=reviewer,
                precision_at_3_returned_denominator=precision,
                ndcg_at_3=ndcg,
                returned_denominator=len(ranked),
                judged_candidates=len(grades),
                eligible_candidates=len(eligible),
                reason=reason,
            )
        )
    return result


def run(bundle, judgments=None, reviewers=None, split='development', as_of='2026-11-18', repeats=3, factual_audit=None):
    day(as_of)
    if not 1 <= repeats <= 100:
        raise ValueError('Latency repeats must be 1..100')
    manifest, corpus, bank = load_bundle(bundle)
    labels, pending, registry = read_labels(
        judgments or bundle / 'judgments.csv', reviewers or bundle / 'reviewers.json', bank, corpus, as_of
    )
    audits = read_factual_audit(factual_audit or bundle / 'factual_audit.csv', bank, corpus, registry, as_of)
    ids = sorted(v['venture_id'] for v in corpus)
    observation_map = {o['observation_id']: o for v in corpus for o in v['observations']}
    tasks = [t for t in bank.tasks if t.split == split]
    results = []
    from . import comparison_runs

    actual_digest = comparison_runs.corpus_digest
    with closing(connect(bundle / 'corpus.sqlite')) as conn:
        for task in tasks:
            if task.status != 'runnable':
                continue
            statements = []
            conn.set_trace_callback(statements.append)
            response = compare(conn, query=task.query_text, mode=task.mode, policy=manifest['policy'])
            conn.set_trace_callback(None)
            elapsed = []
            digest_times = []

            def measured_digest(c):
                start = time.perf_counter()
                value = actual_digest(c)
                digest_times.append((time.perf_counter() - start) * 1000)
                return value

            for _ in range(repeats):
                start = time.perf_counter()
                with patch('backend.comparison_runs.corpus_digest', side_effect=measured_digest):
                    repeated = compare(conn, query=task.query_text, mode=task.mode, policy=manifest['policy'])
                    canonical(repeated)
                elapsed.append((time.perf_counter() - start) * 1000)
                if result_signature(repeated) != result_signature(response):
                    raise ValueError('Non-reproducible ranking')
            ranked = [r['venture']['venture_id'] for r in response['results']]
            evidence = [e['observation'] for r in response['results'] for e in r['evidence']]
            valid = sum(
                o['observation_id'] in observation_map
                and observation_map[o['observation_id']]['source_id'] == o['source_id']
                and observation_map[o['observation_id']]['venture_id'] == o['venture_id']
                for o in evidence
            )
            results.append(
                dict(
                    query_id=task.query_id,
                    group_id=task.group_id,
                    ranked_ids=ranked,
                    run=response['run'],
                    abstention=response['abstention_reason'],
                    metrics=query_metrics(task.query_id, ranked, ids, labels),
                    aggregate_metrics={
                        'ndcg_at_3': None,
                        'precision_at_3_returned_denominator': None,
                        'reason': 'judgments_missing'
                        if not labels
                        else 'Reviewer-specific metrics are retained without invented adjudication',
                    },
                    evidence_reference_checks={
                        'checked': len(evidence),
                        'resolved_subject_and_source': valid,
                        'semantic_entailment': 'not_evaluated_human_audit_missing',
                    },
                    latency={
                        'repeats': repeats,
                        'median_ms': round(statistics.median(elapsed), 3),
                        'p95_ms': round(sorted(elapsed)[math.ceil(0.95 * len(elapsed)) - 1], 3),
                        'digest_median_ms': round(statistics.median(digest_times), 3),
                        'scope': 'Warm offline comparison plus JSON serialization, digest included; no browser/network',
                    },
                    selects=sum(s.lstrip().upper().startswith('SELECT') for s in statements),
                )
            )
    disagreements = []
    pairs = defaultdict(list)
    for (q, v, r), value in labels.items():
        pairs[(q, v)].append(
            {
                'reviewer_id': r,
                'grade': value['relevance_grade'],
                'rationale': value['rationale'],
                'independence_declared': value['reviewer']['independent_of_author'],
            }
        )
    for (q, v), values in pairs.items():
        if len({r['grade'] for r in values}) > 1:
            disagreements.append(
                dict(query_id=q, venture_id=v, independent_records=values, adjudication='not_supplied')
            )
    label_hash = digest([labels[k] for k in sorted(labels)])
    return dict(
        protocol_version=VERSION,
        manifest_id=manifest['manifest_id'],
        input_hashes=manifest['files'],
        method_version=METHOD['version'],
        policy=manifest['policy'],
        split=split,
        status='not_evaluated' if not labels else 'human_judgments_partial_or_complete',
        reason='judgments_missing' if not labels else None,
        label_digest=label_hash,
        eligible_ids=ids,
        reviewers=registry,
        judgments=[labels[k] for k in sorted(labels)],
        pending_review_rows=pending,
        tasks_pending=[t.query_id for t in tasks if t.status != 'runnable'],
        queries=results,
        disagreements=disagreements,
        coverage={
            'tasks_run': len(results),
            'with_results': sum(bool(r['ranked_ids']) for r in results),
            'abstentions': sum(not r['ranked_ids'] for r in results),
            'result_coverage': sum(bool(r['ranked_ids']) for r in results) / len(results) if results else None,
        },
        uncertainty={
            'interval': None,
            'reason': 'No intervals without real complete paired labels and adequate independent query groups',
        },
        factual_audit={
            'status': 'provided_human_audits' if audits else 'not_evaluated',
            'reason': None
            if audits
            else 'No human factual-support audit supplied; structural references are checked separately',
            'counts': {
                status: sum(a['entailment_status'] == status for a in audits)
                for status in ('supported', 'contradicted', 'insufficient')
            }
            if audits
            else None,
            'records': audits,
        },
        environment={
            'python': platform.python_version(),
            'sqlite': sqlite3.sqlite_version,
            'platform': platform.platform(),
        },
        limits=[
            'No unjudged-as-irrelevant assumption',
            'Precision denominator is returned results, nDCG requires complete eligible-corpus judgments per reviewer',
            'No recall, relevance generalisation, usefulness or time-saving claim from blank templates',
        ],
    )


def paired_bootstrap(group_differences, seed=314, draws=2000):
    if not isinstance(draws, int) or not 100 <= draws <= 100000:
        raise ValueError('Bootstrap draws must be 100..100000')
    if len(group_differences) < 8:
        return {
            'interval': None,
            'reason': 'Fewer than eight independent query groups; minimum is protocol choice, not proof of generalisation',
        }
    if any(not math.isfinite(v) for v in group_differences.values()):
        raise ValueError('Non-finite paired outcomes')
    values = list(group_differences.values())
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(draws))
    return {
        'interval': [means[int(0.025 * draws)], means[min(draws - 1, int(0.975 * draws))]],
        'method': 'Seeded paired cluster bootstrap over declared independent groups',
        'groups': len(values),
        'draws': draws,
        'seed': seed,
    }


def validate_report_metrics(report):
    if report['protocol_version'] != VERSION or digest(report['judgments']) != report['label_digest']:
        raise ValueError('Report label provenance mismatch')
    labels = {}
    for row in report['judgments']:
        if type(row['relevance_grade']) is not int or not 0 <= row['relevance_grade'] <= 3:
            raise ValueError('Invalid reported human grade')
        reviewer = Reviewer.model_validate(row['reviewer'])
        if reviewer.reviewer_id != row['reviewer_id']:
            raise ValueError('Reported reviewer mismatch')
        key = (row['query_id'], row['venture_id'], row['reviewer_id'])
        if key in labels:
            raise ValueError('Duplicate reported judgment')
        labels[key] = row
    for q in report['queries']:
        if (
            len(set(q['ranked_ids'])) != len(q['ranked_ids'])
            or len(q['ranked_ids']) > 3
            or not set(q['ranked_ids']) <= set(report['eligible_ids'])
        ):
            raise ValueError('Reported results outside frozen eligibility')
        expected = query_metrics(q['query_id'], q['ranked_ids'], report['eligible_ids'], labels)
        if canonical(expected) != canonical(q['metrics']):
            raise ValueError('Unsupported reported relevance metrics; do not invent missing labels')


def compare_reports(left, right):
    for key in ('input_hashes', 'eligible_ids', 'policy', 'split', 'label_digest'):
        if left[key] != right[key]:
            raise ValueError('Method comparison requires identical corpus/tasks/policy/labels: ' + key)
    validate_report_metrics(left)
    validate_report_metrics(right)
    lq = {q['query_id']: q for q in left['queries']}
    rq = {q['query_id']: q for q in right['queries']}
    if set(lq) != set(rq):
        raise ValueError('Unpaired task IDs')
    differences = defaultdict(list)
    for q, a in lq.items():
        b = rq[q]
        if a['group_id'] != b['group_id']:
            raise ValueError('Query group mismatch')
        ma = {m['reviewer_id']: m['ndcg_at_3'] for m in a['metrics']}
        mb = {m['reviewer_id']: m['ndcg_at_3'] for m in b['metrics']}
        if set(ma) != set(mb):
            raise ValueError('Reviewer mismatch')
        values = [mb[r] - ma[r] for r in ma if ma[r] is not None and mb[r] is not None]
        if values:
            differences[a['group_id']].append(statistics.mean(values))
    grouped = {g: statistics.mean(v) for g, v in differences.items()}
    return {
        'methods': [left['method_version'], right['method_version']],
        'paired_group_differences': grouped,
        'mean_difference': statistics.mean(grouped.values()) if grouped else None,
        'uncertainty': paired_bootstrap(grouped),
        'status': 'not_evaluated_judgments_missing_or_incomplete' if not grouped else 'paired_declared_groups_only',
    }
