import json

with open("/Users/brandon/Documents/GitHub/itm_352_F25_/assignment1/questions.json") as f:
    content = f.read()

print("First 50 characters:")
print(repr(content[:50]))

print("\nLast 50 characters:")
print(repr(content[-50:]))

print("\nFirst character is '[' ?", content[0] == '[')
print("Last non-whitespace character is ']' ?", content.strip()[-1] == ']')

quiz_data = json.loads(content)
print("\nType:", type(quiz_data))

if isinstance(quiz_data, list):
    print("It's a list! Length:", len(quiz_data))
else:
    print("It's NOT a list, it's a:", type(quiz_data).__name__)
