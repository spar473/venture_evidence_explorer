"""Validate the research packet only; never imports or opens the app database.

Requires Python 3.10+ and jsonschema with Draft 2020-12 support.
Run from any directory: python3 /absolute/path/validate_research_example.py
"""
from pathlib import Path
from datetime import date
from copy import deepcopy
import json
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/'Research_Interchange_v0.2.1.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR=Draft202012Validator(SCHEMA,format_checker=FormatChecker())
COLLECTIONS={'subjects':'subject_id','parties':'party_id','sources':'source_id',
 'observations':'observation_id','events':'event_id','event_reports':'report_id',
 'unknowns':'unknown_id','proposed_annotations':'annotation_id','readiness':'readiness_id',
 'reconciliation_cases':'case_id','access_gaps':'gap_id','review_events':'review_event_id'}

def require(test,message):
    if not test:raise ValueError(message)

def validate(packet, validation_as_of=None):
    VALIDATOR.validate(packet)
    prepared = date.fromisoformat(packet['metadata']['prepared_on'])
    # The caller's clock is independent of dates supplied inside the packet.
    as_of = date.fromisoformat(validation_as_of) if validation_as_of else date.today()
    require(prepared <= as_of, 'preparation after validation-as-of date')
    indexes={}
    all_ids=[]
    for name,key in COLLECTIONS.items():
        rows=packet[name];indexes[name]={r[key]:r for r in rows}
        require(len(indexes[name])==len(rows),'duplicate IDs: '+name)
        all_ids.extend(r[key] for r in rows)
    conclusions=[c for r in packet['readiness'] for c in r['supported_conclusions']]
    requirements=[q for r in packet['readiness'] for q in r['requirements']]
    all_ids.extend(c['conclusion_id'] for c in conclusions)
    all_ids.extend(q['requirement_id'] for q in requirements)
    require(len(set(all_ids))==len(all_ids),'IDs must be globally unique')
    def refs(values,collection):
        require(all(v in indexes[collection] for v in values),'unresolved '+collection+' reference')
    def subject_refs(values):refs(values,'subjects')
    def obs_refs(values,subjects=None):
        refs(values,'observations')
        if subjects is not None:
            require(all(indexes['observations'][v]['subject_id'] in subjects for v in values),'observation subject mismatch')
    def unknown_refs(values,subjects):
        refs(values,'unknowns')
        require(all(indexes['unknowns'][v]['subject_id'] in subjects for v in values),'unknown subject mismatch')
    def case_refs(values,subjects):
        refs(values,'reconciliation_cases')
        require(all(set(indexes['reconciliation_cases'][v]['subject_ids']) <= set(subjects) for v in values),'case subject mismatch')
    def lower(t):
        if t['precision']=='unknown':return None
        suffix={'year':'-01-01','month':'-01','day':''}[t['precision']]
        return date.fromisoformat(t['value']+suffix)
    def same_time(a,b):
        return a['value']==b['value'] and a['precision']==b['precision']
    def walk(value,key=''):
        if isinstance(value,dict):
            if {'value','precision','basis','unknown_reason'} <= value.keys():
                d=lower(value)
                if d is not None and 'target' not in key:
                    require(d<=prepared,'non-target time after research cutoff')
            # These are raw ISO dates, not precision-bearing time objects.
            for k in ('retrieved_on','checked_on','reviewed_on','as_of','evidence_cutoff'):
                if k in value:
                    require(date.fromisoformat(value[k])<=prepared,k+' after preparation date')
            for k,v in value.items():walk(v,k)
        elif isinstance(value,list):
            for v in value:walk(v,key)
    walk(packet)
    for s in packet['sources']:
        pub=lower(s['published_time'])
        require(pub is None or pub<=date.fromisoformat(s['retrieved_on']),'publication after retrieval')
        updated=lower(s['updated_time'])
        require(updated is None or updated<=date.fromisoformat(s['retrieved_on']),'source update after retrieval')
    for o in packet['observations']:
        subject_refs([o['subject_id']]);refs([o['source_id']],'sources')
        require(indexes['sources'][o['source_id']]['access_status']=='text_read','observation cites unread source')
        require(o['review']['checked_on']>=indexes['sources'][o['source_id']]['retrieved_on'],'observation check before source retrieval')
        if o['related_party_id']:refs([o['related_party_id']],'parties')
        case_refs(o['conflict_ids'],[o['subject_id']])
        if o['field']=='launch_target':
            require(o['assertion_nature']=='intention_target' and lower(o['target_time']) is not None,'launch target must remain intention with target time')
            require(lower(o['effective_time']) is None,'target year is not an actual launch date')
        if o['money'] and o['money']['currency']['value'] is None:
            require(bool(o['money']['currency']['unknown_reason']),'missing currency reason')
    for e in packet['events']:
        subject_refs([e['subject_id']]);refs(e['state_basis_report_ids'],'event_reports')
        reports=[indexes['event_reports'][r] for r in e['state_basis_report_ids']]
        require(all(r['event_id']==e['event_id'] and r['subject_id']==e['subject_id'] for r in reports),'event/report subject or identity mismatch')
        require(e['event_state'] in [r['reported_event_state'] for r in reports],'unsupported event-state projection')
        if e['scenario']=='target':
            require(lower(e['occurrence_time']) is None and lower(e['target_time']) is not None,'target occurrence conflation')
            require(all(r['assertion_nature']=='intention_target' for r in reports),'target report needs intention nature')
        if lower(e['occurrence_time']) is not None:
            require(any(same_time(r['reported_occurrence_time'],e['occurrence_time']) for r in reports),'event date lacks matching report precision')
        if lower(e['target_time']) is not None:
            require(any(same_time(r['reported_target_time'],e['target_time']) for r in reports),'event target lacks matching report precision')
        if e['identity_resolution']=='unresolved_possible_duplicate':
            require(any(c['case_kind']=='possible_duplicate_event' and e['event_id'] in c['event_ids'] for c in packet['reconciliation_cases']),'duplicate candidate missing open reconciliation case')
    for r in packet['event_reports']:
        refs([r['event_id']],'events');refs([r['source_id']],'sources')
        e=indexes['events'][r['event_id']]
        require(r['report_id'] in e['state_basis_report_ids'],'report not linked by event')
        require(r['subject_id']==e['subject_id'],'report/event subject mismatch')
        obs_refs(r['observation_ids'],[r['subject_id']])
        support=[indexes['observations'][o] for o in r['observation_ids']]
        require(all(o['source_id']==r['source_id'] for o in support),'report mixes source documents')
        require(all(o['assertion_nature']==r['assertion_nature'] and o['source_relationship']==r['source_relationship'] for o in support),'report mixes claim nature or source relationship')
        for report_key,obs_key in [('reported_target_time','target_time'),('reported_occurrence_time','effective_time')]:
            if lower(r[report_key]) is not None:
                require(any(same_time(r[report_key],o[obs_key]) for o in support),'report time lacks matching observation precision: '+report_key)
        require(r['review']['checked_on']>=indexes['sources'][r['source_id']]['retrieved_on'],'report check before source retrieval')
    for u in packet['unknowns']:
        subject_refs([u['subject_id']]);refs(u['inspected_source_ids'],'sources');refs(u['access_gap_ids'],'access_gaps')
        require(all(u['subject_id'] in indexes['access_gaps'][g]['subject_ids'] for g in u['access_gap_ids']),'gap/unknown subject mismatch')
        require(all(indexes['sources'][s]['retrieved_on']<=u['as_of'] for s in u['inspected_source_ids']),'unknown assessed before source inspection')
        require(all(indexes['access_gaps'][g]['retrieved_on']<=u['as_of'] for g in u['access_gap_ids']),'unknown assessed before access attempt')
        require(u['review']['checked_on']>=u['as_of'],'unknown review before assessment')
    for a in packet['proposed_annotations']:
        subject_refs(a['subject_ids']);obs_refs(a['basis_observation_ids'],a['subject_ids'])
    for c in packet['reconciliation_cases']:
        subject_refs(c['subject_ids']);refs(c['event_ids'],'events');obs_refs(c['observation_ids'],c['subject_ids'])
        require(all(indexes['events'][e]['subject_id'] in c['subject_ids'] for e in c['event_ids']),'case/event subject mismatch')
        if c['case_kind']=='possible_duplicate_event':require(len(c['event_ids'])>=2,'duplicate case needs multiple candidates')
    for gap in packet['access_gaps']:subject_refs(gap['subject_ids'])
    for r in packet['readiness']:
        subjs=r['subject_ids'];subject_refs(subjs);obs_refs(r['supporting_observation_ids'],subjs)
        unknown_refs(r['missing_unknown_ids'],subjs);case_refs(r['unresolved_case_ids'],subjs)
        for oid in r['supporting_observation_ids']:
            source=indexes['sources'][indexes['observations'][oid]['source_id']]
            require(source['retrieved_on']<=r['evidence_cutoff'],'support retrieved after readiness cutoff')
        require(all(indexes['unknowns'][u]['as_of']<=r['evidence_cutoff'] for u in r['missing_unknown_ids']),'unknown assessed after readiness cutoff')
        for cid in r['unresolved_case_ids']:
            case=indexes['reconciliation_cases'][cid]
            require(all(indexes['sources'][indexes['observations'][o]['source_id']]['retrieved_on']<=r['evidence_cutoff'] for o in case['observation_ids']),'case evidence after readiness cutoff')
        for q in r['requirements']:
            required=q['required_subject_ids']
            require(set(required)<=set(subjs),'requirement outside question subjects')
            subject_refs(required)
            obs_refs(q['supporting_observation_ids'],required);unknown_refs(q['missing_unknown_ids'],required);case_refs(q['unresolved_case_ids'],required)
            covered={indexes['observations'][o]['subject_id'] for o in q['supporting_observation_ids']}
            if q['status']=='supported':
                require(set(required)<=covered,'supported requirement lacks required subject coverage')
                require(not q['missing_unknown_ids'] and not q['unresolved_case_ids'],'supported requirement still has gaps or disputes')
            if q['status']=='partially_supported':
                require(q['supporting_observation_ids'] and (q['missing_unknown_ids'] or q['unresolved_case_ids']),'partial requirement needs evidence and explicit gaps')
            if q['status']=='missing':require(q['missing_unknown_ids'],'missing requirement lacks explicit gap')
            if q['status']=='disputed':require(q['unresolved_case_ids'],'disputed requirement lacks case')
        for field,subfield in [('supporting_observation_ids','supporting_observation_ids'),('missing_unknown_ids','missing_unknown_ids'),('unresolved_case_ids','unresolved_case_ids')]:
            require(set(r[field])=={x for q in r['requirements'] for x in q[subfield]},'readiness union does not match requirements')
        for conclusion in r['supported_conclusions']:
            require(set(conclusion['subject_ids'])<=set(subjs),'conclusion outside question subjects')
            obs_refs(conclusion['basis_observation_ids'],conclusion['subject_ids'])
            covered={indexes['observations'][o]['subject_id'] for o in conclusion['basis_observation_ids']}
            require(set(conclusion['subject_ids'])<=covered,'conclusion lacks declared subject coverage')
            require(set(conclusion['basis_observation_ids'])<=set(r['supporting_observation_ids']),'conclusion not in readiness evidence')
            actual={indexes['observations'][o]['source_id'] for o in conclusion['basis_observation_ids']}
            require(set(conclusion['source_ids'])==actual,'conclusion source lineage mismatch')
            for sid in actual:require(indexes['sources'][sid]['retrieved_on']<=r['evidence_cutoff'],'source retrieved after readiness cutoff')
        require(bool(r['supported_conclusions'])==(r['assessment']=='limited_conclusions_supported'),'readiness label disagrees with supported conclusion presence')
    typed_targets={kind:indexes[collection] for kind,collection in [('subject','subjects'),('observation','observations'),('event','events'),('event_report','event_reports'),('unknown','unknowns'),('readiness','readiness')]}
    typed_targets['conclusion']={c['conclusion_id']:c for c in conclusions}
    review_targets={tid:(kind,target) for kind,rows in typed_targets.items() for tid,target in rows.items()}
    for rev in packet['review_events']:
        require(rev['target_id'] in typed_targets[rev['target_type']],'review target type/ID mismatch')
    accepted=0
    for tid,(kind,target) in review_targets.items():
        review=target['review']
        if review['state']=='accepted':
            accepted+=1;refs([review['acceptance_review_id']],'review_events')
            decision=indexes['review_events'][review['acceptance_review_id']]
            require(decision['target_id']==tid and decision['target_type']==kind and decision['decision']=='accepted','acceptance decision target mismatch')
            require(decision['actor_role']==review['actor_role'],'acceptance reviewer-role mismatch')
            require(decision['reviewed_on']<=review['checked_on'],'acceptance decision after projected review state')
    require(accepted==packet['metadata']['accepted_records_count'],'acceptance count mismatch')
    return {k:len(packet[k]) for k in COLLECTIONS}

def negative_tests(packet, validation_as_of=None):
    results=[]
    def reject(name,mutate):
        bad=deepcopy(packet);mutate(bad)
        try:validate(bad, validation_as_of)
        except (ValueError, ValidationError) as exc:
            results.append({'case':name,'expected_rejection':True,'observed':'REJECTED','category':type(exc).__name__})
        else:raise AssertionError('Negative case unexpectedly passed: '+name)
    reject('duplicate_observation_id',lambda p:p['observations'].append(deepcopy(p['observations'][0])))
    reject('orphan_source',lambda p:p['observations'][0].update(source_id='src_missing'))
    reject('cross_subject_report',lambda p:p['event_reports'][0].update(observation_ids=['obs_rl_price']))
    reject('target_marked_completed',lambda p:next(e for e in p['events'] if e['scenario']=='target').update(event_state='completed'))
    reject('target_year_as_occurrence',lambda p:next(e for e in p['events'] if e['scenario']=='target').update(occurrence_time={'value':'2025','precision':'year','basis':'Incorrectly promoted target.','unknown_reason':None}))
    reject('invalid_calendar_date',lambda p:p['observations'][0].update(effective_time={'value':'2024-13-32','precision':'day','basis':'Invalid date.','unknown_reason':None}))
    reject('missing_currency_reason',lambda p:next(o for o in p['observations'] if o['money'])['money']['currency'].update(unknown_reason=None))
    reject('assistant_acceptance',lambda p:p['observations'][0]['review'].update(state='accepted',acceptance_review_id='review_fake'))
    reject('proposal_used_as_fact',lambda p:p['proposed_annotations'][0].update(eligible_as_accepted_fact=True))
    reject('conclusion_without_evidence',lambda p:p['readiness'][0]['supported_conclusions'][0].update(basis_observation_ids=[]))
    reject('conclusion_wrong_sources',lambda p:p['readiness'][0]['supported_conclusions'][0].update(source_ids=['src_rl_movac']))
    reject('unread_source_as_evidence',lambda p:p['observations'][0].update(source_id='src_healthnz_blocked'))
    reject('hidden_duplicate_candidates',lambda p:p.update(reconciliation_cases=[c for c in p['reconciliation_cases'] if c['case_kind']!='possible_duplicate_event']))
    reject('guessed_zero_unknown',lambda p:p['unknowns'][0].update(value=0))
    return results

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of',default=date.today().isoformat(),help='External validation cutoff; defaults to local calendar date.')
    args=parser.parse_args()
    packet=json.loads((HERE/'Two_Dossier_Research_Example.json').read_text())
    counts=validate(packet,args.as_of);negatives=negative_tests(packet,args.as_of)
    from regression_cases import run_regressions
    regressions=run_regressions(validate,packet,args.as_of)
    print(json.dumps({'schema':'PASS','semantic_checks':'PASS','validation_as_of':args.as_of,'counts':counts,'negative_cases':negatives,'regressions':regressions,'limits':'Structure, represented chronology and linkage only; not issuer truth, source entailment, reviewer identity authentication or usefulness.'},indent=2))
