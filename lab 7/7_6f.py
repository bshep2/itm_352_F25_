# Original tuple
my_tuple = (1, 2, 3)

# Get user input
user_input = input("Enter a value to append to the tuple: ")

# Recast the tuple to a list and use append
temp_list = list(my_tuple)
temp_list.append(user_input)

# Convert back to tuple
appended_tuple = tuple(temp_list)

# Print the appended tuple
print("Appended tuple:", appended_tuple)
