# List of individuals' ages
ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]

# Lists of individuals' names and genders
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

# Use zip() to create a list of (age, gender) tuples
age_gender_tuples = list(zip(ages, gender))

print("List of (age, gender) tuples:")
print(age_gender_tuples)