# Form32AutoFlow

Tools for processing Texas DWC-032 PDFs and generating downstream DWC forms.

## What It Does

`form32-docling` runs a hybrid pipeline:

1. Converts PDF pages with `docling` (OCR/layout).
2. Extracts structured fields with Docling `DocumentExtractor` (VLM templates by page type).
3. Runs regex/location fallback for missing text fields.
4. Runs OpenCV checkbox analysis as fallback (and optional Part 5 override assist).
5. Generates output PDFs:
   - `DWC068` when purpose C, D, or G is checked.
   - `DWC069` always.
   - `DWC073` always.

## Requirements

- Python `>= 3.12`
- Poppler utilities available on PATH (`pdf2image` dependency for checkbox analysis)
- Node.js (only if using the Next.js GUI source directly)

## Install

- Create conda env form32gpu with dependencies from TOML installed.

```bash
cd Form32AutoFlow
conda activate form32gpu
pip install -e .
```

Optional extras:

```bash
pip install -e ".[dev]"        # pytest, ruff, mypy
pip install -e ".[api]"        # fastapi, uvicorn, sqlalchemy
pip install -e ".[ui]"         # PyQt6
pip install -e ".[vlm]"        # torch, torchvision, qwen-vl-utils
```

`gen32form` also imports `faker` (currently in `requirements-gpu.lock`, not in `pyproject.toml`), so install it when using that CLI:

```bash
pip install faker
```

Core runtime dependencies declared in `pyproject.toml`:

- `docling`
- `reportlab`
- `pypdf`
- `opencv-python`
- `numpy`
- `pillow`
- `pdf2image`
- `pydantic`
- `python-dotenv`

## Commands

Installed console scripts:

- `form32-docling` -> process a DWC-032 PDF, fill info fields to populate DWC069, 073, and 068.
- `gen32form` -> generate randomized filled DWC-032
- `form32-db` -> manage GUI SQLite records
- `form32-server` -> start FastAPI backend (and static GUI if built)

### `form32-docling`

```bash
form32-docling path/to/input.pdf [options]
```

Options:

- `-o, --output-dir PATH` override output base directory
- `-v, --verbose` verbose logging + debug artifacts
- `--output-json` write `form32_data.json`
- `--no-part5-checkbox-assist` disable Part 5 checkbox assist/override behavior
- `--version`

Behavior details:

- Input must exist and end with `.pdf`.
- Processing uses VLM extraction mode.
- On success, CLI prints output directory, copied source path, generated form paths, and optional debug artifact paths.
- Logs are written to `form32_processing.log`.

### `gen32form`

```bash
gen32form [-i INPUT_PDF] [-o OUTPUT_DIR] [-v]
```

- Default input: `Form32reader/WorkersCompData/dwc032desdoc-fillable.pdf`
- Writes `DWC032_randomized_<4digits>.pdf` into output directory.

### `form32-db`

```bash
form32-db [list|delete|clean]
```

- Database path: `~/.form32_gui.db`
- `clean` prompts for confirmation.

### `form32-server`

```bash
form32-server
```

- Runs FastAPI on `127.0.0.1:8000` with reload enabled by default.
- Set `FORM32_SERVER_HOST` and `FORM32_SERVER_PORT` to override bind host/port.
- Health endpoint: `GET /api/health`
- If `src/form32_docling/gui/out` exists, FastAPI serves the static UI at `/`.

## Output Layout

Each processed case is written to a patient directory under the configured base output directory:

```text
<patient_name_with_underscores>_<exam_city>_<M.D.YY>/
```

Typical contents:

```text
FORM32 <PATIENT>.pdf
DWC068 <PATIENT>.pdf         # when purpose C/D/G selected
DWC069 <PATIENT>.pdf         # always
DWC073 <PATIENT>.pdf         # always
```

Verbose/debug artifacts:

- `docling_document.json` (with `-v`)
- `docling_document.md` (with `-v`)
- `extracted_fields.json` (verbose processor run)
- `form32_data.json` (with `--output-json` or `-v`)

## Configuration

Environment variables:

- `FORM32_OUTPUT_DIR` base output directory
- `FORM32_PDF_PATH` default PDF source directory
- `FORM32_LOG_LEVEL` logging level when `-v` is not set
- `FORM32_DOCTOR_PHONE` default designated doctor phone
- `FORM32_DOCTOR_LICENSE_TYPE` default designated doctor license type
- `FORM32_DOCTOR_LICENSE_JURISDICTION` default designated doctor license jurisdiction

Defaults from code:

- Linux/WSL output: `~/AIDev/Form32_output`
- Linux/WSL PDF source: `~/AIDev/Form32_pdf`
- Windows output: `D:\AIDev\Form32_ouput`
- Windows PDF source: `D:\AIDev\Form32_pdf`

## API + GUI Notes

FastAPI endpoints include:

- `POST /api/process`
- `GET /api/patients`
- `GET /api/patients/{id}`
- `PATCH /api/patients/{id}`
- `POST /api/generate/{id}`
- `GET /api/download?path=...`
- `DELETE /api/patients/{id}`
- `DELETE /api/patients`

The Next.js UI uses relative `/api/*` fetch calls. The supported deployment path is to build the UI and serve it from `form32-server`.

```bash
cd src/form32_docling/gui
npm install
npm run build
cd ../../..
form32-server
```

Then open `http://localhost:8000`.

## Tests

```bash
pytest
```
