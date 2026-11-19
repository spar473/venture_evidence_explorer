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
from .research_contracts import ResearchDossier, ResearchPacket, ResearchSubjectsResponse
from . import research_repository
from .healthtech import HealthtechComparison, HealthtechCoverage, compare_healthtech, healthtech_coverage


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

    @app.get('/api/research/subjects', response_model=ResearchSubjectsResponse)
    def research_subjects(q: str = Query('',max_length=300), review_state: Literal['','extracted','source_checked','accepted','disputed'] = '', limit: int = Query(25,ge=1,le=100), offset: int = Query(0,ge=0), namespace: Literal['research:0.2.1'] = 'research:0.2.1', packet_sha256: str | None = None):
        with closing(connect(path)) as conn:
            return research_repository.subjects(conn,q=q,review_state=review_state,limit=limit,offset=offset,packet_sha256=packet_sha256)

    @app.get('/api/research/healthtech/coverage', response_model=HealthtechCoverage)
    def research_healthtech_coverage():
        with closing(connect(path)) as conn:
            return healthtech_coverage(conn)

    @app.get('/api/research/subjects/{subject_id}/comparisons', response_model=HealthtechComparison)
    def healthtech_comparisons(subject_id: str, as_of: str = Query(..., pattern=r'^\d{4}-\d{2}-\d{2}$'), view: Literal['research','historical'] = 'research', packet_sha256: str | None = None):
        with closing(connect(path)) as conn:
            try:
                return compare_healthtech(conn, subject_id, as_of=as_of, view=view, packet_sha256=packet_sha256)
            except LookupError as error:
                raise HTTPException(404, str(error)) from error
            except ValueError as error:
                raise HTTPException(422, str(error)) from error

    @app.get('/api/research/subjects/{subject_id}', response_model=ResearchDossier)
    def research_subject(subject_id: str, namespace: Literal['research:0.2.1'] = 'research:0.2.1', packet_sha256: str | None = None):
        with closing(connect(path)) as conn:
            result=research_repository.dossier(conn,subject_id,packet_sha256=packet_sha256)
            if result is None:
                raise HTTPException(404,'Research subject not found')
            return result

    @app.get('/api/research/packets/{packet_sha256}.json',response_model=ResearchPacket)
    def research_packet(packet_sha256: str, namespace: Literal['research:0.2.1'] = 'research:0.2.1'):
        with closing(connect(path)) as conn:
            raw=research_repository.raw_packet(conn,packet_sha256)
            if raw is None:
                raise HTTPException(404,'Research packet not found')
            return Response(raw,media_type='application/json',headers={'Content-Disposition':'attachment; filename="research_packet.json"'})

    @app.get('/api/research/exports/{name}.csv')
    def research_export(name: str, subject_id: str | None = None, namespace: Literal['research:0.2.1'] = 'research:0.2.1', packet_sha256: str | None = None):
        if name not in research_repository.EXPORT_NAMES:
            raise HTTPException(404,'Unknown research export')
        with closing(connect(path)) as conn:
            try:
                output=research_repository.export_csv(conn,name,subject_id=subject_id,packet_sha256=packet_sha256)
            except LookupError as error:
                raise HTTPException(404,'Research subject not found') from error
        return Response(output,media_type='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="research_{name}.csv"'})

    from .intake_api import install as install_intake
    install_intake(app,path)

    from .discovery_api import install as install_discovery
    install_discovery(app,path)

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
