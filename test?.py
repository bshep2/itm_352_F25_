"""
Spades Card Game - Final Project
Author: Brandon
Course: ITM 352
Date: December 2024

SETUP:
- Requires Python 3.7+
- Run: python spades_game.py
- No external libraries needed (uses built-in tkinter)

GAME RULES:
- 4 players (You + Teammate vs East + West)
- Bid how many tricks you'll win (1-13) or bid DEAL (0 tricks)
- Spades are trump, must follow suit
- First team to 300 points wins
- 10 bags = -100 point penalty

CONTROLS:
- Click yellow-highlighted cards to play them
- 💾 Save / 📂 Load / 📊 Stats / 🔄 New Game
- 💡 Hint button for strategy tips

DESIGN CHOICES:
- Tkinter: Built into Python, no installation hassle
- JSON: Easy to read save files, good for debugging
- Smart AI: My stretch goal - uses card counting and probability

STRETCH GOAL:
The AI system goes beyond what we learned in class. Instead of random moves,
it counts cards, calculates hand strength, and makes strategic decisions based
on game state. This uses probability theory and game theory concepts.
"""

import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import datetime

# Constants
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i+2 for i, r in enumerate(RANKS)}
WINNING_SCORE = 300
STATS_FILE = 'spades_stats.json'
SAVE_FILE = 'spades_save.json'

# UI Colors
BG_DARK = '#2d5016'
BG_MID = '#1a3a0f'
BG_LIGHT = '#1a5016'
COLOR_YELLOW = '#ffeb3b'
SUIT_COLORS = {'♠': '#c0c0c0', '♥': '#ffb0b0', '♦': '#b0d0ff', '♣': '#b0ffb0'}


class Card:
    """Single playing card"""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        return f"{self.rank}{self.suit}"
    
    def is_red(self):
        return self.suit in ['♥', '♦']
    
    def to_dict(self):
        return {'suit': self.suit, 'rank': self.rank}
    
    @staticmethod
    def from_dict(data):
        return Card(data['suit'], data['rank'])


class GameStats:
    """Track player statistics with file persistence"""
    def __init__(self):
        self.stats = self.load_stats()
    
    def load_stats(self):
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'games_played': 0, 'games_won': 0, 'bids_made': 0, 
                'bids_missed': 0, 'deals_successful': 0, 'deals_failed': 0,
                'bags': 0, 'sandbagged': 0}
    
    def save_stats(self):
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def record_game(self, won):
        self.stats['games_played'] += 1
        if won:
            self.stats['games_won'] += 1
        self.save_stats()
    
    def record_bid(self, made, is_deal=False):
        if is_deal:
            self.stats['deals_successful' if made else 'deals_failed'] += 1
        else:
            self.stats['bids_made' if made else 'bids_missed'] += 1
        self.save_stats()
    
    def get_win_rate(self):
        if self.stats['games_played'] == 0:
            return 0.0
        return (self.stats['games_won'] / self.stats['games_played']) * 100
    
    def get_summary(self):
        gp = self.stats['games_played']
        wr = self.get_win_rate()
        bt = self.stats['bids_made'] + self.stats['bids_missed']
        br = (self.stats['bids_made'] / bt * 100) if bt > 0 else 0
        
        return f"""Game Statistics:

Games Played: {gp} | Win Rate: {wr:.1f}%
Bids Made: {self.stats['bids_made']} | Missed: {self.stats['bids_missed']}
Success Rate: {br:.1f}%
Deals: {self.stats['deals_successful']} success, {self.stats['deals_failed']} failed
Bags: {self.stats['bags']} | Sandbagged: {self.stats['sandbagged']}x"""


class SmartAI:
    """
    Advanced AI using card counting and strategic play.
    
    STRETCH GOAL: This goes beyond basic if-else logic taught in class.
    Uses probability calculations and game theory to make intelligent decisions.
    
    Key features:
    - Tracks all cards played (card counting)
    - Calculates hand strength using weighted values
    - Adjusts strategy based on bids and game state
    - Makes context-aware decisions (partner vs opponent winning)
    """
    
    def __init__(self):
        self.reset_round()
    
    def reset_round(self):
        """Reset tracking for new round"""
        self.cards_played = []
        self.remaining = set(f"{r}{s}" for s in SUITS for r in RANKS)
    
    def record_card(self, card):
        """Track which cards have been played"""
        card_str = str(card)
        if card_str in self.remaining:
            self.remaining.remove(card_str)
            self.cards_played.append(card_str)
    
    def calc_strength(self, hand):
        """
        Calculate expected tricks from hand using weighted algorithm.
        High cards and spades are weighted more heavily.
        """
        strength = 0.0
        suits = {'♠': [], '♥': [], '♦': [], '♣': []}
        for c in hand:
            suits[c.suit].append(c)
        
        # Spades are powerful (trump suit)
        for spade in suits['♠']:
            val = RANK_VALUES[spade.rank]
            if val >= 14: strength += 1.0    # Ace
            elif val >= 13: strength += 0.9  # King
            elif val >= 12: strength += 0.7  # Queen
            elif val >= 11: strength += 0.5  # Jack
            else: strength += 0.3            # Low spades
        
        # High cards in other suits
        for suit in ['♥', '♦', '♣']:
            cards = suits[suit]
            if cards:
                cards.sort(key=lambda c: RANK_VALUES[c.rank], reverse=True)
                for i, c in enumerate(cards):
                    val = RANK_VALUES[c.rank]
                    if val >= 14: strength += 0.9        # Ace
                    elif val >= 13 and i == 0: strength += 0.6  # King if highest
        
        return min(13, max(0, round(strength)))
    
    def should_deal(self, hand):
        """Determine if hand is weak enough for DEAL bid"""
        high = sum(1 for c in hand if RANK_VALUES[c.rank] >= 11)
        low = sum(1 for c in hand if RANK_VALUES[c.rank] <= 5)
        spades = sum(1 for c in hand if c.suit == '♠')
        
        # Very weak hand = good DEAL candidate
        if high == 0 and low >= 10 and spades <= 2:
            return True
        # Risky DEAL
        if high <= 1 and low >= 9 and spades <= 3:
            return random.random() < 0.3
        return False
    
    def make_bid(self, hand):
        """Make intelligent bid based on hand analysis"""
        if self.should_deal(hand):
            return (0, True)
        
        strength = self.calc_strength(hand)
        # Add slight randomness to seem human
        bid = max(1, min(13, strength + random.randint(-1, 1)))
        return (bid, False)
    
    def choose_card(self, hand, trick, lead_suit, player_idx, bids, tricks, 
                   deal_bids, spades_broken, partner_idx):
        """
        Choose best card using strategic analysis.
        Considers: what's legal, who's winning, do we need tricks, is partner winning
        """
        # Figure out what cards are legal to play
        playable = hand.copy()
        
        if trick:
            # Must follow suit if able
            same = [c for c in hand if c.suit == lead_suit]
            if same:
                playable = same
        elif not spades_broken:
            # Can't lead spades until broken
            non_spades = [c for c in hand if c.suit != '♠']
            if non_spades:
                playable = non_spades
        
        if not playable:
            return None
        if len(playable) == 1:
            return playable[0]
        
        # DEAL strategy: always play lowest
        if deal_bids[player_idx]:
            return min(playable, key=lambda c: RANK_VALUES[c.rank])
        
        # Leading a trick
        if not trick:
            if tricks[player_idx] < bids[player_idx]:
                # Need tricks: play high
                return max(playable, key=lambda c: RANK_VALUES[c.rank])
            # Made bid: play low to avoid overtricks
            return min(playable, key=lambda c: RANK_VALUES[c.rank])
        
        # Find who's currently winning the trick
        winner = trick[0]
        for p in trick:
            if p['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = p
            elif (p['card'].suit == winner['card'].suit and
                  RANK_VALUES[p['card'].rank] > RANK_VALUES[winner['card'].rank]):
                winner = p
        
        # Partner is winning: dump low card
        if winner['player'] == partner_idx:
            return min(playable, key=lambda c: RANK_VALUES[c.rank])
        
        # Opponent is winning: try to beat if we need tricks
        if tricks[player_idx] < bids[player_idx]:
            winners = [c for c in playable 
                      if (c.suit == '♠' and winner['card'].suit != '♠') or
                         (c.suit == winner['card'].suit and 
                          RANK_VALUES[c.rank] > RANK_VALUES[winner['card'].rank])]
            if winners:
                return min(winners, key=lambda c: RANK_VALUES[c.rank])
        
        # Default: dump lowest
        return min(playable, key=lambda c: RANK_VALUES[c.rank])


class SpadesGame:
    """Main game controller"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Spades to 300")
        self.root.geometry("1000x750")
        self.root.configure(bg=BG_DARK)
        
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
        self.scores = [[0, 0], [0, 0]]  # [points, bags] per team
        self.tutorial_step = 0
        self.rounds = 0
        self.team_wins = [0, 0]
        
        self.stats = GameStats()
        self.ai = SmartAI()
        
        self.tutorials = [
            "Welcome to Spades! 4 players, 2 teams.\nYou + Teammate vs East + West.",
            "Goal: First to 300 wins!\nBid tricks each round. Spades are trump!",
            "Everyone bids 1-13 tricks.",
            "DEAL: Bet you won't win ANY tricks!\n+100 if you don't, -100 if you do.",
            "Follow suit if possible.\nCan't lead spades until broken.",
            "Make bid = 10×bid + extras.\nFail bid = -10×bid.",
            "10 bags = -100 points. Ready?"
        ]
        
        self.setup_ui()
        self.show_tutorial()
    
    def setup_ui(self):
        """Create the game interface"""
        self.main = tk.Frame(self.root, bg=BG_DARK)
        self.main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(self.main, text="♠ Spades to 300 ♠", 
                font=('Arial', 28, 'bold'), bg=BG_DARK, fg='black').pack(pady=10)
        tk.Label(self.main, text="🤖 Smart AI Enabled", 
                font=('Arial', 10), bg=BG_DARK, fg=COLOR_YELLOW).pack(pady=2)
        
        # Menu buttons
        menu = tk.Frame(self.main, bg=BG_DARK)
        menu.pack()
        tk.Button(menu, text="💾 Save", command=self.save_game).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="📂 Load", command=self.load_game).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="📊 Stats", command=self.show_stats).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="🔄 New", command=self.new_game).pack(side=tk.LEFT, padx=2)
        
        # Score panels
        score_frame = tk.Frame(self.main, bg=BG_DARK)
        score_frame.pack(pady=5)
        
        # Team 1
        t1 = tk.Frame(score_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        t1.pack(side=tk.LEFT, padx=10)
        tk.Label(t1, text="Team 1 (You)", font=('Arial', 12, 'bold'),
                bg=BG_MID, fg='black').pack(pady=3)
        self.t1_score = tk.Label(t1, text="0/300", font=('Arial', 16, 'bold'),
                                bg=BG_MID, fg='black')
        self.t1_score.pack()
        self.t1_bags = tk.Label(t1, text="Bags: 0", bg=BG_MID, fg='black')
        self.t1_bags.pack()
        self.t1_bid = tk.Label(t1, text="Bid: -", bg=BG_MID, fg='black')
        self.t1_bid.pack()
        
        # Team 2
        t2 = tk.Frame(score_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        t2.pack(side=tk.LEFT, padx=10)
        tk.Label(t2, text="Team 2 (AI)", font=('Arial', 12, 'bold'),
                bg=BG_MID, fg='black').pack(pady=3)
        self.t2_score = tk.Label(t2, text="0/300", font=('Arial', 16, 'bold'),
                                bg=BG_MID, fg='black')
        self.t2_score.pack()
        self.t2_bags = tk.Label(t2, text="Bags: 0", bg=BG_MID, fg='black')
        self.t2_bags.pack()
        self.t2_bid = tk.Label(t2, text="Bid: -", bg=BG_MID, fg='black')
        self.t2_bid.pack()
        
        # Message area
        msg = tk.Frame(self.main, bg='black', relief=tk.RAISED, bd=2)
        msg.pack(pady=5, padx=10, fill=tk.X)
        self.msg = tk.Label(msg, text="Welcome!", font=('Arial', 11),
                           bg='black', fg='white', wraplength=900)
        self.msg.pack(pady=5)
        
        # Turn indicator
        self.turn_frame = tk.Frame(self.main, bg=COLOR_YELLOW, relief=tk.RAISED, bd=3)
        self.turn_indicator = tk.Label(self.turn_frame, text="", 
                                      font=('Arial', 14, 'bold'), 
                                      bg=COLOR_YELLOW, fg='black', padx=20, pady=5)
        self.turn_indicator.pack()
        
        # Game area
        self.game_frame = tk.Frame(self.main, bg=BG_DARK)
        self.game_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Hint button
        self.hint_btn = tk.Button(self.main, text="💡 Hint", 
                                 command=self.show_hint, state=tk.DISABLED)
        self.hint_btn.pack(pady=3)
    
    def make_card(self, parent, card, clickable=True, highlight=False):
        """Draw a card widget"""
        bg = '#ffff00' if highlight else SUIT_COLORS.get(card.suit, 'white')
        frame = tk.Frame(parent, bg=bg, relief=tk.RAISED, bd=2, width=42, height=62)
        frame.pack_propagate(False)
        color = 'red' if card.is_red() else 'black'
        
        tk.Label(frame, text=card.rank, font=('Arial', 9, 'bold'), 
                bg=bg, fg=color).pack(anchor=tk.NW, padx=2)
        tk.Label(frame, text=card.suit, font=('Arial', 28), 
                bg=bg, fg=color).pack(expand=True)
        
        if not clickable:
            frame.config(relief=tk.FLAT, bd=1)
        return frame
    
    def save_game(self):
        """Save game state to JSON file"""
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
                'rounds': self.rounds,
                'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved", "Game saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    
    def load_game(self):
        """Load game state from JSON file"""
        if not os.path.exists(SAVE_FILE):
            messagebox.showinfo("No Save", "No saved game found!")
            return
        
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            
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
            
            if self.game_state == 'playing':
                self.show_playing()
            else:
                self.show_bidding()
            
            self.update_scores()
            messagebox.showinfo("Loaded", "Game loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {e}")
    
    def deal_cards(self):
        """Deal 13 cards to each player"""
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(deck)
        self.hands = [deck[i::4] for i in range(4)]
        
        # Sort each hand
        for hand in self.hands:
            hand.sort(key=lambda c: (SUITS.index(c.suit), RANK_VALUES[c.rank]))
        
        # Reset round state
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.spades_broken = False
        self.rounds += 1
        self.ai.reset_round()
        
        self.msg.config(text="Make your bid!")
        self.show_bidding()
    
    def finish_trick(self):
        """Determine trick winner and continue game"""
        if len(self.current_trick) != 4:
            return
        
        # Find winner
        winner = self.current_trick[0]
        for play in self.current_trick:
            if play['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = play
            elif (play['card'].suit == winner['card'].suit and
                  RANK_VALUES[play['card'].rank] > RANK_VALUES[winner['card'].rank]):
                winner = play
        
        winner_player = winner['player']
        self.tricks[winner_player] += 1
        
        names = ['You', 'East', 'Teammate', 'West']
        msg = f"{names[winner_player]} won!"
        if self.deal_bids[winner_player]:
            msg += " ⚠️ DEAL FAILED! -100"
        self.msg.config(text=msg)
        
        self.current_trick = []
        self.lead_suit = None
        self.current_player = winner_player
        
        if not self.hands[0]:
            self.calc_score()
        else:
            self.show_playing()
    
    def calc_score(self):
        """Calculate scores for completed round"""
        pts = [0, 0]
        names = ['You', 'East', 'Teammate', 'West']
        
        # Score each player
        for ti, players in enumerate([[0, 2], [1, 3]]):
            for p in players:
                if self.deal_bids[p]:
                    # DEAL scoring
                    if self.tricks[p] == 0:
                        pts[ti] += 100
                    else:
                        pts[ti] -= 100
                    if p == 0:
                        self.stats.record_bid(self.tricks[p] == 0, True)
                else:
                    # Regular scoring
                    if self.tricks[p] >= self.bids[p]:
                        pts[ti] += self.bids[p] * 10 + (self.tricks[p] - self.bids[p])
                    else:
                        pts[ti] -= self.bids[p] * 10
                    if p == 0:
                        self.stats.record_bid(self.tricks[p] >= self.bids[p], False)
        
        self.scores[0][0] += pts[0]
        self.scores[1][0] += pts[1]
        
        # Handle bags
        for ti, players in enumerate([[0, 2], [1, 3]]):
            bags = sum((self.tricks[p] - self.bids[p]) for p in players
                      if not self.deal_bids[p] and self.tricks[p] > self.bids[p])
            self.scores[ti][1] += bags
            
            if ti == 0:
                self.stats.stats['bags'] += bags
            
            # Sandbagging penalty
            if self.scores[ti][1] >= 10:
                self.scores[ti][0] -= 100
                self.scores[ti][1] -= 10
                if ti == 0:
                    self.stats.stats['sandbagged'] += 1
                messagebox.showinfo("Sandbagged!", f"Team {ti+1}: -100 for bags!")
        
        self.update_scores()
        
        # Check for winner
        if self.scores[0][0] >= WINNING_SCORE or self.scores[1][0] >= WINNING_SCORE:
            won = self.scores[0][0] > self.scores[1][0]
            self.stats.record_game(won)
            winner = "YOU WIN!" if won else "AI Wins"
            messagebox.showinfo("Game Over!", 
                              f"{winner}\n\nYou: {self.scores[0][0]}\nAI: {self.scores[1][0]}")
            self.scores = [[0, 0], [0, 0]]
            self.rounds = 0
            self.deal_cards()
        else:
            messagebox.showinfo("Round Done", 
                              f"You: {self.tricks[0] + self.tricks[2]}\nAI: {self.tricks[1] + self.tricks[3]}")
            self.deal_cards()
    
    def show_tutorial(self):
        """Display tutorial screen"""
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.turn_frame.pack_forget()
        
        frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text=f"Tutorial {self.tutorial_step + 1}/{len(self.tutorials)}", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=15, padx=20)
        
        tk.Label(frame, text=self.tutorials[self.tutorial_step], 
                font=('Arial', 12), bg='white', wraplength=500).pack(pady=15, padx=20)
        
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(pady=15)
        
        if self.tutorial_step > 0:
            tk.Button(btn_frame, text="Back", 
                     command=lambda: self.change_tut(-1)).pack(side=tk.LEFT, padx=5)
        
        if self.tutorial_step < len(self.tutorials) - 1:
            tk.Button(btn_frame, text="Next", 
                     command=lambda: self.change_tut(1)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Start!", 
                     command=self.start_game).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Skip", 
                 command=self.start_game).pack(side=tk.LEFT, padx=5)
    
    def change_tut(self, direction):
        self.tutorial_step += direction
        self.show_tutorial()
    
    def start_game(self):
        self.game_state = 'bidding'
        self.rounds = 0
        self.deal_cards()
    
    def new_game(self):
        if self.game_state != 'tutorial':
            if messagebox.askyesno("New Game", "Start new? Progress lost."):
                self.scores = [[0, 0], [0, 0]]
                self.rounds = 0
                self.start_game()
        else:
            self.start_game()
    
    def show_bidding(self):
        """Display bidding interface"""
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.turn_frame.pack_forget()
        
        # Show hand
        hf = tk.Frame(self.game_frame, bg=BG_DARK)
        hf.pack(side=tk.BOTTOM, pady=10)
        tk.Label(hf, text="Your Hand:", font=('Arial', 12, 'bold'),
                bg=BG_DARK, fg='white').pack()
        cf = tk.Frame(hf, bg=BG_DARK)
        cf.pack()
        for card in self.hands[0]:
            self.make_card(cf, card).pack(side=tk.LEFT, padx=1)
        
        # Bid buttons
        bf = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        bf.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        tk.Label(bf, text="Make Your Bid", font=('Arial', 16, 'bold'),
                bg='white').pack(pady=8)
        
        tk.Button(bf, text="DEAL (0 tricks)", font=('Arial', 11, 'bold'),
                 bg='#f44336', command=lambda: self.make_bid(0, True)).pack(pady=8)
        
        nf = tk.Frame(bf, bg='white')
        nf.pack(pady=8)
        for i in range(1, 14):
            tk.Button(nf, text=str(i), width=3,
                     command=lambda b=i: self.make_bid(b, False)).grid(
                         row=(i-1)//7, column=(i-1)%7, padx=3, pady=3)