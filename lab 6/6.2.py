# Create a list with different values
my_list = [1, 'apple', 3.14, True, None]  # You can change the length of this list for testing

# Control logic to check the length of the list
if len(my_list) < 5:
    print("The list contains fewer than 5 elements.")
elif 5 <= len(my_list) <= 10:
    print("The list contains between 5 and 10 elements.")
else:
    print("The list contains more than 10 elements.")