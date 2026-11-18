# Review probes

All altered records/actors are synthetic. Never run these against a live evidence DB.

`mapping-probe.py` imports source from a specified repository and creates only temporary databases. With that project’s Python dependencies installed:

```sh
PYTHONDONTWRITEBYTECODE=1 /absolute/python probes/mapping-probe.py --repository /absolute/disposable/application
```

The direct source citation should reject the backdated decision; the pre-fix observation citation incorrectly passes and is stored.

`review-probes.spec.ts` is a diagnostic browser specification, tested in an isolated copy of the project. To reproduce, copy it only into a disposable copy’s `frontend/e2e/`, build there, and run the project’s configured Playwright harness on an unused loopback port using a disposable test DB. Two tests assert observed defects, and a third captures layouts. They must be rewritten as correct-behaviour regressions when fixing the code. Do not interpret their pre-fix passing status as application correctness.
