# Approved repair verification — 2026-10-12

Recovered the surviving FT2/FT3 repair checkpoint. Both original repair source freezes match their commits: 18 FT2 files and 20 FT3 files, zero mismatches. Saved evaluations passed 64/64 content cells, 12/12 content controls, and 13/13 retention controls, with positive witnesses in both settings.

The three regression methods specifically exercising the repaired public-packet and semantic-target paths passed again. Their fresh log is `FT_Repair_Recheck_20261012.log`. This is scoped repair verification, not a fresh full regression.

Only the approved repair source, tests, protocols and readable evaluation records are published here. The full standalone checkpoint import was rejected by automatic approval review. Private recovery details are omitted from this public record.

Current batch: **FT4.1 — autonomous demand formation, pending**. The run lease is released in blocked status. No FT4 implementation or acceptance is claimed. The reference repository was not changed.
