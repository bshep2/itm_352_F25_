import json
import random

def get_quiz_data(filename='questions.json'):

def ask_question(question, options):
    print(question)
    for label, option in options.items():
        print(f"{label}: {option}")
    
    while True:
        answer = input("Select the correct answer by its label: ")
        if answer in options and options[answer] == options['correct']:
            print("Correct!\n")
            return True
        else:
            print("Incorrect, try again.")

def main():
    questions = get_quiz_data('questions.json')
    random.shuffle(questions)

    for question in questions:
        q_text = question['question']
        options = {label: option for label, option in question['options'].items()}
        options['correct'] = question['correct']
        random_options = list(options.items())
        random.shuffle(random_options)
        randomized_options = {label: option for label, option in random_options}
        
        ask_question(q_text, randomized_options)

if __name__ == "__main__":
    main()