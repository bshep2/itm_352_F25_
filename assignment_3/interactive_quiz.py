"""
Simple Quiz Application with Progress Bar, Visual Feedback, and Question Review
"""

import json
import random

class Quiz:
    def __init__(self, questions_file="questionsfor3.json"):
        self.questions = self.load_questions(questions_file)
        self.score = 0
        self.max_score = 0
        self.answers = []
        self.username = ""
    
    def load_questions(self, filename):
        """Load questions from JSON file"""
        try:
            with open(filename, 'r') as f:
                questions = json.load(f)
            print(f"Loaded {len(questions)} questions\n")
            return questions
        except FileNotFoundError:
            print(f"Error: {filename} not found!")
            exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {filename}")
            exit(1)

    def show_progress_bar(self, current, total):
        """Display visual progress bar"""
        percent = (current / total) * 100
        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"\nProgress: [{bar}] {percent:.0f}% ({current}/{total})")

    def start(self):
        """Start the quiz"""
        print("=" * 50)
        print("WELCOME TO THE QUIZ")
        print("=" * 50)
        
        while True:
            self.username = input("\nEnter your name: ").strip()
            if len(self.username) >= 3:
                break
            print("Name must be at least 3 characters")
        
        print(f"\nHello {self.username}!\n")
        
        # Randomize questions and answers
        random.shuffle(self.questions)
        for q in self.questions:
            random.shuffle(q['options'])
        
        self.run_quiz()

    def run_quiz(self):
        """Main quiz loop"""
        for i, q in enumerate(self.questions):
            points = q.get('points', 1)
            category = q.get('category', 'General')
            explanation = q.get('explanation', 'No explanation available.')
            self.max_score += points
            
            # Show progress bar
            self.show_progress_bar(i, len(self.questions))
            
            # Display question
            print(f"\nQuestion {i+1}/{len(self.questions)} | {category} | {points} pts")
            print("-" * 50)
            print(f"{q['question']}\n")
            
            for idx, opt in enumerate(q['options'], 1):
                print(f"{idx}. {opt}")
            
            # Get answer
            answer = self.get_answer(len(q['options']))
            user_answer = q['options'][answer - 1]
            is_correct = user_answer == q['correct']
            
            # Visual feedback (green for correct, red for incorrect)
            if is_correct:
                print("\n" + "=" * 50)
                print("✅ CORRECT! " + "🎉" * 3)
                print("=" * 50)
                print(f"Great job! You earned {points} points!")
            else:
                print("\n" + "=" * 50)
                print("❌ INCORRECT")
                print("=" * 50)
                print(f"The correct answer is: {q['correct']}")
                self.score -= points // 2 if self.score > 0 else 0  # Small penalty
            
            # Show explanation
            print(f"\nExplanation: {explanation}")
            print("-" * 50)
            
            if is_correct:
                self.score += points
            
            # Save answer details
            self.answers.append({
                "question": q['question'],
                "user_answer": user_answer,
                "correct": q['correct'],
                "is_correct": is_correct,
                "points": points if is_correct else 0,
                "max_points": points,
                "category": category,
                "explanation": explanation
            })
            
            input("\nPress Enter to continue...")
        
        self.show_results()

    def get_answer(self, num_options):
        """Get valid answer from user"""
        while True:
            try:
                choice = int(input(f"\nYour answer (1-{num_options}): "))
                if 1 <= choice <= num_options:
                    return choice
                print(f"Enter a number between 1 and {num_options}")
            except ValueError:
                print("Enter a valid number")

    def show_results(self):
        """Display final results"""
        # Final progress bar
        self.show_progress_bar(len(self.questions), len(self.questions))
        
        print("\n" + "=" * 50)
        print("🏆 QUIZ COMPLETE! 🏆")
        print("=" * 50)
        
        percent = (self.score / self.max_score) * 100 if self.max_score > 0 else 0
        print(f"\n{self.username}'s Final Score: {self.score}/{self.max_score} ({percent:.1f}%)\n")
        
        # Performance message with visual feedback
        if percent >= 90:
            print("🌟 EXCELLENT! Outstanding performance!")
        elif percent >= 70:
            print("👍 GOOD JOB! Well done!")
        elif percent >= 50:
            print("📚 NOT BAD! Keep studying!")
        else:
            print("💪 KEEP TRYING! Practice makes perfect!")
        
        # Question review with explanations
        print("\n" + "=" * 50)
        print("QUESTION REVIEW & EXPLANATIONS:")
        print("=" * 50)
        
        for i, ans in enumerate(self.answers, 1):
            status = "✅ CORRECT" if ans['is_correct'] else "❌ INCORRECT"
            
            print(f"\n{'─' * 50}")
            print(f"Q{i}: {status}")
            print(f"{'─' * 50}")
            print(f"Question: {ans['question']}")
            print(f"Your answer: {ans['user_answer']}")
            print(f"Correct answer: {ans['correct']}")
            print(f"Points: {ans['points']}/{ans['max_points']}")
            print(f"\n💡 Explanation: {ans['explanation']}")

    def restart(self):
        """Ask to restart quiz"""
        print("\n" + "=" * 50)
        choice = input("\nTake quiz again? (y/n): ").lower()
        if choice == 'y':
            self.score = 0
            self.max_score = 0
            self.answers = []
            self.questions = self.load_questions("questionsfor3.json")
            self.start()
        else:
            print("\n🎓 Thanks for playing! Keep learning!")
            print("=" * 50 + "\n")


if __name__ == "__main__":
    quiz = Quiz()
    quiz.start()
    quiz.restart()