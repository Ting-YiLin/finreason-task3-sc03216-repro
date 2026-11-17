# Claims and replay scope

| Claim | Evidence included | How to check | Status |
|---|---|---|---|
| E+C 153/332 and R1/R2 arms 153/158/147/153/152 | Author-created 332-case prediction snapshots, original Python prototype, metadata | `score_practice.py` with separately fetched public Practice Gold | **Re-score from author predictions** (not regenerate original E+C) |
| P2 six changed outputs | E+C/P2 snapshots | `verify_release.py` | **Offline verified** |
| P2 Gold-based five rescues, zero regressions, splits and 147 parseable cases | snapshots and metadata | `score_practice.py` after retrieving public Gold | **Re-score possible** |
| Regenerate P1–P5 from supplied Practice fragments | Original `raw_xbrl_prototypes.py`; E+C baseline | `prepare_public_finmr.py`, `raw_xbrl_prototypes.py`, `compare_regenerated.py` | **Source provided; local test receipt separately recorded** |
| R4 BASE158 same as P2 byte for byte | R4 report totals, but no original sealed R4 casewise file | cannot fully establish | **Not verified** |
| R4 SIGN_U and CALC_PARTIAL repairs 174/332 and 140/147 | Paper aggregates only; full casewise rule implementation/logs absent | cannot independently replay | **Reported only** |
| R6 seven official DQC inconsistencies | Casewise verdict values in paper, versions recorded; raw logs/cache absent | cannot independently replay | **Reported, not clean-replayed** |
| R8 full-source 144/147 or exploratory 146/147 | Manuscript summaries, incomplete source map | cannot independently replay | **Reported only** |
| Official Test 538/680 | Organizer-published aggregate | [Task 3 leaderboard](https://the-finai.github.io/IEEE-bigdata-cup/task3/leaderboard/) | **External organizer-judged aggregate** |

**Important:** Gold-informed iterative design on Practice means none of these retrospective Practice measurements is an unseen-Test estimate. Regenerating P2 outputs from fixed code does not remove prior reference exposure during the research design.
