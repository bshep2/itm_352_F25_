# Original tuple
my_tuple = (1, 2, 3)

# Get user input
user_input = input("Enter a value to append to the tuple: ")

try:
    # Convert tuple to list, append the input, and convert back to tuple
    temp_list = list(my_tuple)
    temp_list.append(user_input)
    appended_tuple = tuple(temp_list)

except Exception:
    # Handle the exception by creating a new tuple
    appended_tuple = my_tuple + (user_input,)

# Print the appended tuple
print("Appended tuple:", appended_tuple)
    print("Error:", str(e))