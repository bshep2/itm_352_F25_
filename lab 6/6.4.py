def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return "Leap year"
    else:
        return "Not a leap year"

year = int(input("Enter a year: "))
result = is_leap_year(year)
print(result)