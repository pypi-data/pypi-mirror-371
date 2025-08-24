# WARP.md

This file provides comprehensive guidance for WARP (warp.dev) when working with the XRayLabTool repository. The project now features both a Python API and a powerful CLI with enhanced development workflows.

## Enhanced Development Workflow

**Quick Setup:**
```bash
# Complete development environment setup
make dev-setup
# OR step by step:
make install      # Install with development dependencies  
make install-docs # Install documentation dependencies
```

**Essential Development Commands:**
```bash
# Quick development cycle (format + lint + fast tests)
make dev

# Fast test run (no coverage) - most common during development
make test-fast

# Full validation before committing (format + lint + coverage + CLI tests)
make validate

# Check project status and health
make status

# Quick functionality test (both API and CLI)
make quick-test
```

**Testing & Quality:**
```bash
# Test suites
make test                  # All tests with coverage
make test-integration      # Integration tests only
make test-benchmarks       # Performance benchmarks
make cli-test             # CLI functionality tests
make cli-demo             # Interactive CLI demonstration

# Code quality
make lint                  # Linting with flake8
make format               # Auto-format with black
make check-format         # Check formatting without changes
make type-check           # Type checking with mypy (if available)
```

**Documentation:**
```bash
make docs                  # Build Sphinx documentation
make docs-serve            # Build and serve docs at http://localhost:8000
make docs-clean            # Clean documentation build files
make docs-linkcheck        # Validate all documentation links
```

**Build & Release:**
```bash
make build                 # Build distribution packages
make test-install-local    # Test local wheel installation in clean environment
make test-install-testpypi # Test TestPyPI installation
make upload-test           # Upload to TestPyPI
make upload                # Upload to PyPI (with confirmation)
make release-check         # Complete pre-release validation checklist
```

**CLI Usage Examples:**
```bash
# Install package to enable CLI
pip install -e .

# Single material calculations
xraylabtool calc SiO2 -e 10.0 -d 2.2
xraylabtool calc Si -e 5-15:11 -d 2.33 -o silicon_scan.csv  # Energy range

# Batch processing from CSV
xraylabtool batch materials.csv -o results.csv --workers 4

# Unit conversions
xraylabtool convert energy 8.048,10.0,12.4 --to wavelength

# Formula analysis
xraylabtool formula Ca10P6O26H2  # Complex biological/mineral formulas
xraylabtool atomic Si,Al,Fe      # Atomic data lookup

# Bragg diffraction calculations
xraylabtool bragg -d 3.14,2.45,1.92 -e 8.048

# Reference information
xraylabtool list constants       # Physical constants
xraylabtool list fields         # Available output fields
xraylabtool list examples       # Usage examples

# Advanced CLI features
xraylabtool calc SiO2 -e 1-30:100:log -d 2.2 --format json --precision 8
xraylabtool calc Si -e 10.0 -d 2.33 --fields formula,energy_kev,critical_angle_degrees
```

## Architecture Overview

### High-Level Data Flow
This package calculates X-ray optical properties through a sophisticated pipeline:

1. **Formula Parsing** (`utils.py:parse_formula`) → Regex-based chemical formula decomposition
2. **Atomic Data Bulk Loading** (`core.py:get_bulk_atomic_data`) → LRU-cached mendeleev lookups  
3. **Scattering Factor Interpolation** (`core.py:create_scattering_factor_interpolators`) → PCHIP interpolators from .nff files
4. **Optical Property Calculation** (`core.py:calculate_scattering_factors`) → Dispersion δ, absorption β
5. **Derived Quantities** (`core.py:calculate_derived_quantities`) → Critical angles, attenuation lengths, SLD
6. **Dataclass Wrapping** (`core.py:XRayResult`) → Snake_case fields with legacy property aliases

### Cache Architecture
- **LRU Cache**: Atomic data lookups (`@lru_cache(maxsize=128)` on `get_atomic_number`/`get_atomic_weight`)
- **Module-Level Caches**: Scattering factor files (`_scattering_factor_cache`) and interpolators (`_interpolator_cache`)
- **Bulk Loading**: Pre-computed element paths (`_AVAILABLE_ELEMENTS`) for performance optimization

### Key Files & Responsibilities
- `xraylabtool/__init__.py`: Public API façade, re-exports all main symbols
- `xraylabtool/core.py`: Core calculations, XRayResult dataclass, caching system
- `xraylabtool/constants.py`: Physical constants with validation, helper conversion functions
- `xraylabtool/utils.py`: Formula parsing, atomic data lookups, crystallographic utilities
- `xraylabtool/cli.py`: Command-line interface with 7 subcommands (calc, batch, convert, formula, atomic, bragg, list)

## Project Metadata

**Requirements:**
- Python ≥ 3.12 (uses modern typing features)
- NumPy ≥ 1.20.0, SciPy ≥ 1.7.0, Pandas ≥ 1.3.0
- Mendeleev ≥ 0.10.0 (atomic data), tqdm ≥ 4.60.0 (progress bars)
- matplotlib ≥ 3.4.0 (optional, for plotting examples)

**Development Dependencies:** 
`pip install -e .[dev]` adds pytest, pytest-cov, pytest-benchmark, black, flake8, mypy

**Supported Platforms:** 
Cross-platform (Linux, macOS, Windows) via GitHub Actions CI matrix

**License:** MIT

**Performance Expectations:**
- Single material, single energy: ~0.1 ms
- Single material, 100 energies: ~1 ms  
- 10 materials, 100 energies: ~50 ms (with ThreadPoolExecutor parallelization)

## Public API & XRayResult Dataclass

### Main Functions

**`calculate_single_material_properties(formula: str, energy_keV: Union[float, List, ndarray], density: float) -> XRayResult`**
- Primary function for single material calculations
- Supports scalar, list, or numpy array energy inputs 
- Energy range: 0.03–30 keV (X-ray regime)
- Returns XRayResult with all optical properties

**`calculate_xray_properties(formulas: List[str], energies: Union[float, List, ndarray], densities: List[float]) -> Dict[str, XRayResult]`**
- Multi-material calculation with ThreadPoolExecutor parallelization
- Validates input lengths, sorts energies for consistency
- Returns dictionary mapping formula strings to XRayResult objects

### XRayResult Dataclass (New snake_case Fields)

**Material Properties:**
- `formula: str` — Chemical formula
- `molecular_weight_g_mol: float` — Molecular weight (g/mol) 
- `total_electrons: float` — Total electrons per molecule
- `density_g_cm3: float` — Mass density (g/cm³)
- `electron_density_per_ang3: float` — Electron density (electrons/Å³)

**X-ray Properties (Arrays):**
- `energy_kev: np.ndarray` — X-ray energies (keV)
- `wavelength_angstrom: np.ndarray` — X-ray wavelengths (Å)
- `dispersion_delta: np.ndarray` — Dispersion coefficient δ
- `absorption_beta: np.ndarray` — Absorption coefficient β  
- `scattering_factor_f1: np.ndarray` — Real atomic scattering factor
- `scattering_factor_f2: np.ndarray` — Imaginary atomic scattering factor
- `critical_angle_degrees: np.ndarray` — Critical angles (degrees)
- `attenuation_length_cm: np.ndarray` — Attenuation lengths (cm)
- `real_sld_per_ang2: np.ndarray` — Real SLD (Å⁻²)
- `imaginary_sld_per_ang2: np.ndarray` — Imaginary SLD (Å⁻²)

### Legacy Field Compatibility
Legacy CamelCase fields (`Formula`, `MW`, `Critical_Angle`, etc.) are supported via deprecated property aliases that emit `DeprecationWarning`. Use new snake_case fields for new code:

```python
# ✅ NEW (recommended)
result = calculate_single_material_properties("SiO2", 10.0, 2.2)
print(f"Critical angle: {result.critical_angle_degrees[0]:.3f}°")
print(f"MW: {result.molecular_weight_g_mol:.2f} g/mol")

# ⚠️ OLD (deprecated but functional)
print(f"Critical angle: {result.Critical_Angle[0]:.3f}°")  # Emits warning
print(f"MW: {result.MW:.2f} g/mol")  # Emits warning
```

## Testing & Benchmarks

### Test Suite Structure (145 tests)
- **Integration Tests**: `test_integration.py` — Julia compatibility validation with `numpy.isclose(atol=1e-6)`
- **Unit Tests**: Individual modules (formula parsing, utils, atomic data, core physics)
- **Robustness Tests**: `test_robustness.py` — Complex number handling, type conversions, edge cases
- **Performance Tests**: `TestPerformanceBenchmarks` class using pytest-benchmark

### Running Tests

```bash
# Complete test suite via convenience script
python run_tests.py

# Specific test categories
pytest tests/test_integration.py -v                    # Core integration
pytest tests/test_formula_parsing.py -v               # Chemical formula parsing
pytest tests/test_core_physics.py -v                  # Physics calculations
pytest tests/test_robustness.py -v                    # Edge cases

# Performance benchmarks
pytest tests/test_integration.py::TestPerformanceBenchmarks --benchmark-only -v
pytest tests/test_integration.py::TestPerformanceBenchmarks --benchmark-json=benchmark.json

# Coverage reports
make test-coverage                                     # HTML + XML coverage
pytest tests/ --cov=xraylabtool --cov-report=html
```

### Benchmark Categories
- Single material calculations (various energies)
- Multi-material calculations (parallel processing) 
- Energy sweep calculations (vectorized operations)
- Formula complexity benchmarks (element count scaling)

### Julia Test Compatibility
Integration tests validate exact numerical agreement with original Julia implementation:
- SiO2: dispersion, f1 values, reSLD at specific energy indices
- H2O: dispersion, f1 values, reSLD validation
- Silicon: SubRefrac properties (dispersion, f1, f2, reSLD, imSLD)

## Build & CI/CD Workflow

### GitHub Actions Matrix
**Platforms:** Ubuntu, macOS, Windows
**Python Versions:** 3.12, 3.13
**Workflow:** lint → test → benchmark → Codecov upload

```bash
# CI simulation locally
make ci-test
```

### Package Building

```bash
# Manual build process
python build_package.py                    # Full validation + build
python build_package.py --skip-tests       # Skip tests (faster)

# Or using Make targets
make build          # Build distributions  
make upload-test    # Upload to Test PyPI
make upload         # Upload to production PyPI
```

### Continuous Integration Features
- **Coverage**: Codecov integration with HTML/XML reports
- **Benchmarks**: Performance regression detection via benchmark comparison jobs
- **Cross-platform**: Tests run on 3 OS × 2 Python versions (6 combinations)
- **Lint Enforcement**: flake8 with complexity limits and statistics
- **Format Checking**: black code style validation

### Performance Monitoring
```bash
# Baseline benchmarks
make perf-baseline

# Compare against baseline
make perf-compare
```

The CI pipeline includes benchmark comparison jobs that run on PRs to detect performance regressions by comparing current branch benchmarks against the base branch.

## Development Tips

### Typical Development Cycle
1. `make dev` — Quick cycle: format check + lint + fast tests
2. `make validate` — Full validation before pushing: format + lint + coverage + benchmarks
3. `python run_tests.py` — Comprehensive test run with coverage reports

### Working with Caches
- Tests automatically clear caches via `clear_scattering_factor_cache()` 
- Performance tests may benefit from cache warming
- Cache state affects benchmark results — use consistent cache states for comparisons

### Field Name Migration
When updating code, search for legacy field patterns:
```bash
# Find legacy field usage
grep -r "result\.Formula" --include="*.py" .
grep -r "result\.MW" --include="*.py" .
grep -r "result\.Critical_Angle" --include="*.py" .
```
