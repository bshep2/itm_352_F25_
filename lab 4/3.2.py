first_name = input("Enter your first name: ")
middle_name = input("Enter your middle name (or press Enter if you don't have one): ")
last_name = input("Enter your last name: ")


full_name = first_name + " " +middle_name + " " + last_name if middle_name else first_name + " " + last_name

print("Your full name is:", full_name)