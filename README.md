# Natural Gas Composition Analysis

This project generates random natural gas compositions and calculates their thermodynamic properties using the AGA8 equation of state via the [pvtlib](https://github.com/equinor/pvtlib/) library.

## Description

The script generates 100,000 different random natural gas compositions and calculates:
- Speed of sound (m/s)
- Density (kg/m³)

For a given pressure and temperature (default: 150 bara, 15°C).

## Features

- Generates realistic natural gas compositions with proper component distributions
- Uses GERG-2008 equation of state for accurate PVT calculations
- **Fast performance**: 100,000 compositions in ~7-8 seconds (sequential) or ~5 seconds (parallel)
- Creates beautiful scatter plots showing the relationship between speed of sound and density
- Exports all data to CSV for further analysis
- Includes performance benchmarking tools

## Performance

| Version | Time (100k samples) | Throughput | Use Case |
|---------|---------------------|------------|----------|
| Sequential | ~7-8 seconds | ~17,000 samples/sec | Simple, reliable, low memory |
| Parallel (16 cores) | ~5 seconds | ~20,000 samples/sec | Multi-core systems |
| **Optimized** | **~1.4 seconds** | **~72,000 samples/sec** | **Best choice for most users** |

**Recommendation:** Use the optimized version for 5x speedup!

For detailed performance analysis, see [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md)

For advanced Rust modifications, see [RUST_VECTORIZATION_GUIDE.md](RUST_VECTORIZATION_GUIDE.md)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Pvttest
```

2. Install dependencies:
```bash
pip install numpy scipy pandas matplotlib tqdm pyaga8
```

3. Clone the pvtlib library:
```bash
git clone https://github.com/equinor/pvtlib.git
```

## Usage

### Sequential Version (recommended for most use cases)
Run with default settings (100,000 compositions):
```bash
python gas_composition_analysis.py
```

Run with custom number of samples:
```bash
python gas_composition_analysis.py -n 1000
```

### Optimized Version (RECOMMENDED - 5x faster!)
Best performance without complexity:
```bash
python gas_composition_analysis_optimized.py
```

Custom sample size:
```bash
python gas_composition_analysis_optimized.py -n 1000
```

### Parallel Version (alternative approach)
Use all available CPU cores:
```bash
python gas_composition_analysis_parallel.py
```

Use specific number of cores:
```bash
python gas_composition_analysis_parallel.py -n 100000 -p 8
```

### Testing and Benchmarking
Test the setup:
```bash
python test_gas_analysis.py
```

Run performance benchmark:
```bash
python benchmark_performance.py
```

## Output

The script generates:
- `gas_composition_results.csv` - Complete dataset with compositions and calculated properties
- `speed_of_sound_vs_density.png` - Scatter plot visualization

## Results

For 100,000 random natural gas compositions at 150 bara and 15°C:

**Speed of Sound (m/s):**
- Mean: ~449 m/s
- Range: 421-466 m/s

**Density (kg/m³):**
- Mean: ~143 kg/m³
- Range: 128-179 kg/m³

The scatter plot reveals a clear inverse relationship between density and speed of sound in natural gas under these conditions.

## Gas Components

The analysis includes the following components:
- C1 (Methane) - typically 70-95%
- C2 (Ethane)
- C3 (Propane)
- iC4 (Isobutane)
- nC4 (n-Butane)
- iC5 (Isopentane)
- nC5 (n-Pentane)
- nC6 (Hexane)
- N2 (Nitrogen)
- CO2 (Carbon Dioxide)

## License

This project uses the pvtlib library which is licensed under the MIT License.
