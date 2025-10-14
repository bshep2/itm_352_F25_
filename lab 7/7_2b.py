even_numbers = []
number = 2  # Start from the first even number

while len(even_numbers) == 0 or even_numbers[-1] <= 50:
    even_numbers.append(number)
    number += 2  # Increment by 2 to get the next even number

print(even_numbers)