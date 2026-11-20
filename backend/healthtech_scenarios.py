"""Deterministic monthly cash scenarios and a Venture Frame measurement export."""
from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from .ingestion import StrictModel, Text

Money = Annotated[StrictInt, Field(ge=0, le=1_000_000_000_000)]
Months = Annotated[StrictInt, Field(ge=0, le=120)]
Month = Annotated[StrictInt, Field(ge=1, le=120)]
CaseId = Annotated[str, Field(pattern=r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')]


class ProviderCase(StrictModel):
    case_id: CaseId
    label: Text
    evaluation_months: Month
    evaluation_cost_nzd: Money
    conversion_delay_months: Months | None
    implementation_cost_nzd: Money | None
    monthly_provider_charge_nzd: Money | None
    payment_lag_months: Months | None

    @model_validator(mode='after')
    def conditional_payment_fields(self):
        payment_terms = (self.implementation_cost_nzd, self.monthly_provider_charge_nzd, self.payment_lag_months)
        if self.conversion_delay_months is None:
            if any(value is not None for value in payment_terms):
                raise ValueError('A no-conversion case needs null implementation and payment terms')
        elif any(value is None for value in payment_terms) or self.monthly_provider_charge_nzd == 0:
            raise ValueError('A conversion case needs explicit implementation cost, positive charge and payment lag')
        return self


class ProviderScenarios(StrictModel):
    format_version: Literal['provider-scenarios:1']
    label: Text
    assumption_note: Text
    horizon_months: Month
    opening_cash_nzd: Money
    monthly_operating_outflow_nzd: Money
    evaluation_start_month: Month
    cases: list[ProviderCase] = Field(min_length=1, max_length=12)

    @model_validator(mode='after')
    def validate_cases(self):
        if self.evaluation_start_month > self.horizon_months:
            raise ValueError('The horizon must include the evaluation start')
        if len({case.case_id for case in self.cases}) != len(self.cases):
            raise ValueError('Case IDs must be unique')
        return self


def _calculate_case(model, case):
    service_month = None
    receipt_month = None
    if case.conversion_delay_months is not None:
        service_month = model.evaluation_start_month + case.evaluation_months + case.conversion_delay_months
        receipt_month = service_month + case.payment_lag_months

    balance = model.opening_cash_nzd
    months = []
    for month in range(1, model.horizon_months+1):
        evaluation_cost = case.evaluation_cost_nzd if month == model.evaluation_start_month else 0
        implementation = case.implementation_cost_nzd if month == service_month else 0
        receipt = case.monthly_provider_charge_nzd if receipt_month is not None and month >= receipt_month else 0
        balance += receipt - model.monthly_operating_outflow_nzd - evaluation_cost - implementation
        months.append(dict(month=month, operating_outflow_nzd=model.monthly_operating_outflow_nzd,
            evaluation_outflow_nzd=evaluation_cost, implementation_outflow_nzd=implementation,
            provider_receipt_nzd=receipt, closing_cash_nzd=balance))
    minimum = min([model.opening_cash_nzd] + [row['closing_cash_nzd'] for row in months])
    return dict(case_id=case.case_id, label=case.label, modelled_service_month=service_month,
        modelled_first_receipt_month=receipt_month,
        first_month_below_zero=next((row['month'] for row in months if row['closing_cash_nzd'] < 0), None),
        closing_cash_nzd=balance, minimum_cash_nzd=minimum, funding_gap_nzd=max(0, -minimum), months=months)


MEASUREMENTS = {
    'closing_cash_nzd': ('Cash at end of horizon', 'NZD'),
    'minimum_cash_nzd': ('Lowest modelled cash balance', 'NZD'),
    'funding_gap_nzd': ('Funding gap at lowest balance', 'NZD'),
    'modelled_first_receipt_month': ('First provider cash receipt', 'month'),
}


def scenario_report(model: ProviderScenarios):
    cases = [_calculate_case(model, case) for case in model.cases]
    ranges = {}
    for key in MEASUREMENTS:
        values = [case[key] for case in cases if case[key] is not None]
        ranges[key] = dict(minimum=min(values) if values else None, maximum=max(values) if values else None,
            applicable_cases=len(values))
    return dict(format_version='provider-scenario-report:1', assumptions=model.model_dump(),
        cases=cases, ranges_across_supplied_cases=ranges,
        timing='Cash is calculated at month end. Evaluation cost falls at its start, setup cost at paid service start, and receipts follow the entered payment lag.',
        scope='An arithmetic exercise using supplied assumptions. Deficits show the amount needed to keep modelled month-end cash at or above zero.')


def venture_frame_measurement_draft(project_id, title, description, alternatives, criteria, performances):
    return {
        'schema_version': 1,
        'id': project_id,
        'title': title,
        'description': description,
        'decision_maker': '',
        'alternatives': alternatives,
        'criteria': criteria,
        'performances': performances,
        'weight_profiles': [],
        'scenarios': [],
    }


def venture_frame_project(report):
    """Package unweighted assumption-based measurements for Projects → Import."""
    cases = report['cases']
    alternatives = [
        {'id': case['case_id'], 'name': case['label'], 'metadata': {
            'basis': report['assumptions']['assumption_note'],
            'assumptions': assumptions,
            'horizon_months': report['assumptions']['horizon_months'],
            'evaluation_start_month': report['assumptions']['evaluation_start_month'],
            'opening_cash_nzd': report['assumptions']['opening_cash_nzd'],
            'monthly_operating_outflow_nzd': report['assumptions']['monthly_operating_outflow_nzd'],
        }}
        for case, assumptions in zip(cases, report['assumptions']['cases'], strict=True)
    ]
    criteria = [
        {'id': key, 'name': title, 'order': order, 'scale': {'type': 'interval', 'unit': unit}}
        for order, (key, (title, unit)) in enumerate(MEASUREMENTS.items())
    ]
    performances = [
        {'alternative_id': case['case_id'], 'criterion_id': key, 'value': case[key]}
        for case in cases for key in MEASUREMENTS if case[key] is not None
    ]
    return venture_frame_measurement_draft('healthtech-provider-scenarios', report['assumptions']['label'],
        'Assumption-based provider evaluation cases. Raw measurements are supplied for analyst review.',
        alternatives, criteria, performances)
