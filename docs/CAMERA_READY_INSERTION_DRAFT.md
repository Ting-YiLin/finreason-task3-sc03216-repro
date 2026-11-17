# Camera-ready wording — add only after a real public repository URL exists

Suggested Data and reproducibility paragraph (do not claim public until verified live):

> A frozen research artifact (repository URL and release tag to be supplied after publication) provides the original R1/R2 prototype implementation, 332-case frozen E+C and P1–P5 Practice prediction snapshots, parser/split metadata, and scripts for numeric two-field re-scoring using the separately distributed public FinMR reference data. It permits independent verification of the 153/332 and 158/332 Practice scores, five rescued cases and six changed predictions. The artifact does not reproduce the organizer's hidden-label Test evaluation or the complete R4, R6 and R8 runs; those later original dependencies and full casewise logs are not included. The retrospective Practice experiments had prior reference exposure and do not estimate new held-out accuracy.

After public release, **replace the placeholder** with the exact verified repository/release URL. If a DOI was actually minted, add it only then. Align any existing 'public supplement' statements elsewhere in the article with the actual published content; the stage-1 repository is not a substitute for an unavailable full R6 or R8 casewise log.

Reviewer #2 response excerpt:

> We now provide a limited first-stage reproducibility artifact containing original prototype code, frozen casewise Practice predictions, public-data retrieval instructions, a deterministic re-scorer, and explicit exclusions. The artifact supports independent re-scoring of the R1/R2 development history but not a clean replay of all subsequent R4–R8 experiments. We also clarify the source status of BASE158 and retain the limitations of the retrospective findings.
