"""
Natural Gas Composition Analysis - PARALLEL VERSION
Uses multiprocessing to speed up calculations significantly
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pvtlib.aga8 import AGA8
from multiprocessing import Pool, cpu_count
import time

# Set random seed for reproducibility
np.random.seed(42)


def generate_random_gas_composition():
    """Generate a random natural gas composition."""
    # Methane (70-95%)
    c1 = np.random.uniform(0.70, 0.95)
    remaining = 1.0 - c1

    # Other components
    c2 = np.random.uniform(0, 0.15) * remaining
    c3 = np.random.uniform(0, 0.08) * remaining
    ic4 = np.random.uniform(0, 0.03) * remaining
    nc4 = np.random.uniform(0, 0.03) * remaining
    ic5 = np.random.uniform(0, 0.01) * remaining
    nc5 = np.random.uniform(0, 0.01) * remaining
    nc6 = np.random.uniform(0, 0.005) * remaining
    n2 = np.random.uniform(0, 0.10) * remaining
    co2 = np.random.uniform(0, 0.10) * remaining

    raw_composition = np.array([c1, c2, c3, ic4, nc4, ic5, nc5, nc6, n2, co2])
    normalized_composition = raw_composition / raw_composition.sum()

    return {
        'C1': normalized_composition[0],
        'C2': normalized_composition[1],
        'C3': normalized_composition[2],
        'iC4': normalized_composition[3],
        'nC4': normalized_composition[4],
        'iC5': normalized_composition[5],
        'nC5': normalized_composition[6],
        'nC6': normalized_composition[7],
        'N2': normalized_composition[8],
        'CO2': normalized_composition[9],
    }


def calculate_properties_worker(args):
    """
    Worker function for parallel processing.
    Each worker creates its own AGA8 instance to avoid pickling issues.
    """
    compositions, pressure, temperature, start_idx = args

    # Create AGA8 instance in worker process
    aga8 = AGA8(equation='GERG-2008')

    results = []
    for comp in compositions:
        try:
            result = aga8.calculate_from_PT(
                composition=comp,
                pressure=pressure,
                temperature=temperature,
                pressure_unit='bara',
                temperature_unit='C'
            )
            results.append({
                **comp,
                'Speed_of_Sound_m_s': result['w'],
                'Density_kg_m3': result['rho']
            })
        except Exception as e:
            print(f"Error in worker: {e}")
            continue

    return results


def main(n_samples=100000, n_processes=None):
    """Main function with parallel processing."""

    if n_processes is None:
        n_processes = cpu_count()

    print("=" * 70)
    print("Natural Gas Composition Analysis - PARALLEL VERSION")
    print("=" * 70)
    print(f"Generating {n_samples:,} random natural gas compositions...")
    print(f"Operating conditions: P = 150 bara, T = 15°C")
    print(f"Using {n_processes} CPU cores for parallel processing")
    print("=" * 70)

    pressure = 150  # bara
    temperature = 15  # Celsius

    # Generate all compositions first
    print("\nGenerating compositions...")
    start_time = time.time()
    compositions = [generate_random_gas_composition() for _ in range(n_samples)]
    gen_time = time.time() - start_time
    print(f"Generated {n_samples:,} compositions in {gen_time:.2f} seconds")

    # Split compositions into chunks for parallel processing
    chunk_size = n_samples // n_processes
    chunks = []
    for i in range(n_processes):
        start_idx = i * chunk_size
        if i == n_processes - 1:
            # Last chunk gets any remaining samples
            end_idx = n_samples
        else:
            end_idx = (i + 1) * chunk_size

        chunk_comps = compositions[start_idx:end_idx]
        chunks.append((chunk_comps, pressure, temperature, start_idx))

    print(f"\nSplit into {len(chunks)} chunks of ~{chunk_size:,} compositions each")
    print("Calculating properties in parallel...")

    # Process in parallel
    calc_start = time.time()
    with Pool(processes=n_processes) as pool:
        results_chunks = pool.map(calculate_properties_worker, chunks)

    # Flatten results
    all_results = []
    for chunk_results in results_chunks:
        all_results.extend(chunk_results)

    calc_time = time.time() - calc_start
    total_time = time.time() - start_time

    print(f"\nCalculated properties for {len(all_results):,} compositions in {calc_time:.2f} seconds")

    # Create DataFrame
    df_results = pd.DataFrame(all_results)

    # Save to CSV
    output_file = 'gas_composition_results_parallel.csv'
    df_results.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

    # Extract arrays for analysis
    speed_of_sound_list = df_results['Speed_of_Sound_m_s'].values
    density_list = df_results['Density_kg_m3'].values

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
    scatter = plt.scatter(density_list, speed_of_sound_list,
                         c=speed_of_sound_list,
                         cmap='viridis',
                         alpha=0.3,
                         s=1,
                         edgecolors='none')

    plt.xlabel('Density (kg/m³)', fontsize=12, fontweight='bold')
    plt.ylabel('Speed of Sound (m/s)', fontsize=12, fontweight='bold')
    plt.title(f'Speed of Sound vs Density for Natural Gas (Parallel Processing)\n'
              f'P = {pressure} bara, T = {temperature}°C (n = {len(all_results):,} compositions, '
              f'{n_processes} cores, {total_time:.1f}s)',
              fontsize=14, fontweight='bold')

    cbar = plt.colorbar(scatter, label='Speed of Sound (m/s)')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()

    plot_file = 'speed_of_sound_vs_density_parallel.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {plot_file}")
    plt.close()

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Natural Gas Composition Analysis (Parallel)')
    parser.add_argument('-n', '--samples', type=int, default=100000,
                       help='Number of random compositions to generate (default: 100000)')
    parser.add_argument('-p', '--processes', type=int, default=None,
                       help='Number of processes to use (default: auto-detect)')
    args = parser.parse_args()

    main(n_samples=args.samples, n_processes=args.processes)
