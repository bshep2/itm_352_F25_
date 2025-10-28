import pandas as pd

# Read the JSON file
df = pd.read_json('taxi_trips.json')

# Print the DataFrame
print("Taxi Trips DataFrame:")
print(df)
print("\n")

# Print summary statistics
print("Summary Statistics:")
print(df.describe())
print("\n")

# Print the median for numerical columns
print("Median values:")
print(df.median(numeric_only=True))