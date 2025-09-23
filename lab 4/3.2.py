first_name = input("Enter your first name: ")
middle_name = input("Enter your middle name (or press Enter if you don't have one): ")
last_name = input("Enter your last name: ")


full_name = first_name + " " +middle_name + " " + last_name if middle_name else first_name + " " + last_name

print("Your full name is:", full_name)

#ex1b
#full_name = f"{first_name} {middle_name + ' ' if middle_name else ''}. {last_name}"

#ex1c
#full_name = "%s %s%s. %s" % (first_name, middle_name, " " if middle_name else "", last_name)

#ex1d
#full_name = "{} {}{}. {}".format(first_name, middle_name, " " if middle_name else "", last_name)

#ex1e 
full_name = " ".join([first_name, middle_name, last_name])

#ex1f
name_parts = [first_name, middle_name. last_name]
full_name = "{} {} {}".format(*name_parts)
