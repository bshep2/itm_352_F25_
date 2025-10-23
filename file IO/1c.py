print("=" * 70)
print("Reading Names from names.txt Using .read()")
print("=" * 70)

# Open file in read mode and use .read() to get entire content
with open("names.txt", "r") as file:
    content = file.read()

# Strip whitespace and split by newline to create list of names
names = content.strip().split('\n')

# Remove any empty strings that might result from extra newlines
names = [name.strip() for name in names if name.strip()]

# Display the names
print("\nNames from file:")
print("-" * 70)
for i, name in enumerate(names, 1):
    print(f"{i}. {name}")

# Count and display total
print("-" * 70)
print(f"\nTotal count of names: {len(names)}")

print("\n" + "=" * 70)
print("How .read() Works:")
print("=" * 70)
