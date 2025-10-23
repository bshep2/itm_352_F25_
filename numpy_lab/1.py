import numpy as np

# List of tuples (percentile, income)
income_data = [
    (10, 14629),
    (20, 25600),
    (30, 37002),
    (40, 50000),
    (50, 63179),
    (60, 79542),
    (70, 100162),
    (80, 130000),
    (90, 184292)
]

# Convert to NumPy array
income_array = np.array(income_data)

print("NumPy Array:")
print(income_array)
print()

# Report dimensions and number of elements
print("Dimensions (shape):", income_array.shape)
print("Total number of elements:", income_array.size)
```

**Output:**
```
NumPy Array:
[[    10  14629]
 [    20  25600]
 [    30  37002]
 [    40  50000]
 [    50  63179]
 [    60  79542]
 [    70 100162]
 [    80 130000]
 [    90 184292]]

Dimensions (shape): (9, 2)
Total number of elements: 18