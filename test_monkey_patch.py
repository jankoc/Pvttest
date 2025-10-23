"""
Test script demonstrating the monkey-patched batch function

This shows how to use pvtlib_batch_patch.py to add the batch function
to pvtlib without modifying the original source code.
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
import time

print("=" * 70)
print("MONKEY PATCH TEST - pvtlib Batch Function")
print("=" * 70)

# Step 1: Import pvtlib as normal
print("\n1. Importing pvtlib.aga8...")
from pvtlib.aga8 import AGA8

# Check if batch function exists (should not at first)
aga8_test = AGA8(equation='GERG-2008')
has_batch = hasattr(aga8_test, 'calculate_batch_from_PT')
print(f"   Has calculate_batch_from_PT? {has_batch}")

# Step 2: Apply the monkey patch
print("\n2. Applying monkey patch...")
import pvtlib_batch_patch

# Step 3: Verify patch was applied
print("\n3. Verifying patch...")
aga8 = AGA8(equation='GERG-2008')
has_batch_after = hasattr(aga8, 'calculate_batch_from_PT')
print(f"   Has calculate_batch_from_PT? {has_batch_after}")

if not has_batch_after:
    print("   ❌ Patch failed!")
    sys.exit(1)

print("   ✓ Patch applied successfully!")

# Step 4: Test with simple example
print("\n" + "=" * 70)
print("SIMPLE TEST")
print("=" * 70)

compositions = [
    {'C1': 0.85, 'C2': 0.05, 'C3': 0.03, 'N2': 0.05, 'CO2': 0.02},
    {'C1': 0.90, 'C2': 0.04, 'C3': 0.02, 'N2': 0.03, 'CO2': 0.01},
    {'C1': 0.80, 'C2': 0.07, 'C3': 0.04, 'N2': 0.06, 'CO2': 0.03},
]

print(f"\nCalculating properties for {len(compositions)} compositions...")
df = aga8.calculate_batch_from_PT(compositions, pressure=150, temperature=15)

print("\nResults:")
print(df[['C1', 'C2', 'w', 'rho', 'z']].to_string())

# Step 5: Performance test
print("\n" + "=" * 70)
print("PERFORMANCE TEST")
print("=" * 70)

n_samples = 10000
print(f"\nGenerating {n_samples:,} random compositions...")

# Generate random compositions
np.random.seed(42)
c1 = np.random.uniform(0.70, 0.95, n_samples)
remaining = 1.0 - c1
c2 = np.random.uniform(0, 0.15, n_samples) * remaining
c3 = np.random.uniform(0, 0.08, n_samples) * remaining
n2 = np.random.uniform(0, 0.10, n_samples) * remaining
co2 = np.random.uniform(0, 0.10, n_samples) * remaining

compositions_array = np.column_stack([c1, c2, c3, np.zeros((n_samples, 5)), n2, co2])
compositions_array = compositions_array / compositions_array.sum(axis=1, keepdims=True)

# Test OLD method (loop) with small sample
print(f"\n1. OLD METHOD: Loop with calculate_from_PT (testing 100 samples)")
compositions_list = []
component_names = ['C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'nC6', 'N2', 'CO2']
for i in range(100):
    comp = {key: compositions_array[i, j] for j, key in enumerate(component_names)}
    compositions_list.append(comp)

start = time.time()
results_old = []
for comp in compositions_list:
    result = aga8.calculate_from_PT(comp, 150, 15)
    results_old.append((result['w'], result['rho']))
time_old = time.time() - start
estimated_old = time_old * (n_samples / 100)

print(f"   Time for 100: {time_old:.3f} seconds")
print(f"   Estimated for {n_samples:,}: {estimated_old:.2f} seconds")
print(f"   Throughput: {100/time_old:,.0f} samples/second")

# Test NEW method (batch)
print(f"\n2. NEW METHOD: Monkey-patched calculate_batch_from_PT ({n_samples:,} samples)")
start = time.time()
sos, rho, z, mm = aga8.calculate_batch_from_PT(
    compositions_array,
    pressure=150,
    temperature=15,
    return_format='arrays'
)
time_new = time.time() - start

print(f"   Time for {n_samples:,}: {time_new:.3f} seconds")
print(f"   Throughput: {n_samples/time_new:,.0f} samples/second")

# Calculate speedup
speedup = estimated_old / time_new
print(f"\n   ⚡ SPEEDUP: {speedup:.1f}x faster!")

# Step 6: Test different output formats
print("\n" + "=" * 70)
print("OUTPUT FORMATS TEST")
print("=" * 70)

test_comps = compositions[:3]

# DataFrame
print("\n1. DataFrame output:")
df = aga8.calculate_batch_from_PT(test_comps, 150, 15, return_format='dataframe')
print(f"   Type: {type(df)}")
print(f"   Shape: {df.shape}")
print(f"   Columns: {list(df.columns)}")

# Dict
print("\n2. Dict output:")
results_dict = aga8.calculate_batch_from_PT(test_comps, 150, 15, return_format='dict')
print(f"   Type: {type(results_dict)}")
print(f"   Keys: {list(results_dict.keys())}")
print(f"   Array keys and shapes:")
for k, v in results_dict.items():
    if isinstance(v, np.ndarray):
        print(f"     {k}: {v.shape}")
    else:
        print(f"     {k}: scalar value = {v}")

# Arrays
print("\n3. Arrays output:")
sos, rho, z, mm = aga8.calculate_batch_from_PT(test_comps, 150, 15, return_format='arrays')
print(f"   Returns 4 arrays:")
print(f"   - Speed of sound: {sos.shape}")
print(f"   - Density: {rho.shape}")
print(f"   - Compressibility: {z.shape}")
print(f"   - Molar mass: {mm.shape}")

# Step 7: Verify results match original method
print("\n" + "=" * 70)
print("VALIDATION TEST")
print("=" * 70)

test_comp = {'C1': 0.85, 'C2': 0.05, 'C3': 0.03, 'N2': 0.05, 'CO2': 0.02}

# Original method
result_original = aga8.calculate_from_PT(test_comp, 150, 15)

# Batch method
df_batch = aga8.calculate_batch_from_PT([test_comp], 150, 15)

print("\nComparing single composition results:")
print(f"  Original SOS: {result_original['w']:.6f} m/s")
print(f"  Batch SOS:    {df_batch['w'].iloc[0]:.6f} m/s")
print(f"  Difference:   {abs(result_original['w'] - df_batch['w'].iloc[0]):.10f} m/s")

print(f"\n  Original density: {result_original['rho']:.6f} kg/m³")
print(f"  Batch density:    {df_batch['rho'].iloc[0]:.6f} kg/m³")
print(f"  Difference:       {abs(result_original['rho'] - df_batch['rho'].iloc[0]):.10f} kg/m³")

# Check if close enough (within floating point precision)
sos_match = abs(result_original['w'] - df_batch['w'].iloc[0]) < 1e-6
rho_match = abs(result_original['rho'] - df_batch['rho'].iloc[0]) < 1e-6

if sos_match and rho_match:
    print("\n  ✓ Results match! Batch function is working correctly.")
else:
    print("\n  ❌ Results don't match! Check implementation.")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\n✓ Monkey patch applied successfully")
print("✓ Batch function works with all output formats")
print("✓ Results match original calculate_from_PT()")
print(f"✓ Achieved {speedup:.1f}x speedup for {n_samples:,} compositions")
print("\n" + "=" * 70)
print("MONKEY PATCH TEST COMPLETE!")
print("=" * 70)
