"""Adversarial copies and permitted counterexamples; never persist mutated research."""
from copy import deepcopy
from jsonschema.exceptions import ValidationError


def record(packet, collection, key, value):
    return next(row for row in packet[collection] if row[key] == value)


def target_event(p):
    return record(p, 'events', 'event_id', 'event_qm_launch_target')


def target_report(p):
    return record(p, 'event_reports', 'report_id', 'report_qm_launch_target')


def target_observation(p):
    return record(p, 'observations', 'observation_id', 'obs_qm_launch_target')


def accept_fixture(p, target_type='observation', when='2026-11-18'):
    observation=p['observations'][0]
    observation['review'].update(state='accepted',actor_role='owner',checked_on=when,
                                 acceptance_review_id='review_synthetic_fixture')
    p['review_events'].append(dict(review_event_id='review_synthetic_fixture',
        target_type=target_type,target_id=observation['observation_id'],actor_role='owner',
        reviewer_id='synthetic_fixture_only',decision='accepted',reviewed_on=when,
        rationale='Synthetic regression fixture; never an actual acceptance.'))
    p['metadata']['accepted_records_count']=1


def remove_counterpart(p):
    ready=p['readiness'][0]
    retained=['obs_rl_solution','obs_rl_admin_user']
    ready['requirements'][0]['supporting_observation_ids']=retained[:]
    ready['supporting_observation_ids']=retained[:]
    conclusion=ready['supported_conclusions'][0]
    conclusion.update(subject_ids=['subj_rosterlab'],basis_observation_ids=retained[:],
                      source_ids=['src_rl_pricing'],text='Limited RosterLab description only.')
    # Requirement still explicitly asks for both subjects, unlike the conclusion.


def future_retrieval_and_readiness(p):
    for source in p['sources']:source['retrieved_on']='2099-01-01'
    for ready in p['readiness']:ready['evidence_cutoff']='2099-01-01'


# The four reviewer findings, expressed against either schema version.
REVIEWER_PROBES=[
    ('unsupported_event_target',lambda p:target_event(p)['target_time'].update(value='2099')),
    ('wrong_review_target_type',lambda p:accept_fixture(p,'subject')),
    ('future_review',lambda p:accept_fixture(p,when='2099-01-01')),
    ('missing_required_counterpart',remove_counterpart),
]


def run_regressions(validate, packet, as_of):
    results=[]
    def reject(name, mutate, expected):
        changed=deepcopy(packet);mutate(changed)
        try:validate(changed,as_of)
        except (ValueError,ValidationError) as exc:
            # Check the intended guard, rather than accepting an unrelated failure.
            if expected not in str(exc):
                raise AssertionError(name+' rejected for unexpected reason: '+str(exc)) from exc
            results.append(dict(case=name,expected='REJECTED',observed='REJECTED',guard=expected))
        else:raise AssertionError('Invalid fixture passed: '+name)
    def allow(name,mutate):
        changed=deepcopy(packet);mutate(changed);validate(changed,as_of)
        results.append(dict(case=name,expected='PASS',observed='PASS'))

    for (name,mutate),guard in zip(REVIEWER_PROBES,[
        'event target lacks matching report precision','review target type/ID mismatch',
        'after preparation date','supported requirement lacks required subject coverage']):
        reject(name,mutate,guard)
    reject('target_precision_mismatch',lambda p:target_event(p)['target_time'].update(value='2025-01',precision='month'),'event target lacks matching report precision')
    def both_targets(p):
        target_event(p)['target_time']['value']='2099'
        target_report(p)['reported_target_time']['value']='2099'
    reject('report_target_not_in_observation',both_targets,'report time lacks matching observation precision')
    def unsupported_occurrence(p):
        event=record(p,'events','event_id','event_qm_award')
        report=record(p,'event_reports','report_id','report_qm_award')
        event['occurrence_time']['value']='2024-10-15'
        report['reported_occurrence_time']['value']='2024-10-15'
    reject('report_occurrence_not_in_observation',unsupported_occurrence,'report time lacks matching observation precision')
    reject('future_retrieval_and_readiness',future_retrieval_and_readiness,'retrieved_on after preparation date')
    reject('future_readiness_alone',lambda p:p['readiness'][0].update(evidence_cutoff='2099-01-01'),'evidence_cutoff after preparation date')
    reject('future_check',lambda p:p['observations'][0]['review'].update(checked_on='2099-01-01'),'checked_on after preparation date')
    reject('future_unknown_assessment',lambda p:p['unknowns'][0].update(as_of='2099-01-01'),'as_of after preparation date')
    reject('future_access_attempt',lambda p:p['access_gaps'][0].update(retrieved_on='2099-01-01'),'retrieved_on after preparation date')
    reject('future_preparation',lambda p:p['metadata'].update(prepared_on='2099-01-01'),'preparation after validation-as-of date')
    reject('check_before_retrieval',lambda p:p['observations'][0]['review'].update(checked_on='2026-11-17'),'observation check before source retrieval')
    reject('unknown_before_inspection',lambda p:p['unknowns'][0].update(as_of='2026-11-17'),'unknown assessed before source inspection')
    def update_after_retrieval(p):
        p['sources'][0]['updated_time']=dict(value='2026-11-18',precision='day',basis='Synthetic update.',unknown_reason=None)
        p['sources'][0]['retrieved_on']='2026-11-17'
    reject('update_after_retrieval',update_after_retrieval,'source update after retrieval')
    def conclusion_overclaims(p):
        p['readiness'][1]['supported_conclusions'][0]['subject_ids'].append('subj_quickmas')
    reject('conclusion_missing_subject_evidence',conclusion_overclaims,'conclusion lacks declared subject coverage')
    def partial_without_gap(p):
        p['readiness'][0]['requirements'][0]['status']='partially_supported'
    reject('partial_without_explicit_gap',partial_without_gap,'partial requirement needs evidence and explicit gaps')
    allow('correct_typed_acceptance_fixture',accept_fixture)
    def limited_scope(p):
        remove_counterpart(p)
        p['readiness'][0]['requirements'][0]['required_subject_ids']=['subj_rosterlab']
        p['readiness'][0]['requirements'][0]['description']='RosterLab description only.'
        p['readiness'][0]['withheld_conclusions'].append('A two-subject solution contrast.')
    allow('one_subject_requirement_in_broad_question',limited_scope)
    allow('partial_charging_conclusion_and_withheld_comparison',lambda p:None)
    def future_target(p):
        both_targets(p);target_observation(p)['target_time']['value']='2099'
    allow('consistently_represented_future_target_fixture',future_target)
    return results
