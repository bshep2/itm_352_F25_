import json
import random

def get_quiz_data(filename='questions.json'):

    try:
    with open(filename, 'r') as file:
        quiz_data = json.load(file)
    return quiz_data
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    return None
    except json.JSONDecodeError:
        print(f"Error: The file {filename} is not a valid JSON file.")
    return None

    while True:
        answer = input("Select the correct answer by its label: ").strip().upper()
        if answer in options:
            if options[answer] == correct_answer:
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

    for question in question list:
    total_questionss_asked += 1
    answers = quiz_data [question].copy() 
    correct_answer =answers[0] 

#
Random.shuffle(answers)

#
correct_letter = chr(65 = answers.index(correct_answer) 