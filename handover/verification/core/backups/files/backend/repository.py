"""Database records and provenance; no browser-side seed or inferred facts."""
import json


def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params)]


def detail(conn, venture_id):
    r = conn.execute('SELECT * FROM ventures WHERE venture_id=?', (venture_id,)).fetchone()
    if not r:
        return None
    v = dict(r)
    v['aliases'] = json.loads(v.pop('aliases_json'))
    v['observations'] = rows(conn, '''SELECT o.*, s.title AS source_title,s.url,s.publisher,
        s.published_at,s.retrieved_at,s.limitations FROM observations o
        JOIN sources s USING(source_id) WHERE venture_id=? ORDER BY s.published_at,o.observation_id''', (venture_id,))
    v['awards'] = rows(conn, '''SELECT a.*, s.title AS source_title,s.url,s.publisher,
        s.published_at,s.retrieved_at,s.limitations FROM awards a JOIN sources s USING(source_id)
        WHERE venture_id=? ORDER BY award_year,award_id''', (venture_id,))
    v['connections'] = rows(conn, 'SELECT * FROM connections WHERE venture_id=? ORDER BY connection_id', (venture_id,))
    for c in v['connections']:
        c['evidence'] = next(o for o in v['observations'] if o['observation_id'] == c['observation_id'])
    v['proposed_annotations'] = rows(conn, 'SELECT * FROM annotations WHERE venture_id=? ORDER BY field,annotation_id', (venture_id,))
    for a in v['proposed_annotations']:
        a['basis_observation_ids'] = json.loads(a.pop('basis_observation_ids_json'))
    return v


def browse(conn, q='', programme='', year=None, connection_type=''):
    clauses, params = [], []
    if q.strip():
        # Literal substring search: escape LIKE syntax rather than interpreting user wildcards.
        term = '%' + q.strip().lower().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        clauses.append("(lower(v.display_name) LIKE ? ESCAPE '\\' OR lower(v.aliases_json) LIKE ? ESCAPE '\\' OR EXISTS (SELECT 1 FROM observations o WHERE o.venture_id=v.venture_id AND o.field='product_description' AND lower(o.value_text) LIKE ? ESCAPE '\\'))")
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
    sql = 'SELECT v.venture_id FROM ventures v' + (' WHERE ' + ' AND '.join(clauses) if clauses else '') + ' ORDER BY v.display_name,v.venture_id'
    return [detail(conn, r[0]) for r in conn.execute(sql, params)]


def facets(conn):
    return {
        'programmes': rows(conn, 'SELECT programme,COUNT(*) AS awards,COUNT(DISTINCT venture_id) AS ventures FROM awards GROUP BY programme'),
        'years': [r[0] for r in conn.execute('SELECT DISTINCT award_year FROM awards ORDER BY award_year DESC')],
        'connection_types': rows(conn, 'SELECT * FROM v_connection_coverage ORDER BY connection_type'),
        'counts': {t: conn.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('ventures','sources','observations','awards','connections','annotations')}
    }


EXPORTS = {
    'programme_recognition': 'SELECT * FROM v_programme_recognition ORDER BY award_year,programme',
    'connection_coverage': 'SELECT * FROM v_connection_coverage ORDER BY connection_type',
    'source_coverage': 'SELECT * FROM v_source_coverage ORDER BY venture_id',
    'raw_observations': 'SELECT * FROM v_raw_observations ORDER BY observation_id',
    'proposed_annotations': 'SELECT * FROM v_proposed_annotations ORDER BY annotation_id',
}


def analytics(conn):
    return {k: rows(conn, sql) for k, sql in EXPORTS.items() if k not in ('raw_observations','proposed_annotations')}
