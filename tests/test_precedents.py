from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.precedent_contracts import CompOutcome, WorkbenchAnchor, WorkbenchClaim, WorkbenchRow
from backend.precedent_evidence import checklist, contemporaneous_snapshot, points_for, select_anchor, snapshot_at
from backend.precedent_similarity import (
    MIN_COVERAGE,
    MIN_SIMILARITY,
    VERSION,
    corpus_idf,
    features,
    rank_peers,
    score,
    select_comps,
)
from backend.precedents import COMP_LABELS, PrecedentCatalog, comp_outcome
from backend.reference_pool import EventDate, PoolEvent, Witness
from scripts.healthtech_demo import prepare_demo


@pytest.fixture(scope='module')
def demo_db(tmp_path_factory):
    return Path(prepare_demo(tmp_path_factory.mktemp('precedents'))['database'])


def claim(key='prototype', value='no', *, dated=True, witnessed=True):
    return WorkbenchClaim(
        claim_id='claim_' + key,
        field=key,
        value=value,
        passage='Synthetic test claim.',
        publisher='Example',
        url='https://example.org/',
        published_on='2020-01-01',
        retrieved_on='2026-11-21',
        date_value='2020-01-01' if dated else None,
        date_precision='day' if dated else None,
        lower_on='2020-01-01' if dated else None,
        upper_on='2020-01-01' if dated else None,
        witness=Witness(
            witness_id='witness_case',
            source_id='example',
            kind='publisher_dated',
            available_on='2020-01-01',
            url='https://example.org/',
            locator='Test date',
        )
        if witnessed
        else None,
    )


def row(key, status='observed_no_outcome', rank=2, features=None):
    snapshot = [
        claim(field, value)
        for field, value in (
            features
            or {
                'stage': 'seed',
                'buyer': 'hospital',
                'months_since_founding': 12,
                'description': 'imaging surgical planning',
                'regulatory_class': 2,
            }
        ).items()
    ]
    evidence = claim('last_verified_activity', 'Supported status')
    outcome = (
        CompOutcome(
            rank=rank,
            label=COMP_LABELS[rank],
            date_value=evidence.date_value,
            date_precision=evidence.date_precision,
            claim=evidence,
        )
        if rank is not None
        else None
    )
    return WorkbenchRow(
        company_id=key,
        display_name=key,
        kind='company',
        sector='Healthtech',
        anchor=None,
        points=[],
        snapshot=snapshot,
        claims=snapshot,
        milestones=checklist(snapshot),
        gaps=[],
        status=status,
        outcome_rank=rank,
        outcome_label=None,
        comp_outcome=outcome,
        not_alignable=None,
    )


def test_gower_missingness_numeric_ranges_and_deterministic_text():
    left = {'buyer': 'hospital', 'months_since_founding': 12, 'description': 'imaging planning', 'stage': 'seed'}
    right = {
        'buyer': 'hospital',
        'months_since_founding': 42,
        'description': 'images planning',
        'clinical_user': 'doctor',
    }
    value, coverage, dimensions = score(left, right, corpus_idf([left, right]))
    assert value == pytest.approx((0.25 + 0.20 + 0.15 * 0.75) / (0.25 + 0.20 + 0.15))
    assert coverage == pytest.approx(0.25 / 4 + 0.20 / 3 + 0.15 / 3)
    assert dimensions[3].similarity is None
    assert dimensions[4].different_fields == ['months_since_founding']


def test_top_k_abstention_tie_break_unknown_and_verified_floor():
    subject = row('subject')
    peers = rank_peers(
        subject,
        [row('company_' + str(i).zfill(2)) for i in reversed(range(12))]
        + [row('outside_closure', 'closed_before_outcome', 0)],
    )
    assert len(peers) == 12 and peers[0].row.company_id == 'company_00'
    comps, no_closure, abstains = select_comps(peers)
    assert no_closure and abstains is None
    [comp] = comps
    assert comp.role == 'representative' and comp.peer.row.company_id == 'company_00'
    assert comp.reason == 'closest resolved peers share the same outcome'
    assert select_comps(peers[:2])[2]
    mixed = rank_peers(
        subject,
        [
            row('a_unknown', 'unknown', None),
            row('b_closed', 'closed_before_outcome', 0),
            row('c_exit', 'acquired_or_ipo_before_outcome', 5),
            row('d_observed'),
        ],
    )
    comps, no_closure, abstains = select_comps(mixed)
    assert not no_closure and abstains is None
    assert {comp.role: comp.peer.row.company_id for comp in comps} == {
        'ceiling': 'c_exit',
        'typical': 'd_observed',
        'floor': 'b_closed',
    }
    varied = rank_peers(subject, [row('a_seed'), row('b_seed'), row('c_series', rank=3)])
    assert [(comp.role, comp.peer.row.company_id) for comp in select_comps(varied)[0]] == [
        ('ceiling', 'c_series'),
        ('typical', 'b_seed'),
        ('floor', 'a_seed'),
    ]
    assert [comp.role for comp in select_comps(mixed[:3])[0]] == ['ceiling', 'floor']


def test_clinical_workflow_requires_quarter_similarity_even_when_other_dimensions_clear_thresholds():
    values = {'stage': 'seed', 'buyer': 'hospital', 'months_since_founding': 12, 'regulatory_class': 2}
    subject = row('subject', features={**values, 'modality': 'MRI'})
    no_workflow = row('missing_workflow', features=values)
    similarity, coverage, _ = score(features(subject), features(no_workflow), {})
    assert similarity >= MIN_SIMILARITY and coverage >= MIN_COVERAGE
    differing_workflow = row('different_workflow', features={**values, 'modality': 'ultrasound'})
    assert rank_peers(subject, [no_workflow, differing_workflow]) == []
    left = row(
        'subject_exact',
        features={
            **values,
            'modality': 'MRI',
            'clinical_user': 'radiologist',
            'output_type': 'report',
            'description': 'breast assessment',
        },
    )
    right = row(
        'quarter_match',
        features={
            **values,
            'modality': 'MRI',
            'clinical_user': 'neurologist',
            'output_type': 'scan',
            'description': 'brain triage',
        },
    )
    [peer] = rank_peers(left, [right])
    assert peer.dimensions[0].similarity == 0.25


def test_comp_status_uses_dated_evidence_beyond_the_window_and_respects_disputes():
    anchor = WorkbenchAnchor(kind='first_institutional_round', claim=claim('seed'))

    def record(kind, on, *, instrument='unknown', link='supported', precision='day', disputed=False):
        event_date = EventDate(value=on, precision=precision)
        lower, upper = event_date.bounds()
        event = PoolEvent(
            event_id=kind,
            company_id='example',
            source_id='publisher',
            kind=kind,
            date=event_date,
            date_basis='reported_occurrence',
            claim='Dated event.',
            passage='Test.',
            instrument=instrument,
            entity_link=link,
        )
        evidence = claim(kind, witnessed=False).model_copy(
            update={
                'date_value': on,
                'date_precision': precision,
                'published_on': upper,
                'lower_on': lower,
                'upper_on': upper,
                'review_state': 'disputed' if disputed else 'source_attributed',
            }
        )
        return event, evidence

    series_a = record('series_a', '2022-02', instrument='priced_equity', precision='month')
    series_b = record('series_b', '2024-06-01', instrument='priced_equity')
    closure = record('closed_liquidation', '2025-08-01')
    exit_event = record('acquired', '2025-02-01')
    proposed = record('ipo', '2025-09-01', link='proposed')
    disputed = record('closed_register_removal', '2024-07-01', disputed=True)
    observations = [series_a, series_b, exit_event, closure, proposed, disputed]
    for cutoff, rank, on in [
        ('2022-02-12', None, None),
        ('2023-01-01', 3, '2022-02'),
        ('2024-12-01', 4, '2024-06-01'),
        ('2025-03-01', 5, '2025-02-01'),
        ('2026-11-21', 0, '2025-08-01'),
    ]:
        result = comp_outcome(anchor, observations, None, cutoff)
        assert ((result.rank, result.date_value) if result else (None, None)) == (rank, on)
    unknown_financing = record('series_a', '2024-06-01')
    assert comp_outcome(anchor, [unknown_financing], None, '2026-11-21') is None
    activity = record('last_verified_activity', '2023-01-01')
    review = {
        'activity_event_id': 'last_verified_activity',
        'reviewed_on': '2025-01-10',
        'searched_through': '2025-01-01',
    }
    assert comp_outcome(anchor, [activity], review, '2024-12-31').rank == 2
    quiet = comp_outcome(anchor, [activity], review, '2025-01-10')
    assert (quiet.rank, quiet.date_value, quiet.claim.date_value) == (1, '2025-01-01', '2023-01-01')
    recent = record('provider_deployment', '2024-10-15')
    assert comp_outcome(anchor, [activity, recent], review, '2025-01-10').rank == 2


def test_witness_is_required_by_earliest_anchor_bound_and_no_requires_dated_explicit_claim():
    original = claim('seed', 'Seed')
    anchor = WorkbenchAnchor(
        kind='first_institutional_round',
        claim=original.model_copy(
            update={'date_value': '2020-01', 'date_precision': 'month', 'upper_on': '2020-01-31'}
        ),
    )
    negative = claim()
    later = negative.model_copy(update={'witness': negative.witness.model_copy(update={'available_on': '2020-01-02'})})
    for candidate in (later, claim(witnessed=False), claim(value='No published study'), claim(dated=False)):
        assert checklist(snapshot_at(anchor, [candidate]))[0].value == 'unknown'
    assert checklist(snapshot_at(anchor, [negative]))[0].model_dump() == {
        'milestone': 'prototype',
        'value': 'no',
        'claim_ids': ['claim_prototype'],
    }
    assert checklist([negative, claim(value='yes').model_copy(update={'claim_id': 'affirmed'})])[0].value == 'unknown'
    follow = claim('series_a').model_copy(update={'lower_on': '2020-02-01', 'upper_on': '2020-02-29'})
    points = points_for(anchor, [anchor.claim, follow], '2020-02-29')
    assert points[0].is_anchor and points[0].lower_days == 0
    assert (points[1].lower_days, points[1].upper_days) == (1, 59)
    a = claim('clinical_study').model_copy(update={'upper_on': '2020-01-31'})
    b = a.model_copy(update={'claim_id': 'another_study', 'lower_on': '2020-01-10', 'upper_on': '2020-01-20'})
    assert select_anchor('first_provider_or_clinical_study', [a, b], None, '2020-01-31') is None


def test_live_api_anchors_curation_and_snapshot_abstention(demo_db):
    with TestClient(create_app(demo_db)) as client:
        result = client.get('/api/precedents/subj_ht_mri?as_of=2026-11-21')
        assert result.status_code == 200, result.text
        payload = result.json()
        assert payload['subject']['kind'] == 'research_project'
        assert payload['subject']['points'] == []
        assert len(payload['curated']) == 3 and payload['abstention']
        assert payload['similarity_version'] == VERSION == 'witnessed-gower-b0:3'
        assert payload['witness_mode'] == 'strict'
        date_result = client.get('/api/precedents/subj_ht_mri?as_of=2026-11-21&anchor=first_regulatory_decision').json()
        assert any(
            row['anchor']['claim']['date_value'] == '2023-03-31' for row in date_result['curated'] if row['anchor']
        )
        halter = client.get('/api/precedents/discovery_halter?as_of=2026-11-21').json()
        assert halter['subject']['anchor']['claim']['date_value'] == '2016-12'
        assert halter['subject']['status'] == 'reached_outcome'
        assert all(peer['row']['company_id'] != 'discovery_halter' for peer in halter['peers'])
        checklist_result = client.get('/api/precedents/subj_ht_pulsemap/checklist?as_of=2026-11-21').json()
        assert all(value['value'] == 'unknown' for value in checklist_result['subject']['milestones'])
        assert client.get('/api/precedents/missing?as_of=2026-11-21').status_code == 404
        assert client.get('/api/precedents/subj_ht_mri?as_of=2026-02-30').status_code == 422


def test_outcome_library_reconciles_denominators_pagination_and_events(demo_db):
    with TestClient(create_app(demo_db)) as client:
        response = client.get('/api/workbench/outcomes?limit=3')
        assert response.status_code == 200
        library = response.json()
        assert library['candidate_records'] == 453 and library['total'] == library['cohort_entries'] == 55
        assert len(library['rows']) == 3 and sum(library['counts']['statuses'].values()) == 55
        assert sum(item['denominator'] for item in library['sectors_comparison']) == 55
        assert sum(item['entries'] for item in library['vintage_counts']) == 55
        assert all(sum(item['statuses'].values()) == item['denominator'] for item in library['sectors_comparison'])
        assert [item['deals'] for item in library['benchmarks']] == [66, 76]
        tiro = next(item for item in library['stories'] if item['company_id'] == 'public_tirolifesciencesltd')
        assert tiro['status'] == 'unknown' and all('primary unknown' in note for note in tiro['notes'].values())
        next_page = client.get('/api/workbench/outcomes?limit=3&offset=3').json()
        assert not {item['company_id'] for item in next_page['rows']} & {item['company_id'] for item in library['rows']}
        subset = client.get('/api/workbench/outcomes?vintage=2022&sector=Healthtech&endpoint=secondary').json()
        assert subset['total'] < library['total'] and subset['endpoint'] == 'secondary'
        assert all(row['vintage'] == 2022 and row['sector'] == 'Healthtech' for row in subset['rows'])
        secondary = client.get('/api/workbench/outcomes?endpoint=secondary').json()
        for endpoint in (library, secondary):
            supie = next(row for row in endpoint['stories'] if row['company_id'] == 'public_supie')
            registry = {point['claim']['field']: point['claim']['date_value'] for point in supie['points']}
            assert registry['voluntary_administration'] == '2023-10-30'
            assert registry['closed_liquidation'] == '2023-11-09' and supie['status'] == 'closed_before_outcome'
        halter = next(row for row in secondary['stories'] if row['company_id'] == 'discovery_halter')
        bounded = next(p for p in halter['points'] if p['claim']['field'] == 'secondary_timing_bound')
        assert bounded['claim']['lower_on'] == '2016-12-01'
        assert bounded['claim']['upper_on'] == '2018-01-31'
        gates = client.get('/api/workbench/gates').json()
        assert gates['secondary']['unknown_or_lost'] == 47 and not gates['primary']['gate_ready']
        assert client.get('/api/workbench/outcomes?cohort=B').status_code == 422


def test_swimlane_labels_intervals_straddling_the_window():
    from backend.outcome_library import row_notes

    anchor = WorkbenchAnchor(kind='first_institutional_round', claim=claim('seed'))
    event = claim('series_a').model_copy(update={'lower_on': '2022-12-30', 'upper_on': '2023-01-02'})
    points = points_for(anchor, [anchor.claim, event], '2023-01-03')
    assert row_notes(points, anchor, 'unknown') == {event.claim_id: 'Unresolved at the 36-month boundary'}


def test_append_only_disputes_keep_source_claim_and_gate_response_independent(demo_db, tmp_path):
    import shutil
    import sqlite3
    from uuid import uuid4

    db = tmp_path / 'disputes.sqlite'
    shutil.copyfile(demo_db, db)
    route = '/api/precedents/discovery_halter'
    with TestClient(create_app(db)) as client:
        original = client.get(route + '?as_of=2026-11-21').json()['subject']
        case = next(claim for claim in original['claims'] if claim['claim_id'] == 'halter_series_a_2018')
        body = {
            'claim_id': case['claim_id'],
            'analyst': 'Synthetic review',
            'rationale': 'Verify settlement month.',
            'request_id': str(uuid4()),
        }
        assert (
            client.post(route + '/disputes', json=body, headers={'origin': 'https://elsewhere.example'}).status_code
            == 403
        )
        assert client.post(route + '/disputes', json=dict(body, rationale='  ')).status_code == 422
        assert client.post(route + '/disputes', json=dict(body, claim_id='bogus')).status_code == 404
        response = client.post(route + '/disputes', json=body)
        assert response.status_code == 200, response.text
        assert client.post(route + '/disputes', json=body).json() == response.json()
        assert client.post(route + '/disputes', json=dict(body, rationale='Changed payload')).status_code == 409
        updated = client.get(route + '?as_of=2026-11-21').json()['subject']
        latest = next(claim for claim in updated['claims'] if claim['claim_id'] == case['claim_id'])
        assert latest['passage'] == case['passage'] and latest['url'] == case['url']
        assert latest['review_state'] == 'disputed'
        assert [item['rationale'] for item in latest['review_events']] == [body['rationale']]
        assert updated['status'] == 'unknown'
        gate = client.get('/api/workbench/gates').json()
        assert gate['validation_state'] == 'not_validated'
        assert not gate['primary']['gate_ready'] and not gate['secondary']['gate_ready']
        assert client.get('/api/workbench/outlook').status_code == 404
        assert all('probability' not in key and 'estimate' not in key for key in gate)
    with sqlite3.connect(db) as conn:
        assert conn.execute('SELECT COUNT(*) FROM workbench_claim_reviews').fetchone()[0] == 1
        for statement in (
            'DELETE FROM workbench_claim_reviews',
            "UPDATE workbench_claim_reviews SET rationale='change'",
        ):
            with pytest.raises(sqlite3.IntegrityError, match='append-only'):
                conn.execute(statement)


def test_screening_note_download_round_trips_existing_measurement_draft(demo_db):
    from backend.precedent_contracts import PrecedentResponse
    from backend.screening_note import ScreeningDraft, screening_draft

    with TestClient(create_app(demo_db)) as client:
        path = '/api/precedents/subj_ht_mri'
        query = '?as_of=2026-11-21&anchor=first_regulatory_decision'
        response = client.get(path + '/screening-note' + query)
        assert response.status_code == 200, response.text
        assert 'attachment;' in response.headers['content-disposition']
        draft = ScreeningDraft.model_validate_json(response.content)
        assert draft == ScreeningDraft.model_validate(draft.model_dump())
        [subject] = draft.alternatives
        assert subject.metadata.role == 'subject' and subject.metadata.company_id == 'subj_ht_mri'
        assert subject.metadata.anchor_kind == 'first_regulatory_decision'
        assert subject.metadata.anchor_event is None and subject.metadata.as_of == '2026-11-21'
        assert subject.metadata.snapshot_basis == 'subject_as_of'
        assert draft.performances == draft.weight_profiles == draft.scenarios == []

        real = PrecedentResponse.model_validate(client.get(path + query).json())
        witnessed = claim('prototype', 'yes')
        best = row('positive_peer', status='reached_outcome', rank=4)
        best.anchor = WorkbenchAnchor(kind=real.anchor_kind, claim=claim('regulatory_clearance'))
        best.milestones = checklist([witnessed])
        ranked = rank_peers(row('subject'), [best, row('middle_peer'), row('closed_peer', 'closed_before_outcome', 0)])
        comps, _, _ = select_comps(ranked)
        synthetic = real.model_copy(update={'comps': comps, 'abstention': None})
        with_comps = screening_draft(synthetic)
        restored = ScreeningDraft.model_validate_json(with_comps.model_dump_json())
        assert restored == with_comps
        by_role = {item.metadata.role: item.metadata for item in restored.alternatives}
        assert set(by_role) == {'subject', 'ceiling', 'typical', 'floor'}
        assert by_role['ceiling'].anchor_event.claim.claim_id == 'claim_regulatory_clearance'
        assert by_role['ceiling'].milestones[0].claim_ids == ['claim_prototype']
        assert by_role['ceiling'].dimensions == ranked[0].dimensions
        assert by_role['ceiling'].comp_outcome == best.comp_outcome
        assert restored.performances and not restored.weight_profiles

        representative, _, _ = select_comps(rank_peers(row('subject'), [row(f'peer_{i}') for i in range(3)]))
        single = screening_draft(real.model_copy(update={'comps': representative}))
        assert [item.metadata.role for item in single.alternatives] == ['subject', 'representative']


def test_analogy_uses_current_witnesses_and_toku_excludes_zero_workflow_peers(demo_db):
    from backend.precedent_contracts import PrecedentResponse

    today = '2026-11-21'
    subjects = ('subj_ht_mri', 'subj_ht_neurofanos', 'subj_ht_ivf', 'subj_ht_vistavision', 'subj_ht_pulsemap')
    with TestClient(create_app(demo_db)) as client:
        for key in subjects:
            result = client.get(f'/api/precedents/{key}?as_of={today}')
            result.raise_for_status()
            payload = PrecedentResponse.model_validate(result.json())
            current = [item for item in payload.subject.claims if item.claim_id.startswith(f'witnessed:{key}:')]
            assert current and all(item.witness and item.witness.available_on <= today for item in current)
            assert payload.subject.anchor is None
            assert payload.subject.snapshot == current
        historical = client.get('/api/precedents/subj_ht_mri?as_of=2026-10-27').json()
        assert not historical['subject']['snapshot']
        assert not any(
            claim['claim_id'].startswith('witnessed:subj_ht_mri:') for claim in historical['subject']['claims']
        )

        conflict = client.get(f'/api/precedents/public_carepatron?as_of={today}').json()
        assert not any(
            item['claim_id'].startswith('witnessed:public_carepatron:') for item in conflict['subject']['snapshot']
        )
        for mode in ('strict', 'contemporaneous'):
            result = client.get(f'/api/precedents/toku?as_of={today}&witness_mode={mode}')
            result.raise_for_status()
            comparison = PrecedentResponse.model_validate(result.json())
            assert comparison.peers == comparison.comps == []
            assert features(comparison.subject)['provider_study'] == 'yes'
            assert all(item.peer_witness_delay_days is None for item in comparison.subject.snapshot)
        heartlab = client.get(f'/api/precedents/discovery_heartlab?as_of={today}').json()['subject']
        assert heartlab['status'] == 'observed_no_outcome'
        assert heartlab['comp_outcome']['label'] == 'Operating on seed'
        assert heartlab['comp_outcome']['date_value'] == '2026-06-30'
        heartlab_path = '/api/precedents/discovery_heartlab?as_of='
        before = client.get(heartlab_path + '2026-06-29').json()['subject']['claims']
        dated = client.get(heartlab_path + '2026-06-30').json()['subject']['claims']
        assert not any(item['claim_id'] == 'heartlab_university_2026' for item in before)
        [activity] = [item for item in dated if item['claim_id'] == 'heartlab_university_2026']
        assert activity['witness']['available_on'] == '2026-06-30'
        firstcheck = client.get(f'/api/precedents/public_firstcheckltd?as_of={today}').json()['subject']
        assert firstcheck['status'] == 'unknown' and firstcheck['comp_outcome']['date_value'] == '2021-10-13'


def test_contemporaneous_window_respects_earliest_bound_as_of_disputes_and_strict_fields():
    anchor = WorkbenchAnchor(
        kind='first_institutional_round',
        claim=claim('seed').model_copy(
            update={'date_value': '2020-01', 'date_precision': 'month', 'upper_on': '2020-01-31'}
        ),
    )

    def later(field, on, **updates):
        base = claim(field, 'later value')
        return base.model_copy(
            update={
                'date_value': on,
                'lower_on': on,
                'upper_on': on,
                'published_on': on,
                'witness': base.witness.model_copy(update={'available_on': on}),
                **updates,
            }
        )

    strict = [claim('clinical_user', 'radiologist')]
    additions = [
        later('clinical_user', '2020-01-04'),
        later('buyer', '2020-03-31'),
        later('description', '2020-04-01'),
        later('modality', '2020-01-04', review_state='disputed'),
    ]
    assert contemporaneous_snapshot(anchor, strict, additions, '2020-03-30') == strict
    original, admitted = contemporaneous_snapshot(anchor, strict, additions, '2020-04-02')
    assert original == strict[0] and admitted.field == 'buyer' and admitted.peer_witness_delay_days == 90
    assert additions[1].peer_witness_delay_days is None


def test_contemporaneous_preview_exposes_unranked_witnesses_and_keeps_subject_and_checklist_strict(demo_db):
    with TestClient(create_app(demo_db)) as client:
        path = '/api/precedents/subj_ht_mri'
        query = '?as_of=2026-11-21'
        contemporaneous_query = query + '&witness_mode=contemporaneous'
        strict, extended = [client.get(path + suffix).json() for suffix in (query, contemporaneous_query)]
        assert strict['subject'] == extended['subject'] and not strict['late_witness_peers']
        late = {item['company_id']: item['snapshot'] for item in extended['late_witness_peers']}
        assert {claim['peer_witness_delay_days'] for claim in late['discovery_theinsidescompany']} == {20}
        assert {claim['peer_witness_delay_days'] for claim in late['discovery_respiraq']} == {None, 56}
        assert extended['witness_mode'] == 'contemporaneous' and not extended['peers']
        note = client.get(path + '/screening-note' + contemporaneous_query).json()
        assert note['alternatives'][0]['metadata']['witness_mode'] == 'contemporaneous'
        assert client.get(path + '/checklist' + contemporaneous_query).json()['subject'] == strict['subject']
        assert client.get(path + query + '&witness_mode=invalid').status_code == 422


def test_mri_peer_gaps_at_institutional_and_study_anchors(demo_db):
    from contextlib import closing
    from backend.database import connect
    from backend.precedents import response

    today = '2026-11-21'
    with closing(connect(demo_db)) as conn:
        catalog = PrecedentCatalog(conn, today)
        entry = response(conn, 'subj_ht_mri', 'first_institutional_round', today)
        study = response(conn, 'subj_ht_mri', 'first_provider_or_clinical_study', today)
        left = features(entry.subject)
        assert left == features(study.subject)
        assert set(left) == {'modality', 'clinical_user', 'output_type', 'description'}
        assert entry.peer_count_evaluated == 55 and study.peer_count_evaluated == 1
        assert entry.peers == entry.comps == study.peers == study.comps == []
        assert not features(catalog.row('discovery_formuslabs', entry.anchor_kind))
        assert set(left) - features(catalog.row('discovery_formuslabs', study.anchor_kind)).keys() == {
            'modality',
            'clinical_user',
            'output_type',
        }
        tiro = features(catalog.row('public_tirolifesciencesltd', entry.anchor_kind))
        assert set(left) - tiro.keys() == {'clinical_user', 'output_type'}
        assert score(left, tiro, corpus_idf([left, tiro]))[1] == 0.125


def test_snapshot_packet_refuses_late_or_mismatched_witness_and_anchor():
    import json
    from pydantic import ValidationError
    from backend.witnessed_snapshots import PACKET, WitnessedSnapshotPacket, WitnessedSnapshots

    packet = json.loads(PACKET.read_bytes())
    case = next(profile for profile in packet['profiles'] if profile['subject_id'] == 'toku')
    case['cutoff'] = '2021-06-28'
    with pytest.raises(ValidationError, match='source-version witness by its profile cutoff'):
        WitnessedSnapshotPacket.model_validate(packet)
    case['cutoff'] = '2021-06-29'
    case['features'][0]['source_id'] = 'ws_first_cio_2016'
    with pytest.raises(ValidationError, match='source-version witness by its profile cutoff'):
        WitnessedSnapshotPacket.model_validate(packet)
    catalog = WitnessedSnapshots()
    anchor = WorkbenchAnchor(kind='first_institutional_round', claim=claim('seed'))
    assert catalog.claims('toku', '2026-11-21', entry_anchor=anchor) == []
    matching = anchor.model_copy(
        update={
            'claim': anchor.claim.model_copy(
                update={
                    'claim_id': 'toku_entry',
                    'lower_on': '2021-06-29',
                    'upper_on': '2021-06-29',
                }
            )
        }
    )
    assert catalog.claims('toku', '2026-11-21', entry_anchor=matching)
    mismatched_date = matching.model_copy(
        update={'claim': matching.claim.model_copy(update={'lower_on': '2021-06-28'})}
    )
    assert not catalog.claims('toku', '2026-11-21', entry_anchor=mismatched_date)


def test_abstention_explains_nearest_candidates_without_outcomes_or_threshold_changes(demo_db):
    from backend.precedent_similarity import MIN_CLINICAL_SIMILARITY, MIN_PEERS, TOP_K

    with TestClient(create_app(demo_db)) as client:
        data = client.get('/api/precedents/toku', params={'as_of': '2026-11-21'}).json()
    assert data['comps'] == [] and data['abstention']
    assert data['thresholds'] == {
        'min_clinical_similarity': MIN_CLINICAL_SIMILARITY,
        'min_similarity': MIN_SIMILARITY,
        'min_coverage': MIN_COVERAGE,
        'min_peers': MIN_PEERS,
        'top_k': TOP_K,
    }
    candidates = data['nearest_candidates']
    assert 0 < len(candidates) <= 3
    for candidate in candidates:
        assert 'comp_outcome' not in candidate and 'row' not in candidate
        assert candidate['coverage'] > 0
        assert not (candidate['meets_clinical'] and candidate['meets_similarity'] and candidate['meets_coverage'])
    heartlab = next(item for item in candidates if item['display_name'] == 'HeartLab')
    assert heartlab['clinical_similarity'] == 0 and heartlab['meets_similarity'] and not heartlab['meets_clinical']
    assert 'stage' in heartlab['missing_on_peer']
