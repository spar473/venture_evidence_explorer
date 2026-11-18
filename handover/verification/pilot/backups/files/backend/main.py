"""Loopback-only launcher serves this read-only API and the built React app."""
import csv
import io
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from .contracts import AnalyticsResponse, Comparison, ComparisonRequest, ComparisonRun, Facets, Health, Venture, VenturePage
from .comparison_runs import replay
from .database import DEFAULT_DB, ROOT, connect
from .repository import EXPORTS, analytics, browse, detail, facets
from .retrieval import compare


def create_app(db_path=None):
    app = FastAPI(title='Venture Evidence Explorer', version='1.1.0', docs_url=None, redoc_url=None)
    path = Path(db_path or os.environ.get('VEE_DB', DEFAULT_DB))

    @app.exception_handler(sqlite3.Error)
    async def database_error(request, error):
        return Response('Database unavailable. Run python scripts/bootstrap.py before starting the app.', status_code=503)

    @app.get('/api/health', response_model=Health)
    def health():
        with closing(connect(path)) as conn:
            return {'status': 'ok', 'schema_migrations': [r[0] for r in conn.execute('SELECT version FROM schema_migrations ORDER BY version')]}

    @app.get('/api/facets', response_model=Facets)
    def get_facets():
        with closing(connect(path)) as conn:
            return facets(conn)

    @app.get('/api/ventures', response_model=VenturePage)
    def ventures(q: str = Query('', max_length=300), programme: str = '', year: int | None = None, connection_type: str = '', limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):
        with closing(connect(path)) as conn:
            return browse(conn, q, programme, year, connection_type, limit=limit, offset=offset)

    @app.get('/api/ventures/{venture_id}', response_model=Venture)
    def venture(venture_id: str):
        with closing(connect(path)) as conn:
            result = detail(conn, venture_id)
            if not result:
                raise HTTPException(404, 'Venture not found')
            return result

    @app.post('/api/compare', response_model=Comparison)
    def comparison(body: ComparisonRequest):
        with closing(connect(path)) as conn:
            try:
                return compare(conn, **body.model_dump())
            except LookupError as error:
                raise HTTPException(404, str(error)) from error
            except ValueError as error:
                raise HTTPException(422, str(error)) from error

    @app.post('/api/comparison-runs/replay', response_model=Comparison)
    def replay_comparison(body: ComparisonRun):
        with closing(connect(path)) as conn:
            try:
                return replay(conn, body.model_dump())
            except (ValueError, LookupError) as error:
                raise HTTPException(409, str(error)) from error

    @app.get('/api/analytics', response_model=AnalyticsResponse)
    def get_analytics():
        with closing(connect(path)) as conn:
            return {'scope': 'Selected sample only; overlapping relationships. No success rates or causal programme claims.', 'tables': analytics(conn)}

    @app.get('/api/exports/{name}.csv')
    def export(name: str):
        if name not in EXPORTS:
            raise HTTPException(404, 'Unknown export')
        with closing(connect(path)) as conn:
            cursor = conn.execute(EXPORTS[name])
            output = io.StringIO(newline='')
            writer = csv.writer(output)
            writer.writerow([d[0] for d in cursor.description])
            for row in cursor:
                writer.writerow(["'"+v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r')) else v for v in row])
        return Response(output.getvalue(), media_type='text/csv; charset=utf-8', headers={'Content-Disposition': f'attachment; filename="{name}.csv"'})

    dist = ROOT / 'frontend/dist'
    if (dist / 'assets').is_dir():
        app.mount('/assets', StaticFiles(directory=dist / 'assets'), name='assets')

    @app.get('/')
    def index():
        if not (dist / 'index.html').exists():
            raise HTTPException(503, 'Frontend not built. Run npm ci and npm run build in frontend/.')
        return FileResponse(dist / 'index.html')

    return app


app = create_app()
