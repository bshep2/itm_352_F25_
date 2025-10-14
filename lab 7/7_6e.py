# Original tuple
my_tuple = (1, 2, 3)

# Get user input
user_input = input("Enter a value to append to the tuple: ")

# Use unpacking to create a new tuple with the user input
appended_tuple = (*my_tuple, user_input)

# Print the appended tuple
print("Appended tuple:", appended_tuple)
