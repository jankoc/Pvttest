"""
Quick test script to verify the gas composition analysis works correctly
"""

import sys
sys.path.insert(0, '/home/user/Pvttest/pvtlib')

import numpy as np
from pvtlib.aga8 import AGA8

# Test with a single known composition
test_composition = {
    'C1': 0.85,   # 85% Methane
    'C2': 0.05,   # 5% Ethane
    'C3': 0.03,   # 3% Propane
    'nC4': 0.01,  # 1% n-Butane
    'N2': 0.04,   # 4% Nitrogen
    'CO2': 0.02,  # 2% CO2
}

print("Testing AGA8 calculation with known composition...")
print("\nComposition:")
for comp, fraction in test_composition.items():
    print(f"  {comp}: {fraction:.4f} ({fraction*100:.2f}%)")

print(f"\nOperating Conditions:")
print(f"  Pressure: 150 bara")
print(f"  Temperature: 15°C")

# Create AGA8 calculator
aga8 = AGA8(equation='GERG-2008')

# Calculate properties
results = aga8.calculate_from_PT(
    composition=test_composition,
    pressure=150,
    temperature=15,
    pressure_unit='bara',
    temperature_unit='C'
)

print(f"\nResults:")
print(f"  Speed of Sound: {results['w']:.2f} m/s")
print(f"  Density: {results['rho']:.2f} kg/m³")
print(f"  Compressibility (Z): {results['z']:.4f}")
print(f"  Molar Mass: {results['mm']:.2f} g/mol")

print("\nTest completed successfully!")
