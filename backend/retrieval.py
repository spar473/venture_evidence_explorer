"""B0 v1: transparent token overlap, deliberately conservative abstention."""
import math
import re
from .repository import browse, detail

METHOD = {
    'name': 'Sourced keyword baseline', 'version': 'b0-token-overlap-1.0',
    'normalization': 'Lowercase alphanumeric tokens, fixed stopwords, fixed morphology map (including imaging/images→image, modelling/models→model, surgical→surgery); no learned synonyms. See backend/retrieval.py.',
    'fields': {'product_customer': ['product_description'], 'commercialisation': ['product_description', 'uoa_connection']},
    'scoring': 'Sum of matched token IDFs / sum of query token IDFs. IDF=1+ln((N+1)/(df+1)); each token counted once per venture.',
    'abstention': 'At least two distinct informative matching tokens and query-token coverage >= 0.15. At most three results; stable venture-ID tie break.',
    'limitations': 'Lexical ranking scores, not probabilities, quality or investment scores. No semantic understanding or validated relevance. Pathway mode searches reported product and university-origin wording, not verified deployment milestones. Awards, proposed annotations and press volume are excluded. Sparse wording may miss useful analogies.',
}
STOP = set('a an the and or for to of in on by with from as at is are was were be been being that this it its their our your which what how can could would should has have had into about through using used use team teams venture ventures company companies project projects university auckland reported intended proposed support tool find relevant precedent precedents needs need possible documented comparison comparisons programme challenge velocity'.split())
# Fixed, inspectable morphology normalization; no learned synonym expansion.
INFLECTIONS = {'modelling': 'model', 'modeling': 'model', 'imaging': 'image', 'surgical': 'surgery', 'images': 'image', 'models': 'model', 'tools': 'tool', 'workers': 'worker', 'students': 'student', 'founders': 'founder', 'prizes': 'prize', 'games': 'game', 'conditions': 'condition', 'decisions': 'decision', 'disorders': 'disorder', 'antibiotics': 'antibiotic', 'pathogens': 'pathogen'}
QUESTIONS = [
    'Which dated evidence would establish the intended user and buyer?',
    'What validation would be needed in the intended deployment setting?',
    'Which workflow or integration assumptions should be tested?',
    'What evidence would clarify the research-to-deployment pathway?',
    'Which newer source would resolve the most important current unknown?',
]


def tokens(text):
    normalized = {INFLECTIONS.get(t, t) for t in re.findall(r'[a-z0-9]+', text.lower())}
    return {t for t in normalized if len(t) > 2 and t not in STOP}


def name_key(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())


def compare(conn, query='', subject_id=None, mode='product_customer', programme='', year=None, connection_type=''):
    subject = detail(conn, subject_id) if subject_id else None
    if subject_id and subject is None:
        raise LookupError('Subject venture not found')
    response = {'method': METHOD, 'mode': mode, 'query': query, 'subject': subject, 'results': [], 'questions': QUESTIONS, 'brief_type': 'Deterministic/template brief', 'annotations_used': False}
    all_ventures = browse(conn)
    derive_from_subject = subject is not None
    if not subject and query.strip():
        same = [v for v in all_ventures if name_key(query) in [name_key(n) for n in [v['display_name'], *v['aliases']]]]
        if len(same) > 1:
            return dict(response, abstention_reason='Ambiguous venture name. Select a stable venture identity.')
        if same:
            subject = same[0]
            derive_from_subject = True
            response['subject'] = subject
        else:
            phrase = ' ' + ' '.join(re.findall(r'[a-z0-9]+', query.lower())) + ' '
            mentions = [v for v in all_ventures if any(
                (' ' + ' '.join(re.findall(r'[a-z0-9]+', n.lower())) + ' ') in phrase
                for n in [v['display_name'], *v['aliases']])]
            if len(mentions) > 1:
                return dict(response, abstention_reason='Multiple venture identities named. Select one subject to avoid ambiguous self-matches.')
            if mentions:
                subject = mentions[0]
                response['subject'] = subject
    if mode == 'stage_milestone':
        return dict(response, abstention_reason='Insufficient eligible dated milestone evidence. This release has no verified first-sale, funding-stage or deployment milestone dataset; award dates cannot substitute.')
    fields = METHOD['fields'][mode]
    def eligible(v):
        return [o for o in v['observations'] if o['field'] in fields]
    # Selecting a subject derives the query from its eligible evidence, never annotations.
    query_text = ' '.join(o['value_text'] for o in eligible(subject)) if derive_from_subject else query.strip()
    response['effective_query'] = query_text
    qt = tokens(query_text)
    if not qt:
        return dict(response, abstention_reason='Enter an informative sourced description or select a venture.')
    documents = {v['venture_id']: set().union(*(tokens(o['value_text']) for o in eligible(v))) for v in all_ventures}
    idf = {t: 1 + math.log((len(all_ventures)+1)/(1+sum(t in d for d in documents.values()))) for t in qt}
    candidates = browse(conn, programme=programme, year=year, connection_type=connection_type)
    excluded = subject['venture_id'] if subject else None
    for v in candidates:
        if v['venture_id'] == excluded:
            continue
        matched = qt & documents[v['venture_id']]
        coverage = len(matched)/len(qt)
        if len(matched) < 2 or coverage < .15:
            continue
        evidence = [{'observation': o, 'matched_terms': sorted(qt & tokens(o['value_text']))} for o in eligible(v) if qt & tokens(o['value_text'])]
        response['results'].append({
            'venture': v, 'ranking_score': round(sum(idf[t] for t in matched)/sum(idf.values()), 6),
            'query_token_coverage': round(coverage, 4), 'matched_terms': sorted(matched), 'evidence': evidence,
            'wording_differences': {'query_only_terms': sorted(qt-documents[v['venture_id']]), 'candidate_only_terms': sorted(documents[v['venture_id']]-qt), 'meaning': 'Differences in recorded wording only. Unmentioned features are unknown, not weaknesses or verified absences.'},
            'unavailable_evidence': ['Current operating status', 'Current funding stage', 'Verified legal identity', 'Commercial outcomes', 'Verified buyer and deployment milestones'],
            'brief': 'Recorded wording overlaps on: '+', '.join(sorted(matched))+'. Inspect the dated passages before treating this as a useful analogy.'
        })
    response['results'].sort(key=lambda r: (-r['ranking_score'], r['venture']['venture_id']))
    response['results'] = response['results'][:3]
    response['abstention_reason'] = None if response['results'] else 'No candidate meets the documented minimum token-overlap and coverage rules within these filters. Try different wording; absence of a match is not evidence of irrelevance.'
    return response
