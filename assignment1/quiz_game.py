import json
import random
import os

def get_quiz_data(filename):
    """Return the quiz data list with questions and answers"""
    try:
        with open(filename, 'r') as file:
            quiz_data = json.load(file)
            return quiz_data
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filename}")
        return None

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "questions.json")
    
    # Load questions
    quiz_data = get_quiz_data(json_path)
    
    if quiz_data is None:
        return
    
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
    total = len(quiz_data)
    percent = (score / total) * 100
    
    print('\nQuiz Complete!')
    print(f'Score: {score}/{total}')
    print(f'Percent: {percent:.1f}%')

if __name__ == "__main__":
    main()