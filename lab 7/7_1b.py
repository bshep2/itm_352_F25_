odd_numbers = [num for num in range(1, 51) if num % 2 != 0]
print(odd_numbers)odd_numbers = []
for num in range(1, 51):
    if num % 2 != 0:
        odd_numbers.append(num)
print(odd_numbers)
odd_numbers = [2*num + 1 for num in range(25)]  # Generates odd numbers from 1 to 49
print(odd_numbers)
