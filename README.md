# Approved repair overlay

This branch currently preserves the approved FT2/FT3 repair delta against saved checkpoint `c8bef62d623b55054594d1328dfd649c52811641`. The repaired local checkpoint is `d193ff30d1b74697c9baa72b923fa6fbc5f4cbcc`.

Automatic approval review blocked publishing the full checkout to this public repository twice, including after earlier approval was recovered. The inherited checkout and historical reference were not uploaded. This is not a standalone engine; apply these exact files over the saved checkpoint to reproduce the repair runs.

FT2 passed 64 content cells and 12 controls; FT3 passed 13 controls and independently audited witnesses in both settings. Source hashes match the committed repair freezes. Current eligible plan job is FT4.1 (demand formation). Raw repair evidence publication is in progress. The local checkpoint preserves prior failed attempts.
