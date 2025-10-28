import pandas as pd

# List of individuals' ages
ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]

# Lists of individuals' names and genders
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

# Create DataFrame with names as index and Age and Gender as columns
df = pd.DataFrame({
    'Age': ages,
    'Gender': gender
}, index=names)

# Print the DataFrame
print("DataFrame:")
print(df)
print("\n")

# Summarize the DataFrame using describe()
print("Summary using describe():")
print(df.describe())