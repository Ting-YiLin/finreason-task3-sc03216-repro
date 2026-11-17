# Source and redistribution inventory

**Public source:** `TheFinAI/FinMR`, 332 Practice questions and answers, listed as **CC BY 4.0** by the dataset provider: https://huggingface.co/datasets/TheFinAI/FinMR. Cite the source and FinAuditing. The code in The-FinAI/FinAuditing is separately MIT-licensed; the dataset license does **not** license every external SEC/DQC dependency.

**Included in this author-prepared release:** only the author's output predictions for public Practice, six-case change identities, derived metadata (split and parser status), a research prototype and verification scripts. The source prototype came from the user's 2026-10-29 R1/R2 experiment return, not copied from any competitor. No query fragments, source filing packages, hidden-label Test submissions, Gold records or official grader responses are redistributed.

**External inputs required:** public Practice questions and public reference answers (fetched from their own hosts); optional `lxml` and `datasets`. The user obtains them in the prescribed routes. The public `TheFinAI/FinMR` dataset may change, so maintain a record of exact revision/hash in follow-up releases if verified. Original historical source filenames and SHA-256 are recorded in `docs/ORIGIN_AND_LIMITS.md`.

**Not included / do not add casually:** `SCORING_PRIVATE/`, `SCORE_PRIVATE/`, `PRIVATE_DELTA_all.csv`, full `DATA/INPUT_ONLY` or its XML fragments, private official Test rows, emails/passwords/tokens, source caches and unpublished R8 source maps. Preserve the official Test blind boundary.

**Code reuse license:** This stage-1 package does not automatically grant an OSI-approved license to the author's original code; author to choose before publishing if reusable rights are desired (MIT is common). External dataset rights remain CC BY 4.0 and must be attributed. No blanket license is silently asserted.
