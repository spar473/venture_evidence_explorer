"""Expose cohort release requirements as source-covered counts."""
from typing import Literal

from .cohort_audit import run_audit
from .ingestion import StrictModel


class EndpointGate(StrictModel):
    events: int
    unknown_or_lost: int
    verified_observed_at_36_months: int
    unresolved_at_36_months: int
    gate_ready: bool
    blockers: list[str]


class WorkbenchGates(StrictModel):
    as_of: str
    entries: int
    minimum_entries: Literal[150] = 150
    minimum_events: Literal[30] = 30
    primary: EndpointGate
    secondary: EndpointGate
    validation_state: Literal['not_validated'] = 'not_validated'


def gate_progress(audit):
    follow_up = audit['follow_up']

    def endpoint(value):
        statuses = value['statuses']
        return EndpointGate(events=statuses['reached_outcome'], unknown_or_lost=statuses['unknown'] +
            statuses['lost_to_follow_up'], verified_observed_at_36_months=value['verified_observed_at_36_months'],
            unresolved_at_36_months=value['unresolved_at_36_months'], gate_ready=value['gate_ready'],
            blockers=value['gate_blockers'])

    return WorkbenchGates(as_of=follow_up['as_of'], entries=audit['counts']['included'],
                          primary=endpoint(follow_up), secondary=endpoint(follow_up['secondary']))


def install(app):
    @app.get('/api/workbench/gates', response_model=WorkbenchGates)
    def get_gates():
        return gate_progress(run_audit())
