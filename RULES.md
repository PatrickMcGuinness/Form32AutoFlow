
# RULES.md — Python 3.13 Project Standards

These rules define the “default way” we write, structure, test, and ship this Python 3.13 codebase. If you deviate, leave a short comment in the PR explaining why.

---

## 1) Runtime + Compatibility

### 1.1) Python Version and Environment
- **Target runtime:** Python **3.13** (primary).
- **Minimum supported version:** 3.13 unless explicitly documented otherwise.
- Prefer modern language features when they improve clarity (e.g., `|` unions, `match`, `pathlib`, `dataclasses`, `typing` improvements).
- Use **`tomllib`** (stdlib) for TOML parsing (avoid third-party TOML libs unless necessary).


### 1.2) Use Conda for Environment Management

#### 1.2.1) Dev Environment Activation
- **Always activate the conda environment before running commands:**
  `bash conda activate form32gpu`

#### 1.2.2) Package Installation
- **Prefer `conda install` over `pip install`** for dependencies when available
- Use pip only for packages not available in conda channels
- Example:   
  # Preferred
  `conda install -c conda-forge pytest`
  # Fallback if not in conda
  `pip install some-package`

#### 1.2.3) Running Tests
- Run tests in conda environment ai-ocr
`conda activate ai-ocr & pytest tests/ -v`

#### 1.2.4) Package Installation (editable mode)
`conda activate form32gpu & pip install -e .`


## 2) Dependency Management (TOML / `pyproject.toml`)

### 2.1 Use `pyproject.toml` (single source of truth)
- Project metadata and dependencies live in **`pyproject.toml`** (PEP 621).
- Do not maintain `requirements.txt` as the source of truth (you may export it for deployment targets if required).

### 2.2 Choose one toolchain (and stick to it)

Pick `uv` (recommended for speed and lockfiles).
Lockfiles are required for reproducible installs.

### 2.3 Dependency rules
- Pin **minimum** versions only when needed; prefer compatibility ranges.
- Always separate dependency intent:
  - **runtime dependencies** (app/library needs)
  - **dev dependencies** (lint/test/type/doc tools)
  - **optional extras** (feature flags)

### 2.4 Use standard `pyproject.toml` format

### 2.5 No “works on my machine”
- CI must install from `pyproject.toml` + lockfile.
- Local installs must be reproducible via a single command (documented in `README.md`).

---

## 3) Project Layout
Use a predictable layout. Prefer `src/` layout.

```text
.
├── pyproject.toml
├── README.md
├── RULES.md
├── src/
│   └── your_project/
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── test_*.py
│   └── ...
└── scripts/          # optional: one-off utilities (thin wrappers)
```

### Rules:
- Import from the package (`your_project.*`), not via relative path hacks.
- Keep `scripts/` small. Real logic goes in `src/your_project/`.

---

## 4) Code Style (Readable > Clever)
- Prefer clarity over micro-optimizations.
- Keep functions small and single-purpose.
- Prefer pure functions where possible.
- Avoid hidden side effects (global state, implicit I/O).
- Use `pathlib.Path` for filesystem work.
- Prefer `datetime` with timezone awareness when timestamps matter.

---

## 5) Formatting + Linting

### 5.1 Formatting
- Use one formatter consistently.
- Default recommendation: **Ruff** for lint + formatting (fast and consistent).
- No manual formatting debates—run the formatter.

### 5.2 Linting
- No unused imports, dead code, shadowed variables.
- Treat lint warnings as errors in CI.
- When ignoring a rule, do it narrowly and explain why.

---

## 6) Typing (Required)
Type hints are required for:
- Public functions/methods.
- Module-level constants.
- Complex internal logic.

### Rules:
- Prefer precise types over `Any`.
- Use `|` unions instead of `Union[...]`.
- Use `TypedDict` / `dataclass` / `pydantic` models for structured data—not ad-hoc dicts.
- Recommended tools: **mypy** or **pyright**.
- CI runs type checks.
- Any new module should be type-check clean.

---

## 7) Testing (Required)
- Use **pytest**.

### Test naming:
- Files: `tests/test_*.py`
- Functions: `test_*`

### Write tests for:
- Important business logic.
- Boundary cases.
- Failure modes.

### Best Practices:
- Avoid brittle tests (don’t over-mock internals).
- Prefer:
    - **Unit tests** for pure logic.
    - **Integration tests** for I/O boundaries (HTTP, DB, filesystem).
- **Coverage**:
    - Maintain sensible coverage for core modules.
    - Don’t chase 100% at the cost of quality, but do not reduce coverage without justification.

---

## 8) Error Handling
- Never swallow exceptions silently.
- Use targeted exceptions, not `except Exception` unless re-raising with context.
- Add context when re-raising: `raise ValueError(f"Invalid config: {path}") from e`.
- Validate inputs at boundaries (API handlers, CLI args, file reads).

---

## 9) Logging
- Use the stdlib `logging`.
- Don’t use `print()` in production code (CLI-only scripts may use it).
- Log structured context where useful (ids, paths, counts).
- Do not log secrets or PII.

---

## 10) Configuration + Secrets
Configuration comes from:
- Environment variables.
- Config files (`TOML`/`YAML`/`JSON`) if needed.
- CLI args (for tools).

### Rules:
- Never commit secrets.
- Provide `.env.example` if env vars are required.
- Use `os.environ.get(...)` only at the boundary; pass config into functions/classes.

---

## 11) I/O Boundaries (Clean Architecture)
Keep core logic independent of:
- HTTP frameworks.
- Databases.
- Filesystem.
- Vendor APIs.

- Wrap external systems behind thin adapters.
- Write “domain” code that can be tested without network access.

---

## 12) Performance + Reliability
- Prefer algorithmic clarity first; optimize with measurement.
- If performance matters:
    - Profile before optimizing.
    - Add benchmarks or perf tests.
- Use caching intentionally and document invalidation rules.

---

## 13) Documentation
Every public module should have:
- A short docstring at top explaining purpose.
- Clear function docstrings for non-trivial APIs.

### Keep README.md current:
- Install
- Run
- Test
- Lint/Typecheck

- Document any non-obvious design choices in `docs/` or `README.md`.

---

## 14) Git + PR Rules
- Keep PRs small and focused.

### Every PR must:
- Pass lint/format/typecheck/tests.
- Include tests for new behavior.
- Update docs when behavior changes.

### Commit messages:
- Imperative mood: “Add X”, “Fix Y”.
- Reference issues when relevant.

---

## 15) CI Expectations (Baseline)
CI should run:
- Install (from lockfile).
- Format check.
- Lint.
- Type check.
- Tests (+ coverage report).

- Local dev should have a single “quality” command (e.g., `make check` or `uv run ...`) that matches CI.

---

## 16) “Don’ts” (Hard Rules)
- Don’t add dependencies casually—every new dependency has a cost.
- Don’t mix multiple dependency managers.
- Don’t commit generated artifacts unless required (wheels, build outputs, large binaries).
- Don’t use relative-import hacks or mutate `sys.path`.
- Don’t leave `TODOs` without an issue/link when they affect correctness or security.

---

## 17) When Rules Conflict
- Prefer correctness and security over style.
- Prefer clarity over cleverness.
- If you must break a rule, explain it in the PR and add a test.
