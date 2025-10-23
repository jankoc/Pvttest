# Rust Vectorization Guide for pyaga8

## Summary

I've modified the `pyaga8` library to add a **batch processing method** that processes multiple compositions in a single Rust call, eliminating per-call FFI overhead.

## Python Optimization (Available Now)

Before building the Rust version, you can use the **Python-optimized version** which achieves **5x speedup**:

```bash
python gas_composition_analysis_optimized.py
```

**Performance:**
- Original: 7-8 seconds for 100k samples (~17,000/sec)
- Optimized: **1.4 seconds** for 100k samples (**~72,000/sec**)
- Speedup: **5x**

**Key optimizations:**
1. Reuse single AGA8 and Composition objects
2. Use numpy arrays instead of Python dictionaries
3. Set P and T once globally
4. Minimize Python object creation

## Rust Modification (For Even Better Performance)

The Rust modification adds a `calc_batch_pt()` method to process arrays of compositions natively in Rust.

###Potential Additional Speedup

The Rust batch method could theoretically provide:
- **6-8x speedup** over original (vs current 5x)
- **1.2-1.5x faster** than the Python optimization
- **Estimated time**: 0.9-1.1 seconds for 100k samples

## Modified Code

### File: `pyaga8/src/lib.rs`

I added this method to the `Gerg2008` struct (lines 171-200):

```rust
/// Batch calculation for multiple compositions at the same P and T
/// Returns a list of tuples: [(speed_of_sound, density, z, molar_mass), ...]
fn calc_batch_pt(
    &self,
    compositions: Vec<&Composition>,
    pressure: f64,
    temperature: f64,
) -> Vec<(f64, f64, f64, f64)> {
    let mut results = Vec::with_capacity(compositions.len());

    for comp in compositions {
        // Create a new instance for each calculation
        let mut calc = gerg2008::Gerg2008::new();
        calc.set_composition(&comp.inner).unwrap();
        calc.p = pressure;
        calc.t = temperature;

        // Calculate density and properties
        if calc.density(0).is_ok() {
            calc.properties();
            // Return (speed_of_sound, density, z, molar_mass)
            results.push((calc.w, calc.d * calc.mm, calc.z, calc.mm));
        } else {
            // Return NaN on error
            results.push((f64::NAN, f64::NAN, f64::NAN, f64::NAN));
        }
    }

    results
}
```

## Building the Modified pyaga8

### Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install maturin (Rust-Python build tool)
pip install maturin
```

### Build Steps

```bash
cd pyaga8

# Option 1: Build and install in development mode
maturin develop --release

# Option 2: Build wheel and install
maturin build --release
pip install target/wheels/pyaga8-*.whl
```

### Verify Installation

```python
import pyaga8

# Check for new method
g = pyaga8.Gerg2008()
assert hasattr(g, 'calc_batch_pt'), "Batch method not found!"
print("✓ Batch processing method available!")
```

## Using the Batch Method

```python
import pyaga8
import numpy as np

# Create AGA8 instance
aga8 = pyaga8.Gerg2008()

# Create multiple compositions
compositions = []
for _ in range(1000):
    comp = pyaga8.Composition()
    comp.methane = 0.85
    comp.ethane = 0.05
    comp.propane = 0.03
    comp.carbon_dioxide = 0.02
    comp.nitrogen = 0.05
    compositions.append(comp)

# Batch calculate (single FFI call!)
results = aga8.calc_batch_pt(
    compositions,
    pressure=15000.0,  # kPa
    temperature=288.15  # K
)

# Extract results
for sos, rho, z, mm in results:
    print(f"Speed of sound: {sos:.2f} m/s, Density: {rho:.2f} kg/m³")
```

## Performance Comparison

| Version | Time (100k samples) | Throughput | Speedup |
|---------|---------------------|------------|---------|
| Original Python | 7-8 seconds | ~17,000/sec | 1x |
| Parallel (16 cores) | ~5 seconds | ~20,000/sec | 1.5x |
| **Optimized Python** | **1.4 seconds** | **~72,000/sec** | **5x** |
| Rust Batch (estimated) | ~1.0 seconds | ~100,000/sec | 7x |

## Why the Python Optimization Works So Well

The current bottleneck breakdown:
- **FFI overhead**: 15% (~9 μs per call)
- **Python object creation**: 37% (~22 μs)
- **AGA8 calculation**: 48% (~28 μs)

The Python optimization eliminates most of the object creation overhead and some FFI overhead by:
1. Reusing objects → Eliminates ~22 μs per sample
2. Direct pyaga8 API use → Reduces some wrapper overhead
3. Numpy arrays → Faster than Python lists/dicts

## Network Issues During Build

If you encounter `Access denied` errors when building:

```bash
# The issue is crates.io access being blocked
# Error: failed to get `aga8` as a dependency
```

**Workarounds:**
1. Use a different network/proxy
2. Pre-download dependencies:
   ```bash
   cargo vendor
   mkdir .cargo
   cat > .cargo/config.toml <<EOF
   [source.crates-io]
   replace-with = "vendored-sources"

   [source.vendored-sources]
   directory = "vendor"
   EOF
   ```
3. Use the Python-optimized version (which is already very fast!)

## Conclusion

**Recommendation:** Start with the **Python-optimized version** (`gas_composition_analysis_optimized.py`):
- ✅ 5x speedup (already excellent!)
- ✅ No build required
- ✅ Works immediately
- ✅ Easy to maintain

**Consider Rust modification if:**
- You need to process millions of samples regularly
- Every fraction of a second matters
- You have a proper Rust build environment

The modified `pyaga8` code is ready in `/home/user/Pvttest/pyaga8/src/lib.rs` whenever you can build it!
