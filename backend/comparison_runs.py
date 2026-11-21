"""Portable deterministic run records; runtime database remains read only."""

import hashlib
import json

RUN_VERSION = 'comparison-run-1.0'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def corpus_digest(conn):
    """Hash logical contents, not SQLite page layout or filesystem timestamps.

    Include all user tables (including review/history metadata and import hashes),
    so changed evidence, candidate filters or a new import conservatively invalidate
    an exported run. Binary import bytes are represented losslessly as hex.
    """
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    snapshots = {}
    for table in tables:
        quoted = '"' + table.replace('"', '""') + '"'
        projection = 'rowid AS _append_order,*' if table == 'review_events' else '*'
        cursor = conn.execute('SELECT ' + projection + ' FROM ' + quoted)
        columns = [d[0] for d in cursor.description]
        values = [[{'bytes_hex': x.hex()} if isinstance(x, bytes) else x for x in row] for row in cursor]
        snapshots[table] = {'columns': columns, 'rows': sorted(values, key=canonical)}
    return digest(snapshots)


def result_signature(response):
    return {
        'abstention_reason': response['abstention_reason'],
        'subject_id': response['subject']['venture_id'] if response['subject'] else None,
        'results': [
            dict(
                venture_id=r['venture']['venture_id'],
                ranking_score=r['ranking_score'],
                query_token_coverage=r['query_token_coverage'],
                matched_terms=r['matched_terms'],
                observation_ids=[e['observation']['observation_id'] for e in r['evidence']],
            )
            for r in response['results']
        ],
    }


def comparison_record(conn, request, corpus, response):
    selected = [
        {'observation_id': o['observation_id'], 'review_status': o.get('effective_review_status', o['review_status'])}
        for v in corpus
        for o in v['observations']
        if o['field'] in response['method']['fields'].get(request['mode'], [])
    ]
    record = {
        'record_version': RUN_VERSION,
        'method_version': response['method']['version'],
        'policy_version': response['evidence_policy']['version'],
        'corpus_digest': corpus_digest(conn),
        'request': request,
        'selected_observations': sorted(selected, key=lambda o: o['observation_id']),
        'result_signature': result_signature(response),
    }
    return dict(record, run_id=digest(record))


def replay(conn, record):
    from .retrieval import METHOD, compare

    supplied = dict(record)
    run_id = supplied.pop('run_id', None)
    if run_id != digest(supplied):
        raise ValueError('Comparison run checksum mismatch')
    if (
        supplied['record_version'] != RUN_VERSION
        or supplied['method_version'] != METHOD['version']
        or supplied['policy_version'] != 'evidence-selection-1.0'
    ):
        raise ValueError('Unsupported comparison method, policy or record version')
    if supplied['corpus_digest'] != corpus_digest(conn):
        raise ValueError('Corpus changed; replay requires the recorded corpus snapshot')
    result = compare(conn, **supplied['request'])
    if result['run'] != record:
        raise ValueError('Run does not reproduce with this implementation and configuration')
    return result
