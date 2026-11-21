"""Adapter boundary around the unchanged, vendored research 0.2.1 validator."""

import importlib.util
import json
import math
from datetime import date
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / 'research/framework-v0.2.1'
_spec = importlib.util.spec_from_file_location('vee_research_contract_021', PACKAGE / 'validate_research_example.py')
_contract = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_contract)
COLLECTIONS = dict(_contract.COLLECTIONS)
for _required_format in ('date', 'uri'):
    if _required_format not in _contract.VALIDATOR.format_checker.checkers:
        raise RuntimeError('Required JSON Schema format checker unavailable: ' + _required_format)


class ResearchValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('; '.join(e['path'] + ': ' + e['message'] for e in errors))


def pointer(parts):
    return '/' + '/'.join(str(p).replace('~', '~0').replace('/', '~1') for p in parts)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key: ' + key)
        result[key] = value
    return result


def decode_packet(raw):
    def invalid_number(value):
        raise ValueError('Non-finite JSON number: ' + value)

    try:

        def finite_float(value):
            parsed = float(value)
            if not math.isfinite(parsed):
                raise ValueError('Non-finite JSON number: ' + value)
            return parsed

        return json.loads(
            raw, object_pairs_hook=_unique_object, parse_constant=invalid_number, parse_float=finite_float
        )
    except (ValueError, UnicodeDecodeError) as error:
        raise ResearchValidationError([{'path': '/', 'message': str(error), 'category': 'invalid_json'}]) from error


def validation_errors(packet, as_of):
    # Date is an external invocation parameter, not controlled by packet metadata.
    date.fromisoformat(as_of)
    errors = []
    for error in sorted(_contract.VALIDATOR.iter_errors(packet), key=lambda e: str(list(e.absolute_path))):
        errors.append(
            {
                'path': pointer(error.absolute_path),
                'message': error.message,
                'category': 'unsupported'
                if error.validator in ('additionalProperties', 'enum', 'const')
                else 'invalid',
            }
        )
    if errors:
        return errors
    try:
        _contract.validate(packet, validation_as_of=as_of)
    except (ValueError, KeyError, TypeError) as error:
        return [{'path': '/', 'message': str(error), 'category': 'semantic'}]
    return []


def validate_research_packet(packet, as_of):
    errors = validation_errors(packet, as_of)
    if errors:
        raise ResearchValidationError(errors)
    return {name: len(packet[name]) for name in COLLECTIONS}


def validate_supplied_regressions(packet, as_of):
    spec = importlib.util.spec_from_file_location('vee_research_regressions_021', PACKAGE / 'regression_cases.py')
    regressions = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(regressions)
    return {
        'negative_cases': _contract.negative_tests(packet, as_of),
        'regressions': regressions.run_regressions(_contract.validate, packet, as_of),
    }
