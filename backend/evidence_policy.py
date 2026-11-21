"""Shared policy for raw display, baseline retrieval and accepted matching.

Publication labels never establish historical information availability. The seed
contains no availability witnesses and no fabricated acceptance events.
"""

from datetime import date
import json

POLICIES = {
    'exploration': 'Exploration: source-checked unreviewed publisher reports and accepted reports; rejected, needs-review and superseded statements excluded.',
    'accepted': 'Reviewed matching: accepted observations only; rejected and superseded statements excluded.',
}


def _cutoff(value):
    if value is None:
        return None
    return date.fromisoformat(value).isoformat() if isinstance(value, str) else value.isoformat()


def _date_value(value):
    return (
        {'precision': 'day', 'lower_bound': value, 'upper_bound': value}
        if value
        else {'precision': 'unknown', 'lower_bound': None, 'upper_bound': None}
    )


def enrich_observations(conn, observations, cutoff=None):
    """Return a copied, enriched list; preserve every raw statement for display."""
    cutoff = _cutoff(cutoff)
    dates = {
        (r['owner_kind'], r['owner_id'], r['date_role']): {k: r[k] for k in ('precision', 'lower_bound', 'upper_bound')}
        for r in map(dict, conn.execute('SELECT * FROM evidence_dates'))
    }
    reviews = {}
    sql = 'SELECT rowid,* FROM review_events WHERE observation_id IS NOT NULL'
    params = ()
    if cutoff:
        sql += ' AND substr(reviewed_at,1,10)<=?'
        params = (cutoff,)
    sql += ' ORDER BY reviewed_at,rowid'
    for row in map(dict, conn.execute(sql, params)):
        reviews[row['observation_id']] = row['decision']
    sql = 'SELECT * FROM observation_relations'
    if cutoff:
        sql += ' WHERE recorded_at<=?'
    relations = list(map(dict, conn.execute(sql, (cutoff,) if cutoff else ())))
    superseded = {r['observation_id'] for r in relations}
    values = {
        r['observation_id']: {r['value_type']: json.loads(r['value_json'])}
        for r in map(dict, conn.execute('SELECT * FROM observation_values'))
    }
    result = []
    for original in observations:
        row = dict(original)
        oid, sid = row['observation_id'], row['source_id']
        row['published_at'] = row.get('published_at') or None
        row['publication_date'] = dates.get(('source', sid, 'publication'), _date_value(row['published_at']))
        row['effective_date'] = dates.get(('observation', oid, 'effective'), _date_value(row.get('effective_at')))
        row['announcement_date'] = dates.get(('observation', oid, 'announcement'), _date_value(None))
        row['effective_review_status'] = reviews.get(
            oid, 'needs_review' if row['review_status'] == 'accepted' else row['review_status']
        )
        row['superseded'] = oid in superseded
        row['relations'] = [r for r in relations if oid in (r['observation_id'], r['replacement_id'])]
        row.update(values.get(oid, {}))
        result.append(row)
    return result


def select_observations(conn, policy='exploration', cutoff=None):
    if policy not in POLICIES:
        raise ValueError('Unknown evidence selection policy: ' + str(policy))
    cutoff = _cutoff(cutoff)
    sql = '''SELECT o.*,s.title AS source_title,s.url,s.publisher,s.published_at,
        s.retrieved_at,s.limitations FROM observations o JOIN sources s USING(source_id)'''
    params = ()
    if cutoff:
        sql += ''' JOIN source_availability a USING(source_id)
                   WHERE a.available_at<=?'''
        params = (cutoff,)
    sql += ' ORDER BY o.observation_id'
    observations = enrich_observations(conn, [dict(r) for r in conn.execute(sql, params)], cutoff=cutoff)
    eligible = {'accepted'} if policy == 'accepted' else {'accepted', 'source_checked_owner_review_pending'}
    return [
        r
        for r in observations
        if r['assertion_type'] == 'publisher_report'
        and r['effective_review_status'] in eligible
        and not r['superseded']
    ]


def enrich_awards(conn, awards):
    """Calendar precision for raw award display, without inventing event days."""
    dates = {
        (r['owner_kind'], r['owner_id'], r['date_role']): {k: r[k] for k in ('precision', 'lower_bound', 'upper_bound')}
        for r in map(dict, conn.execute('SELECT * FROM evidence_dates'))
    }
    result = []
    for original in awards:
        row = dict(original)
        row['published_at'] = row.get('published_at') or None
        row['publication_date'] = dates.get(
            ('source', row['source_id'], 'publication'), _date_value(row['published_at'])
        )
        row['event_interval'] = dates.get(('award', row['award_id'], 'event'), _date_value(row.get('event_date')))
        result.append(row)
    return result
