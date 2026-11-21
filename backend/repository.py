"""Separate directory, raw profiles and lightweight retrieval documents."""

import json
from collections import defaultdict


def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params)]


def identity(row):
    value = dict(row)
    value['aliases'] = json.loads(value.pop('aliases_json'))
    return value


def detail_many(conn, venture_ids):
    """Batch full evidence for only the selected profile/shortlist identities."""
    ids = list(dict.fromkeys(venture_ids))
    if not ids:
        return {}
    placeholders = ','.join('?' for _ in ids)
    profiles = {
        r['venture_id']: dict(identity(r), observations=[], awards=[], connections=[], proposed_annotations=[])
        for r in conn.execute('SELECT * FROM ventures WHERE venture_id IN (' + placeholders + ')', ids)
    }
    observations = rows(
        conn,
        'SELECT o.*,s.title AS source_title,s.url,s.publisher,s.published_at,s.retrieved_at,s.limitations FROM observations o JOIN sources s USING(source_id) WHERE o.venture_id IN ('
        + placeholders
        + ') ORDER BY s.published_at,o.observation_id',
        ids,
    )
    from .evidence_policy import enrich_awards, enrich_observations

    observations = enrich_observations(conn, observations)
    observations_by_id = {o['observation_id']: o for o in observations}
    for observation in observations:
        profiles[observation['venture_id']]['observations'].append(observation)
    awards = rows(
        conn,
        'SELECT a.*,s.title AS source_title,s.url,s.publisher,s.published_at,s.retrieved_at,s.limitations FROM awards a JOIN sources s USING(source_id) WHERE a.venture_id IN ('
        + placeholders
        + ') ORDER BY award_year,award_id',
        ids,
    )
    for award in enrich_awards(conn, awards):
        profiles[award['venture_id']]['awards'].append(award)
    for connection in rows(
        conn, 'SELECT * FROM connections WHERE venture_id IN (' + placeholders + ') ORDER BY connection_id', ids
    ):
        connection['evidence'] = observations_by_id[connection['observation_id']]
        profiles[connection['venture_id']]['connections'].append(connection)
    for annotation in rows(
        conn, 'SELECT * FROM annotations WHERE venture_id IN (' + placeholders + ') ORDER BY field,annotation_id', ids
    ):
        annotation['basis_observation_ids'] = json.loads(annotation.pop('basis_observation_ids_json'))
        profiles[annotation['venture_id']]['proposed_annotations'].append(annotation)
    return profiles


def detail(conn, venture_id):
    return detail_many(conn, [venture_id]).get(venture_id)


def filter_clause(q='', programme='', year=None, connection_type=''):
    clauses, params = [], []
    if q.strip():
        term = '%' + q.strip().lower().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        clauses.append(
            "(lower(v.display_name) LIKE ? ESCAPE '\\' OR lower(v.aliases_json) LIKE ? ESCAPE '\\' OR EXISTS (SELECT 1 FROM observations o WHERE o.venture_id=v.venture_id AND o.field='product_description' AND lower(o.value_text) LIKE ? ESCAPE '\\'))"
        )
        params += [term] * 3
    if programme or year is not None:
        award_clauses = ['a.venture_id=v.venture_id']
        if programme:
            award_clauses.append('a.programme=?')
            params.append(programme)
        if year is not None:
            award_clauses.append('a.award_year=?')
            params.append(year)
        clauses.append('EXISTS (SELECT 1 FROM awards a WHERE ' + ' AND '.join(award_clauses) + ')')
    if connection_type:
        clauses.append('EXISTS (SELECT 1 FROM connections c WHERE c.venture_id=v.venture_id AND c.connection_type=?)')
        params.append(connection_type)
    return (' WHERE ' + ' AND '.join(clauses) if clauses else ''), params


def candidate_ids(conn, programme='', year=None, connection_type='', cutoff=None):
    clause, params = filter_clause(programme=programme, year=year, connection_type=connection_type)
    if cutoff:
        # Cohort/recognition facts also need witnessed information availability.
        # Do not form a historical shortlist from a future relationship report.
        if programme or year is not None:
            bound = [
                'a.venture_id=v.venture_id',
                'EXISTS (SELECT 1 FROM source_availability av WHERE av.source_id=a.source_id AND av.available_at<=?)',
            ]
            extra = [cutoff]
            if programme:
                bound.append('a.programme=?')
                extra.append(programme)
            if year is not None:
                bound.append('a.award_year=?')
                extra.append(year)
            clause += (
                (' AND ' if clause else ' WHERE ') + 'EXISTS (SELECT 1 FROM awards a WHERE ' + ' AND '.join(bound) + ')'
            )
            params.extend(extra)
        if connection_type:
            clause += (
                (' AND ' if clause else ' WHERE ')
                + 'EXISTS (SELECT 1 FROM connections c JOIN observations o USING(observation_id) JOIN source_availability av USING(source_id) WHERE c.venture_id=v.venture_id AND c.connection_type=? AND av.available_at<=?)'
            )
            params.extend([connection_type, cutoff])
    return {r[0] for r in conn.execute('SELECT v.venture_id FROM ventures v' + clause, params)}


def browse(conn, q='', programme='', year=None, connection_type='', limit=25, offset=0):
    """A bounded summary page. Full evidence is available only through detail()."""
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError('limit must be 1..100 and offset nonnegative')
    clause, params = filter_clause(q, programme, year, connection_type)
    counts = conn.execute(
        'SELECT (SELECT COUNT(*) FROM ventures v' + clause + '), (SELECT COUNT(*) FROM ventures)', params
    ).fetchone()
    values = [
        identity(r)
        for r in conn.execute(
            'SELECT v.* FROM ventures v' + clause + ' ORDER BY v.display_name,v.venture_id LIMIT ? OFFSET ?',
            [*params, limit, offset],
        )
    ]
    page = {
        'items': values,
        'total': counts[0],
        'filtered_ventures': counts[0],
        'total_ventures': counts[1],
        'limit': limit,
        'offset': offset,
    }
    if not values:
        return page
    placeholders = ','.join('?' for _ in values)
    ids = [v['venture_id'] for v in values]
    awards, connections, observations = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in rows(
        conn,
        'SELECT venture_id,award_id,programme,award_year FROM awards WHERE venture_id IN ('
        + placeholders
        + ') ORDER BY award_year,award_id',
        ids,
    ):
        awards[r.pop('venture_id')].append(r)
    for r in rows(
        conn,
        'SELECT DISTINCT venture_id,connection_type FROM connections WHERE venture_id IN ('
        + placeholders
        + ') ORDER BY connection_type',
        ids,
    ):
        connections[r['venture_id']].append(r['connection_type'])
    for r in rows(
        conn,
        'SELECT o.venture_id,o.field,o.value_text,o.source_id,s.published_at FROM observations o JOIN sources s USING(source_id) WHERE o.venture_id IN ('
        + placeholders
        + ') ORDER BY o.observation_id',
        ids,
    ):
        observations[r['venture_id']].append(r)
    for v in values:
        obs = observations[v['venture_id']]
        v.update(
            product_excerpt=next((o['value_text'] for o in obs if o['field'] == 'product_description'), None),
            recognitions=awards[v['venture_id']],
            award_count=len(awards[v['venture_id']]),
            connection_types=connections[v['venture_id']],
            source_count=len({o['source_id'] for o in obs}),
            publication_dates=sorted({o['published_at'] for o in obs if o['published_at']})
            + ([None] if any(not o['published_at'] for o in obs) else []),
        )
    return page


def corpus_documents(conn, policy='exploration', cutoff=None):
    """One identity query plus batched evidence policy queries; no profiles."""
    from .evidence_policy import select_observations

    documents = {
        r['venture_id']: dict(identity(r), observations=[])
        for r in conn.execute('SELECT * FROM ventures ORDER BY venture_id')
    }
    for observation in select_observations(conn, policy=policy, cutoff=cutoff):
        documents[observation['venture_id']]['observations'].append(observation)
    return list(documents.values())


def facets(conn):
    return {
        'programmes': rows(
            conn,
            'SELECT programme,COUNT(*) AS awards,COUNT(DISTINCT venture_id) AS ventures FROM awards GROUP BY programme',
        ),
        'years': [r[0] for r in conn.execute('SELECT DISTINCT award_year FROM awards ORDER BY award_year DESC')],
        'connection_types': rows(conn, 'SELECT * FROM v_connection_coverage ORDER BY connection_type'),
        'counts': {
            t: conn.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
            for t in ('ventures', 'sources', 'observations', 'awards', 'connections', 'annotations')
        },
    }


EXPORTS = {
    'programme_recognition': 'SELECT * FROM v_programme_recognition ORDER BY award_year,programme',
    'connection_coverage': 'SELECT * FROM v_connection_coverage ORDER BY connection_type',
    'source_coverage': 'SELECT * FROM v_source_coverage ORDER BY venture_id',
    'raw_observations': 'SELECT * FROM v_raw_observations ORDER BY observation_id',
    'proposed_annotations': 'SELECT * FROM v_proposed_annotations ORDER BY annotation_id',
}


def analytics(conn):
    return {k: rows(conn, sql) for k, sql in EXPORTS.items() if k not in ('raw_observations', 'proposed_annotations')}
