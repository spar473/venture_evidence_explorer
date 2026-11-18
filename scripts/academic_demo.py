#!/usr/bin/env python3
"""Run explicitly hypothetical research-budget fixture; never touches SQLite."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.experiments.budget import Task, allocate
from backend.experiments.structured import research_status

if __name__ == '__main__':
    tasks = [Task('hypothetical_a', 10, 60), Task('hypothetical_b', 20, 100), Task('hypothetical_c', 30, 120)]
    print(json.dumps({'label': 'SYNTHETIC ONLY: hypothetical minutes and arbitrary declared utility proxies',
                      'budget_sensitivity': {str(b): allocate(tasks, b) for b in (20, 30, 40, 50)},
                      'structured_similarity': research_status(),
                      'technical_diligence': {'status': 'deferred', 'reason': 'Needs domain-specific reviewed evidence and user validation'}}, indent=2))
