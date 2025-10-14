# Original tuple
my_tuple = (1, 2, 3)

# Get user input
user_input = input("Enter a value to append to the tuple: ")

# Convert tuple to list, append the input, and convert back to tuple
temp_list = list(my_tuple)
temp_list.append(user_input)
appended_tuple = tuple(temp_list)

# Print the appended tuple
print("Appended tuple:", appended_tuple)