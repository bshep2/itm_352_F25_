import csv


# Read the CSV file and calculate statistics
filename = 'my_custom_spreadsheet.csv'


# Check if the file exists and is readable before opening it
try:
    with open(filename, 'r') as file:
       # Read the file using the csv module
       reader = csv.DictReader(file)
      
       # Initialize variables to calculate statistics
       total_salary = 0
       max_salary = float('-inf')
       min_salary = float('inf')
       salary_count = 0
      
       # Iterate over each row in the CSV file
       for row in reader:
           salary = float(row['Annual_Salary'])
           total_salary += salary
           max_salary = max(max_salary, salary)
           min_salary = min(min_salary, salary)
           salary_count += 1
      
       # Calculate the average salary
       if salary_count > 0:
           average_salary = total_salary / salary_count
       else:
           average_salary = 0
      
       # Print out the results
       print(f"Average Annual Salary: ${average_salary:.2f}")
