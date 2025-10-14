def generate_odd_numbers(n):
    return [i for i in range(1, 2*n + 1) if i % 2 != 0]
    return list(range(1, 2*n + 1, 2))

# Example usage
n = 10
odd_numbers = generate_odd_numbers(n)
print(odd_numbers)