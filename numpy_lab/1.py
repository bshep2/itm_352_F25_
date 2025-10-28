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

print("Percentile   Income")
for percentile, income in income_data:
    print(f"{percentile}           {income}")