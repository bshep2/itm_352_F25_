# Define the tuples
celebrities_tuple = ("Taylor Swift", "Lionel Messi", "Max Verstappen", "Keanu Reeves", "Angelina Jolie")
ages_tuple = (35, 37, 27, 60, 49)

# Initialize lists
celebrities_list = []
ages_list = []

# Iterate through the tuples and append to the lists
for celebrity, age in zip(celebrities_tuple, ages_tuple):
    celebrities_list.append(celebrity)
    ages_list.append(age)

# Create a dictionary with the lists
celebrities_dict = {
    "celebrities": celebrities_list,
    "ages": ages_list
}

# Print the dictionary
print(celebrities_dict)