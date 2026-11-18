"""Lossless typed research API models derived from the bundled 0.2.1 schema.

The importer still owns authoritative JSON Schema and semantic validation. This
small offline projection maps every declared property to a response field; it
never drops unknown nested fields or substitutes a business inference.
"""
import json
from pathlib import Path
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, create_model


class ResearchContract(BaseModel):
    model_config = ConfigDict(extra='forbid')


SCHEMA_PATH = Path(__file__).resolve().parents[1]/'research/framework-v0.2.1/Research_Interchange_v0.2.1.schema.json'
_SCHEMA = json.loads(SCHEMA_PATH.read_text())
_MODELS = {}
_NAMES = {'unknown_string':'ResearchUnknownString', 'review_event':'ResearchReviewEvent', 'annotation':'ResearchAnnotation', 'gap':'ResearchGap'}


def _name(value):
    return _NAMES.get(value, 'Research'+''.join(word.title() for word in value.split('_')))


def _model(name, node):
    if name in _MODELS:
        return _MODELS[name]
    required = set(node.get('required', []))
    fields = {}
    for field, spec in node.get('properties', {}).items():
        annotation = _type(spec, name+''.join(word.title() for word in field.split('_')))
        fields[field] = (annotation, ... if field in required else None)
    result = create_model(name, __base__=ResearchContract, **fields)
    _MODELS[name] = result
    return result


def _type(node, name):
    if '$ref' in node:
        ref = node['$ref']
        if not ref.startswith('#/$defs/'):
            raise ValueError('Only local research schema definitions are supported')
        key = ref.rsplit('/',1)[-1]
        return _model(_name(key), _SCHEMA['$defs'][key])
    if 'const' in node:
        return Literal[node['const']]
    if 'enum' in node:
        return Literal[tuple(node['enum'])]
    union = node.get('anyOf',node.get('oneOf'))
    if union is not None:
        return Union[tuple(_type(option,name) for option in union)]
    kind = node.get('type')
    if isinstance(kind,list):
        return Union[tuple(_type(dict(node,type=part),name) for part in kind)]
    if kind=='object':
        return _model(name,node)
    if kind=='array':
        return list[_type(node['items'],name+'Item')]
    if kind=='number':
        return Union[StrictInt,StrictFloat]
    if kind=='integer':
        return StrictInt
    if kind=='string':
        return StrictStr
    if kind=='boolean':
        return StrictBool
    if kind=='null':
        return type(None)
    raise ValueError('Unsupported research response schema: '+repr(node))


ResearchPacket = _model('ResearchPacket',_SCHEMA)
globals().update(_MODELS)


class ResearchSubjectSummary(ResearchContract):
    namespace: str
    subject_id: str
    display_name: str
    subject_kind: str
    identity_link_status: str
    proposed_application_id: str
    review_state: str
    observation_count: int
    event_candidate_count: int
    unknown_count: int
    open_case_count: int
    packet_digest: str


class ResearchSubjectsResponse(ResearchContract):
    items: list[ResearchSubjectSummary]
    total: int
    total_subjects: int
    limit: int
    offset: int


class ResearchIdentityMapping(ResearchContract):
    mapping_id: str
    namespace: str
    subject_id: str
    venture_id: str
    state: str
    scope: str
    actor_role: str
    actor_id: str | None
    decided_on: str | None
    evidence_ids: list[str]
    rationale: str
    source_packet_sha256: str
    legal_identity_state: str
    decision_document_sha256: str | None = None
    supersedes_mapping_id: str | None = None


class ResearchDateProjection(ResearchContract):
    collection: str
    record_id: str
    field_path: str
    value: str | None
    precision: Literal['day','month','year','unknown']
    lower_bound: str | None
    upper_bound: str | None
    basis: str
    unknown_reason: str | None


class ResearchDossier(ResearchContract):
    packet_view_kind: Literal['subject_reference_closure']
    is_standalone_import_packet: Literal[False]
    namespace: str
    subject: ResearchSubject
    packet: ResearchPacket
    identity_mapping: ResearchIdentityMapping | None
    packet_digest: str
    source_packet_sha256s: list[str]
    graph_sha256: str
    date_intervals: list[ResearchDateProjection]
    counts: dict[str,int]
    limitations: list[str]
