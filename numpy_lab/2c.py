import pandas as pd

# List of individuals' ages
ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]

# Lists of individuals' names and genders
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

# Create DataFrame
df = pd.DataFrame({
    'Age': ages,
    'Gender': gender
}, index=names)

# Calculate and print average age by gender
print("Average Age by Gender:")
print(df.groupby('Gender')['Age'].mean())