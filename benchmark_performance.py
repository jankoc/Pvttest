"""
Performance benchmark for gas composition analysis
Analyzes where time is spent and whether Python loop is a bottleneck
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
import time
from pvtlib.aga8 import AGA8

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

    components = {
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

    return components


def benchmark_composition_generation(n_samples):
    """Benchmark just the composition generation."""
    start = time.time()

    compositions = []
    for i in range(n_samples):
        comp = generate_random_gas_composition()
        compositions.append(comp)

    elapsed = time.time() - start
    return elapsed, compositions


def benchmark_aga8_calculations(compositions, pressure, temperature):
    """Benchmark the AGA8 calculations."""
    aga8 = AGA8(equation='GERG-2008')

    start = time.time()

    results = []
    for comp in compositions:
        result = aga8.calculate_from_PT(
            composition=comp,
            pressure=pressure,
            temperature=temperature,
            pressure_unit='bara',
            temperature_unit='C'
        )
        results.append((result['w'], result['rho']))

    elapsed = time.time() - start
    return elapsed, results


def benchmark_aga8_single_call():
    """Benchmark a single AGA8 call to measure overhead."""
    aga8 = AGA8(equation='GERG-2008')

    composition = {
        'C1': 0.85, 'C2': 0.05, 'C3': 0.03, 'nC4': 0.01,
        'N2': 0.04, 'CO2': 0.02,
    }

    # Warm up
    for _ in range(10):
        aga8.calculate_from_PT(composition, 150, 15, 'bara', 'C')

    # Benchmark
    n_calls = 1000
    start = time.time()
    for _ in range(n_calls):
        aga8.calculate_from_PT(composition, 150, 15, 'bara', 'C')
    elapsed = time.time() - start

    return elapsed / n_calls


def main():
    print("=" * 70)
    print("PERFORMANCE BENCHMARK")
    print("=" * 70)

    # Test different sample sizes
    test_sizes = [100, 1000, 10000]

    for n_samples in test_sizes:
        print(f"\n{'='*70}")
        print(f"Testing with {n_samples:,} samples")
        print('='*70)

        # Benchmark composition generation
        gen_time, compositions = benchmark_composition_generation(n_samples)
        print(f"\n1. Composition Generation:")
        print(f"   Total time: {gen_time:.3f} seconds")
        print(f"   Per sample: {gen_time/n_samples*1000:.3f} ms")
        print(f"   Rate: {n_samples/gen_time:,.0f} compositions/second")

        # Benchmark AGA8 calculations
        calc_time, results = benchmark_aga8_calculations(compositions, 150, 15)
        print(f"\n2. AGA8 Calculations:")
        print(f"   Total time: {calc_time:.3f} seconds")
        print(f"   Per sample: {calc_time/n_samples*1000:.3f} ms")
        print(f"   Rate: {n_samples/calc_time:,.0f} calculations/second")

        # Total time
        total_time = gen_time + calc_time
        print(f"\n3. Total Pipeline:")
        print(f"   Total time: {total_time:.3f} seconds")
        print(f"   Per sample: {total_time/n_samples*1000:.3f} ms")
        print(f"   Rate: {n_samples/total_time:,.0f} samples/second")

        # Breakdown
        print(f"\n4. Time Breakdown:")
        print(f"   Composition generation: {gen_time/total_time*100:.1f}%")
        print(f"   AGA8 calculations: {calc_time/total_time*100:.1f}%")

        # Estimate for 100,000 samples
        estimated_100k = total_time * (100000 / n_samples)
        print(f"\n5. Estimated time for 100,000 samples: {estimated_100k:.1f} seconds")

    # Single call overhead
    print(f"\n{'='*70}")
    print("SINGLE CALL OVERHEAD ANALYSIS")
    print('='*70)

    single_call_time = benchmark_aga8_single_call()
    print(f"\nAverage time per AGA8 call: {single_call_time*1000:.3f} ms")
    print(f"Maximum theoretical throughput: {1/single_call_time:,.0f} calls/second")

    # Analysis
    print(f"\n{'='*70}")
    print("BOTTLENECK ANALYSIS")
    print('='*70)

    print("""
The main bottlenecks are:

1. **Python-Rust FFI Overhead**: Each call to calculate_from_PT() crosses the
   Python-Rust boundary, which has overhead from:
   - Python dictionary -> Rust struct conversion
   - Return value conversion (Rust -> Python)
   - Python GIL (Global Interpreter Lock) management

2. **Object Creation**: Creating Python dictionaries for each composition and
   result adds overhead.

3. **AGA8 Calculation**: The actual thermodynamic calculation in Rust is
   relatively fast, but still the dominant factor.

Potential optimizations:
- Vectorize: Modify pvtlib to accept arrays of compositions (would require
  changes to the underlying library)
- Parallel processing: Use multiprocessing to distribute work across CPU cores
- Cython/Numba: JIT-compile the Python loop
- Pre-allocate: Use numpy arrays instead of Python lists
""")

    # Test parallel processing potential
    print(f"\n{'='*70}")
    print("PARALLEL PROCESSING POTENTIAL")
    print('='*70)

    import multiprocessing
    n_cores = multiprocessing.cpu_count()
    print(f"\nAvailable CPU cores: {n_cores}")
    print(f"Theoretical speedup with {n_cores} cores: {n_cores}x")
    print(f"Estimated time for 100,000 samples with parallelization: {estimated_100k/n_cores:.1f} seconds")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
