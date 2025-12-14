"""
Spades Card Game - Educational Implementation
A full-featured Spades game with tutorial, statistics tracking, and save/load functionality.

Major Topics Covered:
1. GUI (Tkinter)
2. File I/O (JSON save/load)
3. Data Analysis (Statistics tracking and visualization)
4. Error Handling (Try-catch blocks, input validation)
5. Object-Oriented Programming (Classes, encapsulation)

Author: [Your Name]
Date: December 2024
AI Assistance: Used for code refactoring, bug fixes, and feature suggestions
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import random
import json
import os
from datetime import datetime
from collections import defaultdict

# Constants
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i+2 for i, r in enumerate(RANKS)}
WINNING_SCORE = 300
STATS_FILE = 'spades_stats.json'
SAVE_FILE = 'spades_save.json'

# Color scheme constants
COLOR_GREEN_DARK = '#2d5016'
COLOR_GREEN_MID = '#1a3a0f'
COLOR_GREEN_LIGHT = '#1a5016'
COLOR_YELLOW = '#ffeb3b'
COLOR_WHITE = 'white'
COLOR_BLACK = 'black'
COLOR_RED = 'red'

class Card:
    """
    Represents a playing card with a suit and rank.
    
    Attributes:
        suit (str): Card suit (♠, ♥, ♦, ♣)
        rank (str): Card rank (2-10, J, Q, K, A)
    """
    def __init__(self, suit, rank):
        assert suit in SUITS, f"Invalid suit: {suit}"
        assert rank in RANKS, f"Invalid rank: {rank}"
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        return f"{self.rank}{self.suit}"
    
    def is_red(self):
        """Check if card is red (hearts or diamonds)"""
        return self.suit in ['♥', '♦']
    
    def to_dict(self):
        """Convert card to dictionary for JSON serialization"""
        return {'suit': self.suit, 'rank': self.rank}
    
    @staticmethod
    def from_dict(data):
        """Create card from dictionary"""
        return Card(data['suit'], data['rank'])

class GameStats:
    """
    Tracks game statistics including wins, losses, and performance metrics.
    Implements File I/O and Data Analysis requirements.
    """
    def __init__(self):
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Load statistics from JSON file (File I/O)"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
            return self.initialize_stats()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading stats: {e}")
            return self.initialize_stats()
    
    def initialize_stats(self):
        """Initialize empty statistics dictionary"""
        return {
            'games_played': 0,
            'games_won': 0,
            'games_lost': 0,
            'total_points_scored': 0,
            'bids_made': 0,
            'bids_missed': 0,
            'deals_successful': 0,
            'deals_failed': 0,
            'bags_accumulated': 0,
            'sandbagged_count': 0,
            'game_history': []
        }
    
    def save_stats(self):
        """Save statistics to JSON file (File I/O)"""
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except IOError as e:
            print(f"Error saving stats: {e}")
    
    def record_game(self, won, final_score, rounds_played):
        """Record game results for data analysis"""
        self.stats['games_played'] += 1
        if won:
            self.stats['games_won'] += 1
        else:
            self.stats['games_lost'] += 1
        
        self.stats['game_history'].append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'won': won,
            'score': final_score,
            'rounds': rounds_played
        })
        
        # Keep only last 50 games
        if len(self.stats['game_history']) > 50:
            self.stats['game_history'] = self.stats['game_history'][-50:]
        
        self.save_stats()
    
    def record_bid_result(self, made_bid, was_deal=False):
        """Track bidding success rate"""
        if was_deal:
            if made_bid:
                self.stats['deals_successful'] += 1
            else:
                self.stats['deals_failed'] += 1
        else:
            if made_bid:
                self.stats['bids_made'] += 1
            else:
                self.stats['bids_missed'] += 1
        self.save_stats()
    
    def get_win_rate(self):
        """Calculate win rate (Data Analysis)"""
        if self.stats['games_played'] == 0:
            return 0.0
        return (self.stats['games_won'] / self.stats['games_played']) * 100
    
    def get_bid_success_rate(self):
        """Calculate bid success rate (Data Analysis)"""
        total = self.stats['bids_made'] + self.stats['bids_missed']
        if total == 0:
            return 0.0
        return (self.stats['bids_made'] / total) * 100
    
    def get_summary(self):
        """Generate statistics summary string"""
        return f"""Game Statistics:
        
Games Played: {self.stats['games_played']}
Win Rate: {self.get_win_rate():.1f}%
Bid Success Rate: {self.get_bid_success_rate():.1f}%

Bids Made: {self.stats['bids_made']}
Bids Missed: {self.stats['bids_missed']}
Deals Successful: {self.stats['deals_successful']}
Deals Failed: {self.stats['deals_failed']}

Bags: {self.stats['bags_accumulated']}
Sandbagged: {self.stats['sandbagged_count']} times"""

class SpadesGame:
    """
    Main game class managing all game state, UI, and logic.
    Implements comprehensive error handling and robust game management.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Spades to 300")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLOR_GREEN_DARK)
        
        # Game state
        self.game_state = 'tutorial'
        self.hands = [[], [], [], []]
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.current_player = 0
        self.lead_suit = None
        self.spades_broken = False
        self.scores = [[0, 0], [0, 0]]  # [points, bags] for each team
        self.tutorial_step = 0
        self.rounds_played = 0
        
        # Statistics tracking
        self.stats = GameStats()
        
        self.tutorials = [
            "Welcome to Spades! 4 players, 2 teams.\nYou and North vs East and West.",
            "Goal: First team to 300 wins!\nBid tricks each round. Spades are trump!",
            "Each player gets 13 cards.",
            "Everyone bids (1-13). Team bids add up.",
            "DEAL: Bet you won't win ANY tricks!\n+100 if success, -100 if fail.",
            "Follow suit if possible. Can't lead spades until broken.",
            "Highest card wins, unless spade played.",
            "Score: Make bid = 10 × bid + extra. Fail = -10 × bid.",
            "Play rounds until 300. Ready?"
        ]
        
        self.setup_ui()
        self.show_tutorial()
    
    def setup_ui(self):
        """Initialize all UI components with proper error handling"""
        try:
            self.main_frame = tk.Frame(self.root, bg=COLOR_GREEN_DARK)
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            tk.Label(self.main_frame, text="♠ Spades to 300 ♠", 
                    font=('Arial', 28, 'bold'), bg=COLOR_GREEN_DARK, fg=COLOR_BLACK).pack(pady=10)
            
            # Menu bar
            menu_frame = tk.Frame(self.main_frame, bg=COLOR_GREEN_DARK)
            menu_frame.pack()
            
            tk.Button(menu_frame, text="💾 Save Game", font=('Arial', 9), bg='#4caf50', 
                     fg=COLOR_WHITE, command=self.save_game).pack(side=tk.LEFT, padx=2)
            tk.Button(menu_frame, text="📂 Load Game", font=('Arial', 9), bg='#2196f3', 
                     fg=COLOR_WHITE, command=self.load_game).pack(side=tk.LEFT, padx=2)
            tk.Button(menu_frame, text="📊 Statistics", font=('Arial', 9), bg='#ff9800', 
                     fg=COLOR_WHITE, command=self.show_statistics).pack(side=tk.LEFT, padx=2)
            tk.Button(menu_frame, text="🔄 New Game", font=('Arial', 9), bg='#f44336', 
                     fg=COLOR_WHITE, command=self.confirm_new_game).pack(side=tk.LEFT, padx=2)
            
            # Score display
            score_frame = tk.Frame(self.main_frame, bg=COLOR_GREEN_DARK)
            score_frame.pack(pady=5)
            
            # Team 1
            team1_frame = tk.Frame(score_frame, bg=COLOR_GREEN_MID, relief=tk.RAISED, bd=2)
            team1_frame.pack(side=tk.LEFT, padx=10)
            tk.Label(team1_frame, text="Team 1 (You & North)", 
                    font=('Arial', 12, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK).pack(pady=3)
            self.team1_score = tk.Label(team1_frame, text="0/300", 
                                        font=('Arial', 16, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK)
            self.team1_score.pack()
            self.team1_bags = tk.Label(team1_frame, text="Bags: 0", 
                                       font=('Arial', 9), bg=COLOR_GREEN_MID, fg=COLOR_BLACK)
            self.team1_bags.pack(pady=3)
            
            # Team 2
            team2_frame = tk.Frame(score_frame, bg=COLOR_GREEN_MID, relief=tk.RAISED, bd=2)
            team2_frame.pack(side=tk.LEFT, padx=10)
            tk.Label(team2_frame, text="Team 2 (East & West)", 
                    font=('Arial', 12, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK).pack(pady=3)
            self.team2_score = tk.Label(team2_frame, text="0/300", 
                                        font=('Arial', 16, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK)
            self.team2_score.pack()
            self.team2_bags = tk.Label(team2_frame, text="Bags: 0", 
                                       font=('Arial', 9), bg=COLOR_GREEN_MID, fg=COLOR_BLACK)
            self.team2_bags.pack(pady=3)
            
            # Message area
            msg_frame = tk.Frame(self.main_frame, bg=COLOR_YELLOW, relief=tk.RAISED, bd=2)
            msg_frame.pack(pady=5, padx=10, fill=tk.X)
            self.msg_label = tk.Label(msg_frame, text="Welcome!", 
                                      font=('Arial', 11), bg=COLOR_YELLOW, wraplength=900)
            self.msg_label.pack(pady=5, padx=5)
            
            self.game_frame = tk.Frame(self.main_frame, bg=COLOR_GREEN_DARK)
            self.game_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            self.hint_btn = tk.Button(self.main_frame, text="💡 Hint", 
                                     font=('Arial', 10, 'bold'), bg='#2196f3', fg=COLOR_WHITE,
                                     command=self.show_hint, state=tk.DISABLED)
            self.hint_btn.pack(pady=3)
            
        except Exception as e:
            messagebox.showerror("UI Error", f"Failed to initialize interface: {e}")
    
    def save_game(self):
        """Save current game state to JSON file (File I/O requirement)"""
        try:
            if self.game_state == 'tutorial':
                messagebox.showinfo("Cannot Save", "Start a game first!")
                return
            
            # Convert Card objects to dictionaries
            hands_serializable = [[card.to_dict() for card in hand] for hand in self.hands]
            trick_serializable = [{'player': p['player'], 'card': p['card'].to_dict()} 
                                 for p in self.current_trick]
            
            game_data = {
                'game_state': self.game_state,
                'hands': hands_serializable,
                'bids': self.bids,
                'deal_bids': self.deal_bids,
                'tricks': self.tricks,
                'current_trick': trick_serializable,
                'current_player': self.current_player,
                'lead_suit': self.lead_suit,
                'spades_broken': self.spades_broken,
                'scores': self.scores,
                'rounds_played': self.rounds_played,
                'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(SAVE_FILE, 'w') as f:
                json.dump(game_data, f, indent=2)
            
            messagebox.showinfo("Game Saved", "Your game has been saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save game: {e}")
    
    def load_game(self):
        """Load game state from JSON file (File I/O requirement)"""
        try:
            if not os.path.exists(SAVE_FILE):
                messagebox.showinfo("No Save File", "No saved game found!")
                return
            
            with open(SAVE_FILE, 'r') as f:
                game_data = json.load(f)
            
            # Restore game state with validation
            assert 'game_state' in game_data, "Invalid save file: missing game_state"
            
            self.game_state = game_data['game_state']
            self.hands = [[Card.from_dict(c) for c in hand] for hand in game_data['hands']]
            self.bids = game_data['bids']
            self.deal_bids = game_data['deal_bids']
            self.tricks = game_data['tricks']
            self.current_trick = [{'player': p['player'], 'card': Card.from_dict(p['card'])} 
                                 for p in game_data['current_trick']]
            self.current_player = game_data['current_player']
            self.lead_suit = game_data.get('lead_suit')
            self.spades_broken = game_data['spades_broken']
            self.scores = game_data['scores']
            self.rounds_played = game_data.get('rounds_played', 0)
            
            # Refresh display
            if self.game_state == 'playing':
                self.show_playing()
            elif self.game_state == 'bidding':
                self.show_bidding()
            
            self.update_scores()
            messagebox.showinfo("Game Loaded", 
                              f"Game loaded from {game_data.get('saved_at', 'unknown time')}")
            
        except (json.JSONDecodeError, KeyError, AssertionError) as e:
            messagebox.showerror("Load Error", f"Failed to load game: {e}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Unexpected error loading game: {e}")
    
    def show_statistics(self):
        """Display game statistics (Data Analysis requirement)"""
        try:
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Game Statistics")
            stats_window.geometry("400x450")
            stats_window.configure(bg=COLOR_WHITE)
            
            tk.Label(stats_window, text="📊 Your Spades Statistics", 
                    font=('Arial', 16, 'bold'), bg=COLOR_WHITE).pack(pady=15)
            
            stats_text = tk.Text(stats_window, font=('Courier', 11), width=40, height=18,
                                bg='#f0f0f0', relief=tk.SUNKEN, bd=2)
            stats_text.pack(pady=10, padx=20)
            stats_text.insert('1.0', self.stats.get_summary())
            stats_text.config(state=tk.DISABLED)
            
            btn_frame = tk.Frame(stats_window, bg=COLOR_WHITE)
            btn_frame.pack(pady=10)
            
            tk.Button(btn_frame, text="Reset Stats", font=('Arial', 10), bg='#f44336', 
                     fg=COLOR_WHITE, command=lambda: self.reset_stats(stats_window)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Close", font=('Arial', 10), bg='#757575', 
                     fg=COLOR_WHITE, command=stats_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Statistics Error", f"Failed to display statistics: {e}")
    
    def reset_stats(self, window):
        """Reset all statistics with confirmation"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all statistics?"):
            self.stats.stats = self.stats.initialize_stats()
            self.stats.save_stats()
            window.destroy()
            messagebox.showinfo("Stats Reset", "All statistics have been reset.")
    
    def confirm_new_game(self):
        """Confirm before starting new game"""
        if self.game_state != 'tutorial':
            if messagebox.askyesno("New Game", "Start a new game? Current progress will be lost."):
                self.scores = [[0, 0], [0, 0]]
                self.rounds_played = 0
                self.start_game()
        else:
            self.start_game()
    
    def show_tutorial(self):
        """Display tutorial screen"""
        try:
            for w in self.game_frame.winfo_children():
                w.destroy()
            
            frame = tk.Frame(self.game_frame, bg=COLOR_WHITE, relief=tk.RAISED, bd=4)
            frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            tk.Label(frame, text=f"Tutorial {self.tutorial_step + 1}/{len(self.tutorials)}", 
                    font=('Arial', 16, 'bold'), bg=COLOR_WHITE, fg=COLOR_BLACK).pack(pady=15, padx=20)
            
            tk.Label(frame, text=self.tutorials[self.tutorial_step], 
                    font=('Arial', 12), bg=COLOR_WHITE, fg=COLOR_BLACK, wraplength=500).pack(pady=15, padx=20)
            
            btn_frame = tk.Frame(frame, bg=COLOR_WHITE)
            btn_frame.pack(pady=15)
            
            if self.tutorial_step > 0:
                tk.Button(btn_frame, text="Previous", font=('Arial', 11), bg='#757575', 
                         fg=COLOR_WHITE, padx=15, pady=8, 
                         command=lambda: self.change_tutorial(-1)).pack(side=tk.LEFT, padx=5)
            
            if self.tutorial_step < len(self.tutorials) - 1:
                tk.Button(btn_frame, text="Next", font=('Arial', 11), bg='#4caf50', 
                         fg=COLOR_WHITE, padx=15, pady=8,
                         command=lambda: self.change_tutorial(1)).pack(side=tk.LEFT, padx=5)
            else:
                tk.Button(btn_frame, text="Start Game!", font=('Arial', 12, 'bold'), 
                         bg='#2196f3', fg=COLOR_WHITE, padx=20, pady=8,
                         command=self.start_game).pack(side=tk.LEFT, padx=5)
                         
        except Exception as e:
            messagebox.showerror("Tutorial Error", f"Error displaying tutorial: {e}")
    
    def change_tutorial(self, direction):
        """Navigate tutorial steps"""
        self.tutorial_step += direction
        self.show_tutorial()
    
    def start_game(self):
        """Initialize new game"""
        self.game_state = 'bidding'
        self.rounds_played = 0
        self.deal_cards()
    
    def deal_cards(self):
        """Deal cards to all players with validation"""
        try:
            deck = [Card(s, r) for s in SUITS for r in RANKS]
            assert len(deck) == 52, "Invalid deck size"
            random.shuffle(deck)
            
            self.hands = [deck[i::4] for i in range(4)]
            for hand in self.hands:
                hand.sort(key=lambda c: (SUITS.index(c.suit), RANK_VALUES[c.rank]))
            
            self.bids = [None] * 4
            self.deal_bids = [False] * 4
            self.tricks = [0] * 4
            self.current_trick = []
            self.spades_broken = False
            self.rounds_played += 1
            
            self.msg_label.config(text="Bid tricks you'll win, or bid DEAL!")
            self.show_bidding()
            
        except Exception as e:
            messagebox.showerror("Deal Error", f"Error dealing cards: {e}")
            self.start_game()
    
    def show_bidding(self):
        """Display bidding interface"""
        try:
            for w in self.game_frame.winfo_children():
                w.destroy()
            
            # Show hand
            hand_frame = tk.Frame(self.game_frame, bg=COLOR_GREEN_DARK)
            hand_frame.pack(side=tk.BOTTOM, pady=10)
            tk.Label(hand_frame, text="Your Hand:", font=('Arial', 12, 'bold'), 
                    bg=COLOR_GREEN_DARK, fg=COLOR_BLACK).pack()
            cards_frame = tk.Frame(hand_frame, bg=COLOR_GREEN_DARK)
            cards_frame.pack()
            for card in self.hands[0]:
                self.make_card(cards_frame, card).pack(side=tk.LEFT, padx=1)
            
            # Bid options
            bid_frame = tk.Frame(self.game_frame, bg=COLOR_WHITE, relief=tk.RAISED, bd=4)
            bid_frame.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
            
            tk.Label(bid_frame, text="Place Your Bid", font=('Arial', 16, 'bold'), 
                    bg=COLOR_WHITE, fg=COLOR_BLACK).pack(pady=8)
            
            tk.Button(bid_frame, text="🤝 DEAL (+100 for 0 tricks, -100 if any)", 
                     font=('Arial', 11, 'bold'), bg='#f44336', fg=COLOR_BLACK, 
                     padx=15, pady=8, command=lambda: self.make_bid(0, True)).pack(pady=8)
            
            num_frame = tk.Frame(bid_frame, bg=COLOR_WHITE)
            num_frame.pack(pady=8)
            for i in range(1, 14):
                tk.Button(num_frame, text=str(i), font=('Arial', 12, 'bold'), 
                         bg='#2196f3', fg=COLOR_BLACK, width=3,
                         command=lambda b=i: self.make_bid(b, False)).grid(
                             row=(i-1)//7, column=(i-1)%7, padx=3, pady=3)
            
            self.hint_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Bidding Error", f"Error displaying bidding: {e}")
    
    def make_bid(self, bid, is_deal):
        """Process player's bid with validation"""
        try:
            assert 0 <= bid <= 13, f"Invalid bid: {bid}"
            self.bids[0] = 0 if is_deal else bid
            self.deal_bids[0] = is_deal
            self.msg_label.config(text=f"You bid {'DEAL' if is_deal else bid}. AI bidding...")
            self.root.after(1000, self.ai_bids)
        except AssertionError as e:
            messagebox.showerror("Invalid Bid", str(e))
    
    def ai_bids(self):
        """AI players make bids"""
        for i in range(1, 4):
            if random.random() < 0.15:
                self.bids[i] = 0
                self.deal_bids[i] = True
            else:
                self.bids[i] = random.randint(1, 5)
        
        self.msg_label.config(text="Bidding done! You lead!")
        self.game_state = 'playing'
        self.current_player = 0
        self.show_playing()
    
    def show_playing(self):
        """Display main playing interface"""
        try:
            for w in self.game_frame.winfo_children():
                w.destroy()
            
            # North player
            north = tk.Frame(self.game_frame, bg=COLOR_GREEN_MID, relief=tk.RAISED, bd=2)
            north.pack(side=tk.TOP, pady=5)
            tk.Label(north, text=f"North - {self.bid_text(2)} | Won: {self.tricks[2]}", 
                    font=('Arial', 10, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK).pack(pady=3)
            nc = tk.Frame(north, bg=COLOR_GREEN_MID)
            nc.pack()
            for card in self.hands[2]:
                self.make_card(nc, card, clickable=False).pack(side=tk.LEFT, padx=1)
            
            # Middle section
            mid = tk.Frame(self.game_frame, bg=COLOR_GREEN_DARK)
            mid.pack(fill=tk.BOTH, expand=True)
            
            # West player
            west = tk.Frame(mid, bg=COLOR_GREEN_MID, relief=tk.RAISED, bd=2)
            west.pack(side=tk.LEFT, padx=5, anchor=tk.W)
            tk.Label(west, text=f"West\n{self.bid_text(3)}\nWon: {self.tricks[3]}", 
                    font=('Arial', 9, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK).pack(pady=3)
            for card in self.hands[3]:
                self.make_card(west, card, clickable=False).pack(pady=1)
            
            # Center trick area
            center = tk.Frame(mid, bg=COLOR_GREEN_LIGHT, relief=tk.SUNKEN, bd=4, width=350, height=250)
            center.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
            center.pack_propagate(False)
            
            if self.current_trick:
                trick = tk.Frame(center, bg=COLOR_GREEN_LIGHT)
                trick.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                names = ['You', 'East', 'North', 'West']
                for play in self.current_trick:
                    cf = tk.Frame(trick, bg=COLOR_GREEN_LIGHT)
                    cf.pack(side=tk.LEFT, padx=8)
                    self.make_card(cf, play['card'], False).pack()
                    tk.Label(cf, text=names[play['player']], 
                            font=('Arial', 9), bg=COLOR_GREEN_LIGHT, fg=COLOR_BLACK).pack()
            
            # East player
            east = tk.Frame(mid, bg=COLOR_GREEN_MID, relief=tk.RAISED, bd=2)
            east.pack(side=tk.LEFT, padx=5, anchor=tk.E)
            tk.Label(east, text=f"East\n{self.bid_text(1)}\nWon: {self.tricks[1]}", 
                    font=('Arial', 9, 'bold'), bg=COLOR_GREEN_MID, fg=COLOR_BLACK).pack(pady=3)
            for card in self.hands[1]:
                self.make_card(east, card, clickable=False).pack(pady=1)
            
            # Your hand
            hand = tk.Frame(self.game_frame, bg=COLOR_GREEN_DARK)
            hand.pack(side=tk.BOTTOM, pady=5)
            tk.Label(hand, text="Your Hand:", font=('Arial', 12, 'bold'), 
                    bg=COLOR_GREEN_DARK, fg=COLOR_BLACK).pack()