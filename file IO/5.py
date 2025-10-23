import json


# Specify the filename where the JSON data is saved
filename = 'questions.json'


# Read the JSON file and print its content
try:
   with open(filename, 'r') as json_file:
       quiz_data = json.load(json_file)
       print(json.dumps(quiz_data, indent=4))  # Print the content in a pretty format
except FileNotFoundError:
   print(f"The file {filename} was not found.")
except json.JSONDecodeError:
   print(f"There was an error decoding the JSON from {filename}.")
except Exception as e:
   print(f"An error occurred: {e}")