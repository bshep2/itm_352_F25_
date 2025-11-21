"""
Flask Quiz Application - Backend Server
Serves the quiz web application with RESTful APIs
"""

from flask import Flask, render_template, jsonify, request, session
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this'

# Load questions from JSON file
def load_questions():
    """Load questions from JSON file"""
    try:
        with open('questionsfor3.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route('/')
def index():
    """Serve the main quiz page"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_quiz():
    """Initialize a new quiz session"""
    data = request.get_json()
    username = data.get('username', 'Guest')
    
    # Load and randomize questions
    questions = load_questions()
    random.shuffle(questions)
    
    # Randomize answer options for each question
    for q in questions:
        random.shuffle(q['options'])
    
    # Store in session
    session['username'] = username
    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    session['max_score'] = sum(q.get('points', 1) for q in questions)
    session['answers'] = []
    
    return jsonify({'success': True})

@app.route('/api/question', methods=['GET'])
def get_question():
    """Get the current question"""
    current = session.get('current_question', 0)
    questions = session.get('questions', [])
    
    if current >= len(questions):
        return jsonify({'done': True})
    
    question = questions[current]
    return jsonify({
        'done': False,
        'num': current + 1,
        'total': len(questions),
        'question': question['question'],
        'options': question['options'],
        'category': question.get('category', 'General'),
        'points': question.get('points', 1)
    })

@app.route('/api/answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get feedback"""
    data = request.get_json()
    user_answer = data.get('answer')
    
    current = session.get('current_question', 0)
    questions = session.get('questions', [])
    question = questions[current]
    
    is_correct = user_answer == question['correct']
    points = question.get('points', 1)
    
    # Update score
    if is_correct:
        session['score'] = session.get('score', 0) + points
    
    # Save answer
    answers = session.get('answers', [])
    answers.append({
        'question': question['question'],
        'user_answer': user_answer,
        'correct_answer': question['correct'],
        'is_correct': is_correct,
        'points': points if is_correct else 0,
        'max_points': points,
        'category': question.get('category', 'General'),
        'explanation': question.get('explanation', 'No explanation available.')
    })
    session['answers'] = answers
    
    # Move to next question
    session['current_question'] = current + 1
    
    return jsonify({
        'correct': is_correct,
        'answer': question['correct'],
        'explanation': question.get('explanation', 'No explanation available.'),
        'points': points if is_correct else 0,
        'done': session['current_question'] >= len(questions)
    })

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get final quiz results"""
    score = session.get('score', 0)
    max_score = session.get('max_score', 0)
    answers = session.get('answers', [])
    
    percent = (score / max_score * 100) if max_score > 0 else 0
    
    return jsonify({
        'score': score,
        'total': max_score,
        'percent': round(percent, 1),
        'answers': answers
    })

if __name__ == '__main__':
    app.run(debug=True)