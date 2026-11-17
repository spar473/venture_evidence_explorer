#!/usr/bin/env python3
"""Start the built application locally; never bind a public interface."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import uvicorn

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=8000)
args = parser.parse_args()
uvicorn.run('backend.main:app', host='127.0.0.1', port=args.port)
