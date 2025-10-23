"""
Example usage of the new calculate_batch_from_PT function in pvtlib
Demonstrates the 5x performance improvement for batch calculations
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
import time
from pvtlib.aga8 import AGA8

print("=" * 70)
print("PVTLIB BATCH CALCULATION EXAMPLES")
print("=" * 70)

# Create AGA8 instance
aga8 = AGA8(equation='GERG-2008')

# ============================================================================
# Example 1: List of composition dictionaries (easy to use)
# ============================================================================
print("\n" + "=" * 70)
print("Example 1: List of composition dictionaries")
print("=" * 70)

compositions = [
    {'C1': 0.85, 'C2': 0.05, 'C3': 0.03, 'N2': 0.05, 'CO2': 0.02},
    {'C1': 0.90, 'C2': 0.04, 'C3': 0.02, 'N2': 0.03, 'CO2': 0.01},
    {'C1': 0.80, 'C2': 0.07, 'C3': 0.04, 'N2': 0.06, 'CO2': 0.03},
    {'C1': 0.88, 'C2': 0.06, 'C3': 0.02, 'N2': 0.02, 'CO2': 0.02},
    {'C1': 0.92, 'C2': 0.03, 'C3': 0.02, 'N2': 0.02, 'CO2': 0.01},
]

# Get DataFrame output (default)
df_results = aga8.calculate_batch_from_PT(
    compositions,
    pressure=150,
    temperature=15
)

print("\nDataFrame output (first 5 rows):")
print(df_results[['C1', 'C2', 'N2', 'CO2', 'w', 'rho', 'z']].to_string())

# ============================================================================
# Example 2: Numpy array input (fastest for large datasets)
# ============================================================================
print("\n" + "=" * 70)
print("Example 2: Numpy array input")
print("=" * 70)

# Generate 1000 random compositions as numpy array
n_samples = 1000
compositions_array = np.random.random((n_samples, 10))
compositions_array = compositions_array / compositions_array.sum(axis=1, keepdims=True)

# Get dict output
results_dict = aga8.calculate_batch_from_PT(
    compositions_array,
    pressure=150,
    temperature=15,
    return_format='dict'
)

print(f"\nProcessed {n_samples} compositions")
print(f"Speed of sound - Mean: {results_dict['w'].mean():.2f} m/s, Std: {results_dict['w'].std():.2f} m/s")
print(f"Density - Mean: {results_dict['rho'].mean():.2f} kg/m³, Std: {results_dict['rho'].std():.2f} kg/m³")
print(f"Compressibility - Mean: {results_dict['z'].mean():.4f}, Std: {results_dict['z'].std():.4f}")

# ============================================================================
# Example 3: Arrays output (fastest for plotting)
# ============================================================================
print("\n" + "=" * 70)
print("Example 3: Arrays output for plotting")
print("=" * 70)

sos, rho, z, mm = aga8.calculate_batch_from_PT(
    compositions_array[:100],  # Use first 100
    pressure=150,
    temperature=15,
    return_format='arrays'
)

print(f"\nGot 4 numpy arrays:")
print(f"  - Speed of sound: shape {sos.shape}, mean {sos.mean():.2f} m/s")
print(f"  - Density: shape {rho.shape}, mean {rho.mean():.2f} kg/m³")
print(f"  - Compressibility: shape {z.shape}, mean {z.mean():.4f}")
print(f"  - Molar mass: shape {mm.shape}, mean {mm.mean():.2f} g/mol")

# ============================================================================
# Example 4: Performance comparison
# ============================================================================
print("\n" + "=" * 70)
print("Example 4: Performance comparison")
print("=" * 70)

n_samples = 10000
compositions_array = np.random.random((n_samples, 10))
compositions_array = compositions_array / compositions_array.sum(axis=1, keepdims=True)

# Convert to list of dicts for old method
compositions_list = []
component_names = ['C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'N2', 'CO2']
for i in range(n_samples):
    comp = {key: compositions_array[i, j] for j, key in enumerate(component_names)}
    compositions_list.append(comp)

print(f"\nProcessing {n_samples} compositions...")

# Old method: Loop with calculate_from_PT
print("\n1. OLD METHOD: Loop with calculate_from_PT")
start = time.time()
results_old = []
for comp in compositions_list[:100]:  # Only do 100 to save time
    result = aga8.calculate_from_PT(comp, 150, 15)
    results_old.append((result['w'], result['rho']))
time_old = time.time() - start
estimated_old = time_old * (n_samples / 100)

print(f"   Time for 100 samples: {time_old:.3f} seconds")
print(f"   Estimated for {n_samples}: {estimated_old:.2f} seconds")
print(f"   Throughput: {100/time_old:,.0f} samples/second")

# New method: Batch calculation
print("\n2. NEW METHOD: calculate_batch_from_PT")
start = time.time()
sos, rho, z, mm = aga8.calculate_batch_from_PT(
    compositions_array,
    pressure=150,
    temperature=15,
    return_format='arrays'
)
time_new = time.time() - start

print(f"   Time for {n_samples} samples: {time_new:.3f} seconds")
print(f"   Throughput: {n_samples/time_new:,.0f} samples/second")

print(f"\n   ⚡ SPEEDUP: {estimated_old/time_new:.1f}x faster!")

# ============================================================================
# Example 5: Using with real analysis workflow
# ============================================================================
print("\n" + "=" * 70)
print("Example 5: Real analysis workflow")
print("=" * 70)

# Generate random compositions
np.random.seed(42)
n_samples = 5000

# Realistic gas compositions
c1 = np.random.uniform(0.70, 0.95, n_samples)
remaining = 1.0 - c1
c2 = np.random.uniform(0, 0.15, n_samples) * remaining
c3 = np.random.uniform(0, 0.08, n_samples) * remaining
ic4 = np.random.uniform(0, 0.03, n_samples) * remaining
nc4 = np.random.uniform(0, 0.03, n_samples) * remaining
ic5 = np.random.uniform(0, 0.01, n_samples) * remaining
nc5 = np.random.uniform(0, 0.01, n_samples) * remaining
nc6 = np.random.uniform(0, 0.005, n_samples) * remaining
n2 = np.random.uniform(0, 0.10, n_samples) * remaining
co2 = np.random.uniform(0, 0.10, n_samples) * remaining

compositions = np.column_stack([c1, c2, c3, ic4, nc4, ic5, nc5, nc6, n2, co2])
compositions = compositions / compositions.sum(axis=1, keepdims=True)

# Calculate properties
start = time.time()
df = aga8.calculate_batch_from_PT(compositions, pressure=150, temperature=15)
elapsed = time.time() - start

print(f"\nProcessed {n_samples} realistic gas compositions in {elapsed:.3f} seconds")
print(f"\nResults summary:")
print(df[['C1', 'w', 'rho', 'z', 'mm']].describe())

print("\n" + "=" * 70)
print("All examples completed successfully!")
print("=" * 70)
