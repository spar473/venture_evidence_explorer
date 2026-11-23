"""Live routes for the same payloads used by the Pages build."""

from typing import Annotated, Any
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr

from .analytics_contracts import (
    AnalyticsCohort,
    AnalyticsMethod,
    AnalyticsProfile,
    AnalyticsRobustness,
    AnalyticsScenario,
)
from .analytics_views import (
    LABEL,
    cohort_payload,
    comparison,
    live_inputs,
    profile_payload,
    robustness,
    scenario_result,
    validate_overrides,
)
from .synthetic_method import method_lab


class ScenarioBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    overrides: dict[str, StrictStr | StrictInt]


def install(app: FastAPI) -> None:
    @app.get('/api/views/cohort', response_model=AnalyticsCohort)
    def cohort() -> dict[str, Any]:
        return cohort_payload(live_inputs())

    @app.get('/api/views/profile/{company_id}', response_model=AnalyticsProfile)
    def profile(company_id: str) -> dict[str, Any] | JSONResponse:
        try:
            return profile_payload(live_inputs(), company_id)
        except KeyError:
            return JSONResponse({**LABEL, 'detail': 'Unknown company profile'}, status_code=404)

    @app.post('/api/scenario/{company_id}', response_model=AnalyticsScenario)
    def scenario(company_id: str, body: ScenarioBody) -> dict[str, Any] | JSONResponse:
        try:
            return scenario_result(
                comparison(live_inputs(), company_id), validate_overrides(body.overrides), hypothetical=True
            )
        except KeyError:
            return JSONResponse({**LABEL, 'detail': 'Unknown company profile'}, status_code=404)
        except ValueError as error:
            return JSONResponse({**LABEL, 'scenario': True, 'detail': str(error)}, status_code=422)

    @app.get('/api/robustness/{company_id}', response_model=AnalyticsRobustness)
    def perturbations(
        company_id: str,
        draws: Annotated[int, Query(ge=1, le=10000)] = 2000,
        seed: int = 7,
    ) -> dict[str, Any] | JSONResponse:
        try:
            return robustness(live_inputs(), company_id, draws, seed)
        except KeyError:
            return JSONResponse({**LABEL, 'detail': 'Unknown company profile'}, status_code=404)

    @app.get('/api/views/method', response_model=AnalyticsMethod)
    def method() -> dict[str, Any]:
        return method_lab(7)
