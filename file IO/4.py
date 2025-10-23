import csv


# Initialize variables
total_fare = 0
total_trip_miles = 0
max_trip_miles = 0
fare_count = 0


# Read the CSV file
filename = 'taxi_1000.csv'


try:
   with open(filename, mode='r') as file:
       reader = csv.DictReader(file)
      
       # Iterate over each row in the file
       for row in reader:
           try:
               # Convert fare and trip miles to floats for calculations
               fare = float(row['Fare'])
               trip_miles = float(row['Trip Miles'])


               # Update total fare and trip miles, count fares
               total_fare += fare
               total_trip_miles += trip_miles
               max_trip_miles = max(max_trip_miles, trip_miles)
               fare_count += 1


           except ValueError as e:
               print(f"Skipping row due to error in data: {row}")
      
       # Calculate the average fare
       if fare_count > 0:
           average_fare = total_fare / fare_count
       else:
           average_fare = 0


       # Print the results
       print(f"Total Fare (for fares > 10): ${total_fare:.2f}")
       print(f"Average Fare (for fares > 10): ${average_fare:.2f}")
       print(f"Maximum Trip Miles (for fares > 10): {max_trip_miles} miles")


except FileNotFoundError:
   print(f"The file {filename} was not found.")
except IOError:
   print(f"The file {filename} could not be read.")