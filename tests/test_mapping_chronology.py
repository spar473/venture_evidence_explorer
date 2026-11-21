"""Synthetic mapping decisions only; no actual human acceptance."""

import json
import sqlite3
import pytest
from backend.ingestion import load_seed
from backend.research_adapter import EXAMPLE, import_research, dry_run_research, _proposal_id


def snapshot(db):
    with sqlite3.connect(db) as c:
        return {
            n: c.execute('SELECT * FROM "' + n + '" ORDER BY rowid').fetchall()
            for (n,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }


def decision(path, evidence, when='2020-01-01', mid='synthetic-chronology'):
    doc = {
        'format_version': 'identity-mappings:1',
        'decisions': [
            dict(
                mapping_id=mid,
                subject_id='subj_rosterlab',
                venture_id='v_rosterlab',
                state='resolved',
                scope='brand_project_only',
                actor_role='owner',
                actor_id='Synthetic regression fixture only',
                decided_on=when,
                evidence_ids=[evidence],
                rationale='Synthetic chronology test, not a genuine resolution',
                supersedes_mapping_id=_proposal_id('subj_rosterlab'),
            )
        ],
    }
    path.write_text(json.dumps(doc))
    return path


@pytest.mark.parametrize(
    'evidence',
    [
        'src_rl_pricing',
        'obs_rl_solution',
        'report_rl_uoa_financing',
        'event_rl_financing_uoa',
        'conclusion_solutions',
        'req_solutions',
        'ready_solutions',
        'unknown_rl_reported_paying_organisation',
        'ann_rl_relevance',
    ],
)
def test_direct_and_indirect_backdating_rejected_before_writes(tmp_path, evidence):
    # Find actual editorial IDs where spelling differs; never invent source data.
    packet = json.loads(EXAMPLE.read_bytes())
    if evidence == 'report_rl_uoa_financing':
        evidence = next(r['report_id'] for r in packet['event_reports'] if r['subject_id'] == 'subj_rosterlab')
    if evidence == 'ann_rl_relevance':
        evidence = packet['proposed_annotations'][0]['annotation_id']
    db = tmp_path / 'probe.sqlite'
    load_seed(db)
    import_research(db, EXAMPLE, as_of='2026-11-18')
    before = snapshot(db)
    path = decision(tmp_path / 'decision.json', evidence)
    report = dry_run_research(EXAMPLE, db, '2026-11-18', path)
    assert report['status'] == 'rejected' and any('predates' in e['message'] for e in report['mapping_errors'])
    with pytest.raises(ValueError, match='predates'):
        import_research(db, EXAMPLE, as_of='2026-11-18', mapping_decisions_path=path)
    assert snapshot(db) == before


@pytest.mark.parametrize('evidence', ['obs_rl_solution', 'conclusion_solutions', 'req_solutions'])
def test_valid_same_day_decision_and_repeat_keep_legal_identity_separate(tmp_path, evidence):
    db = tmp_path / 'probe.sqlite'
    load_seed(db)
    path = decision(tmp_path / 'decision.json', evidence, '2026-11-18')
    assert dry_run_research(EXAMPLE, db, '2026-11-18', path)['status'] == 'valid_dry_run'
    import_research(db, EXAMPLE, as_of='2026-11-18', mapping_decisions_path=path)
    before = snapshot(db)
    import_research(db, EXAMPLE, as_of='2026-11-18', mapping_decisions_path=path)
    assert snapshot(db) == before
    with sqlite3.connect(db) as c:
        assert (
            c.execute("SELECT legal_identity_state FROM research_identity_mappings WHERE state='resolved'").fetchone()[
                0
            ]
            == 'unresolved'
        )


def test_source_less_subject_refused_even_at_later_date(tmp_path):
    db = tmp_path / 'probe.sqlite'
    load_seed(db)
    before = snapshot(db)
    path = decision(tmp_path / 'decision.json', 'subj_rosterlab', '2026-11-18')
    report = dry_run_research(EXAMPLE, db, '2026-11-18', path)
    assert report['status'] == 'rejected' and any('source-backed' in e['message'] for e in report['mapping_errors'])
    with pytest.raises(ValueError, match='source-backed'):
        import_research(db, EXAMPLE, as_of='2026-11-18', mapping_decisions_path=path)
    assert snapshot(db) == before


def test_assessment_chronology_and_partial_event_dates_are_distinct(tmp_path):
    packet = json.loads(EXAMPLE.read_bytes())
    # Resolver-only synthetic date alteration isolates inspection from assessment.
    # This fixture is never imported or described as a valid research packet.
    for source in packet['sources']:
        source['retrieved_on'] = '2026-11-17'
    from backend.research_adapter import _mapping_provenance, _records

    prepared = {'packet': packet, 'records': _records(packet)}
    sources, dates = _mapping_provenance(prepared, 'conclusion_solutions')
    assert sources and '2026-11-18' in dates and '2026-11-17' in dates
    assert all(len(d) == 10 for d in dates)
    # Year targets / unknown occurrences are not converted to decision cutoff days.
    report = next(r for r in packet['event_reports'] if r['subject_id'] == 'subj_rosterlab')
    _, dates = _mapping_provenance(prepared, report['report_id'])
    assert '2026-12-31' not in dates


def test_rejected_batch_does_not_write_an_earlier_valid_decision(tmp_path):
    db = tmp_path / 'probe.sqlite'
    load_seed(db)
    import_research(db, EXAMPLE, as_of='2026-11-18')
    before = snapshot(db)
    path = decision(tmp_path / 'batch.json', 'obs_rl_solution', '2026-11-18')
    doc = json.loads(path.read_text())
    doc['decisions'].append(dict(doc['decisions'][0], mapping_id='synthetic-backdated-second', decided_on='2020-01-01'))
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='predates'):
        import_research(db, EXAMPLE, as_of='2026-11-18', mapping_decisions_path=path)
    assert snapshot(db) == before


def test_valid_later_decision_preserves_raw_partial_dates(tmp_path):
    db = tmp_path / 'probe.sqlite'
    load_seed(db)
    path = decision(tmp_path / 'decision.json', 'obs_rl_solution', '2026-11-19')
    import_research(db, EXAMPLE, as_of='2026-11-19', mapping_decisions_path=path)
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT raw_bytes FROM research_imports').fetchone()[0] == EXAMPLE.read_bytes()
        assert c.execute("SELECT COUNT(*) FROM research_time_values WHERE precision='year'").fetchone()[0] > 0
        assert c.execute("SELECT COUNT(*) FROM research_time_values WHERE precision='unknown'").fetchone()[0] > 0


def test_acceptance_review_day_is_followed_without_looping_through_target():
    from backend.research_adapter import _mapping_provenance

    prepared = {
        'packet': {'readiness': []},
        'records': [
            ('sources', 'synthetic-source', {'retrieved_on': '2026-11-18', 'access_status': 'text_read'}),
            (
                'observations',
                'synthetic-observation',
                {
                    'source_id': 'synthetic-source',
                    'review': {'checked_on': '2026-11-18', 'acceptance_review_id': 'synthetic-review'},
                },
            ),
            ('review_events', 'synthetic-review', {'reviewed_on': '2026-11-19', 'target_id': 'synthetic-observation'}),
        ],
    }
    sources, dates = _mapping_provenance(prepared, 'synthetic-observation')
    assert sources == {'synthetic-source'} and dates == {'2026-11-18', '2026-11-19'}

    # Failed access retains chronology but is not an inspected textual basis.
    prepared['records'][0][2]['access_status'] = 'blocked_403'
    assert _mapping_provenance(prepared, 'synthetic-observation')[0] == set()
