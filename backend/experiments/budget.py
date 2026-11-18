"""Tiny exact research queue and greedy baseline; utilities are declared proxies."""
import math
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Task:
    task_id: str
    cost: float
    utility: float
    requires: tuple = ()
    covers: tuple = ()


def allocate(tasks, budget, required_coverage=()):
    if not math.isfinite(budget) or budget < 0 or len(tasks) > 20:
        raise ValueError('Finite nonnegative budget; enumeration limited to 20 tasks')
    ids = {task.task_id for task in tasks}
    if len(ids) != len(tasks) or any(not t.task_id.strip() or not math.isfinite(t.cost) or t.cost <= 0 or not math.isfinite(t.utility) or t.utility < 0 or not set(t.requires) <= ids or t.task_id in t.requires for t in tasks):
        raise ValueError('Unique task IDs, finite positive costs, nonnegative utilities, valid prerequisites required')
    feasible = lambda group: (sum(t.cost for t in group) <= budget and
        all(set(t.requires) <= {g.task_id for g in group} for t in group) and
        set(required_coverage) <= {c for t in group for c in t.covers})
    candidates = (group for n in range(len(tasks)+1) for group in combinations(tasks, n))
    groups = [group for group in candidates if feasible(group)]
    if not groups:
        return {'status': 'infeasible', 'exact': None, 'greedy': None}
    # Stable objective tie break prefers lower cost then IDs.
    exact = min(groups, key=lambda g: (-sum(t.utility for t in g), sum(t.cost for t in g), tuple(sorted(t.task_id for t in g))))
    greedy = []
    for task in sorted(tasks, key=lambda t: (-t.utility/t.cost, t.task_id)):
        if sum(t.cost for t in greedy)+task.cost <= budget and set(task.requires) <= {t.task_id for t in greedy}:
            greedy.append(task)
    render = lambda group: {'task_ids': sorted(t.task_id for t in group), 'cost': sum(t.cost for t in group), 'utility': sum(t.utility for t in group)}
    return {'status': 'optimal_by_enumeration', 'exact': render(exact),
            'greedy': render(greedy) if feasible(greedy) else None,
            'meaning': 'Investigation priority under supplied proxy values; no investment attractiveness inference'}
