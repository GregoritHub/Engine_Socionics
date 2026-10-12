# Reproducibility report

- Theory kernel: fully deterministic; no wall-clock reads (timestamps
  exist only in the empirical ledger).  `python3 bin/le.py verify all`
  is bit-stable across runs.
- Randomization: seeded (`randomization_seed` in study.json), plan
  written to the append-only ledger before any outcome; verified
  reproducible from seed by the acceptance suite.
- Dataset freezes: `dataset_frozen` ledger events carry sha256 hashes of
  the exported rows.
- Protocol freeze: `study_protocol_frozen` carries the sha256 of
  study.json.
- Source manifest: manifests/source_manifest.json pins sha256 of the
  three uploaded source artifacts this build derives from.
- Synthetic generator: version + full parameter set stored on every
  synthetic observation row.
- To reproduce the demonstration exactly: delete data/, re-run the
  eleven commands in README (the generator is seeded from the study
  seed).
