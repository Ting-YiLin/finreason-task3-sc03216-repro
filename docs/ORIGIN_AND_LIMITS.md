# Original research inputs and audit constraints

Source return `FINR_T3_RESEARCH_EVIDENCE_RETURN_20261117.zip` (2026-11-17) contained three original returns:

- `FINR_T3_R1_R2_RESEARCH_EXPERIMENTS_20261029.zip`: SHA-256 `07f63022fe2e466f392b473d3902507e67ecc68fb1ef14c17ca40593a015a453`
- `FINR_T3_WINNER_METHODS_RETURN_V1.zip`: SHA-256 `5bb226602043a464fc6a0dbd639f0f304f9ea78af8b73eeb6f7c7853e1551c43`
- `FINR_T3_80_TO_99_RESEARCH_WORKPACK_V1_20261029.zip`: SHA-256 `c23f1ed7061688202b0039620c4ba656fb3d46b9f6edc99829174e60d5184d28`

The original reports were re-examined 2026-11-17. Its P2 changed 6 predicted pairs, of which 5 were retrospective rescues and one changed pair remained incorrect; no original correct pairs regressed. All five were in discovery/training split. The independent Winner C100 experiment changed only 4 extracted values but no full pairs became correct, providing an independent explanation for why extraction alone was insufficient.

**Original R4 BASE158 sealed casewise output was not present in the source return.** The six aggregate comparisons match the P2 output but not byte identity. Original R6 engine logs/cache and complete R8 source map/logs were not present for independent full replay. Do not claim their reproduction.

`DATA/BASELINE/EC_FROZEN_332.jsonl` is an author-generated snapshot stripped of internal `merge_trace`; all original field values/IDs were retained. P1–P5 snapshots retain only the `id`, `extracted_value`, `calculated_value` fields. `DATA/METADATA/split_and_parse_status.csv` is a stripped derivative of internal audits, containing no Gold labels. SHA-256 in this release is for **sanitized** bytes; it is not the hash of the original unredacted files.
