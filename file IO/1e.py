with open("names.txt", "r") as file:
    lines = file.readlines()

names = [line.strip() for line in lines if line.strip()]

print("Names:")
for i, name in enumerate(names, 1):
    print(f"{i}. {name}")
print(f"Total: {len(names)}")
