# tometo_tomato

**tometo_tomato** is a Python CLI tool for performing fuzzy joins between two CSV files, even in the presence of typos, abbreviations, or different formatting. It leverages DuckDB and the rapidfuzz extension to associate similar records across different sources.

## Features
- Join between two CSV files based on textual similarity
- Multi-column support (you can specify multiple column pairs or automatically use those with the same name)
- Configurable similarity threshold
- Separate output for clean and ambiguous matches
- Execution statistics logging

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` or `uv` (recommended)

### Install from source
1. Clone the repository:
   ```bash
   git clone https://github.com/aborruso/tometo_tomato.git
   cd tometo_tomato
   ```
2. Install the package:
   Using `uv` (recommended):
   ```bash
   uv pip install .
   # Or, for an isolated CLI tool:
   uv tool install .
   ```
   Using `pip`:
   ```bash
   pip install .
   ```

After installation, the `tometo_tomato` command will be available in your terminal.

## Usage

### Basic example
Suppose we have two files:
- `data/input.csv` (input data with possible variations)
- `data/ref.csv` (reference data)

These sample files contain names with various formatting issues:
- Case variations (Mario Rossi vs MARIO ROSSI)
- Extra whitespace (Anna  Bianchi vs Anna Bianchi)
- Accented characters (José Álvarez vs Jose Alvarez)
- Different character encodings (Müller vs Muller)

### Basic example
If the columns to compare have the same name in both files:

```bash
tometo_tomato data/input.csv data/ref.csv --add-field city_code --threshold 90 --show-score --output-clean output.csv
```

If the columns have different names:

```bash
tometo_tomato input.csv ref.csv \
  --join-pair regione,regio \
  --join-pair comune,comu \
  --add-field codice_comune \
  --threshold 90 \
  --show-score \
  --output-clean output.csv
```

### Automated Processing

For scripts and automated workflows, use `--force` to skip file overwrite confirmations:

```bash
tometo_tomato input.csv ref.csv \
  --join-pair regione,regio \
  --join-pair comune,comu \
  --add-field codice_comune \
  --threshold 90 \
  --show-score \
  --output-clean output.csv \
  --force
```

### Handling Field Names with Spaces

If your column names in the CSV files contain spaces, you must enclose the arguments for `--join-pair` (`-j`) and `--add-field` (`-a`) in quotes. This ensures that the shell treats them as a single argument.

**Example:**

Suppose your files have columns named `"Input City"` and `"Reference City"`, and you want to add a field named `"Special Code"`.

```bash
tometo_tomato "input data.csv" "reference data.csv" \
  --join-pair "Input City,Reference City" \
  --add-field "Special Code" \
  --output-clean "clean output.csv"
```


### Normalization Options

#### Remove Special Characters with --keep-alphanumeric
To ignore punctuation and special characters in join columns, use `--keep-alphanumeric` (or `-k`). This keeps only letters, numbers, and spaces before matching:

```bash
tometo_tomato data/input.csv data/ref.csv \
  --join-pair name,ref_name \
  --keep-alphanumeric \
  --add-field city_code \
  --threshold 85 \
  --output-clean output.csv
```

This will match names like:
- `John O'Connor` with `John OConnor`
- `Mary-Jane Smith` with `Mary Jane Smith`
- `Anna & Co.` with `Anna Co`

You can also use the short version:
```bash
tometo_tomato data/input.csv data/ref.csv -j name,ref_name -k -o output.csv
```

#### Character Normalization with --latinize
For data with accented characters or different character encodings, use `--latinize` to normalize characters before matching:

```bash
tometo_tomato data/input.csv data/ref.csv \
  --join-pair name,ref_name \
  --latinize \
  --add-field city_code \
  --threshold 85 \
  --output-clean output.csv
```

This will match names like:
- `José Álvarez` with `Jose Alvarez`
- `Müller` with `Muller`
- `François` with `Francois`

The original accented characters are preserved in the output.

#### Case Sensitivity Control
By default, matching is case-insensitive. Use `--raw-case` for case-sensitive matching:

```bash
tometo_tomato data/input.csv data/ref.csv \
  --join-pair name,ref_name \
  --raw-case \
  --threshold 90 \
  --output-clean output.csv
```

#### Whitespace Handling
By default, whitespace is normalized (trimmed and multiple spaces reduced to single space). Use `--raw-whitespace` to disable this:

```bash
tometo_tomato data/input.csv data/ref.csv \
  --join-pair name,ref_name \
  --raw-whitespace \
  --threshold 90 \
  --output-clean output.csv
```

### Main parameters
- `input.csv` : CSV file to enrich/correct
- `ref.csv`   : Reference CSV file
- `--join-pair colA,colB` : Pair of columns to compare (repeatable)

- `--add-field field`     : Field from the reference file to add to the output
- `--threshold N`         : Minimum similarity threshold (default: 90)
- `--show-score`          : Show average similarity score
- `--output-clean`        : Output file for clean matches (mandatory)
- `--output-ambiguous`    : Output file for ambiguous matches (optional)
- `--scorer ALGO`         : Fuzzy matching algorithm (`ratio` or `token_set_ratio`). Default: `ratio`.
- `--clean-whitespace`    : Remove redundant whitespace from columns before fuzzy matching
- `--force`, `-f`         : Overwrite existing output files without prompting

## Logic and Behavior

- Fuzzy comparison is case-insensitive by default (the tool applies `LOWER()` during matching). Use `--raw-case` to enable case-sensitive comparisons.
- Matching uses the configured join pairs and returns the best match per input row when that match's average similarity (`avg_score`) meets or exceeds the configured `--threshold`.
- Ambiguity definition and handling: an input row is considered "ambiguous" when two or more reference rows obtain the same maximum `avg_score` for that input (and that maximum score is >= `--threshold`). Ambiguous input rows are excluded from the "clean" output to avoid adding potentially incorrect data.
- Use `--output-ambiguous` to save a separate CSV with the ambiguous candidate reference rows (the rows having the equal maximum score). If `--output-ambiguous` is not provided, the program will still detect ambiguous inputs and will print a warning advising how to inspect them.
- The clean output file contains only inputs with a single best reference match (unique maximum score >= threshold). If multiple reference rows tie for the best score, that input will not appear in the clean output and will be reported as ambiguous.
- You can add extra fields from the reference file using `--add-field`.
- The `--latinize` and whitespace/case options control normalization before scoring (see the "Normalization Options" section above).
- **File Overwrite Protection**: By default, the script will prompt for confirmation before overwriting existing output files. Use `--force` to bypass this protection for automated scripts.

## Output
- A CSV file with clean matches (name and path always specified with `--output-clean`).
- A CSV file with ambiguous matches (only if you specify `--output-ambiguous`).

## Use case example
See the file [docs/PRD.md](docs/PRD.md) for a detailed description and practical example.

## Notes
- The `--scorer token_set_ratio` is recommended for cases where names have different word counts (e.g., "Reggio Calabria" vs. "Reggio di Calabria").
- If you don't specify `--join-pair`, all columns with the same name in both files will be used.
- Use `--clean-whitespace` when your data contains inconsistent spacing (e.g., "Rome  City" vs " Rome City ") to improve matching accuracy.
- The tool is designed to be simple, robust, and easily integrable into data cleaning workflows.

## Development


### Running tests


**Consigliato:** usa un ambiente virtuale (venv) per isolare le dipendenze:

```bash
python3 -m venv .venv_test_tometo
source .venv_test_tometo/bin/activate
pip install -e .
pip install pytest
pytest -v
```

**Alternativa:** puoi anche eseguire i test senza installare il pacchetto, impostando il `PYTHONPATH`:

```bash
# Run all tests
PYTHONPATH=$(pwd)/src pytest -v

# Run specific test files
PYTHONPATH=$(pwd)/src pytest tests/test_read_header.py -v
```

Se non hai pytest installato, puoi aggiungerlo con:
```bash
pip install pytest
```

---

For questions, suggestions, or bugs, open an issue on GitHub!
