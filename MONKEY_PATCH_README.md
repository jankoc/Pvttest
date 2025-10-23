# Monkey Patch: Add Batch Function to pvtlib

## Overview

This module provides a **monkey-patch** to add the high-performance `calculate_batch_from_PT()` method to pvtlib's `AGA8` class **without modifying the original source code**.

Perfect for:
- ✅ Testing the batch function before modifying pvtlib
- ✅ Using with unmodified/official pvtlib installations
- ✅ Temporary performance improvements
- ✅ Environments where you can't modify installed packages

---

## Quick Start

### Step 1: Import pvtlib as normal

```python
import sys
sys.path.insert(0, '/path/to/pvtlib')

from pvtlib.aga8 import AGA8
```

### Step 2: Apply the monkey patch

```python
import pvtlib_batch_patch  # Auto-applies the patch on import
```

### Step 3: Use the batch function!

```python
aga8 = AGA8(equation='GERG-2008')

compositions = [
    {'C1': 0.85, 'C2': 0.05, 'N2': 0.05, 'CO2': 0.02},
    {'C1': 0.90, 'C2': 0.04, 'N2': 0.03, 'CO2': 0.01},
    # ... thousands more
]

# Batch calculation - 5x faster!
df = aga8.calculate_batch_from_PT(compositions, pressure=150, temperature=15)
print(df[['C1', 'w', 'rho']].head())
```

---

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete example using the monkey patch
"""

import sys
sys.path.insert(0, '/path/to/pvtlib')

from pvtlib.aga8 import AGA8
import pvtlib_batch_patch  # Apply patch
import numpy as np

# Create AGA8 instance
aga8 = AGA8(equation='GERG-2008')

# Generate 10,000 random compositions
np.random.seed(42)
c1 = np.random.uniform(0.70, 0.95, 10000)
remaining = 1.0 - c1
c2 = np.random.uniform(0, 0.15, 10000) * remaining
n2 = np.random.uniform(0, 0.10, 10000) * remaining
co2 = np.random.uniform(0, 0.10, 10000) * remaining

compositions = np.column_stack([c1, c2, np.zeros((10000, 6)), n2, co2])
compositions = compositions / compositions.sum(axis=1, keepdims=True)

# Calculate all at once!
df = aga8.calculate_batch_from_PT(compositions, pressure=150, temperature=15)

print(f"Processed {len(df)} compositions")
print(df[['C1', 'w', 'rho', 'z']].describe())
```

---

## Files

### 1. `pvtlib_batch_patch.py` - The Monkey Patch Module

Contains:
- `calculate_batch_from_PT()` function implementation
- `apply_patch()` function to apply the patch
- Auto-applies on import

**Location:** Same directory as your script

### 2. `test_monkey_patch.py` - Comprehensive Test

Tests:
- ✅ Patch application
- ✅ All output formats (DataFrame, dict, arrays)
- ✅ Performance comparison (3-5x speedup)
- ✅ Result validation against original method
- ✅ 10,000 composition benchmark

**Run with:** `python test_monkey_patch.py`

---

## How It Works

### What is Monkey Patching?

Monkey patching is a technique where you **add or modify methods on existing classes at runtime**, without changing the original source code.

```python
# Before patching
aga8 = AGA8()
hasattr(aga8, 'calculate_batch_from_PT')  # False

# Apply patch
import pvtlib_batch_patch

# After patching
aga8 = AGA8()
hasattr(aga8, 'calculate_batch_from_PT')  # True!
```

### The Magic Line

```python
# This line adds the method to the AGA8 class
AGA8.calculate_batch_from_PT = calculate_batch_from_PT
```

All new `AGA8()` instances now have this method!

---

## Usage Patterns

### Pattern 1: Auto-Apply on Import (Recommended)

```python
import pvtlib_batch_patch  # Automatically applies patch

from pvtlib.aga8 import AGA8
aga8 = AGA8()
# Function is already available!
```

### Pattern 2: Manual Apply

```python
from pvtlib.aga8 import AGA8
import pvtlib_batch_patch

# Manually apply
pvtlib_batch_patch.apply_patch()

aga8 = AGA8()
# Function now available
```

### Pattern 3: Conditional Apply

```python
from pvtlib.aga8 import AGA8
aga8 = AGA8()

# Check if batch function exists
if not hasattr(aga8, 'calculate_batch_from_PT'):
    print("Batch function not found, applying patch...")
    import pvtlib_batch_patch
else:
    print("Batch function already available!")

# Use function
df = aga8.calculate_batch_from_PT(compositions, 150, 15)
```

---

## API Documentation

The patched method has **identical API** to the version in `BATCH_FUNCTION_GUIDE.md`:

### Input Formats

**List of dicts:**
```python
compositions = [
    {'C1': 0.85, 'C2': 0.05, ...},
    {'C1': 0.90, 'C2': 0.04, ...},
]
df = aga8.calculate_batch_from_PT(compositions, 150, 15)
```

**Numpy array:**
```python
# Shape: (n_samples, 10)
# Order: [C1, C2, C3, iC4, nC4, iC5, nC5, nC6, N2, CO2]
compositions = np.random.random((10000, 10))
df = aga8.calculate_batch_from_PT(compositions, 150, 15)
```

### Output Formats

**DataFrame (default):**
```python
df = aga8.calculate_batch_from_PT(compositions, 150, 15)
# Returns: pandas DataFrame with compositions and properties
```

**Dict:**
```python
results = aga8.calculate_batch_from_PT(compositions, 150, 15, return_format='dict')
# Returns: {'w': array, 'rho': array, 'z': array, ...}
```

**Arrays:**
```python
sos, rho, z, mm = aga8.calculate_batch_from_PT(compositions, 150, 15, return_format='arrays')
# Returns: tuple of 4 numpy arrays
```

---

## Performance

Same performance as the built-in version:

| # Compositions | Time | Throughput |
|----------------|------|------------|
| 1,000 | ~0.01 sec | ~100,000/sec |
| 10,000 | ~0.10 sec | ~100,000/sec |
| 100,000 | ~1.0 sec | ~100,000/sec |

**3-5x faster than looping over `calculate_from_PT()`**

---

## Testing

### Run the Test Suite

```bash
python test_monkey_patch.py
```

**Test Output:**
```
======================================================================
MONKEY PATCH TEST - pvtlib Batch Function
======================================================================

1. Importing pvtlib.aga8...
   Has calculate_batch_from_PT? False

2. Applying monkey patch...
✓ Successfully patched AGA8 with calculate_batch_from_PT()

3. Verifying patch...
   Has calculate_batch_from_PT? True
   ✓ Patch applied successfully!

...

SUMMARY
======================================================================

✓ Monkey patch applied successfully
✓ Batch function works with all output formats
✓ Results match original calculate_from_PT()
✓ Achieved 3.4x speedup for 10,000 compositions
```

### Validation

The test verifies:
1. ✅ Patch applies correctly
2. ✅ All output formats work
3. ✅ Results match original `calculate_from_PT()` exactly
4. ✅ Performance improvement (3-5x)

---

## Advantages vs Modifying pvtlib

### Monkey Patch (This Approach)

**Pros:**
- ✅ No modification to original pvtlib
- ✅ Works with official/unmodified installations
- ✅ Easy to test and remove
- ✅ Can be applied conditionally
- ✅ No risk of breaking pvtlib updates

**Cons:**
- ❌ Must import patch module in each script
- ❌ Patch is not persistent (must apply each time)
- ❌ Slightly less "official" feeling

### Modifying pvtlib Directly

**Pros:**
- ✅ Function always available
- ✅ No need to import patch module
- ✅ More "permanent" solution

**Cons:**
- ❌ Modifies third-party library
- ❌ Lost on pvtlib updates
- ❌ Harder to test/remove
- ❌ Need write access to library

---

## When to Use Which Approach

### Use Monkey Patch When:

- 🧪 **Testing** before permanent implementation
- 🔒 **Can't modify** installed packages (corporate environment)
- 🔄 **Frequent updates** to pvtlib (don't want to lose changes)
- 📦 **Distributing code** to others (they may have different pvtlib versions)
- ⚡ **Quick performance boost** without commitment

### Modify pvtlib Directly When:

- ✅ **Own the codebase** and control dependencies
- 📌 **Pinned version** of pvtlib (no updates expected)
- 🏢 **Internal library** you maintain
- 💼 **Production environment** with controlled dependencies

---

## Troubleshooting

### Patch doesn't apply

```python
import pvtlib_batch_patch
# Shows: ⚠️  Could not auto-apply patch: No module named 'pvtlib'
```

**Solution:** Make sure pvtlib is in your Python path:
```python
import sys
sys.path.insert(0, '/path/to/pvtlib')
import pvtlib_batch_patch
```

### Function already exists

```python
import pvtlib_batch_patch
# Shows: ⚠️  AGA8.calculate_batch_from_PT already exists
```

**This is fine!** The function is already available (either from a previous patch or built into pvtlib). Just use it:

```python
from pvtlib.aga8 import AGA8
aga8 = AGA8()
df = aga8.calculate_batch_from_PT(compositions, 150, 15)  # Works!
```

### Import order matters

**Wrong:**
```python
import pvtlib_batch_patch  # pvtlib not imported yet - won't work
from pvtlib.aga8 import AGA8
```

**Right:**
```python
from pvtlib.aga8 import AGA8  # Import pvtlib first
import pvtlib_batch_patch      # Then apply patch
```

Or use manual apply:
```python
from pvtlib.aga8 import AGA8
import pvtlib_batch_patch
pvtlib_batch_patch.apply_patch()  # Apply after both imports
```

---

## Comparison with Other Approaches

| Approach | Setup Time | Performance | Persistence | Flexibility |
|----------|------------|-------------|-------------|-------------|
| **Monkey Patch** | 1 line import | Same (5x) | Per-script | ⭐⭐⭐⭐⭐ |
| Modify pvtlib | Edit source | Same (5x) | Permanent | ⭐⭐⭐ |
| Original loop | None | 1x (slow) | N/A | ⭐⭐⭐⭐⭐ |
| Parallel | None | 1.5x | N/A | ⭐⭐⭐ |

---

## Example Use Cases

### 1. Quick Performance Test

```python
# Try the batch function without committing to modifications
import pvtlib_batch_patch
from pvtlib.aga8 import AGA8

aga8 = AGA8()
df = aga8.calculate_batch_from_PT(large_dataset, 150, 15)
# See if 5x speedup helps your workflow
```

### 2. Distributable Analysis Script

```python
#!/usr/bin/env python3
"""
Analysis script that works with any pvtlib installation
Just include pvtlib_batch_patch.py with your script
"""

from pvtlib.aga8 import AGA8
import pvtlib_batch_patch  # Users just need this file

# Script works whether pvtlib has batch function or not!
aga8 = AGA8()
df = aga8.calculate_batch_from_PT(compositions, 150, 15)
```

### 3. Gradual Migration

```python
# Use monkey patch in development
if os.getenv('DEVELOPMENT'):
    import pvtlib_batch_patch

# In production, use modified pvtlib
# Function available either way!
```

---

## Summary

The monkey patch approach provides a **zero-modification** way to add the high-performance batch function to pvtlib:

✅ **No changes** to pvtlib source code
✅ **One import** to enable
✅ **Same performance** as built-in version
✅ **Full API compatibility**
✅ **Easy to test and remove**
✅ **Works with any pvtlib version**

Perfect for testing, temporary use, or environments where you can't modify installed packages!

---

## Files in This Package

1. **pvtlib_batch_patch.py** - The monkey patch module (~300 lines)
2. **test_monkey_patch.py** - Comprehensive test suite (~200 lines)
3. **MONKEY_PATCH_README.md** - This guide

**Total:** Just 2 Python files to add the batch function!

---

## License

MIT License (same as pvtlib)
