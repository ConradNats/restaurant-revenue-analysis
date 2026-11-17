# Scripts

The notebook is the deliverable; these scripts keep it reproducible and reviewable.

## Notebook build pipeline

| Script | Purpose |
|---|---|
| `nb_cells_part1.py` | Setup, design system, profiling, cleaning, distributions, composition |
| `nb_cells_part2.py` | Relationships, correlation, data-mining Q1–Q3 |
| `nb_cells_part3.py` | Q4–Q8, insights, recommendations, limitations, LinkedIn draft, export |
| `build_notebook.py` | Combines the three cell modules into `Restaurant_Data_Visualization.ipynb` |
| `execute_notebook.py` | Executes the notebook in place with `nbclient` and writes all outputs |

Rebuild and re-run everything:

```bash
python scripts/build_notebook.py
python scripts/execute_notebook.py
```

> `build_notebook.py` creates a clean notebook **without outputs**. Run `execute_notebook.py` afterwards to embed results and regenerate `figures/`.

## Verification scripts

These stand-alone scripts were used to validate every number quoted in the notebook's markdown. They read `restaurant_data.csv` from the project root and print tables to stdout.

| Script | What it checks |
|---|---|
| `01_profile.py` | Shape, dtypes, missing values, duplicates, ranges, correlations |
| `02_explore_numbers.py` | Revenue shares, marketing controls, regression, group tests, k-means |
| `03_confirm_pattern.py` | The revenue/(seats × price) ratio and residual distribution |
| `04_segments.py` | Segment profiles, partial correlations, concentration numbers |

Run them from the project root, for example:

```bash
python scripts/02_explore_numbers.py
```

They are intentionally plain scripts — no notebook state, no hidden variables.
