from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.precedent_contracts import WorkbenchAnchor, WorkbenchClaim, WorkbenchRow
from backend.precedent_evidence import checklist, points_for, select_anchor, snapshot_at
from backend.precedent_similarity import corpus_idf, rank_peers, score, select_comps
from backend.reference_pool import Witness
from scripts.healthtech_demo import prepare_demo


@pytest.fixture(scope='module')
def demo_db(tmp_path_factory):
    return Path(prepare_demo(tmp_path_factory.mktemp('precedents'))['database'])


def claim(key='prototype', value='no', *, dated=True, witnessed=True):
    return WorkbenchClaim(claim_id='claim_' + key, field=key, value=value, passage='Synthetic test claim.',
        publisher='Example', url='https://example.org/', published_on='2020-01-01', retrieved_on='2026-11-21',
        date_value='2020-01-01' if dated else None, date_precision='day' if dated else None,
        lower_on='2020-01-01' if dated else None, upper_on='2020-01-01' if dated else None,
        witness=Witness(witness_id='witness_case', source_id='example', kind='publisher_dated',
            available_on='2020-01-01', url='https://example.org/', locator='Test date') if witnessed else None)


def row(key, status='observed_no_outcome', rank=2, features=None):
    snapshot = [claim(field, value) for field, value in (features or {
        'stage': 'seed', 'buyer': 'hospital', 'months_since_founding': 12,
        'description': 'imaging surgical planning', 'regulatory_class': 2,
    }).items()]
    return WorkbenchRow(company_id=key, display_name=key, kind='company', sector='Healthtech',
        anchor=None, points=[], snapshot=snapshot, claims=snapshot, milestones=checklist(snapshot),
        gaps=[], status=status, outcome_rank=rank, outcome_label=None, not_alignable=None)


def test_gower_missingness_numeric_ranges_and_deterministic_text():
    left = {'buyer':'hospital', 'months_since_founding':12, 'description':'imaging planning', 'stage':'seed'}
    right = {'buyer':'hospital', 'months_since_founding':42, 'description':'images planning', 'clinical_user':'doctor'}
    value, coverage, dimensions = score(left, right, corpus_idf([left, right]))
    assert value == pytest.approx((.25 + .20 + .15 * .75) / (.25 + .20 + .15))
    assert coverage == pytest.approx(.25 / 4 + .20 / 3 + .15 / 3)
    assert dimensions[3].similarity is None
    assert dimensions[4].different_fields == ['months_since_founding']


def test_top_k_abstention_tie_break_unknown_and_verified_floor():
    subject = row('subject')
    peers = rank_peers(subject, [row('company_' + str(i).zfill(2)) for i in reversed(range(12))]
                      + [row('outside_closure', 'closed_before_outcome', 0)])
    assert len(peers) == 12 and peers[0].row.company_id == 'company_00'
    comps, no_closure, abstains = select_comps(peers)
    assert no_closure and abstains is None
    assert {comp.peer.row.company_id for comp in comps} == {'company_00'}
    assert select_comps(peers[:2])[2]
    mixed = rank_peers(subject, [row('a_unknown','unknown',None), row('b_closed','closed_before_outcome',0),
                                row('c_exit','acquired_or_ipo_before_outcome',5), row('d_observed')])
    comps, no_closure, abstains = select_comps(mixed)
    assert not no_closure and abstains is None
    assert {comp.role:comp.peer.row.company_id for comp in comps} == {
        'ceiling':'c_exit', 'typical':'d_observed', 'floor':'b_closed',
    }
    assert rank_peers(subject, [row('only_stage', features={'stage':'seed'})]) == []


def test_witness_is_required_by_earliest_anchor_bound_and_no_requires_dated_explicit_claim():
    original = claim('seed', 'Seed')
    anchor = WorkbenchAnchor(kind='first_institutional_round', claim=original.model_copy(
        update={'date_value':'2020-01', 'date_precision':'month', 'upper_on':'2020-01-31'}))
    negative = claim()
    later = negative.model_copy(update={'witness':negative.witness.model_copy(update={'available_on':'2020-01-02'})})
    for candidate in (later, claim(witnessed=False), claim(value='No published study'), claim(dated=False)):
        assert checklist(snapshot_at(anchor, [candidate]))[0].value == 'unknown'
    assert checklist(snapshot_at(anchor, [negative]))[0].model_dump() == {
        'milestone':'prototype', 'value':'no', 'claim_ids':['claim_prototype'],
    }
    assert checklist([negative, claim(value='yes').model_copy(update={'claim_id':'affirmed'})])[0].value == 'unknown'
    follow = claim('series_a').model_copy(update={'lower_on':'2020-02-01','upper_on':'2020-02-29'})
    points = points_for(anchor, [anchor.claim, follow], '2020-02-29')
    assert points[0].is_anchor and points[0].lower_days == 0
    assert (points[1].lower_days, points[1].upper_days) == (1, 59)
    a = claim('clinical_study').model_copy(update={'upper_on':'2020-01-31'})
    b = a.model_copy(update={'claim_id':'another_study','lower_on':'2020-01-10','upper_on':'2020-01-20'})
    assert select_anchor('first_provider_or_clinical_study', [a,b], None, '2020-01-31') is None


def test_live_api_anchors_curation_and_snapshot_abstention(demo_db):
    with TestClient(create_app(demo_db)) as client:
        result = client.get('/api/precedents/subj_ht_mri?as_of=2026-11-21')
        assert result.status_code == 200, result.text
        payload = result.json()
        assert payload['subject']['kind'] == 'research_project'
        assert payload['subject']['points'] == []
        assert len(payload['curated']) == 3 and payload['abstention']
        assert payload['similarity_version'] == 'witnessed-gower-b0:1'
        date_result = client.get('/api/precedents/subj_ht_mri?as_of=2026-11-21&anchor=first_regulatory_decision').json()
        assert any(row['anchor']['claim']['date_value'] == '2023-03-31'
                   for row in date_result['curated'] if row['anchor'])
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
    event = claim('series_a').model_copy(update={'lower_on':'2022-12-30', 'upper_on':'2023-01-02'})
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
        body = {'claim_id':case['claim_id'], 'analyst':'Synthetic review', 'rationale':'Verify settlement month.',
                'request_id':str(uuid4())}
        assert client.post(route + '/disputes', json=body, headers={'origin':'https://elsewhere.example'}).status_code == 403
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
        for statement in ('DELETE FROM workbench_claim_reviews', "UPDATE workbench_claim_reviews SET rationale='change'"):
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
        assert draft.performances == draft.weight_profiles == draft.scenarios == []

        real = PrecedentResponse.model_validate(client.get(path + query).json())
        witnessed = claim('prototype', 'yes')
        best = row('positive_peer', status='reached_outcome', rank=4)
        best.anchor = WorkbenchAnchor(kind=real.anchor_kind, claim=claim('regulatory_clearance'))
        best.milestones = checklist([witnessed])
        ranked = rank_peers(row('subject'), [best, row('middle_peer'), row('closed_peer', 'closed_before_outcome', 0)])
        comps, _, _ = select_comps(ranked)
        synthetic = real.model_copy(update={'comps':comps, 'abstention':None})
        with_comps = screening_draft(synthetic)
        restored = ScreeningDraft.model_validate_json(with_comps.model_dump_json())
        assert restored == with_comps
        by_role = {item.metadata.role: item.metadata for item in restored.alternatives}
        assert set(by_role) == {'subject', 'ceiling', 'typical', 'floor'}
        assert by_role['ceiling'].anchor_event.claim.claim_id == 'claim_regulatory_clearance'
        assert by_role['ceiling'].milestones[0].claim_ids == ['claim_prototype']
        assert by_role['ceiling'].dimensions == ranked[0].dimensions
        assert restored.performances and not restored.weight_profiles


def test_event_witness_enrichment_ranks_company_peers_and_keeps_projects_as_analogies(demo_db):
    from backend.precedent_similarity import MIN_COVERAGE, MIN_SIMILARITY, features
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
            assert payload.subject.snapshot == payload.peers == payload.comps == []
        historical = client.get('/api/precedents/subj_ht_mri?as_of=2026-10-27').json()
        assert not any(claim['claim_id'].startswith('witnessed:subj_ht_mri:') for claim in historical['subject']['claims'])

        conflict = client.get(f'/api/precedents/public_carepatron?as_of={today}').json()
        assert not any(item['claim_id'].startswith('witnessed:public_carepatron:')
                       for item in conflict['subject']['snapshot'])
        result = client.get(f'/api/precedents/toku?as_of={today}')
        result.raise_for_status()
        ranked = PrecedentResponse.model_validate(result.json())
        assert {peer.row.company_id for peer in ranked.peers} >= {
            'discovery_heartlab', 'public_firstcheckltd', 'discovery_respiraq',
        }
        assert {item.role for item in ranked.comps} == {'ceiling', 'typical', 'floor'}
        assert all(peer.similarity >= MIN_SIMILARITY and peer.coverage >= MIN_COVERAGE for peer in ranked.peers)
        assert all(comp.peer.row.status != 'unknown' for comp in ranked.comps)
        assert features(ranked.subject)['provider_study'] == 'yes'
        for peer in ranked.peers:
            anchor = peer.row.anchor.claim.lower_on
            assert all(item.witness.available_on <= anchor for item in peer.row.snapshot)


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
    matching = anchor.model_copy(update={'claim':anchor.claim.model_copy(update={
        'claim_id':'toku_entry', 'lower_on':'2021-06-29', 'upper_on':'2021-06-29',
    })})
    assert catalog.claims('toku', '2026-11-21', entry_anchor=matching)
    mismatched_date = matching.model_copy(update={'claim':matching.claim.model_copy(update={'lower_on':'2021-06-28'})})
    assert not catalog.claims('toku', '2026-11-21', entry_anchor=mismatched_date)
