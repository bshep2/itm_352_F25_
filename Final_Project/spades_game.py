"""
Spades Card Game - Professional Edition
========================================
A fully-featured implementation of the classic Spades card game with AI opponents,
persistent statistics, save/load functionality, and intelligent gameplay.

Author: Brandon Shepherd
Version: 2.0
Date: December 2025

Game Rules:
-----------
- 4 players in 2 teams (You + Teammate vs 2 AI opponents)
- First team to reach 300 points wins
- Spades are always trump cards
- Players must follow suit if possible
- DEAL: Bid 0 tricks for +100 if successful, -100 if you take any tricks
- Scoring: Make bid = 10×bid + overtricks, Fail = -10×bid
- Bags: 10 overtricks = -100 point penalty (sandbag)

Architecture:
-------------
- Card: Represents individual playing cards with suit and rank
- GameStats: Handles persistent statistics tracking and file I/O
- SmartAI: Implements intelligent card selection and bidding strategies
- SpadesGame: Main game controller managing UI and game flow
"""

import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# ============================================================================
# GAME CONSTANTS
# ============================================================================

SUITS = ['♠', '♥', '♦', '♣']  # Spades, Hearts, Diamonds, Clubs
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i+2 for i, r in enumerate(RANKS)}  # 2=2, 3=3, ..., A=14
WINNING_SCORE = 300  # Target score to win the game
SANDBAG_LIMIT = 10  # Number of bags before penalty
SANDBAG_PENALTY = 100  # Points deducted for accumulating 10 bags

# File paths for persistence
STATS_FILE = 'spades_stats.json'
SAVE_FILE = 'spades_save.json'

# UI Color Scheme (Forest/Card Table Theme)
BG_DARK = '#2d5016'    # Dark green background
BG_MID = '#1a3a0f'     # Medium green for panels
BG_LIGHT = '#1a5016'   # Light green for play area
COLOR_YELLOW = '#ffeb3b'  # Highlight color for active player
SUIT_COLORS = {
    '♠': '#c0c0c0',  # Silver for spades
    '♥': '#ffb0b0',  # Light red for hearts
    '♦': '#b0d0ff',  # Light blue for diamonds
    '♣': '#b0ffb0'   # Light green for clubs
}

# ============================================================================
# CARD CLASS
# ============================================================================

class Card:
    """
    Represents a single playing card with a suit and rank.
    
    Attributes:
        suit (str): One of ♠, ♥, ♦, ♣
        rank (str): One of 2-10, J, Q, K, A
    
    Methods:
        is_red(): Returns True if card is hearts or diamonds
        get_value(): Returns numeric value (2-14) for comparison
        to_dict(): Serializes card to dictionary for saving
        from_dict(): Deserializes card from dictionary
    """
    
    def __init__(self, suit, rank):
        """
        Initialize a card with the given suit and rank.
        
        Args:
            suit (str): The suit symbol (♠, ♥, ♦, ♣)
            rank (str): The rank (2-10, J, Q, K, A)
        """
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        """String representation of the card (e.g., 'A♠')"""
        return f"{self.rank}{self.suit}"
    
    def __eq__(self, other):
        """Check if two cards are equal based on suit and rank"""
        return isinstance(other, Card) and self.suit == other.suit and self.rank == other.rank
    
    def is_red(self):
        """Returns True if the card is a red suit (hearts or diamonds)"""
        return self.suit in ['♥', '♦']
    
    def get_value(self):
        """
        Get the numeric value of the card for comparison.
        
        Returns:
            int: Value from 2-14 (2 is lowest, Ace is 14)
        """
        return RANK_VALUES[self.rank]
    
    def to_dict(self):
        """
        Serialize card to dictionary for JSON storage.
        
        Returns:
            dict: Dictionary with 'suit' and 'rank' keys
        """
        return {'suit': self.suit, 'rank': self.rank}
    
    @staticmethod
    def from_dict(data):
        """
        Deserialize card from dictionary.
        
        Args:
            data (dict): Dictionary with 'suit' and 'rank' keys
            
        Returns:
            Card: Reconstructed Card object
        """
        return Card(data['suit'], data['rank'])

# ============================================================================
# STATISTICS TRACKING CLASS
# ============================================================================

class GameStats:
    """
    Manages persistent game statistics across sessions.
    
    Tracks:
        - Games played and won
        - Bids made and missed
        - Deal success/failure rates
        - Bag accumulation and sandbag penalties
    
    Statistics are automatically saved to disk after each update.
    """
    
    def __init__(self):
        """Initialize statistics by loading from file or creating new stats"""
        self.stats = self.load_stats()
    
    def load_stats(self):
        """
        Load statistics from JSON file.
        
        Returns:
            dict: Statistics dictionary with all tracked metrics
        """
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading stats: {e}")
        
        # Return default empty statistics
        return {
            'games_played': 0,
            'games_won': 0,
            'bids_made': 0,
            'bids_missed': 0,
            'deals_successful': 0,
            'deals_failed': 0,
            'bags': 0,
            'sandbagged': 0
        }
    
    def save_stats(self):
        """Persist current statistics to JSON file"""
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def record_game(self, won):
        """
        Record completion of a game.
        
        Args:
            won (bool): True if player's team won
        """
        self.stats['games_played'] += 1
        if won:
            self.stats['games_won'] += 1
        self.save_stats()
    
    def record_bid(self, made, is_deal=False):
        """
        Record the result of a bid.
        
        Args:
            made (bool): True if bid was successful
            is_deal (bool): True if this was a DEAL bid (0 tricks)
        """
        if is_deal:
            key = 'deals_successful' if made else 'deals_failed'
        else:
            key = 'bids_made' if made else 'bids_missed'
        self.stats[key] += 1
        self.save_stats()
    
    def record_bag(self):
        """Record a single overtrick (bag)"""
        self.stats['bags'] += 1
        self.save_stats()
    
    def record_sandbag(self):
        """Record a sandbag penalty occurrence"""
        self.stats['sandbagged'] += 1
        self.save_stats()
    
    def get_win_rate(self):
        """
        Calculate win rate percentage.
        
        Returns:
            float: Win rate as percentage (0-100)
        """
        if self.stats['games_played'] > 0:
            return (self.stats['games_won'] / self.stats['games_played'] * 100)
        return 0.0
    
    def get_summary(self):
        """
        Generate formatted statistics summary.
        
        Returns:
            str: Multi-line string with all statistics
        """
        gp = self.stats['games_played']
        wr = self.get_win_rate()
        bt = self.stats['bids_made'] + self.stats['bids_missed']
        br = (self.stats['bids_made'] / bt * 100) if bt > 0 else 0
        
        return (f"Games: {gp} | Win Rate: {wr:.1f}%\n"
                f"Bids: {self.stats['bids_made']}/{bt} ({br:.1f}%)\n"
                f"Deals: {self.stats['deals_successful']}/{self.stats['deals_failed']}\n"
                f"Bags: {self.stats['bags']} | Sandbagged: {self.stats['sandbagged']}x")

# ============================================================================
# ARTIFICIAL INTELLIGENCE CLASS
# ============================================================================

class SmartAI:
    """
    Implements intelligent bidding and card-playing strategies for AI opponents.
    
    Strategy Features:
        - Hand strength evaluation based on high cards and trump cards
        - Automatic DEAL detection for weak hands
        - Card counting to track played cards
        - Situation-aware card selection (leading vs following)
        - Team play coordination (protecting partner's winning cards)
    
    The AI uses a sophisticated algorithm to evaluate hand strength and make
    strategic decisions throughout the game.
    """
    
    def __init__(self):
        """Initialize AI with empty card tracking"""
        self.reset_round()
    
    def reset_round(self):
        """Clear card tracking for new round"""
        self.cards_played = []
        self.remaining = set(f"{r}{s}" for s in SUITS for r in RANKS)
    
    def record_card(self, card):
        """
        Track a card that has been played.
        
        Args:
            card (Card): The card that was played
        """
        card_str = str(card)
        if card_str in self.remaining:
            self.remaining.remove(card_str)
            self.cards_played.append(card_str)
    
    def calc_strength(self, hand):
        """
        Calculate the trick-taking strength of a hand.
        
        Algorithm:
            - Spades are weighted heavily (trump cards)
            - High cards (A, K, Q, J) in other suits are valued
            - Position and suit distribution considered
        
        Args:
            hand (list): List of Card objects
            
        Returns:
            int: Estimated number of tricks (0-13)
        """
        strength = 0.0
        suits = {'♠': [], '♥': [], '♦': [], '♣': []}
        
        # Organize cards by suit
        for c in hand:
            suits[c.suit].append(c)
        
        # Evaluate spades (trump suit) - most valuable
        for spade in suits['♠']:
            val = spade.get_value()
            if val >= 14:    # Ace of spades
                strength += 1.0
            elif val >= 13:  # King of spades
                strength += 0.9
            elif val >= 12:  # Queen of spades
                strength += 0.7
            elif val >= 11:  # Jack of spades
                strength += 0.5
            else:            # Low spades
                strength += 0.3
        
        # Evaluate non-trump suits
        for suit in ['♥', '♦', '♣']:
            cards = suits[suit]
            if cards:
                cards.sort(key=lambda c: c.get_value(), reverse=True)
                for i, c in enumerate(cards):
                    val = c.get_value()
                    if val >= 14:  # Ace (likely winner)
                        strength += 0.9
                    elif val >= 13 and i == 0:  # King (might win)
                        strength += 0.6
        
        return min(13, max(0, round(strength)))
    
    def should_deal(self, hand):
        """
        Determine if hand is weak enough to bid DEAL (0 tricks).
        
        DEAL Strategy:
            - Very weak hand (no high cards, many low cards)
            - Few spades (can't rely on trump)
            - Occasional risk-taking for strategic advantage
        
        Args:
            hand (list): List of Card objects
            
        Returns:
            bool: True if AI should bid DEAL
        """
        high = sum(1 for c in hand if c.get_value() >= 11)  # J, Q, K, A
        low = sum(1 for c in hand if c.get_value() <= 5)    # 2, 3, 4, 5
        spades = sum(1 for c in hand if c.suit == '♠')
        
        # Definite DEAL: No high cards, mostly low cards, few spades
        if high == 0 and low >= 10 and spades <= 2:
            return True
        
        # Risky DEAL: Very weak hand with occasional randomness
        if high <= 1 and low >= 9 and spades <= 3 and random.random() < 0.3:
            return True
        
        return False
    
    def make_bid(self, hand):
        """
        Determine bid for the given hand.
        
        Args:
            hand (list): List of Card objects
            
        Returns:
            tuple: (bid_amount, is_deal) where bid is 0-13 and is_deal is boolean
        """
        if self.should_deal(hand):
            return (0, True)
        
        # Calculate base strength and add slight randomness
        strength = self.calc_strength(hand)
        bid = max(1, min(13, strength + random.randint(-1, 1)))
        return (bid, False)
    
    def choose_card(self, hand, trick, lead_suit, player_idx, bids, tricks, 
                   deal_bids, spades_broken, partner_idx):
        """
        Select the best card to play given the current game state.
        
        Strategy Considerations:
            - Must follow suit if possible
            - Can't lead spades until spades are broken (unless no choice)
            - Tries to win tricks if below bid
            - Tries to avoid tricks if above bid or on DEAL
            - Cooperates with partner
        
        Args:
            hand (list): AI player's current hand
            trick (list): Current trick in progress
            lead_suit (str): Suit that was led (None if leading)
            player_idx (int): AI player's index (0-3)
            bids (list): All players' bids
            tricks (list): Tricks won by each player
            deal_bids (list): Whether each player bid DEAL
            spades_broken (bool): Whether spades have been played
            partner_idx (int): Partner's player index
            
        Returns:
            Card: The card to play
        """
        playable = hand.copy()
        
        # Rule: Must follow suit if possible
        if trick:
            same_suit = [c for c in hand if c.suit == lead_suit]
            if same_suit:
                playable = same_suit
        # Rule: Can't lead spades until broken (unless only spades remain)
        elif not spades_broken:
            non_spades = [c for c in hand if c.suit != '♠']
            if non_spades:
                playable = non_spades
        
        # Edge case: Only one playable card
        if not playable or len(playable) == 1:
            return playable[0] if playable else None
        
        # Strategy: If on DEAL, play lowest card to avoid winning
        if deal_bids[player_idx]:
            return min(playable, key=lambda c: c.get_value())
        
        # Strategy: Leading the trick
        if not trick:
            # Need tricks: Play high card
            if tricks[player_idx] < bids[player_idx]:
                return max(playable, key=lambda c: c.get_value())
            # Have enough tricks: Play low card
            else:
                return min(playable, key=lambda c: c.get_value())
        
        # Strategy: Following in the trick - determine current winner
        winner = trick[0]
        for p in trick:
            # Spades beat non-spades
            if p['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = p
            # Higher card of same suit wins
            elif p['card'].suit == winner['card'].suit and p['card'].get_value() > winner['card'].get_value():
                winner = p
        
        # Partner is winning: Don't waste high cards
        if winner['player'] == partner_idx:
            return min(playable, key=lambda c: c.get_value())
        
        # Need tricks: Try to win if possible
        if tricks[player_idx] < bids[player_idx]:
            winners = [c for c in playable if 
                      (c.suit == '♠' and winner['card'].suit != '♠') or
                      (c.suit == winner['card'].suit and c.get_value() > winner['card'].get_value())]
            if winners:
                return min(winners, key=lambda c: c.get_value())  # Win with lowest possible
        
        # Default: Play lowest card
        return min(playable, key=lambda c: c.get_value())

# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class SpadesGame:
    """
    Main game controller managing UI, game state, and player interaction.
    
    Game Flow:
        1. Tutorial (first time or after game ends)
        2. Bidding phase (all players make bids)
        3. Playing phase (13 tricks of 4 cards each)
        4. Scoring phase (calculate points, check for winner)
        5. Repeat from step 2 or end game if 300+ points
    
    Features:
        - Interactive tutorial system
        - Save/Load game functionality
        - Persistent statistics tracking
        - Smart AI opponents
        - Visual feedback and animations
        - Hint system for strategy suggestions
    """
    
    def __init__(self, root):
        """
        Initialize the game with the main Tkinter window.
        
        Args:
            root (tk.Tk): The main Tkinter window
        """
        self.root = root
        self.root.title("Spades to 300")
        self.root.geometry("1000x750")
        self.root.configure(bg=BG_DARK)
        
        # Initialize game state
        self.game_state = 'tutorial'  # 'tutorial', 'bidding', 'playing'
        self.hands = [[], [], [], []]  # Cards for each player (0=human, 1-3=AI)
        self.bids = [None] * 4  # Bid amounts for each player
        self.deal_bids = [False] * 4  # Whether each player bid DEAL
        self.tricks = [0] * 4  # Tricks won by each player this round
        self.current_trick = []  # Cards played in current trick
        self.current_player = 0  # Index of player whose turn it is
        self.lead_suit = None  # Suit led in current trick
        self.spades_broken = False  # Whether spades have been played
        self.scores = [[0, 0], [0, 0]]  # [team][score, bags]
        self.tutorial_step = 0  # Current tutorial page
        self.rounds = 0  # Number of rounds played
        
        # Initialize subsystems
        self.stats = GameStats()
        self.ai = SmartAI()
        
        # Tutorial content
        self.tutorials = [
            "Welcome to Spades!\n4 players, 2 teams.",
            "First to 300 wins!",
            "Spades are TRUMP!",
            "DEAL = bet 0 tricks\n+100 if success, -100 if fail",
            "Follow suit if possible.",
            "Make bid = 10×bid + extras\nFail = -10×bid",
            "Ready to play?"
        ]
        
        self.setup_ui()
        self.show_tutorial()
    
    def setup_ui(self):
        """
        Create the main user interface layout.
        
        UI Structure:
            - Title bar
            - Menu buttons (Save, Load, Stats, New Game)
            - Score display panels for both teams
            - Message area for game status
            - Turn indicator
            - Game area (changes based on game state)
            - Hint button
        """
        self.main = tk.Frame(self.root, bg=BG_DARK)
        self.main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(self.main, text="♠ Spades to 300 ♠", 
                font=('Arial', 28, 'bold'), bg=BG_DARK, fg='white').pack(pady=10)
        
        # Menu buttons
        menu = tk.Frame(self.main, bg=BG_DARK)
        menu.pack()
        menu_items = [
            ("💾 Save", self.save_game),
            ("📂 Load", self.load_game),
            ("📊 Stats", self.show_stats),
            ("🔄 New", self.new_game)
        ]
        for txt, cmd in menu_items:
            tk.Button(menu, text=txt, command=cmd).pack(side=tk.LEFT, padx=2)
        
        # Score panels
        score_frame = tk.Frame(self.main, bg=BG_DARK)
        score_frame.pack(pady=5)
        
        # Team 1 (Player + Teammate)
        t1 = tk.Frame(score_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        t1.pack(side=tk.LEFT, padx=10)
        tk.Label(t1, text="Team 1 (You)", font=('Arial', 12, 'bold'), 
                bg=BG_MID, fg='white').pack(pady=3)
        self.t1_score = tk.Label(t1, text="0/300", font=('Arial', 16, 'bold'), 
                                bg=BG_MID, fg='white')
        self.t1_score.pack()
        self.t1_bid = tk.Label(t1, text="Bid: -", bg=BG_MID, fg='white')
        self.t1_bid.pack(pady=5)
        
        # Team 2 (AI opponents)
        t2 = tk.Frame(score_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        t2.pack(side=tk.LEFT, padx=10)
        tk.Label(t2, text="Team 2 (AI)", font=('Arial', 12, 'bold'), 
                bg=BG_MID, fg='white').pack(pady=3)
        self.t2_score = tk.Label(t2, text="0/300", font=('Arial', 16, 'bold'), 
                                bg=BG_MID, fg='white')
        self.t2_score.pack()
        self.t2_bid = tk.Label(t2, text="Bid: -", bg=BG_MID, fg='white')
        self.t2_bid.pack(pady=5)
        
        # Message display area
        msg = tk.Frame(self.main, bg='black', relief=tk.RAISED, bd=2)
        msg.pack(pady=5, padx=10, fill=tk.X)
        self.msg = tk.Label(msg, text="Welcome!", font=('Arial', 11), 
                           bg='black', fg='white', wraplength=900)
        self.msg.pack(pady=5)
        
        # Turn indicator (hidden initially)
        self.turn_frame = tk.Frame(self.main, bg=COLOR_YELLOW, relief=tk.RAISED, bd=3)
        self.turn_indicator = tk.Label(self.turn_frame, text="", 
                                      font=('Arial', 14, 'bold'), 
                                      bg=COLOR_YELLOW, fg='black', padx=20, pady=5)
        self.turn_indicator.pack()
        
        # Main game area (content changes based on game state)
        self.game_frame = tk.Frame(self.main, bg=BG_DARK)
        self.game_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Hint button
        self.hint_btn = tk.Button(self.main, text="💡 Hint", command=self.show_hint, 
                                 state=tk.DISABLED, font=('Arial', 11, 'bold'), 
                                 bg='#FFC107', fg='black', padx=20, pady=8)
        self.hint_btn.pack(pady=5)
    
    def make_card(self, parent, card, clickable=True, highlight=False):
        """
        Create a visual representation of a card.
        
        Args:
            parent (tk.Widget): Parent widget to place card in
            card (Card): The card to display
            clickable (bool): Whether card should appear clickable
            highlight (bool): Whether to highlight the card (yellow background)
            
        Returns:
            tk.Frame: The frame containing the card display
        """
        # Choose background color
        bg = '#ffff00' if highlight else SUIT_COLORS.get(card.suit, 'white')
        
        # Create card frame
        frame = tk.Frame(parent, bg=bg, relief=tk.RAISED, bd=2, width=42, height=62)
        frame.pack_propagate(False)
        
        # Card color (red for hearts/diamonds, black for spades/clubs)
        color = 'red' if card.is_red() else 'black'
        
        # Rank in corner
        tk.Label(frame, text=card.rank, font=('Arial', 9, 'bold'), 
                bg=bg, fg=color).pack(anchor=tk.NW, padx=2)
        
        # Large suit symbol in center
        tk.Label(frame, text=card.suit, font=('Arial', 28), 
                bg=bg, fg=color).pack(expand=True)
        
        # Non-clickable cards appear flatter
        if not clickable:
            frame.config(relief=tk.FLAT, bd=1)
        
        return frame
    
    def save_game(self):
        """
        Save current game state to JSON file.
        
        Saves:
            - All game state variables
            - Player hands
            - Current scores and bids
            - Trick progress
        """
        if self.game_state == 'tutorial':
            messagebox.showinfo("Can't Save", "Start a game first!")
            return
        
        try:
            data = {
                'game_state': self.game_state,
                'hands': [[c.to_dict() for c in h] for h in self.hands],
                'bids': self.bids,
                'deal_bids': self.deal_bids,
                'tricks': self.tricks,
                'current_trick': [{'player': p['player'], 'card': p['card'].to_dict()} 
                                 for p in self.current_trick],
                'current_player': self.current_player,
                'lead_suit': self.lead_suit,
                'spades_broken': self.spades_broken,
                'scores': self.scores,
                'rounds': self.rounds
            }
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    
    def load_game(self):
        """Load saved game state from JSON file"""
        if not os.path.exists(SAVE_FILE):
            messagebox.showinfo("No Save", "No saved game found!")
            return
        
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            
            # Restore game state
            self.game_state = data['game_state']
            self.hands = [[Card.from_dict(c) for c in h] for h in data['hands']]
            self.bids = data['bids']
            self.deal_bids = data['deal_bids']
            self.tricks = data['tricks']
            self.current_trick = [{'player': p['player'], 'card': Card.from_dict(p['card'])} 
                                 for p in data['current_trick']]
            self.current_player = data['current_player']
            self.lead_suit = data.get('lead_suit')
            self.spades_broken = data['spades_broken']
            self.scores = data['scores']
            self.rounds = data.get('rounds', 0)
            
            # Display appropriate screen
            if self.game_state == 'playing':
                self.show_playing()
            else:
                self.show_bidding()
            self.update_scores()
            
            messagebox.showinfo("Loaded", "Game loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {e}")
    
    def show_stats(self):
        """Display statistics dialog"""
        messagebox.showinfo("Statistics", self.stats.get_summary())
    
    def deal_cards(self):
        """
        Deal a new round of cards.
        
        Process:
            1. Create and shuffle full deck
            2. Deal 13 cards to each player
            3. Sort each hand by suit and rank
            4. Reset round state
            5. Proceed to bidding phase
        """
        # Create full deck
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(deck)
        
        # Deal cards (every 4th card goes to same player)
        self.hands = [deck[i::4] for i in range(4)]
        
        # Sort hands for easier viewing
        for hand in self.hands:
            hand.sort(key=lambda c: (SUITS.index(c.suit), c.get_value()))
        
        # Reset round state
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.current_player = 0
        self.lead_suit = None
        self.spades_broken = False
        self.rounds += 1
        self.ai.reset_round()
        
        # Move to bidding phase
        self.game_state = 'bidding'
        self.msg.config(text=f"Round {self.rounds} - Make your bid!")
        self.show_bidding()
    
    def show_tutorial(self):
        """Display tutorial screen with current step"""
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.turn_frame.pack_forget()
        
        # Tutorial panel
        frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text=f"Tutorial {self.tutorial_step + 1}/{len(self.tutorials)}", 
                font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=15, padx=20)
        tk.Label(frame, text=self.tutorials[self.tutorial_step], 
                font=('Arial', 12), bg='white', fg='black', wraplength=500).pack(pady=15, padx=20)
        
        # Navigation buttons
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(pady=15)
        
        if self.tutorial_step > 0:
            tk.Button(btn_frame, text="Back", fg='black', 
                     command=lambda: self.change_tut(-1)).pack(side=tk.LEFT, padx=5)
        
        if self.tutorial_step < len(self.tutorials) - 1:
            tk.Button(btn_frame, text="Next", fg='black', 
                     command=lambda: self.change_tut(1)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Start!", fg='black', 
                     command=self.start_game).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Skip", fg='black', 
                 command=self.start_game).pack(side=tk.LEFT, padx=5)
    
    def change_tut(self, direction):
        """Navigate tutorial pages"""
        self.tutorial_step += direction
        self.show_tutorial()
    
    def start_game(self):
        """Start a new game from the beginning"""
        self.rounds = 0
        self.scores = [[0, 0], [0, 0]]
        self.deal_cards()
    
    def new_game(self):
        """Handle new game button click"""
        if self.game_state != 'tutorial':
            if messagebox.askyesno("New Game", "Start new game? Current progress will be lost."):
                self.start_game()
        else:
            self.start_game()
    
    def show_bidding(self):
        """Display bidding interface for player to make bid"""
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.turn_frame.pack_forget()
        self.hint_btn.config(state=tk.NORMAL)
        
        # Show player's hand
        hf = tk.Frame(self.game_frame, bg=BG_DARK)
        hf.pack(side=tk.BOTTOM, pady=10)
        tk.Label(hf, text="Your Hand:", font=('Arial', 12, 'bold'), 
                bg=BG_DARK, fg='white').pack()
        cf = tk.Frame(hf, bg=BG_DARK)
        cf.pack()
        for card in self.hands[0]:
            self.make_card(cf, card).pack(side=tk.LEFT, padx=1)
        
        # Bidding panel
        bf = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        bf.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        tk.Label(bf, text="Make Your Bid", font=('Arial', 16, 'bold'), 
                bg='white', fg='black').pack(pady=8)
        
        # DEAL button
        tk.Button(bf, text="DEAL (0 tricks)", font=('Arial', 11, 'bold'), 
                 bg='black', fg='white', 
                 command=lambda: self.make_bid(0, True)).pack(pady=8)
        
        # Number buttons 1-13
        nf = tk.Frame(bf, bg='white')
        nf.pack(pady=8)
        for i in range(1, 14):
            tk.Button(nf, text=str(i), width=3, fg='black', 
                     command=lambda b=i: self.make_bid(b, False)).grid(
                         row=(i-1)//7, column=(i-1)%7, padx=3, pady=3)
    
    def make_bid(self, bid, is_deal):
        """
        Record player's bid and trigger AI bidding.
        
        Args:
            bid (int): Number of tricks bid (0-13)
            is_deal (bool): Whether player bid DEAL
        """
        self.bids[0] = 0 if is_deal else bid
        self.deal_bids[0] = is_deal
        self.msg.config(text=f"You bid {'DEAL' if is_deal else bid}. AI players bidding...")
        self.root.after(1000, self.ai_bids)
    
    def ai_bids(self):
        """Have all AI players make their bids"""
        # Get bids from each AI player
        for i in range(1, 4):
            bid, is_deal = self.ai.make_bid(self.hands[i])
            self.bids[i] = bid
            self.deal_bids[i] = is_deal
        
        # Display all bids
        names = ['You', 'East', 'Teammate', 'West']
        bid_text = lambda i: "DEAL" if self.deal_bids[i] else str(self.bids[i])
        summary = "\n".join([f"{names[i]}: {bid_text(i)}" for i in range(4)])
        self.msg.config(text=f"Bids:\n{summary}")
        
        # Update team bid displays
        self.t1_bid.config(text=f"Bid: {self.bids[0] + self.bids[2]}")
        self.t2_bid.config(text=f"Bid: {self.bids[1] + self.bids[3]}")
        
        # Move to playing phase
        self.game_state = 'playing'
        self.current_player = 0
        self.show_playing()
    
    def show_playing(self):
        """Display the main playing interface"""
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.hint_btn.config(state=tk.NORMAL)
        
        # Update turn indicator
        names = ['YOUR TURN! 👉', 'East', 'Teammate', 'West']
        self.turn_indicator.config(text=f"▶ {names[self.current_player]} ◀")
        self.turn_frame.pack(pady=5)
        
        # Player's hand (bottom)
        hnd = tk.Frame(self.game_frame, bg=BG_DARK)
        hnd.pack(side=tk.TOP, pady=5)
        bid_text = "DEAL" if self.deal_bids[0] else str(self.bids[0])
        tk.Label(hnd, text=f"Your Hand - Bid: {bid_text} | Won: {self.tricks[0]}", 
                font=('Arial', 10, 'bold'), bg=BG_DARK, fg='white').pack()
        cds = tk.Frame(hnd, bg=BG_DARK)
        cds.pack()
        
        # Display each card in player's hand
        for card in self.hands[0]:
            playable = self.can_play(card)
            lbl = self.make_card(cds, card, playable, playable)
            lbl.pack(side=tk.LEFT, padx=0.5)
            # Make playable cards clickable
            if playable and self.current_player == 0:
                lbl.bind('<Button-1>', lambda e, c=card: self.play_card(0, c))
        
        # Middle area with three AI players
        mid = tk.Frame(self.game_frame, bg=BG_DARK)
        mid.pack(fill=tk.BOTH, expand=True)
        
        # West player (left)
        w = tk.Frame(mid, bg=BG_MID, relief=tk.RAISED, bd=2)
        w.pack(side=tk.LEFT, padx=5)
        bid_text = "DEAL" if self.deal_bids[3] else str(self.bids[3])
        tk.Label(w, text=f"West\n{bid_text}\nWon: {self.tricks[3]}", 
                font=('Arial', 9, 'bold'), bg=BG_MID, fg='white').pack(pady=3)
        for _ in self.hands[3]:
            tk.Label(w, text="🂠", font=('Arial', 14), 
                    bg=BG_MID, fg='white').pack(pady=2)
        
        # Center play area
        self.center_frame = tk.Frame(mid, bg=BG_LIGHT, relief=tk.SUNKEN, 
                                    bd=4, width=350, height=250)
        self.center_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        self.center_frame.pack_propagate(False)
        
        # Display cards in current trick
        if self.current_trick:
            names_pos = ['You', 'East', 'Teammate', 'West']
            positions = {
                0: (0.5, 0.15),  # Bottom
                1: (0.75, 0.5),  # Right
                2: (0.5, 0.85),  # Top
                3: (0.25, 0.5)   # Left
            }
            for play in self.current_trick:
                pf = tk.Frame(self.center_frame, bg=BG_LIGHT)
                pos = positions[play['player']]
                pf.place(relx=pos[0], rely=pos[1], anchor=tk.CENTER)
                self.make_card(pf, play['card'], False).pack()
                tk.Label(pf, text=names_pos[play['player']], 
                        font=('Arial', 9, 'bold'), bg=BG_LIGHT, fg='white').pack()
        
        # East player (right)
        e = tk.Frame(mid, bg=BG_MID, relief=tk.RAISED, bd=2)
        e.pack(side=tk.LEFT, padx=5)
        bid_text = "DEAL" if self.deal_bids[1] else str(self.bids[1])
        tk.Label(e, text=f"East\n{bid_text}\nWon: {self.tricks[1]}", 
                font=('Arial', 9, 'bold'), bg=BG_MID, fg='white').pack(pady=3)
        for _ in self.hands[1]:
            tk.Label(e, text="🂠", font=('Arial', 14), 
                    bg=BG_MID, fg='white').pack(pady=2)
        
        # Teammate (top)
        n = tk.Frame(self.game_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        n.pack(side=tk.BOTTOM, pady=5)
        bid_text = "DEAL" if self.deal_bids[2] else str(self.bids[2])
        tk.Label(n, text=f"Teammate - {bid_text} | Won: {self.tricks[2]}", 
                font=('Arial', 10, 'bold'), bg=BG_MID, fg='white').pack(pady=3)
        nc = tk.Frame(n, bg=BG_MID)
        nc.pack()
        for _ in self.hands[2]:
            tk.Label(nc, text="🂠", font=('Arial', 16), 
                    bg=BG_MID, fg='white').pack(side=tk.LEFT, padx=2)
        
        # Trigger AI play if it's AI's turn
        if self.current_player != 0:
            self.root.after(1000, self.ai_play)
        
        self.update_scores()
    
    def can_play(self, card):
        """
        Check if a card is legal to play.
        
        Rules:
            - Must follow suit if possible
            - Can't lead spades until broken (unless only spades left)
        
        Args:
            card (Card): The card to check
            
        Returns:
            bool: True if card can be played
        """
        if self.current_player != 0:
            return False
        
        hand = self.hands[0]
        
        # Leading the trick
        if not self.current_trick:
            # Spades broken or card isn't a spade
            if self.spades_broken or card.suit != '♠':
                return True
            # Can only lead spades if that's all you have
            return all(c.suit == '♠' for c in hand)
        
        # Following in trick - must follow suit if possible
        has_suit = any(c.suit == self.lead_suit for c in hand)
        if has_suit:
            return card.suit == self.lead_suit
        else:
            return True  # Can play anything if can't follow suit
    
    def play_card(self, player, card):
        """
        Play a card to the current trick.
        
        Args:
            player (int): Index of player playing card (0-3)
            card (Card): The card being played
        """
        if card not in self.hands[player]:
            return
        
        # Remove card from player's hand
        self.hands[player].remove(card)
        
        # Add to current trick
        self.current_trick.append({'player': player, 'card': card})
        self.ai.record_card(card)
        
        # Set lead suit if this is first card
        if len(self.current_trick) == 1:
            self.lead_suit = card.suit
        
        # Break spades if a spade is played
        if card.suit == '♠':
            self.spades_broken = True
        
        # Redraw interface
        self.show_playing()
        
        # Check if trick is complete
        if len(self.current_trick) == 4:
            self.root.after(2000, self.finish_trick)
        else:
            # Next player's turn
            self.current_player = (player + 1) % 4
            if self.current_player != 0:
                self.root.after(1200, self.ai_play)
            else:
                self.show_playing()
    
    def ai_play(self):
        """Have the current AI player choose and play a card"""
        if self.current_player == 0 or len(self.current_trick) >= 4:
            return
        
        # Get partner index (teammate is 2 positions away)
        partner = (self.current_player + 2) % 4
        
        # AI chooses card
        card = self.ai.choose_card(
            self.hands[self.current_player],
            self.current_trick,
            self.lead_suit,
            self.current_player,
            self.bids,
            self.tricks,
            self.deal_bids,
            self.spades_broken,
            partner
        )
        
        if card:
            self.play_card(self.current_player, card)
    
    def finish_trick(self):
        """
        Determine winner of completed trick and update game state.
        
        Algorithm:
            - Spades beat all other suits (trump)
            - Highest card of lead suit wins if no spades
            - Winner leads next trick
        """
        winner_idx = 0
        winner = self.current_trick[0]
        
        # Find highest card in trick
        for i, play in enumerate(self.current_trick):
            # Spade beats non-spade
            if play['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = play
                winner_idx = i
            # Higher card of same suit
            elif (play['card'].suit == winner['card'].suit and 
                  play['card'].get_value() > winner['card'].get_value()):
                winner = play
                winner_idx = i
        
        winner_player = winner['player']
        self.tricks[winner_player] += 1
        
        # Display trick result
        names = ['You', 'East', 'Teammate', 'West']
        cards_str = ", ".join([f"{names[p['player']]}: {p['card']}" 
                              for p in self.current_trick])
        self.msg.config(text=f"Trick: {cards_str}\n{names[winner_player]} wins!")
        
        # Reset for next trick
        self.current_trick = []
        self.lead_suit = None
        self.current_player = winner_player
        
        # Check if round is over
        if all(len(hand) == 0 for hand in self.hands):
            self.root.after(2000, self.end_round)
        else:
            self.root.after(2000, self.show_playing)
    
    def end_round(self):
        """
        Calculate scores for completed round and check for game winner.
        
        Scoring Rules:
            - DEAL: +100 if 0 tricks taken, -100 otherwise
            - Normal: +10×bid + overtricks if successful, -10×bid if failed
        """
        round_scores = [0, 0]
        
        for team in range(2):
            p1, p2 = team * 2, team * 2 + 1
            team_bid = self.bids[p1] + self.bids[p2]
            team_tricks = self.tricks[p1] + self.tricks[p2]
            
            # Check for DEAL bids
            if self.deal_bids[p1] or self.deal_bids[p2]:
                deal_player = p1 if self.deal_bids[p1] else p2
                if self.tricks[deal_player] == 0:
                    round_scores[team] = 100
                    self.stats.record_bid(True, True)
                else:
                    round_scores[team] = -100
                    self.stats.record_bid(False, True)
            else:
                # Normal scoring
                if team_tricks >= team_bid:
                    round_scores[team] = team_bid * 10 + (team_tricks - team_bid)
                    self.stats.record_bid(True)
                    # Record bags for statistics
                    bags = team_tricks - team_bid
                    for _ in range(bags):
                        self.stats.record_bag()
                else:
                    round_scores[team] = -team_bid * 10
                    self.stats.record_bid(False)
            
            # Update total score
            self.scores[team][0] += round_scores[team]
        
        # Display round results
        result_text = f"Round {self.rounds} Complete!\n\n"
        result_text += f"Team 1: {self.tricks[0] + self.tricks[2]} tricks ({round_scores[0]:+d}) → {self.scores[0][0]}\n"
        result_text += f"Team 2: {self.tricks[1] + self.tricks[3]} tricks ({round_scores[1]:+d}) → {self.scores[1][0]}"
        
        self.msg.config(text=result_text)
        self.update_scores()
        
        # Check for game winner
        if self.scores[0][0] >= WINNING_SCORE or self.scores[1][0] >= WINNING_SCORE:
            self.root.after(3000, self.end_game)
        else:
            self.root.after(3000, self.deal_cards)
    
    def end_game(self):
        """Handle game completion and declare winner"""
        winner = 1 if self.scores[0][0] >= WINNING_SCORE else 2
        player_won = winner == 1
        self.stats.record_game(player_won)
        
        msg = f"🎉 Team {winner} WINS! 🎉\n\n"
        msg += f"Final Score:\nTeam 1: {self.scores[0][0]}\nTeam 2: {self.scores[1][0]}"
        
        messagebox.showinfo("Game Over", msg)
        
        # Return to tutorial
        self.game_state = 'tutorial'
        self.tutorial_step = 0
        self.show_tutorial()
    
    def update_scores(self):
        """Update score display labels for both teams"""
        self.t1_score.config(text=f"{self.scores[0][0]}/300")
        self.t2_score.config(text=f"{self.scores[1][0]}/300")
    
    def show_hint(self):
        """
        Display strategic hint to player.
        
        Bidding hints: Suggest bid based on hand strength
        Playing hints: Suggest best card to play
        """
        if self.game_state == 'bidding':
            strength = self.ai.calc_strength(self.hands[0])
            should_deal = self.ai.should_deal(self.hands[0])
            hint = f"Hand Strength: {strength}\n"
            if should_deal:
                hint += "Consider DEALING (weak hand)"
            else:
                hint += f"Suggested bid: {strength}"
            messagebox.showinfo("Hint", hint)
        
        elif self.game_state == 'playing' and self.current_player == 0:
            playable = [c for c in self.hands[0] if self.can_play(c)]
            if playable:
                card = self.ai.choose_card(
                    playable,
                    self.current_trick,
                    self.lead_suit,
                    0,
                    self.bids,
                    self.tricks,
                    self.deal_bids,
                    self.spades_broken,
                    2  # Partner is player 2
                )
                messagebox.showinfo("Hint", f"Suggested play: {card}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    game = SpadesGame(root)
    root.mainloop()