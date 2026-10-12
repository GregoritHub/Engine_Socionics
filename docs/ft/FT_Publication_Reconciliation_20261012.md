# FT publication reconciliation — 2026-10-12

Current batch: **FT4.1 — autonomous demand formation, pending**. No FT4 implementation, protocol acceptance or complete-model result is claimed.

## Surviving work and ownership
The clean local checkout survived at ea4e0eb6afdacd2579f8feec2e5042ea1f106523, preserving the accepted repaired source at d193ff30d1b74697c9baa72b923fa6fbc5f4cbcc. All 4,168 entries in the intended full-tree manifest match that accepted commit by Git blob identity. Private recovery metadata is excluded from this publication.

The destination started at f9d21f2a85fd1d5275e7dfbefe3d24f294215209, with 33/104 text batches committed. Its foreign lease expired at 14:10:37 UTC. This worker claimed a 30-minute lease by expected-head update at 56512424f0f5c7dc63c7cdf8b6a93299dd37d1d6. The final checkpoint releases it. The read-only source repository remains at fdede6f16721f06422d0798a79d84170969b83f8.

## Unaffected recovery completed
Staged tree ff7cbfeb9b8ba53f84abb1109acf5bae524ccb5f adds exactly five files and deletes none relative to the starting destination tree. These are text import batches 34–37 (zero-based payloads 033–036). Each staged blob matches both its saved payload and the accepted repaired source. This checkpoint preserves those previously accepted objects:

- C7_Corrective_Delivery_Source_Manifest_v1.json: eab230444ed3e44020c29c412220064ee94e9b67
- C7_Corrective_Final_Source_Freeze_v1.json: 80219d71438e1d8cb544cad076f29d9260514aa4
- C7_Final_Ledger_v1.json: 4c45e4a5231f00126d3041227062a92f120cf0a1
- C7_Final_Ledger_v2.json: a9028d783c336c0cbaa319d41371e5d6730100f9
- C7_Final_Ledger_v3.json: bc52ae2815ab79eccd599d37cb7e8329c241cad1

This advances committed text import to 37/104. Before new reconciliation metadata, the staged tree has 2,621 exact matches to the 4,168-file source manifest, 1,546 absent required files and one deliberately different operational run-state. Three pre-existing destination recovery/progress files are additional. Binary transfer remains incomplete. This is an exact partial-tree accounting, **not** complete publication.

## Verification and retained unsuccessful invocation
The FT2 frozen-source inventory matches its accepted df80582 commit (18 files, zero mismatches); FT3 matches d193ff3 (20 files, zero mismatches). Saved results still report FT2 64/64 cells and 12/12 controls; FT3 13/13 methods and two independently audited positive witnesses. Those are prior acceptance results, not reruns of their complete panels.

A fresh three-method repair recheck passed in 4.037 seconds with no source changes. The first invocation omitted the historical baseline import path and produced three unittest loader errors, all ModuleNotFoundError: No module named 'hle'; no test body ran. That failed invocation is retained here rather than counted as an engine failure or discarded. The corrected command follows the import paths in the existing evaluators:

```sh
PYTHONPATH=.:baseline/HLE_Rebuild_R21B python -m unittest -v tests_ft2.test_content.ContentTests.test_public_packet_requires_exact_scoped_paid_uptake tests_ft2.test_content.ContentTests.test_nonphysical_semantic_scope_and_tampering tests_ft3.test_retention.RetentionTests.test_nonphysical_scope_and_wrong_target_control
```

The exact passing output is saved in FT_Publication_Recheck_20261012.log. These checks validate the repaired implementation only, not the theory as an empirical account of people.

## Unresolved stop condition
Automatic approval review previously rejected publication of C7_Final_Source_Freeze_v5.json, C7_Progress_Ledger_v1.json and C7_Second_Setting_Delivered_Source_Manifest_v1.json. The carried-forward task explicitly prohibits retries or bypasses. The exact per-file reviewer rationale was not preserved in the available publication state; this run does not invent it. No new rejected-file upload, opaque substitute, workflow or alternate-route publication was attempted.

The user's standing approval is sufficient; another per-batch permission prompt is not required. A platform-supported resolution of those denials is still missing. Complete publication is a required unresolved recovery step, so the plan's unrecoverable source/access stop rule applies. Accepted local work and failed attempts remain preserved. Stop and pause continuation rather than claim the import complete or repeat status-only runs.

Resume only after the platform restriction is resolved through an allowed process: inspect current head and lease; finish pending text/binary import; verify the complete allowed source tree while separating operational metadata; then start the prospective FT4.1a demand-formation protocol.
