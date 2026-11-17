# FinReason Cup 2026 Task 3 — SC03216 reproducibility (stage 1)

**Paper:** *What Makes XBRL Financial Reasoning Reliable? Task Heterogeneity, Source Sufficiency, and Evidence-Gated Repair*  
**Author:** Ting-Yi Lin (Independent Researcher); **registered Task 3 Test name:** `Ting-Yi`.  
**Scope:** independently checkable *retrospective Practice 332* predictions, prototype behavior and casewise history. **Not** an executable recreation of the organizer-judged Test run, the entire R4–R8 pipeline or a prospective result.

## Reproduce in 3 steps

Requirements: Python 3.10+ for standard-library scoring; Python plus `lxml` for prototype regeneration. External official public Practice data is **not included**.

1. `python tools/verify_release.py` — check all distributed files, 332 IDs per arm, and the six P2 output changes **without** reference answers.
2. Obtain the *public* 332-item FinMR Practice data via the official [Task 3 starter instructions](https://the-finai.github.io/IEEE-bigdata-cup/task3/submit/) or the [TheFinAI/FinMR](https://huggingface.co/datasets/TheFinAI/FinMR) dataset (CC BY 4.0). To prepare directly (internet access + separate optional `datasets` package needed):
   ```
   python -m pip install datasets
   python tools/prepare_public_finmr.py --huggingface
   python tools/score_practice.py --gold LOCAL_ONLY/practice_332_gold.jsonl
   ```
   Or prepare from a locally retrieved `id,dqc_id,query,answer` JSONL using `--jsonl PATH`. Expected exact-pair matches: baseline 153, P1 153, P2 158, P3 147, P4 153, P5 152 of 332. No score is independently checkable without public reference answers.
3. Optionally regenerate the **Gold-free** R1/R2 original prototypes (the source logic is preserved from the original 2026-10-29 research return):
   ```
   python -m pip install lxml==6.1.1
   python IMPLEMENTATIONS/raw_xbrl_prototypes.py --output-dir OUTPUT_REPLAY
   python tools/compare_regenerated.py --output-dir OUTPUT_REPLAY
   ```
   This reads only the externally obtained public query fragments and distributed frozen baseline predictions. It does *not* read reference answers. All five 332-case output pairs must match the distributed snapshots.

## Findings reproduced (only with reference answers)

- Frozen E+C: **153/332**. P2_SIGN_0015: **158/332**, with five case-level rescues, no regressions; **six** output pairs changed. All five rescues occurred in the retrospectively used `TRAIN_DISCOVERY` split.
- P2 strictly parseable supplied-XML slice: **124/147** (frozen baseline **119/147**). This must not be confused with the separately defined **119/146** subset in the paper.
- P3_DIM_0117: **147/332**, including six regressions; P5 combined: **152/332**.
- `BASE158` in later R4 reports matches P2 on overall scores, strict-XML group and company-split counts; the separately sealed original **R4 BASE158 casewise file was not available for bytewise identity verification**.

## What this release **does not** prove

R4 SIGN_U/CALC_PARTIAL results (up to 174/332), R6 full-filing official DQC replay (seven cases across five SEC filings) and R8 source-augmented results (178/332, exploratory 180/332) are **reported in the manuscript** but full original dependencies and casewise logs are not available here for clean reproduction. The seven R6 DQC messages are **calculation-inconsistency detections**, not validation of organizer answers. The official hidden-label Test **538/680 (79.12%)** is an organizer aggregate, not reproduced by this release. Neither the prototype nor evidence-gated architecture has prospective held-out validation in this package.

Full scope: [`docs/REPRODUCIBILITY_MATRIX.md`](docs/REPRODUCIBILITY_MATRIX.md). Data rights: [`docs/SOURCES_AND_RIGHTS.md`](docs/SOURCES_AND_RIGHTS.md).
