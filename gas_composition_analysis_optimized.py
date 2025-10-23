"""
Natural Gas Composition Analysis - OPTIMIZED VERSION
Python-side optimizations to minimize FFI overhead
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyaga8
import time

# Set random seed for reproducibility
np.random.seed(42)


def generate_random_gas_composition_array(n_samples):
    """
    Generate random natural gas compositions as numpy arrays (faster than dict creation).
    Returns array of shape (n_samples, 10) for the 10 components.
    """
    # Methane (70-95%)
    c1 = np.random.uniform(0.70, 0.95, n_samples)
    remaining = 1.0 - c1

    # Other components
    c2 = np.random.uniform(0, 0.15, n_samples) * remaining
    c3 = np.random.uniform(0, 0.08, n_samples) * remaining
    ic4 = np.random.uniform(0, 0.03, n_samples) * remaining
    nc4 = np.random.uniform(0, 0.03, n_samples) * remaining
    ic5 = np.random.uniform(0, 0.01, n_samples) * remaining
    nc5 = np.random.uniform(0, 0.01, n_samples) * remaining
    nc6 = np.random.uniform(0, 0.005, n_samples) * remaining
    n2 = np.random.uniform(0, 0.10, n_samples) * remaining
    co2 = np.random.uniform(0, 0.10, n_samples) * remaining

    # Stack and normalize
    compositions = np.column_stack([c1, c2, c3, ic4, nc4, ic5, nc5, nc6, n2, co2])
    compositions = compositions / compositions.sum(axis=1, keepdims=True)

    return compositions


def calculate_batch_optimized(compositions_array, pressure, temperature):
    """
    Optimized batch calculation using pre-created pyaga8 objects.

    Optimizations:
    1. Reuse single AGA8 instance
    2. Reuse single Composition object
    3. Pre-allocate result arrays
    4. Minimize Python object creation
    """
    n_samples = compositions_array.shape[0]

    # Pre-allocate result arrays
    speed_of_sound = np.zeros(n_samples)
    density = np.zeros(n_samples)

    # Create reusable objects (avoid recreation overhead)
    aga8 = pyaga8.Gerg2008()
    comp = pyaga8.Composition()

    # Set constant P and T once
    aga8.pressure = pressure
    aga8.temperature = temperature

    # Process each composition
    for i in range(n_samples):
        # Update composition object (faster than creating new dict)
        comp.methane = compositions_array[i, 0]
        comp.ethane = compositions_array[i, 1]
        comp.propane = compositions_array[i, 2]
        comp.isobutane = compositions_array[i, 3]
        comp.n_butane = compositions_array[i, 4]
        comp.isopentane = compositions_array[i, 5]
        comp.n_pentane = compositions_array[i, 6]
        comp.hexane = compositions_array[i, 7]
        comp.nitrogen = compositions_array[i, 8]
        comp.carbon_dioxide = compositions_array[i, 9]

        # Calculate (pressure and temperature already set)
        aga8.set_composition(comp)
        aga8.calc_density(0)
        aga8.calc_properties()

        # Extract results
        speed_of_sound[i] = aga8.w
        density[i] = aga8.d * aga8.mm  # Convert molar density to mass density

    return speed_of_sound, density, compositions_array


def main(n_samples=100000):
    """Main function with optimized processing."""

    print("=" * 70)
    print("Natural Gas Composition Analysis - OPTIMIZED VERSION")
    print("=" * 70)
    print(f"Generating {n_samples:,} random natural gas compositions...")
    print(f"Operating conditions: P = 150 bara, T = 15°C")
    print(f"Optimizations: Object reuse, numpy arrays, minimal Python overhead")
    print("=" * 70)

    pressure = 150 * 100  # Convert to kPa
    temperature = 15 + 273.15  # Convert to K

    # Generate compositions
    print("\nGenerating compositions...")
    gen_start = time.time()
    compositions_array = generate_random_gas_composition_array(n_samples)
    gen_time = time.time() - gen_start
    print(f"Generated {n_samples:,} compositions in {gen_time:.2f} seconds")

    # Calculate properties
    print("\nCalculating properties (optimized)...")
    calc_start = time.time()
    speed_of_sound, density, comps = calculate_batch_optimized(
        compositions_array, pressure, temperature
    )
    calc_time = time.time() - calc_start
    total_time = time.time() - gen_start

    print(f"Calculated properties for {n_samples:,} compositions in {calc_time:.2f} seconds")

    # Create DataFrame
    component_names = ['C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'N2', 'CO2']
    df_compositions = pd.DataFrame(comps, columns=component_names)
    df_properties = pd.DataFrame({
        'Speed_of_Sound_m_s': speed_of_sound,
        'Density_kg_m3': density
    })
    df_results = pd.concat([df_compositions, df_properties], axis=1)

    # Save to CSV
    output_file = 'gas_composition_results_optimized.csv'
    df_results.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

    # Print summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"\nSpeed of Sound (m/s):")
    print(f"  Mean:   {np.mean(speed_of_sound):.2f}")
    print(f"  Std:    {np.std(speed_of_sound):.2f}")
    print(f"  Min:    {np.min(speed_of_sound):.2f}")
    print(f"  Max:    {np.max(speed_of_sound):.2f}")

    print(f"\nDensity (kg/m³):")
    print(f"  Mean:   {np.mean(density):.2f}")
    print(f"  Std:    {np.std(density):.2f}")
    print(f"  Min:    {np.min(density):.2f}")
    print(f"  Max:    {np.max(density):.2f}")

    # Performance metrics
    print("\n" + "=" * 70)
    print("PERFORMANCE METRICS")
    print("=" * 70)
    print(f"\nComposition generation: {gen_time:.2f} seconds ({gen_time/total_time*100:.1f}%)")
    print(f"AGA8 calculations: {calc_time:.2f} seconds ({calc_time/total_time*100:.1f}%)")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {n_samples/total_time:,.0f} samples/second")
    print(f"Per-sample time: {total_time/n_samples*1000:.3f} ms")

    # Create scatter plot
    print("\n" + "=" * 70)
    print("Creating scatter plot...")
    print("=" * 70)

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(density, speed_of_sound,
                         c=speed_of_sound,
                         cmap='viridis',
                         alpha=0.3,
                         s=1,
                         edgecolors='none')

    plt.xlabel('Density (kg/m³)', fontsize=12, fontweight='bold')
    plt.ylabel('Speed of Sound (m/s)', fontsize=12, fontweight='bold')
    plt.title(f'Speed of Sound vs Density for Natural Gas (Optimized)\n'
              f'P = 150 bara, T = 15°C (n = {n_samples:,} compositions, {total_time:.1f}s)',
              fontsize=14, fontweight='bold')

    cbar = plt.colorbar(scatter, label='Speed of Sound (m/s)')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()

    plot_file = 'speed_of_sound_vs_density_optimized.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {plot_file}")
    plt.close()

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Natural Gas Composition Analysis (Optimized)')
    parser.add_argument('-n', '--samples', type=int, default=100000,
                       help='Number of random compositions to generate (default: 100000)')
    args = parser.parse_args()

    main(n_samples=args.samples)
