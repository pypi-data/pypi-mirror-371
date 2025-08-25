# Data Analysis

Combine, transform, and analyze data from multiple runs using pyNGB's comprehensive analysis tools.

## Combine datasets

```python
import polars as pl
from pyngb import read_ngb

files = ["a.ngb-ss3", "b.ngb-ss3"]
frames = []
for f in files:
    t = read_ngb(f)
    df = pl.from_arrow(t).with_columns(pl.lit(f).alias("source_file"))
    frames.append(df)

combined = pl.concat(frames)
print(combined.shape)
```

## Quick stats

```python
if {'time', 'sample_temperature'} <= set(combined.columns):
    stats = combined.select([
        pl.col('time').max().alias('duration_s'),
        pl.col('sample_temperature').min().alias('min_temp_c'),
        pl.col('sample_temperature').max().alias('max_temp_c'),
    ])
    print(stats)
```

## Mass and DSC Normalization

Normalize thermal analysis data to initial sample mass for quantitative comparison across samples with different masses.

### Basic Normalization

```python
from pyngb import read_ngb
from pyngb.api.analysis import normalize_to_initial_mass
import polars as pl

# Load thermal analysis data
metadata, table = read_ngb("sample.ngb-ss3")

# Normalize mass and DSC to initial sample mass (in place)
normalized_table = normalize_to_initial_mass(table)
df = pl.from_arrow(normalized_table)

print(f"Sample mass from metadata: {metadata['sample_mass']:.3f} mg")
print(f"Columns (unchanged count): {normalized_table.column_names}")

# Check updated units after normalization
from pyngb.api.metadata import get_column_units
mass_units = get_column_units(normalized_table, 'mass')
dsc_units = get_column_units(normalized_table, 'dsc_signal')
print(f"Mass units after normalization: {mass_units}")  # mg/mg
print(f"DSC units after normalization: {dsc_units}")    # µV/mg

# Compare values - columns updated in place
print(f"Mass starts at: {df['mass'][0]:.6f} (fraction of initial mass)")
print(f"DSC starts at: {df['dsc_signal'][0]:.6f} (per mg of initial mass)")
```

### Cross-Sample Comparison

```python
# Normalize multiple samples for comparison
files = ["sample_5mg.ngb-ss3", "sample_12mg.ngb-ss3", "sample_8mg.ngb-ss3"]
normalized_data = []

for file_path in files:
    metadata, table = read_ngb(file_path)
    normalized_table = normalize_to_initial_mass(table)
    df = pl.from_arrow(normalized_table)

    normalized_data.append({
        'file': file_path,
        'initial_mass': metadata['sample_mass'],
        'df': df,
        'final_mass_fraction': df['mass'][-1]  # Fraction remaining (column updated in place)
    })

# Compare mass loss across samples
print("Sample Comparison (normalized to initial mass):")
for data in normalized_data:
    mass_loss_percent = (1 - data['final_mass_fraction']) * 100
    print(f"{data['file']}: {data['initial_mass']:.1f}mg → {mass_loss_percent:.1f}% mass loss")
```

### Quantitative DSC Analysis

```python
import matplotlib.pyplot as plt
import numpy as np

# Normalize and analyze DSC signals
plt.figure(figsize=(12, 8))

for i, data in enumerate(normalized_data):
    df = data['df']
    temperature = df['sample_temperature'].to_numpy()
    dsc_normalized = df['dsc_signal'].to_numpy()  # Column updated in place

    sample_name = data['file'].replace('.ngb-ss3', '')
    plt.plot(temperature, dsc_normalized,
             label=f'{sample_name} ({data["initial_mass"]:.1f}mg)',
             linewidth=2, alpha=0.8)

plt.xlabel('Temperature (°C)')
plt.ylabel('Normalized DSC Signal (µV/mg)')  # Updated units
plt.title('DSC Comparison - Normalized to Initial Sample Mass')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Calculate specific heat capacity peaks
for data in normalized_data:
    df = data['df']
    dsc_norm = df['dsc_signal'].to_numpy()  # Column updated in place
    temp = df['sample_temperature'].to_numpy()

    # Find peak DSC signal (endothermic events)
    peak_idx = np.argmin(dsc_norm)  # Most negative value
    peak_temp = temp[peak_idx]
    peak_intensity = abs(dsc_norm[peak_idx])

    print(f"{data['file']}: Peak at {peak_temp:.1f}°C, "
          f"Intensity: {peak_intensity:.3f} µV/mg")  # Updated units
```

## DSC Calibration

Convert raw DSC signals from microvolts (µV) to physically meaningful power units (mW) using instrument calibration constants stored in the metadata.

### Basic DSC Calibration

```python
from pyngb import read_ngb
from pyngb.api.analysis import apply_dsc_calibration
from pyngb.api.metadata import get_column_units, get_processing_history
import polars as pl

# Load thermal analysis data with calibration constants
table = read_ngb("sample.ngb-ss3")

# Check original DSC signal units
print(f"Original DSC units: {get_column_units(table, 'dsc_signal')}")  # µV

# Apply DSC calibration to convert µV to mW
calibrated_table = apply_dsc_calibration(table)

# Verify calibration results
print(f"Calibrated DSC units: {get_column_units(calibrated_table, 'dsc_signal')}")  # mW
print(f"Processing history: {get_processing_history(calibrated_table, 'dsc_signal')}")  # ['raw', 'calibration_applied']

# Convert to DataFrame for analysis
df = pl.from_arrow(calibrated_table)
print(f"DSC signal now represents actual heat flow: {df['dsc_signal'].mean():.3f} mW")
```

### Order-Independent Operations

DSC calibration works seamlessly with normalization in any order:

```python
# Method 1: Calibrate first, then normalize
cal_then_norm = apply_dsc_calibration(table)
cal_then_norm = normalize_to_initial_mass(cal_then_norm, columns=['dsc_signal'])
units1 = get_column_units(cal_then_norm, 'dsc_signal')  # mW/mg

# Method 2: Normalize first, then calibrate
norm_then_cal = normalize_to_initial_mass(table, columns=['dsc_signal'])
norm_then_cal = apply_dsc_calibration(norm_then_cal)
units2 = get_column_units(norm_then_cal, 'dsc_signal')  # mW/mg

print(f"Both methods result in same units: {units1} == {units2}")  # True

# Results are mathematically identical (within machine precision)
df1 = pl.from_arrow(cal_then_norm)
df2 = pl.from_arrow(norm_then_cal)
max_diff = (df1['dsc_signal'] - df2['dsc_signal']).abs().max()
print(f"Maximum difference: {max_diff:.2e}")  # ~1e-15 (machine precision)
```

### Complete Workflow with Baseline Subtraction

For quantitative DSC analysis, combine baseline subtraction, calibration, and normalization:

```python
from pyngb.baseline import subtract_baseline

# Complete DSC analysis workflow
sample_file = "sample.ngb-ss3"
baseline_file = "baseline.ngb-bs3"

# Step 1: Load original data
original_table = read_ngb(sample_file)

# Step 2: Apply baseline subtraction
baseline_df = subtract_baseline(
    sample_file=sample_file,
    baseline_file=baseline_file,
    dynamic_axis="sample_temperature"
)

# Convert back to PyArrow table (preserving metadata)
baseline_table = baseline_df.to_arrow()
# Preserve metadata from original (detailed implementation omitted for brevity)

# Step 3: Apply DSC calibration (µV → mW)
calibrated_table = apply_dsc_calibration(baseline_table)

# Step 4: Normalize to sample mass (mW → mW/mg)
final_table = normalize_to_initial_mass(calibrated_table, columns=['dsc_signal'])

# Check final result
final_units = get_column_units(final_table, 'dsc_signal')
final_history = get_processing_history(final_table, 'dsc_signal')

print(f"Final DSC units: {final_units}")  # mW/mg
print(f"Complete processing history: {final_history}")
# ['raw', 'baseline_subtracted', 'calibration_applied', 'normalized']

# Analyze calibrated results
df_final = pl.from_arrow(final_table)
dsc_calibrated = df_final['dsc_signal'].to_numpy()
temperature = df_final['sample_temperature'].to_numpy()

# Find peak heat flow (most exothermic event)
peak_idx = np.argmin(dsc_calibrated)
peak_temp = temperature[peak_idx]
peak_power = abs(dsc_calibrated[peak_idx])

print(f"Peak analysis:")
print(f"  Temperature: {peak_temp:.1f}°C")
print(f"  Heat flow: {peak_power:.2f} mW/mg")
print(f"  Expected for wood pyrolysis: 1.0-1.4 mW/mg ✓")
```

### Multi-Sample DSC Comparison

Compare calibrated DSC signals across multiple samples:

```python
import matplotlib.pyplot as plt

# Process multiple samples with complete calibration workflow
files = ["oak.ngb-ss3", "pine.ngb-ss3", "birch.ngb-ss3"]
baseline_files = ["oak_baseline.ngb-bs3", "pine_baseline.ngb-bs3", "birch_baseline.ngb-bs3"]

calibrated_samples = []

for sample_file, baseline_file in zip(files, baseline_files):
    # Apply complete workflow
    original = read_ngb(sample_file)
    baseline_df = subtract_baseline(sample_file, baseline_file, "sample_temperature")
    baseline_table = baseline_df.to_arrow()  # Simplified - preserve metadata as needed
    calibrated = apply_dsc_calibration(baseline_table)
    final = normalize_to_initial_mass(calibrated, columns=['dsc_signal'])

    # Store results
    df = pl.from_arrow(final)
    calibrated_samples.append({
        'name': sample_file.replace('.ngb-ss3', ''),
        'temperature': df['sample_temperature'].to_numpy(),
        'dsc_mw_per_mg': df['dsc_signal'].to_numpy(),
        'sample_mass': json.loads(original.schema.metadata[b"file_metadata"].decode())['sample_mass']
    })

# Plot calibrated DSC comparison
plt.figure(figsize=(12, 8))
colors = ['blue', 'red', 'green', 'orange', 'purple']

for i, sample in enumerate(calibrated_samples):
    plt.plot(sample['temperature'], sample['dsc_mw_per_mg'],
             label=f"{sample['name']} ({sample['sample_mass']:.1f}mg)",
             color=colors[i % len(colors)], linewidth=2)

plt.xlabel('Temperature (°C)')
plt.ylabel('Heat Flow (mW/mg)')
plt.title('Calibrated DSC Comparison - Mass Normalized')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Quantitative peak analysis
print("\nCalibrated Peak Analysis:")
for sample in calibrated_samples:
    # Find pyrolysis peak (usually most exothermic)
    temp_mask = (sample['temperature'] >= 300) & (sample['temperature'] <= 500)
    if temp_mask.sum() > 0:
        peak_idx = np.argmin(sample['dsc_mw_per_mg'][temp_mask])
        peak_temp = sample['temperature'][temp_mask][peak_idx]
        peak_power = abs(sample['dsc_mw_per_mg'][temp_mask][peak_idx])

        print(f"{sample['name']:12}: {peak_temp:6.1f}°C, {peak_power:6.2f} mW/mg")
```

### Calibration Validation

Verify calibration results are physically meaningful:

```python
def validate_dsc_calibration(calibrated_table, sample_type="wood"):
    """Validate DSC calibration results against expected ranges."""
    df = pl.from_arrow(calibrated_table)

    # Check units
    units = get_column_units(calibrated_table, 'dsc_signal')
    if 'mW' not in units:
        print("❌ Warning: DSC units should contain 'mW'")
        return False

    # Check calibration flag
    from pyngb.util import get_column_metadata
    metadata = get_column_metadata(calibrated_table, 'dsc_signal')
    if not metadata.get('calibration_applied', False):
        print("❌ Warning: Calibration flag not set")
        return False

    # Check magnitude for common materials
    dsc_values = df['dsc_signal'].to_numpy()
    temp_values = df['sample_temperature'].to_numpy()

    # Expected ranges for different materials (mW/mg)
    expected_ranges = {
        'wood': (0.5, 2.0),
        'polymer': (0.1, 1.0),
        'pharmaceutical': (0.05, 0.5),
        'metal': (0.01, 0.1)
    }

    if sample_type in expected_ranges:
        expected_min, expected_max = expected_ranges[sample_type]

        # Find peak in typical decomposition range
        decomp_mask = (temp_values >= 200) & (temp_values <= 600)
        if decomp_mask.sum() > 0:
            peak_magnitude = abs(dsc_values[decomp_mask]).max()

            if expected_min <= peak_magnitude <= expected_max:
                print(f"✓ Peak magnitude {peak_magnitude:.2f} mW/mg is within expected range for {sample_type}")
                return True
            else:
                print(f"⚠️  Peak magnitude {peak_magnitude:.2f} mW/mg outside expected range {expected_min}-{expected_max} for {sample_type}")
                return False

    print(f"✓ Calibration appears valid (units: {units})")
    return True

# Validate calibration results
for sample in calibrated_samples:
    sample_table = calibrated_samples[0]  # Use first sample as example
    is_valid = validate_dsc_calibration(final_table, sample_type="wood")
    if not is_valid:
        print(f"Consider checking calibration constants or sample type")
```

## DTG Analysis on Multiple Datasets

### Batch DTG Calculation

```python
from pyngb import dtg
import numpy as np
import matplotlib.pyplot as plt

# Calculate DTG for each file - simplified workflow
files = ["sample1.ngb-ss3", "sample2.ngb-ss3", "sample3.ngb-ss3"]
dtg_results = []

for file_path in files:
    table = read_ngb(file_path)
    df = pl.from_arrow(table)

    # Convert to numpy arrays
    time = df.get_column('time').to_numpy()
    mass = df.get_column('mass').to_numpy()
    temperature = df.get_column('sample_temperature').to_numpy()

    # Calculate DTG - one line, perfect defaults
    dtg_values = dtg(time, mass)

    # Store results
    dtg_results.append({
        'file': file_path,
        'time': time,
        'temperature': temperature,
        'mass': mass,
        'dtg': dtg_values,
        'max_rate': np.max(np.abs(dtg_values)),
        'temp_at_max_rate': temperature[np.argmax(np.abs(dtg_values))]
    })

# Print summary
for result in dtg_results:
    print(f"{result['file']}: Max rate = {result['max_rate']:.3f} mg/min "
          f"at {result['temp_at_max_rate']:.1f}°C")
```

### Comparative DTG Plotting

```python
# Plot all DTG curves together
plt.figure(figsize=(12, 8))

colors = ['blue', 'red', 'green', 'orange', 'purple']

for i, result in enumerate(dtg_results):
    color = colors[i % len(colors)]
    sample_name = result['file'].replace('.ngb-ss3', '')

    plt.plot(result['temperature'], result['dtg'],
             label=f'{sample_name}', color=color, linewidth=2)

plt.xlabel('Temperature (°C)')
plt.ylabel('DTG (mg/min)')
plt.title('DTG Comparison Across Samples')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Create subplot for individual analysis
fig, axes = plt.subplots(len(dtg_results), 1, figsize=(12, 4*len(dtg_results)))
if len(dtg_results) == 1:
    axes = [axes]

for i, result in enumerate(dtg_results):
    ax = axes[i]
    sample_name = result['file'].replace('.ngb-ss3', '')

    # Plot mass and DTG
    ax2 = ax.twinx()

    line1 = ax.plot(result['temperature'], result['mass'], 'b-', linewidth=2, label='Mass')
    line2 = ax2.plot(result['temperature'], result['dtg'], 'r-', linewidth=2, label='DTG')

    ax.set_ylabel('Mass (mg)', color='b')
    ax2.set_ylabel('DTG (mg/min)', color='r')
    ax.set_xlabel('Temperature (°C)')
    ax.set_title(f'{sample_name} - Mass Loss and DTG')

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper right')

plt.tight_layout()
plt.show()
```

### Statistical Analysis of DTG Data

```python
import pandas as pd
from scipy import stats

# Create summary statistics DataFrame
summary_data = []
for result in dtg_results:
    summary_data.append({
        'file': result['file'].replace('.ngb-ss3', ''),
        'max_dtg_rate': result['max_rate'],
        'temp_at_max_rate': result['temp_at_max_rate'],
        'total_mass_loss': result['mass'][0] - result['mass'][-1],
        'mass_loss_percent': ((result['mass'][0] - result['mass'][-1]) / result['mass'][0]) * 100,
        'dtg_std': np.std(result['dtg']),
        'dtg_mean_abs': np.mean(np.abs(result['dtg']))
    })

summary_df = pd.DataFrame(summary_data)
print("\nDTG Analysis Summary:")
print(summary_df.round(3))

# Statistical comparisons
if len(summary_data) > 1:
    print("\nStatistical Analysis:")
    print(f"Max rate range: {summary_df['max_dtg_rate'].min():.3f} - {summary_df['max_dtg_rate'].max():.3f} mg/min")
    print(f"Temperature at max rate range: {summary_df['temp_at_max_rate'].min():.1f} - {summary_df['temp_at_max_rate'].max():.1f}°C")
    print(f"Mass loss range: {summary_df['mass_loss_percent'].min():.1f} - {summary_df['mass_loss_percent'].max():.1f}%")

    # Correlation analysis
    if len(summary_data) >= 3:
        corr_coef, p_value = stats.pearsonr(summary_df['max_dtg_rate'], summary_df['temp_at_max_rate'])
        print(f"Correlation (max rate vs temperature): r = {corr_coef:.3f}, p = {p_value:.3f}")
```

### Advanced Multi-Sample Analysis

```python
# Compare different smoothing levels across samples
smoothing_levels = ["strict", "medium", "loose"]
smoothing_analysis = []

for result in dtg_results:
    sample_analysis = {'file': result['file']}

    # Calculate DTG with each smoothing level
    for level in smoothing_levels:
        dtg_smooth = dtg(result['time'], result['mass'], smooth=level)
        sample_analysis[f'max_rate_{level}'] = np.max(np.abs(dtg_smooth))
        sample_analysis[f'std_{level}'] = np.std(dtg_smooth)

    smoothing_analysis.append(sample_analysis)

# Create comparison DataFrame
comparison_df = pd.DataFrame(smoothing_analysis)
print("\nSmoothing Level Comparison:")
print(comparison_df.round(3))

# Recommend best smoothing for each sample
print("\nSmoothing Recommendations:")
for analysis in smoothing_analysis:
    file_name = analysis['file']

    # Simple heuristic: if std varies significantly, recommend medium
    std_variation = (analysis['std_loose'] - analysis['std_strict']) / analysis['std_strict']

    if std_variation > 0.5:
        recommended = "medium"  # High variation, use balanced smoothing
    elif analysis['std_strict'] < 0.1:
        recommended = "strict"  # Low noise, preserve features
    else:
        recommended = "loose"   # Noisy data, smooth more

    print(f"{file_name}: {recommended} (std variation: {std_variation:.1%})")
```

## Peak Detection and Characterization

```python
from scipy.signal import find_peaks
from scipy.integrate import trapz

def characterize_dtg_peaks(temperature, dtg, min_height=0.01, min_distance=20):
    """Characterize peaks in DTG data."""
    # Find peaks (looking for negative values, so invert)
    peaks, properties = find_peaks(-dtg, height=min_height, distance=min_distance)

    peak_data = []
    for i, peak_idx in enumerate(peaks):
        peak_temp = temperature[peak_idx]
        peak_rate = -dtg[peak_idx]  # Convert back to negative

        # Find peak boundaries (where rate returns to ~10% of peak height)
        threshold = abs(peak_rate * 0.1)

        # Find left boundary
        left_idx = peak_idx
        while left_idx > 0 and abs(dtg[left_idx]) > threshold:
            left_idx -= 1

        # Find right boundary
        right_idx = peak_idx
        while right_idx < len(dtg) - 1 and abs(dtg[right_idx]) > threshold:
            right_idx += 1

        # Calculate peak area (mass lost in this peak)
        peak_area = abs(trapz(dtg[left_idx:right_idx], temperature[left_idx:right_idx]))

        peak_data.append({
            'peak_number': i + 1,
            'temperature': peak_temp,
            'rate': abs(peak_rate),
            'temp_start': temperature[left_idx],
            'temp_end': temperature[right_idx],
            'temp_width': temperature[right_idx] - temperature[left_idx],
            'area': peak_area
        })

    return peak_data

# Apply peak detection to all samples
all_peaks = []
for result in dtg_results:
    # Use the pre-calculated DTG values
    peaks = characterize_dtg_peaks(result['temperature'], result['dtg'])
    sample_name = result['file'].replace('.ngb-ss3', '')

    print(f"\n{sample_name} - Detected Peaks:")
    for peak in peaks:
        print(f"  Peak {peak['peak_number']}: {peak['temperature']:.1f}°C, "
              f"Rate: {peak['rate']:.3f} mg/min, Width: {peak['temp_width']:.1f}°C")

        # Add sample identifier
        peak['sample'] = sample_name
        all_peaks.append(peak)

# Create summary of all peaks
if all_peaks:
    peaks_df = pd.DataFrame(all_peaks)

    print("\nPeak Summary Across All Samples:")
    print(peaks_df[['sample', 'peak_number', 'temperature', 'rate', 'temp_width', 'area']].round(2))

    # Group by peak number to compare similar decomposition events
    if len(set(peaks_df['peak_number'])) > 1:
        print("\nPeak Comparison by Peak Number:")
        for peak_num in sorted(peaks_df['peak_number'].unique()):
            peak_group = peaks_df[peaks_df['peak_number'] == peak_num]
            if len(peak_group) > 1:
                print(f"\nPeak {peak_num}:")
                print(f"  Temperature range: {peak_group['temperature'].min():.1f} - {peak_group['temperature'].max():.1f}°C")
                print(f"  Rate range: {peak_group['rate'].min():.3f} - {peak_group['rate'].max():.3f} mg/min")
                print(f"  Width range: {peak_group['temp_width'].min():.1f} - {peak_group['temp_width'].max():.1f}°C")
```

## Export and Visualization

```python
# Export analysis results
def export_dtg_analysis(dtg_results, output_dir="./analysis_results/"):
    """Export DTG analysis results to files."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Export individual DTG data
    for result in dtg_results:
        sample_name = result['file'].replace('.ngb-ss3', '')

        # Create DataFrame with all data
        export_df = pl.DataFrame({
            'time_s': result['time'],
            'temperature_c': result['temperature'],
            'mass_mg': result['mass'],
            'dtg_mg_per_min': result['dtg']
        })

        # Export to CSV
        export_df.write_csv(f"{output_dir}{sample_name}_dtg_data.csv")

        # Export to Parquet
        export_df.write_parquet(f"{output_dir}{sample_name}_dtg_data.parquet")

    # Export summary statistics
    if 'summary_df' in locals():
        summary_df.to_csv(f"{output_dir}dtg_summary_statistics.csv", index=False)

    # Export peak data
    if 'peaks_df' in locals():
        peaks_df.to_csv(f"{output_dir}detected_peaks.csv", index=False)

    print(f"Analysis results exported to {output_dir}")

# Run export
export_dtg_analysis(dtg_results)

# Create comprehensive analysis report
def create_analysis_report(dtg_results, output_file="dtg_analysis_report.txt"):
    """Create a comprehensive text report of DTG analysis."""
    with open(output_file, 'w') as f:
        f.write("DTG ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Number of Samples: {len(dtg_results)}\n\n")

        for i, result in enumerate(dtg_results, 1):
            sample_name = result['file'].replace('.ngb-ss3', '')
            f.write(f"SAMPLE {i}: {sample_name}\n")
            f.write("-" * 30 + "\n")
            f.write(f"Temperature range: {result['temperature'].min():.1f} - {result['temperature'].max():.1f}°C\n")
            f.write(f"Initial mass: {result['mass'][0]:.3f} mg\n")
            f.write(f"Final mass: {result['mass'][-1]:.3f} mg\n")
            f.write(f"Total mass loss: {result['mass'][0] - result['mass'][-1]:.3f} mg\n")
            f.write(f"Mass loss percentage: {((result['mass'][0] - result['mass'][-1]) / result['mass'][0]) * 100:.1f}%\n")
            f.write(f"Maximum DTG rate: {result['max_rate']:.3f} mg/min\n")
            f.write(f"Temperature at max rate: {result['temp_at_max_rate']:.1f}°C\n\n")

        f.write("COMPARATIVE ANALYSIS\n")
        f.write("-" * 30 + "\n")
        if len(dtg_results) > 1:
            all_max_rates = [r['max_rate'] for r in dtg_results]
            all_max_temps = [r['temp_at_max_rate'] for r in dtg_results]
            f.write(f"Max rate range: {min(all_max_rates):.3f} - {max(all_max_rates):.3f} mg/min\n")
            f.write(f"Temp at max rate range: {min(all_max_temps):.1f} - {max(all_max_temps):.1f}°C\n")
            f.write(f"Max rate std dev: {np.std(all_max_rates):.3f} mg/min\n")
        else:
            f.write("Only one sample analyzed - no comparative statistics available.\n")

    print(f"Analysis report saved to {output_file}")

create_analysis_report(dtg_results)
```

## Integration with Validation

```python
from pyngb.validation import QualityChecker

# Validate all datasets before DTG analysis
validation_results = []

for file_path in files:
    table = read_ngb(file_path)
    df = pl.from_arrow(table)

    # Perform validation
    checker = QualityChecker(df)
    result = checker.full_validation()

    validation_results.append({
        'file': file_path,
        'is_valid': result.is_valid,
        'errors': result.summary()['error_count'],
        'warnings': result.summary()['warning_count']
    })

    # Print validation summary
    print(f"{file_path}: Valid={result.is_valid}, Errors={result.summary()['error_count']}, Warnings={result.summary()['warning_count']}")

    if not result.is_valid:
        print(f"  Issues: {result.report()}")

# Only proceed with DTG analysis for valid files
valid_files = [v['file'] for v in validation_results if v['is_valid']]
print(f"\nProceeding with DTG analysis for {len(valid_files)} valid files out of {len(files)} total.")
```
