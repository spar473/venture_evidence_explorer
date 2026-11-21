from contextlib import closing
import csv
import io
import json
from fastapi import HTTPException, Query
from fastapi.responses import Response
from .database import connect
from . import discovery as d


def csv_export(conn, collection):
    if collection not in d.KEYS:
        raise LookupError('Unknown discovery export')
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['record_id', 'collection', 'packet_sha256', 'review_disposition', 'raw_json'])
    for r in conn.execute(
        'SELECT r.record_id,r.record_json,group_concat(m.packet_sha256) FROM discovery_records r JOIN discovery_membership m USING(record_id) WHERE collection=? GROUP BY r.record_id,r.record_json ORDER BY r.record_id',
        (collection,),
    ):
        raw = json.loads(r[1])
        status = raw.get(
            'review_status', raw.get('legal_identity_review', raw.get('status', 'discovery_reference_unreviewed'))
        )
        values = [r[0], collection, r[2], status, r[1]]
        writer.writerow(
            ["'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r')) else v for v in values]
        )
    return output.getvalue()


def install(app, path):
    @app.get('/api/discovery/facets', response_model=d.DiscoveryFacets)
    def facets():
        with closing(connect(path)) as c:
            return {
                'families': [
                    {k: r[k] for k in ('organisation_id', 'name', 'coverage_status')}
                    for r in d.data(c, 'organisations')
                ],
                'outcome_years': sorted(
                    {int(r['date_value'][:4]) for r in d.data(c, 'targeted_outcome_events') if r['date_value']}
                ),
            }

    @app.get('/api/discovery', response_model=d.DiscoveryPage)
    def queue(
        q: str = Query('', max_length=300),
        family: str = '',
        status: str = '',
        year: int | None = Query(None, ge=2000, le=9999),
        gap: str = '',
        unknown_period: bool = False,
        limit: int = Query(25, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        with closing(connect(path)) as c:
            return d.queue(c, q, family, status, year, gap, unknown_period, limit, offset)

    @app.get('/api/discovery/candidates/{discovery_id}', response_model=d.DiscoveryDetail)
    def detail(discovery_id: str):
        with closing(connect(path)) as c:
            result = d.preview(c, discovery_id)
            if result is None:
                raise HTTPException(404, 'Discovery candidate not found')
            return result

    @app.get('/api/discovery/candidates/{discovery_id}/promotion', response_model=d.PromotionPreview)
    def promotion(discovery_id: str):
        with closing(connect(path)) as c:
            try:
                return d.promotion_preview(c, discovery_id)
            except LookupError as e:
                raise HTTPException(404, str(e)) from e

    @app.get('/api/discovery/exports/{collection}.csv')
    def export(collection: str):
        with closing(connect(path)) as c:
            try:
                raw = csv_export(c, collection)
            except LookupError as e:
                raise HTTPException(404, str(e)) from e
        return Response(
            raw,
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="discovery_{collection}.csv"'},
        )
