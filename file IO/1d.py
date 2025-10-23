names = []
with open("names.txt", "r") as file:
    while True:
        line = file.readline()
        if not line:
            break
        name = line.strip()
        if name:
            names.append(name)

print("Names:")
for i, name in enumerate(names, 1):
    print(f"{i}. {name}")
print(f"Total: {len(names)}")

with open("names.txt", "r") as f:
    first_5 = [f.readline().strip() for _ in range(5) if f.readline().strip()]