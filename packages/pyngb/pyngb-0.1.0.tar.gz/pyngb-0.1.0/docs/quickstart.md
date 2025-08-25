# Quick Start Guide

This guide will help you get started with pyngb quickly.

## Basic Usage

### Loading Data

pyngb provides a simple, intuitive function for loading data:

```python
from pyngb import read_ngb

# Default mode: Load as PyArrow Table with embedded metadata
table = read_ngb("sample.ngb-ss3")
print(f"Loaded {table.num_rows} rows with {table.num_columns} columns")

# Advanced mode: Get structured data with separate metadata
metadata, data = read_ngb("sample.ngb-ss3", return_metadata=True)
print(f"Sample: {metadata.get('sample_name', 'Unknown')}")
```

### Working with Data

Convert to different formats and analyze:

```python
import polars as pl

# Convert to Polars DataFrame
df = pl.from_arrow(table)

# Basic analysis
print(df.describe())
print(f"Columns: {df.columns}")

# Filter data
temperature_data = df.filter(pl.col("sample_temperature") > 100)

# Save to files
df.write_parquet("output.parquet")
df.write_csv("output.csv")
```

### Baseline Subtraction

pyngb supports automatic baseline subtraction with temperature program validation:

```python
from pyngb import read_ngb, subtract_baseline

# Method 1: Integrated approach (recommended)
corrected_data = read_ngb(
    "sample.ngb-ss3",
    baseline_file="baseline.ngb-bs3"
)

# Method 2: Standalone function
corrected_df = subtract_baseline("sample.ngb-ss3", "baseline.ngb-bs3")

# Advanced options
corrected_data = read_ngb(
    "sample.ngb-ss3",
    baseline_file="baseline.ngb-bs3",
    dynamic_axis="time"  # Default: "sample_temperature"
)
```

**Key Features:**
- Automatic temperature program validation ensures scientific accuracy
- Dynamic segments aligned by sample temperature (default) or time/furnace temperature
- Isothermal segments always aligned by time
- Only measurement columns (mass, DSC signal) are corrected

## Command Line Interface

pyngb includes a powerful CLI for batch processing:

### Basic Commands (single file)

```bash
python -m pyngb sample.ngb-ss3 -f parquet

# Convert to CSV
python -m pyngb sample.ngb-ss3 -f csv

# Convert to both formats (Parquet and CSV)
python -m pyngb sample.ngb-ss3 -f all
```

### Baseline Subtraction

```bash
# Basic baseline subtraction (default: sample_temperature axis)
python -m pyngb sample.ngb-ss3 -b baseline.ngb-bs3

# Use time axis for dynamic segments
python -m pyngb sample.ngb-ss3 -b baseline.ngb-bs3 --dynamic-axis time

# Use furnace temperature axis for dynamic segments
python -m pyngb sample.ngb-ss3 -b baseline.ngb-bs3 --dynamic-axis furnace_temperature

# Output includes "_baseline_subtracted" suffix
python -m pyngb sample.ngb-ss3 -b baseline.ngb-bs3 -f all -o ./corrected/
```

### Multiple files

```bash
# The CLI processes one input file at a time.
# Use a simple shell loop for multiple files, or see the Batch Processor.
for f in *.ngb-ss3; do
    python -m pyngb "$f" -f parquet -o ./results
done
```

### Advanced Options

```bash
# Verbose output
python -m pyngb sample.ngb-ss3 -f parquet -v

# Get help
python -m pyngb --help
```

## Common Use Cases

### Data Exploration

```python
from pyngb import read_ngb
import polars as pl

# Load and explore
table = read_ngb("sample.ngb-ss3")
df = pl.from_arrow(table)

# Check data structure
print("Available columns:", df.columns)
print("Data types:", df.dtypes)
print("Shape:", df.shape)

# Basic statistics
print(df.select(pl.col("sample_temperature", "time", "dsc_signal")).describe())

# Check for missing values
print(df.null_count())
```

### Column Metadata Tracking

pyngb automatically tracks metadata for all columns including units, processing history, and baseline correction status:

```python
from pyngb import read_ngb
from pyngb.api.metadata import get_column_units, get_processing_history, inspect_column_metadata

# Load data - automatic metadata initialization
table = read_ngb("sample.ngb-ss3")

# Check column units (automatically assigned)
print(f"Mass units: {get_column_units(table, 'mass')}")        # "mg"
print(f"DSC units: {get_column_units(table, 'dsc_signal')}")   # "µV"
print(f"Time units: {get_column_units(table, 'time')}")        # "min"

# Check processing history
print(f"Mass history: {get_processing_history(table, 'mass')}")  # ["raw"]

# Full metadata inspection
mass_metadata = inspect_column_metadata(table, 'mass')
print(f"Complete mass metadata: {mass_metadata}")
# {'units': 'mg', 'processing_history': ['raw'], 'source': 'measurement', 'baseline_subtracted': False}

# Metadata is preserved through analysis operations
from pyngb.api.analysis import add_dtg, normalize_to_initial_mass

# Add DTG - preserves existing metadata, adds DTG metadata
table_with_dtg = add_dtg(table)
print(f"DTG units: {get_column_units(table_with_dtg, 'dtg')}")  # "mg/min"

# Normalize - updates units and processing history in place
normalized_table = normalize_to_initial_mass(table_with_dtg)
print(f"Mass units after normalization: {get_column_units(normalized_table, 'mass')}")      # "mg/mg"
print(f"DSC units after normalization: {get_column_units(normalized_table, 'dsc_signal')}")  # "µV/mg"
print(f"Mass processing history: {get_processing_history(normalized_table, 'mass')}")        # ["raw", "normalized"]
```

### DSC Calibration

Convert DSC signals from microvolts (µV) to physically meaningful power units (mW) using calibration constants stored in the file metadata:

```python
from pyngb import read_ngb
from pyngb.api.analysis import apply_dsc_calibration, normalize_to_initial_mass
from pyngb.api.metadata import get_column_units, get_processing_history

# Load thermal analysis data
table = read_ngb("sample.ngb-ss3")

# Check original DSC units
print(f"Original DSC units: {get_column_units(table, 'dsc_signal')}")  # µV

# Apply DSC calibration (µV → mW)
calibrated_table = apply_dsc_calibration(table)
print(f"Calibrated DSC units: {get_column_units(calibrated_table, 'dsc_signal')}")  # mW
print(f"Processing history: {get_processing_history(calibrated_table, 'dsc_signal')}")  # ['raw', 'calibration_applied']

# Calibration works in any order with normalization
# Method 1: Calibrate then normalize
cal_then_norm = apply_dsc_calibration(table)
cal_then_norm = normalize_to_initial_mass(cal_then_norm, columns=['dsc_signal'])
final_units_1 = get_column_units(cal_then_norm, 'dsc_signal')  # mW/mg

# Method 2: Normalize then calibrate
norm_then_cal = normalize_to_initial_mass(table, columns=['dsc_signal'])
norm_then_cal = apply_dsc_calibration(norm_then_cal)
final_units_2 = get_column_units(norm_then_cal, 'dsc_signal')  # mW/mg

print(f"Both approaches result in: {final_units_1} (identical results)")

# Check calibrated values are physically meaningful
import polars as pl
df_cal = pl.from_arrow(cal_then_norm)
temp_mask = (df_cal['sample_temperature'] >= 300) & (df_cal['sample_temperature'] <= 500)
peak_power = abs(df_cal['dsc_signal'][temp_mask]).max()
print(f"Peak heat flow: {peak_power:.2f} mW/mg (expected: 1-2 mW/mg for wood)")
```

**Key Benefits of DSC Calibration:**
- Converts raw sensor voltages to physically meaningful power units
- Enables quantitative comparison between different samples and instruments
- Essential for accurate heat capacity and enthalpy measurements
- Works seamlessly with baseline subtraction and mass normalization

### Plotting Data

```python
import matplotlib.pyplot as plt
import polars as pl
from pyngb import read_ngb

# Load data
table = read_ngb("sample.ngb-ss3")
df = pl.from_arrow(table)

# Simple temperature vs time plot
if 'time' in df.columns and 'sample_temperature' in df.columns:
    plt.figure(figsize=(10, 6))
    plt.plot(df['time'], df['sample_temperature'])
    plt.xlabel('Time (s)')
    plt.ylabel('Sample Temperature (°C)')
    plt.title('Sample Temperature Program')
    plt.grid(True)
    plt.show()

# Multiple plots
if 'dsc_signal' in df.columns:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Temperature plot
    ax1.plot(df['time'], df['sample_temperature'])
    ax1.set_ylabel('Sample Temperature (°C)')
    ax1.grid(True)

    # DSC plot
    ax2.plot(df['time'], df['dsc_signal'])
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('DSC Signal (µV)')
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
```

### DTG (Derivative Thermogravimetry) Analysis

```python
from pyngb.api.analysis import add_dtg, normalize_to_initial_mass
import matplotlib.pyplot as plt
import numpy as np

# Load data
table = read_ngb("sample.ngb-ss3")
df = pl.from_arrow(table)

if 'mass' in df.columns:
    # Method 1: Add DTG column directly to table (recommended)
    table_with_dtg = add_dtg(table, method="savgol", smooth="medium")
    df_with_dtg = pl.from_arrow(table_with_dtg)

    print(f"Added DTG column: {table_with_dtg.column_names[-1]}")

    # Method 2: Compare different smoothing levels
    table_strict = add_dtg(table, smooth="strict", column_name="dtg_strict")
    table_loose = add_dtg(table, smooth="loose", column_name="dtg_loose")

    # Combine for comparison
    df_strict = pl.from_arrow(table_strict)
    df_loose = pl.from_arrow(table_loose)

    # Create DTG comparison plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Mass loss plot
    ax1.plot(df_with_dtg['sample_temperature'], df_with_dtg['mass'], 'b-', linewidth=2, label='Mass')
    ax1.set_ylabel('Mass (mg)')
    ax1.set_title('Thermogravimetric Analysis')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # DTG plot with different smoothing
    ax2.plot(df_strict['sample_temperature'], df_strict['dtg_strict'], 'g-', alpha=0.7, label='Strict smoothing')
    ax2.plot(df_with_dtg['sample_temperature'], df_with_dtg['dtg'], 'r-', linewidth=2, label='Medium smoothing')
    ax2.plot(df_loose['sample_temperature'], df_loose['dtg_loose'], 'b-', alpha=0.7, label='Loose smoothing')
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('DTG (mg/min)')
    ax2.set_title('Derivative Thermogravimetry')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.show()

    # Print DTG summary using table data
    dtg_values = df_with_dtg['dtg'].to_numpy()
    temperature = df_with_dtg['sample_temperature'].to_numpy()
    mass = df_with_dtg['mass'].to_numpy()

    print(f"DTG Analysis Summary:")
    print(f"Maximum mass loss rate: {np.max(np.abs(dtg_values)):.3f} mg/min")
    print(f"Temperature at max rate: {temperature[np.argmax(np.abs(dtg_values))]:.1f}°C")
    print(f"Total mass loss: {mass[0] - mass[-1]:.3f} mg ({((mass[0] - mass[-1])/mass[0]*100):.1f}%)")

    # Normalize data for quantitative cross-sample comparison
    metadata, _ = read_ngb("sample.ngb-ss3", return_metadata=True)
    normalized_table = normalize_to_initial_mass(table)
    df_normalized = pl.from_arrow(normalized_table)

    print(f"\nNormalization Summary:")
    print(f"Sample mass from metadata: {metadata['sample_mass']:.1f} mg")
    print(f"Normalized mass range: {df_normalized['mass_normalized'].min():.6f} to {df_normalized['mass_normalized'].max():.6f}")
    print(f"Added columns: {[c for c in df_normalized.columns if '_normalized' in c]}")
```

### Batch Processing Multiple Files

```python
from pathlib import Path
from pyngb import read_ngb
import polars as pl

# Process all files in a directory
data_dir = Path("./sta_files")
results = []

for file in data_dir.glob("*.ngb-ss3"):
    try:
        metadata, data = read_ngb(str(file), return_metadata=True)

        # Extract key information
        result = {
            'filename': file.name,
            'sample_name': metadata.get('sample_name', 'Unknown'),
            'operator': metadata.get('operator', 'Unknown'),
            'data_points': data.num_rows,
            'columns': len(data.column_names),
            'file_size_mb': file.stat().st_size / 1024 / 1024
        }
        results.append(result)
        print(f"✓ Processed {file.name}")

    except Exception as e:
        print(f"✗ Error processing {file.name}: {e}")

# Create summary DataFrame
if results:
    summary_df = pl.DataFrame(results)
    print("\nProcessing Summary:")
    print(summary_df)

    # Save summary
    summary_df.write_csv("processing_summary.csv")
    print("Summary saved to processing_summary.csv")
```

### Data Analysis Workflow with DTG

```python
import polars as pl
from pyngb import read_ngb, dtg
import numpy as np

# Load multiple files and calculate DTG for each
files = ["sample1.ngb-ss3", "sample2.ngb-ss3", "sample3.ngb-ss3"]
analysis_results = []

for file in files:
    table = read_ngb(file)
    df = pl.from_arrow(table)

    # Calculate DTG if mass data is available
    if 'mass' in df.columns:
        time = df.get_column('time').to_numpy()
        mass = df.get_column('mass').to_numpy()
        temperature = df.get_column('sample_temperature').to_numpy()

        # One line DTG calculation with smart defaults
        dtg_values = dtg(time, mass)

        analysis_results.append({
            'file': file,
            'duration': time.max(),
            'temp_range': f"{temperature.min():.1f}-{temperature.max():.1f}°C",
            'mass_loss': mass[0] - mass[-1],
            'mass_loss_percent': ((mass[0] - mass[-1]) / mass[0]) * 100,
            'max_dtg_rate': np.max(np.abs(dtg_values)),
            'temp_at_max_rate': temperature[np.argmax(np.abs(dtg_values))]
        })

# Create summary DataFrame
if analysis_results:
    summary_df = pl.DataFrame(analysis_results)
    print("DTG Analysis Summary:")
    print(summary_df)

    # Save results
    summary_df.write_csv("dtg_analysis_summary.csv")
    print("Results saved to dtg_analysis_summary.csv")
```

## Tips and Best Practices

!!! tip "Performance Tips"
    - Use `read_ngb()` for large datasets - it returns PyArrow tables which are more memory efficient
    - Convert to Polars DataFrames for analysis - they're faster than Pandas for most operations
    - Use Parquet format for storing processed data - it's much faster to read/write than CSV
    - **New in v0.0.2**: Optimized conversions automatically reduce overhead when working with both PyArrow and Polars
    - Pass Polars DataFrames directly to validation functions for zero-conversion overhead

!!! warning "Common Pitfalls"
    - Always check if expected columns exist before using them
    - Handle exceptions when processing multiple files
    - Be aware of memory usage with very large datasets

!!! info "Next Steps"
    - Check the [DTG Analysis Guide](user-guide/dtg-analysis.md) for comprehensive DTG documentation
    - See the [API Reference](api.md) for detailed function documentation
    - Browse [Data Analysis](user-guide/data-analysis.md) for advanced multi-sample workflows
    - See [Development](development.md) for contributing guidelines
    - Browse the [troubleshooting guide](troubleshooting.md) for common issues
