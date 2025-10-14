def generate_odd_numbers(n):
    return list(range(1, 2*n + 1, 2))

# Example usage
n = 10
odd_numbers = generate_odd_numbers(n)
print(odd_numbers)