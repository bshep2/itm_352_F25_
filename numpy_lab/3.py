import pandas as pd

# Create a dictionary
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
    'Age': [25, 30, 35, 40, 22],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Salary': [70000, 80000, 120000, 90000, 60000]
}

# Convert dictionary to DataFrame
df = pd.DataFrame(data)

# Print the DataFrame
print("DataFrame:")
print(df)