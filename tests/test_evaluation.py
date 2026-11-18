"""Synthetic numerical fixtures verify code, never research relevance."""
import pytest
from backend.evaluation import read_judgments, relevance_report
from backend.experiments.budget import Task, allocate
from backend.experiments.robustness import mask_observations
from backend.experiments.structured import Dimension, research_status


def test_blank_and_missing_labels_never_become_metrics(tmp_path):
    path = tmp_path/'empty.csv'
    path.write_text('query_id,venture_id,reviewer_id,relevance_grade\nq,v,,\n')
    labels = read_judgments(path, {'q'}, {'v'})
    ranking = [{'query_id':'q', 'ranked_ids':['v'], 'eligible_ids':['v','other']}]
    report = relevance_report(ranking, labels)
    assert report['status'] == 'pending_human_judgments'
    assert report['queries'][0]['precision_at_returned'] is None
    assert report['queries'][0]['ndcg_at_3'] is None
    partial = relevance_report(ranking, {('q','v'):{'synthetic-test-reviewer':3}})
    assert partial['queries'][0]['precision_at_returned'] == 1
    assert partial['queries'][0]['ndcg_at_3'] is None


def test_metrics_on_complete_synthetic_grades():
    ranks = [{'query_id':'q', 'ranked_ids':['v','other'], 'eligible_ids':['v','other']}]
    labels = {('q','v'):{'fixture':3}, ('q','other'):{'fixture':0}}
    result = relevance_report(ranks, labels)['queries'][0]
    assert result['precision_at_returned'] == .5
    assert result['ndcg_at_3'] == 1
    ranks[0]['ranked_ids'].reverse()
    assert relevance_report(ranks, labels)['queries'][0]['ndcg_at_3'] < 1


def test_budget_enumeration_beats_greedy_and_checks_constraints():
    tasks = [Task('a',10,60),Task('b',20,100),Task('c',30,120)]
    result = allocate(tasks,50)
    assert result['exact']['utility'] == 220
    assert result['greedy']['utility'] == 160
    constrained = [Task('a',2,3,covers=('identity',)),Task('b',3,8,requires=('a',),covers=('buyer',))]
    assert allocate(constrained,4,('buyer',))['status'] == 'infeasible'
    assert allocate(constrained,5,('buyer',))['exact']['task_ids'] == ['a','b']
    with pytest.raises(ValueError):
        allocate([Task('a',0,1)],3)


def test_masking_is_seeded_reviewed_only_and_does_not_mutate():
    observations = [{'observation_id':str(i),'field':'buyer','review_status':'accepted'} for i in range(10)]
    result = mask_observations(observations, {'buyer'}, .5, 233)
    assert result == mask_observations(observations, {'buyer'}, .5, 233)
    assert len(observations) == 10
    assert 0 < len(result['removed_ids']) < 10
    with pytest.raises(ValueError, match='reviewed'):
        mask_observations([dict(observations[0],review_status='unreviewed')], {'buyer'},.5,233)
    with pytest.raises(ValueError):
        Dimension('amount',1,'numeric_range')
    assert research_status()['scoring_enabled'] is False


def test_blank_judgments_have_no_relevance_metrics(tmp_path):
    from backend.evaluation import read_judgments, relevance_report
    path = tmp_path / 'blank.csv'
    path.write_text('query_id,venture_id,reviewer_id,relevance_grade,rationale,supporting_observation_ids,reviewed_at\nq1,v1,,,,,\n')
    judgments = read_judgments(path, {'q1'}, {'v1', 'v2'})
    report = relevance_report([{'query_id':'q1','ranked_ids':['v1'],'eligible_ids':['v1','v2']}],judgments)
    assert report['status'] == 'pending_human_judgments'
    assert report['queries'][0]['precision_at_returned'] is None
    assert report['queries'][0]['ndcg_at_3'] is None


def test_partial_human_labels_never_become_zero_grades():
    from backend.evaluation import relevance_report
    ranking = [{'query_id':'q1','ranked_ids':['v1'],'eligible_ids':['v1','v2']}]
    report = relevance_report(ranking,{('q1','v1'):{'real_fixture_reviewer':3}})
    assert report['queries'][0]['precision_at_returned'] == 1
    assert report['queries'][0]['ndcg_at_3'] is None
    complete = relevance_report(ranking,{('q1','v1'):{'fixture':3},('q1','v2'):{'fixture':0}})
    assert complete['queries'][0]['ndcg_at_3'] == 1


def test_invalid_duplicate_and_unknown_judgments_refused(tmp_path):
    from backend.evaluation import read_judgments
    path = tmp_path/'labels.csv'
    header='query_id,venture_id,reviewer_id,relevance_grade,rationale,supporting_observation_ids,reviewed_at\n'
    row='q1,v1,synthetic_test_reviewer,3,Test only,o1,2026-11-18\n'
    path.write_text(header+row+row)
    with pytest.raises(ValueError,match='duplicate'):
        read_judgments(path,{'q1'},{'v1'})
    path.write_text(header+row.replace(',3,',',4,'))
    with pytest.raises(ValueError,match='grade'):
        read_judgments(path,{'q1'},{'v1'})
    path.write_text(header+row)
    with pytest.raises(ValueError,match='unknown'):
        read_judgments(path,{'another_query'},{'v1'})


def test_budget_optimizer_matches_independent_subsets():
    from itertools import product
    tasks=[Task('a',3,5),Task('b',4,7),Task('c',7,11)]
    for budget in range(15):
        expected=max(sum(t.utility*x for t,x in zip(tasks,bits)) for bits in product((0,1),repeat=3) if sum(t.cost*x for t,x in zip(tasks,bits))<=budget)
        assert allocate(tasks,budget)['exact']['utility']==expected
