"""
Natural Gas Composition Analysis
This script generates 100,000 random natural gas compositions and calculates
their speed of sound and density at specified pressure and temperature conditions
using the pvtlib library (AGA8 equation of state).
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pvtlib.aga8 import AGA8
from tqdm import tqdm

# Set random seed for reproducibility
np.random.seed(42)

def generate_random_gas_composition():
    """
    Generate a random natural gas composition with realistic component distributions.

    Returns:
        dict: Gas composition with component names as keys and mole fractions as values
    """
    # Define typical components in natural gas
    components = {
        'C1': 0,   # Methane (typically 70-95%)
        'C2': 0,   # Ethane
        'C3': 0,   # Propane
        'iC4': 0,  # Isobutane
        'nC4': 0,  # n-Butane
        'iC5': 0,  # Isopentane
        'nC5': 0,  # n-Pentane
        'nC6': 0,  # Hexane
        'N2': 0,   # Nitrogen
        'CO2': 0,  # Carbon dioxide
    }

    # Generate random values with different distributions for realistic compositions
    # Methane is the dominant component (70-95%)
    c1 = np.random.uniform(0.70, 0.95)

    # Remaining fraction to distribute among other components
    remaining = 1.0 - c1

    # Generate random fractions for other components
    # Heavier components typically have lower concentrations
    c2 = np.random.uniform(0, 0.15) * remaining
    c3 = np.random.uniform(0, 0.08) * remaining
    ic4 = np.random.uniform(0, 0.03) * remaining
    nc4 = np.random.uniform(0, 0.03) * remaining
    ic5 = np.random.uniform(0, 0.01) * remaining
    nc5 = np.random.uniform(0, 0.01) * remaining
    nc6 = np.random.uniform(0, 0.005) * remaining
    n2 = np.random.uniform(0, 0.10) * remaining
    co2 = np.random.uniform(0, 0.10) * remaining

    # Create composition array
    raw_composition = np.array([c1, c2, c3, ic4, nc4, ic5, nc5, nc6, n2, co2])

    # Normalize to ensure sum equals 1.0
    normalized_composition = raw_composition / raw_composition.sum()

    # Assign to components dictionary
    comp_keys = list(components.keys())
    for i, key in enumerate(comp_keys):
        components[key] = normalized_composition[i]

    return components


def calculate_gas_properties(composition, pressure, temperature):
    """
    Calculate gas properties using AGA8 equation of state.

    Parameters:
        composition (dict): Gas composition
        pressure (float): Pressure in bara
        temperature (float): Temperature in Celsius

    Returns:
        tuple: (speed_of_sound, density) or (None, None) if calculation fails
    """
    try:
        # Create AGA8 calculator (using GERG-2008 equation of state)
        aga8 = AGA8(equation='GERG-2008')

        # Calculate properties
        results = aga8.calculate_from_PT(
            composition=composition,
            pressure=pressure,
            temperature=temperature,
            pressure_unit='bara',
            temperature_unit='C'
        )

        # Extract speed of sound (m/s) and density (kg/m3)
        speed_of_sound = results['w']  # Speed of sound in m/s
        density = results['rho']  # Density in kg/m3

        return speed_of_sound, density

    except Exception as e:
        print(f"Error calculating properties: {e}")
        return None, None


def main(n_samples=100000):
    """Main function to generate compositions, calculate properties, and plot results."""

    print("=" * 70)
    print("Natural Gas Composition Analysis")
    print("=" * 70)
    print(f"Generating {n_samples:,} random natural gas compositions...")
    print(f"Operating conditions: P = 150 bara, T = 15°C")
    print("=" * 70)

    # Operating conditions
    pressure = 150  # bara
    temperature = 15  # Celsius

    # Lists to store results
    compositions_list = []
    speed_of_sound_list = []
    density_list = []

    # Generate compositions and calculate properties
    print("\nCalculating gas properties...")

    # Use tqdm for progress bar (if available, otherwise fall back to simple counter)
    try:
        for i in tqdm(range(n_samples), desc="Processing"):
            # Generate random composition
            composition = generate_random_gas_composition()

            # Calculate properties
            sos, rho = calculate_gas_properties(composition, pressure, temperature)

            if sos is not None and rho is not None:
                compositions_list.append(composition)
                speed_of_sound_list.append(sos)
                density_list.append(rho)
    except ImportError:
        # Fallback if tqdm is not available
        for i in range(n_samples):
            if (i + 1) % 10000 == 0:
                print(f"Processed {i + 1}/{n_samples} compositions...")

            composition = generate_random_gas_composition()
            sos, rho = calculate_gas_properties(composition, pressure, temperature)

            if sos is not None and rho is not None:
                compositions_list.append(composition)
                speed_of_sound_list.append(sos)
                density_list.append(rho)

    # Create DataFrame
    print(f"\nSuccessfully calculated properties for {len(speed_of_sound_list)} compositions")

    # Convert compositions to DataFrame
    df_compositions = pd.DataFrame(compositions_list)
    df_properties = pd.DataFrame({
        'Speed_of_Sound_m_s': speed_of_sound_list,
        'Density_kg_m3': density_list
    })

    # Combine into single DataFrame
    df_results = pd.concat([df_compositions, df_properties], axis=1)

    # Save to CSV
    output_file = 'gas_composition_results.csv'
    df_results.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

    # Print summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"\nSpeed of Sound (m/s):")
    print(f"  Mean:   {np.mean(speed_of_sound_list):.2f}")
    print(f"  Std:    {np.std(speed_of_sound_list):.2f}")
    print(f"  Min:    {np.min(speed_of_sound_list):.2f}")
    print(f"  Max:    {np.max(speed_of_sound_list):.2f}")

    print(f"\nDensity (kg/m³):")
    print(f"  Mean:   {np.mean(density_list):.2f}")
    print(f"  Std:    {np.std(density_list):.2f}")
    print(f"  Min:    {np.min(density_list):.2f}")
    print(f"  Max:    {np.max(density_list):.2f}")

    # Create scatter plot
    print("\n" + "=" * 70)
    print("Creating scatter plot...")
    print("=" * 70)

    plt.figure(figsize=(12, 8))

    # Create scatter plot with transparency and color gradient
    scatter = plt.scatter(density_list, speed_of_sound_list,
                         c=speed_of_sound_list,
                         cmap='viridis',
                         alpha=0.3,
                         s=1,
                         edgecolors='none')

    plt.xlabel('Density (kg/m³)', fontsize=12, fontweight='bold')
    plt.ylabel('Speed of Sound (m/s)', fontsize=12, fontweight='bold')
    plt.title(f'Speed of Sound vs Density for Natural Gas\nP = {pressure} bara, T = {temperature}°C (n = {len(speed_of_sound_list):,} compositions)',
              fontsize=14, fontweight='bold')

    # Add colorbar
    cbar = plt.colorbar(scatter, label='Speed of Sound (m/s)')

    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--')

    # Tight layout
    plt.tight_layout()

    # Save plot
    plot_file = 'speed_of_sound_vs_density.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {plot_file}")

    # Close plot to free memory
    plt.close()

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Parse command line arguments for number of samples
    import argparse
    parser = argparse.ArgumentParser(description='Natural Gas Composition Analysis')
    parser.add_argument('-n', '--samples', type=int, default=100000,
                       help='Number of random compositions to generate (default: 100000)')
    args = parser.parse_args()

    main(n_samples=args.samples)
