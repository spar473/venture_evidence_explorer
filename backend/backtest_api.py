"""Read-only Time Machine route with explicit provisional labelling."""

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from .backtest import current_inputs, registered_subject, render_backtest
from .backtest_contracts import BacktestResponse, EvidenceMode, PeerHistory, Track
from .backtest_coverage import PREVIEW_LABEL


def install(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> Response:
        response = await request_validation_exception_handler(request, exc)
        if request.url.path.startswith('/api/backtest/') and request.query_params.get('track', 'preview') == 'preview':
            return JSONResponse(
                {'provisional': True, 'label': PREVIEW_LABEL, 'detail': exc.errors()},
                status_code=response.status_code,
            )
        if request.url.path.startswith(('/api/views/profile/', '/api/scenario/', '/api/robustness/')):
            return JSONResponse(
                {
                    'provisional': True,
                    'label': PREVIEW_LABEL,
                    **({'scenario': True} if request.url.path.startswith('/api/scenario/') else {}),
                    'detail': exc.errors(),
                },
                status_code=response.status_code,
            )
        return response

    @app.get('/api/backtest/{company_id}', response_model=BacktestResponse)
    def backtest(
        company_id: str,
        track: Track = 'preview',
        witness_mode: EvidenceMode = 'strict',
        peer_history: PeerHistory = 'as_of_anchor',
    ) -> BacktestResponse | JSONResponse:
        if not registered_subject(company_id):
            return JSONResponse(
                {
                    'provisional': track == 'preview',
                    'label': PREVIEW_LABEL if track == 'preview' else None,
                    'detail': 'Time Machine subject not found.',
                },
                status_code=404,
            )
        return render_backtest(current_inputs(track), company_id, witness_mode, peer_history)
