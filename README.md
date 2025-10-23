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
- Processes 100,000 compositions in ~8 seconds
- Creates a beautiful scatter plot showing the relationship between speed of sound and density
- Exports all data to CSV for further analysis

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

Run with default settings (100,000 compositions):
```bash
python gas_composition_analysis.py
```

Run with custom number of samples:
```bash
python gas_composition_analysis.py -n 1000
```

Test the setup:
```bash
python test_gas_analysis.py
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
