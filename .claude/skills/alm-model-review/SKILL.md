---
name: alm-model-review
description: Read-only review of the Swiss pension-fund ALM simulation (asset/liability ratio, Deckungsgrad) in the target-fluctuation-reserves repository. Produces a short LaTeX report with a summary, a description of the current model, errors in what is already implemented with fixes, sensible additions, and scores. Use when asked to "review the simulation", "check the funding ratio model", or "repeat the ALM review".
---

# ALM model review (Swiss pension fund)

## Hard rules
- **Read-only.** Do not modify, commit or push anything in the repository. Verification scripts go in the scratchpad (or `/tmp`) and must not write into the repo (use `PYTHONDONTWRITEBYTECODE=1`). Finish by confirming with `git status --short` that the repository is clean.
- Keep **errors** (section 3) and **additions** (section 4) strictly separate. Errors only cover features that are already implemented. Missing features belong only in additions.
- Every claimed error must cite `file:line` and, where possible, be **verified numerically** (step counts, optimiser output, portfolio μ/σ). Say "verified" only when you actually ran a check.
- Report length: **at most 2 pages** (aim for about 1–1.5 pages). Write in English and use German technical terms where they fit (Deckungsgrad, Altersguthaben, Wertschwankungsreserve, Sanierungsmassnahmen).

## Procedure
1. **Record the state:** `git log --oneline | head -5`. Note the commit hash for the report title.
2. **Read every file** in `src/` plus `README.md` and `requirements.txt`. The repo is small, so read the files fully rather than searching.
3. **Map the model** (section 2 of the report):
   - Assets: process (GBM? discretisation?), correlation, initial values and weights, contributions, rebalancing (calendar/corridor), transaction costs.
   - Liabilities: process, growth rate, initial value, cash flows.
   - Funding ratio: definition, initial value $DG_0$, outputs and statistics.
4. **Check for errors.** Use this checklist and add anything new:
   - **Consistency between assets and liabilities:** does every cash flow (contributions, benefits) hit both sides correctly? Savings contributions raise $L$ one-to-one.
   - **Time grid:** are there $N$ or $N-1$ increments? Is $t=0$ stored? Do modulo triggers (`i % k == 0 and i != 0`) miss the last event? Is the value recorded before or after cash flows and rebalancing? Do asset and liability grids match?
   - **Optimisation and rebalancing:** are the units in the objective consistent (CHF² vs CHF)? Does the cost term actually change the solution? Test this with a shocked portfolio and compare the optimiser's trades with naive rebalancing. Check tolerances and any unfinished code paths.
   - **Calibration:** compare rates with the current BVG minimum interest rate and with typical technical interest rates. Look up current values and do not assume them (for reference, as of 2026: BVG minimum rate 1.25 %, technical rates ≈ 1.5–2.5 %, mandatory conversion rate 6.8 %).
   - **Reporting:** arithmetic vs geometric return ($\mu_p - \sigma_p^2/2$), axis units, horizon labels, underfunding measured only at $T$.
   - **Minor issues:** duplicated parameters (e.g. Δt), comments or docstrings that contradict the code, a missing random seed.
5. **Verify** with a small script in the scratchpad. Install missing packages with pip if needed. Example checks:
   ```python
   steps = [i for i in range(T) if i % k == 0 and i != 0]   # how many events actually fire
   x = rb.optimized_target_portfolio(pf, w, 0.001)          # vs naive w*V - V_i
   sigma_p = sqrt(w @ (outer(s, s) * C) @ w)                # geometric return = mu_p - sigma_p**2 / 2
   ```
6. **Additions** (section 4), specific to Swiss pension funds. Mark items as already implemented where they are:
   - Liabilities split into active members' savings (credited at ≥ BVG minimum rate) and pensioners' capital (technical rate, BVG/VZ generational tables), plus technical provisions.
   - Stochastic interest rates driving both bond returns and the liability discount rate.
   - Cash flows: age-dependent savings credits (7/10/15/18 %), pensions, lump sums, vested benefits (Freizügigkeit), conversion-rate losses.
   - Target fluctuation reserve (VaR/ES-based); $DG$ defined per BVV 2 Art. 44.
   - $DG$-dependent rules: interest crediting, recovery measures if $DG < 100 \%$ (Art. 65d BVG).
   - Assets: BVV 2 Art. 55 limits, currency hedging, fees (TER), fat tails, smoothed real-estate valuations.
   - Risk measures: underfunding at any year-end, $P(DG < 90 \%)$, expected shortfall, stress scenarios, comparison of allocations.
7. **Score** each criterion from 0 to 10 with a one-sentence rationale, then give the overall score (the mean):
   - **Accuracy:** how realistic the model is.
   - **Focus:** whether effort goes to what matters, or whether details are overengineered while key features are ignored.
   - **Correctness:** whether what exists is implemented correctly.
   - **Sophistication:** whether most sensible features already exist, or many highly relevant additions are still open.
   When repeating the review, compare with the previous scores and state which errors have been fixed.

## Report template (LaTeX)
```latex
\documentclass[10pt,a4paper]{article}
\usepackage[margin=1.8cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,amsmath,booktabs,enumitem}
\setlist{nosep,leftmargin=*}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\newcommand{\code}[1]{\texttt{\small #1}}
\title{\vspace{-1.2cm}Review: Modelling of the Asset/Liability Ratio\\
\large \code{target-fluctuation-reserves} (commit \code{<hash>})}
\author{}\date{<date>}
\begin{document}
\maketitle\vspace{-1.4cm}
\begin{abstract}\noindent <3--5 sentences: model, main errors, main additions, overall score> \end{abstract}
\section{Current model}            % one paragraph: assets, liabilities, output
\section{Errors and corrections}   % enumerate E1.., each: problem (file:line), effect, \emph{Fix:}
\section{Sensible additions for a Swiss pension fund}  % enumerate A1.., one line each
\section{Assessment}               % booktabs table: Criterion | Score | Rationale; then overall line
\end{document}
```

## Delivery
- Write the report to `<scratchpad>/alm_review.tex`, send it to the user, and also paste the full source in the chat.
- LaTeX is usually not installed in the container, so the page count can't be checked by compiling. Keep the source to about 800–1000 words to stay under two pages, and tell the user it was not compiled.
- In the chat reply, give a short summary of the main errors and the scores.
