from flask import Flask, render_template, jsonify, request, session
from datetime import datetime, timedelta
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'my-secret-key-12345'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# File names
QUESTIONS_FILE = 'Questionsfor3.JSON'
SCORES_FILE = 'scores.json'

# LOAD DATA FROM FILES

def load_questions():
    """Load questions from JSON file"""
    if not os.path.exists(QUESTIONS_FILE):
        print(f"ERROR: {QUESTIONS_FILE} not found!")
        return []
    
    with open(QUESTIONS_FILE, 'r') as file:
        questions = json.load(file)
    return questions


def load_scores():
    """Load saved scores from JSON file"""
    if not os.path.exists(SCORES_FILE):
        return []
    
    with open(SCORES_FILE, 'r') as file:
        scores = json.load(file)
    return scores


def save_score(score_data):
    """Save a score to the JSON file"""
    scores = load_scores()
    scores.append(score_data)
    
    with open(SCORES_FILE, 'w') as file:
        json.dump(scores, file, indent=2)


# HELPER FUNCTIONS

def shuffle_options(question):
    """Randomize the order of answer options"""
    new_question = question.copy()
    new_question['options'] = question['options'].copy()
    random.shuffle(new_question['options'])
    return new_question


def calculate_percentage(correct, total):
    """Calculate percentage score"""
    if total == 0:
        return 0
    return round((correct / total) * 100, 2)

# API ROUTES

@app.route('/api/start-quiz', methods=['POST'])
def start_quiz():
    """Start a new quiz"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    # Check username
    if not username or len(username) < 3:
        return jsonify({
            'success': False,
            'error': 'Username must be at least 3 characters'
        }), 400
    
    # Load and shuffle questions
    questions = load_questions()
    if not questions:
        return jsonify({
            'success': False,
            'error': 'No questions found'
        }), 500
    
    random.shuffle(questions)
    
    # Randomize answer options for each question
    for i in range(len(questions)):
        questions[i] = shuffle_options(questions[i])
    
    # Save to session
    session['quiz_active'] = True
    session['username'] = username
    session['questions'] = questions
    session['current_index'] = 0
    session['score'] = 0
    session['answers'] = []
    session['start_time'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'total_questions': len(questions),
        'username': username
    })


@app.route('/api/get-question', methods=['GET'])
def get_question():
    """Get the current question"""
    if not session.get('quiz_active'):
        return jsonify({
            'success': False,
            'error': 'No active quiz'
        }), 400
    
    questions = session.get('questions', [])
    index = session.get('current_index', 0)
    
    # Check if quiz is done
    if index >= len(questions):
        return jsonify({
            'success': False,
            'quiz_complete': True
        })
    
    question = questions[index]
    
    # Send question without the answer
    return jsonify({
        'success': True,
        'question': {
            'id': question['id'],
            'question': question['question'],
            'options': question['options'],
            'category': question.get('category', 'General'),
            'difficulty': question.get('difficulty', 'medium'),
            'question_number': index + 1,
            'total_questions': len(questions)
        }
    })


@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer"""
    if not session.get('quiz_active'):
        return jsonify({
            'success': False,
            'error': 'No active quiz'
        }), 400
    
    data = request.get_json()
    user_answer = data.get('answer', '').strip()
    
    if not user_answer:
        return jsonify({
            'success': False,
            'error': 'Please select an answer'
        }), 400
    
    questions = session['questions']
    index = session['current_index']
    question = questions[index]
    correct_answer = question['correct_answer']
    
    # Check if correct
    is_correct = (user_answer == correct_answer)
    
    # Update score
    if is_correct:
        session['score'] += 1
    
    # Save this answer
    session['answers'].append({
        'question': question['question'],
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct
    })
    
    # Move to next question
    session['current_index'] += 1
    
    # Check if done
    quiz_complete = (session['current_index'] >= len(questions))
    
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'quiz_complete': quiz_complete
    })


@app.route('/api/get-results', methods=['GET'])
def get_results():
    """Get final quiz results"""
    if not session.get('quiz_active'):
        return jsonify({
            'success': False,
            'error': 'No active quiz'
        }), 400
    
    questions = session['questions']
    score = session['score']
    answers = session['answers']
    username = session['username']
    start_time = datetime.fromisoformat(session['start_time'])
    
    # Calculate time taken
    time_taken = int((datetime.now() - start_time).total_seconds())
    
    # Calculate percentage
    percentage = calculate_percentage(score, len(questions))
    
    # Determine performance message
    if percentage >= 80:
        message = "Excellent work!"
    elif percentage >= 60:
        message = "Great job!"
    elif percentage >= 40:
        message = "Good effort!"
    else:
        message = "Keep practicing!"
    
    # Save score
    score_data = {
        'username': username,
        'score': score,
        'total': len(questions),
        'percentage': percentage,
        'time_taken': time_taken,
        'date': datetime.now().isoformat()
    }
    save_score(score_data)
    
    # End quiz
    session['quiz_active'] = False
    
    return jsonify({
        'success': True,
        'results': {
            'username': username,
            'score': score,
            'total': len(questions),
            'percentage': percentage,
            'time_taken': time_taken,
            'message': message,
            'answers': answers
        }
    })


@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    """Get top scores"""
    scores = load_scores()
    
    # Sort by percentage (highest first)
    scores.sort(key=lambda x: x['percentage'], reverse=True)
    
    # Get top 10
    top_scores = scores[:10]
    
    return jsonify({
        'success': True,
        'leaderboard': top_scores
    })

# PAGE ROUTES

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

    # Start the server
    print("\nStarting Quiz App...")
    print("Go to: http://127.0.0.1:5000")
    app.run(debug=True)