# GEMINI.md

## Project Overview

This project, "tometo_tomato," is designed to implement a flexible and robust data processing procedure for performing "fuzzy joins" between tabular datasets. The core problem it solves is joining tables on key columns that have inconsistencies, typos, or variations (e.g., 'Reggio di Calabria' vs. 'Reggio Calabria'), where a standard SQL join would fail.

The process is defined in detail in the [Product Requirements Document](docs/PRD.md).

**Main Technologies:**
*   **Data Engine:** DuckDB CLI
*   **Fuzzy Matching:** The `rapidfuzz` community extension for DuckDB.

**Architecture:**
The project is centered around a Python script (`tometo_tomato.py`) that orchestrates data processing using the `duckdb` engine.
*   `data/`: Contains the data, subdivided into:
    *   `raw/`: Original, immutable source data.
    *   `interim/`: Intermediate, transformed data.
    *   `processed/`: Final, clean data ready for use.
*   `docs/`: Contains project documentation, including the main `PRD.md`.
*   `scripts/`: Contains the implementation scripts (likely Shell scripts wrapping DuckDB commands or pure `.sql` files) for the fuzzy join logic.

## Building and Running

The core of this project is the `tometo_tomato` Python CLI tool, which orchestrates data processing by executing SQL queries via the `duckdb` engine.

A typical workflow within a script would involve:
1.  Installing and loading the `rapidfuzz` extension.
2.  Running a SQL query to perform the fuzzy join.
3.  Exporting the results to the `data/processed` directory.

**Example DuckDB commands:**

```sql
-- Install and load the extension
INSTALL rapidfuzz FROM community;
LOAD rapidfuzz;

-- Example query to perform the join and save results
-- (This is a simplified conceptual query)
COPY (
  WITH scores AS (
    SELECT
      a.*,
      b.*,
      rapidfuzz_ratio(a.key_column, b.key_column) AS score
    FROM read_csv_auto('data/raw/table_a.csv') AS a
    CROSS JOIN read_csv_auto('data/raw/table_b.csv') AS b
  ),
  ranked_scores AS (
    SELECT *,
           ROW_NUMBER() OVER(PARTITION BY a.id ORDER BY score DESC) as rn
    FROM scores
    WHERE score > 85 -- Apply threshold
  )
  SELECT *
  FROM ranked_scores
  WHERE rn = 1 -- Select best match
) TO 'data/processed/joined_data.csv' (HEADER, DELIMITER ',');

```

## Development Conventions

*   **Data Flow:** Data should flow from `data/raw` through `data/interim` to `data/processed`. The `raw` directory is read-only.
*   **Core Logic:** The main logic is implemented in the `tometo_tomato.py` Python script, which utilizes DuckDB for data processing.
*   **Orchestration:** The `tometo_tomato` Python CLI tool handles the overall execution flow, chaining commands and managing parameters.
*   **Documentation:** All significant project decisions, goals, and requirements are documented in `docs/PRD.md`.
*   **Logging:** Project progress and key events should be tracked in `LOG.md`.
