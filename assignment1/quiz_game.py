import json
import random
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "questions.json")

# Load questions from JSON file
try:
    with open(json_path) as f:
        content = f.read()
        quiz_data = json.loads(content)
    
    if not isinstance(quiz_data, list):
        print("Error: JSON should be a list/array")
        exit()
        
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Shuffle questions
random.shuffle(quiz_data)

score = 0
letters = ['A', 'B', 'C', 'D']

print('=' * 50)
print('Welcome to the Quiz Game!')
print('=' * 50)

# Loop through each question
for i, question in enumerate(quiz_data, 1):
    print(f'\nQuestion {i}: {question["question"]}')
    
    # Display options
    for j, option in enumerate(question['options']):
        print(f'  {letters[j]}. {option}')
    
    # Get user answer
    while True:
        answer = input('\nYour answer (A/B/C/D): ').strip().upper()
        if answer in letters[:len(question['options'])]:
            break
        print('Invalid input! Please enter A, B, C, or D.')
    
    # Check answer
    correct_index = question['options'].index(question['answer'])
    correct_letter = letters[correct_index]
    
    if answer == correct_letter:
        print('✓ Correct!')
        score += 1
    else:
        print(f'✗ Wrong! The correct answer was {correct_letter}. {question["answer"]}')
    
    # Show explanation if available
    if 'explanation' in question:
        print(f'\n  Explanation: {question["explanation"]}')

# Display final score
print('\n' + '=' * 50)
print('Quiz Complete!')
print('=' * 50)
print(f'Your Score: {score}/{len(quiz_data)}')
print(f'Percentage: {(score/len(quiz_data)*100):.1f}%')
print('=' * 50)