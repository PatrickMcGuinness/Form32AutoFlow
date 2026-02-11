# Form32reader

An application for processing Texas Department of Insurance (TDI) Form 32 PDFs and doctor examination orders, then automatically generating associated medical forms
(DWC-068, DWC-069, DWC-073).

## Prerequisites

Before running the application, install the following system dependencies.

See associated TOML file for dependencies.


## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:BillyKnott/Form32reader.git
cd Form32reader
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Linux/WSL2:**
```bash
conda activate form32gpu
```


### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Package in Development Mode

```bash
pip install -e .
```

## Configuration

The application auto-detects your platform and uses appropriate default paths.

### Environment Variables (Optional)

Override default paths using environment variables:



Example (Linux/WSL2):
```bash
export FORM32_OUTPUT_DIR="/mnt/d/ProcessedForms"
export FORM32_PDF_PATH="/mnt/d/Form32PDFs"
```

### Logging Configuration

Log level is controlled via environment variable or CLI flag:

| Method | Priority | Effect |
|--------|----------|--------|
| `-v` / `--verbose` flag | Highest | DEBUG level logging |
| `FORM32_LOG_LEVEL` env var | Medium | Set to `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| Default | Lowest | INFO level |

Example:
```bash
# Set log level via environment variable
export FORM32_LOG_LEVEL=DEBUG

# Or use -v flag for verbose output (takes precedence)
form32-docling -v path/to/form.pdf
```

## Usage

### Option 1: Form32 Docling CLI

The `form32-docling` package provides a dedicated command-line interface for modern document processing using the `docling` library.

#### Basic Usage
```bash
form32-docling path/to/your/form32.pdf
```

#### Advanced Options
- `-o`, `--output-dir <path>`: Set a custom output directory (overrides default).
- `-v`, `--verbose`: Enable detailed debug logging.
- `--version`: Show package version.

#### Alternative Execution
If the `form32-docling` command is not in your system path:
```bash
python -m form32_docling.cli path/to/your/form32.pdf
```

### Run Test Script

Process a sample PDF using the included test script:

```bash
python tests/test_process.py
```

Edit `tests/test_process.py` to change the input PDF path.

### Utility: gen32form (Randomized Data Generation)

The `gen32form` tool generates randomized data based on the Form 32 templates and populates a fillable PDF for testing purposes.

#### Usage
```bash
gen32form [-i INPUT_PDF] [-o OUTPUT_DIR] [-v]
```

#### Options:
- `-i`, `--input`: Specific input PDF form path (default: `Form32reader/WorkersCompData/dwc032desdoc-fillable.pdf`).
- `-o`, `--output-dir`: Directory where the randomized PDF will be saved (default: current directory `.`).
- `-v`, `--verbose`: Enable detailed debug logging, showing the constructed JSON data.

#### What it does:
1. Generates 10 random entries for every field in the Form 32 template.
2. Randomly selects one entry per field to create a complete JSON record.
3. Populates the provided fillable PDF with this data.
4. Saves the resulting PDF with a randomized filename (e.g., `DWC032_randomized_2481.pdf`) in the specified output directory.

### Option 4: form32-db (Database Management)

The `form32-db` tool provides a command-line interface for managing the SQLite database used by the GUI (`~/.form32_gui.db`).

#### Usage
```bash
form32-db [list|delete|clean]
```

#### Commands:
- `list`: Show all patient records stored in the database.
- `delete <ID>`: Remove a specific patient record and its associated injury evaluations by ID.
- `clean`: Remove **all** records from the database (requires confirmation).

#### Execution:
Run from the project root using the conda environment:
```bash
conda run -n form32gpu form32-db list
```
Or via the Python module:
```bash
conda run -n form32gpu python -m form32_docling.cli_db list
```

## Output

Processed files are saved to the output directory in subdirectories named:

```
{date} {PATIENT_NAME} {CITY}/
├── [Original Form 32 PDF]
├── DWC-068.pdf  (if boxes C, D, or G checked)
├── DWC-069.pdf  (always generated)
└── DWC-073.pdf  (if box E checked)
```

Default output locations:
- **Linux/WSL2**: `~/pending_exams/`
- **Windows**: `C:\Pending Exams\`

## Building Executable

> [!NOTE]
> Executable building for the new Docling-based version is currently under development.

## Project Structure

```
Form32reader/
├── src/
│   └── form32_docling/      # Docling-based processor (Recommended)
│       ├── config/          # Configuration settings
│       ├── core/            # Processing logic
│       ├── forms/           # Form generators and templates
│       ├── models/          # Data models
│       └── utils/           # Utility functions
├── pyproject.toml           # Package configuration and entry points
└── tests/
    └── test_process.py      # Test script
```

## Running GUI and API

The application includes a FastAPI backend and a Next.js frontend.

### 1. Start the API Server

The API handles document processing and database management. It can be run using the standalone command:

```bash
conda run -n form32gpu form32-server
```

Or manually:
```bash
conda run -n form32gpu python -m form32_docling.api.main
```

The API will be available at `http://localhost:8000`. You can verify it's running by visiting `http://localhost:8000/api/health`.

### 2. Start the GUI Frontend

From the `Form32reader/src/form32_docling/gui` directory:

```bash
npm run dev
```

The GUI will be available at `http://localhost:3000`.

### 3. Workflow
1. Open the Dashboard at `http://localhost:3000`.
2. Upload a Form 32 PDF.
3. Review and edit extracted data in the Workbench.
4. Generate final PDFs (DWC-068, DWC-069, DWC-073).


### Unified Production Deployment (Recommended)

For cloud or production deployment, you can serve the frontend directly from the FastAPI server. This simplifies the architecture to a single running process.

1. **Build the Frontend**:
   ```bash
   cd src/form32_docling/gui
   npm install
   npm run build
   ```
   This generates a static `out/` directory.

2. **Start the Unified Server**:
   ```bash
   # From project root
   conda run -n form32gpu form32-server
   ```
   The GUI will now be available at `http://localhost:8000` (the same port as the API).

---

## Troubleshooting



### PDF Processing Fails

- Verify the PDF is a valid Form 32 document
- Check that the PDF is not password-protected
- Try running with `verbose=True` for detailed logging
- Check `form32_processing.log` for error details

### GUI Not Working in WSL2

If running the GUI in WSL2, you need an X server:

1. Install an X server on Windows (VcXsrv, X410, or use WSLg on Windows 11)
2. Set the DISPLAY variable:
   ```bash
   export DISPLAY=:0
   ```

Alternatively, use command-line processing instead of the GUI.

## Dependencies

Key libraries used:
- **docling**: Modern document extraction and processing
- **reportlab**: PDF generation
- **pypdf**: PDF manipulation
- **opencv-python**: Image processing
- **pydantic**: Data validation
