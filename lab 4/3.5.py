# Initial list of responses
responses = [5, 7, 3, 8]

# Append "0" to the end
responses = responses + [0]  # Now: [5, 7, 3, 8, 0]

# Insert "6" between 7 and 3 (i.e., at index 2)
responses = responses[:2] + [6] + responses[2:]  # Now: [5, 7] + [6] + [3, 8, 0]

# Print the updated list
print(responses)
