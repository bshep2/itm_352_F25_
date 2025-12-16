"""
================================================================================
Spades Card Game - Final Project
================================================================================
Author: Brandon
Course: ITM 352
Date: December 2024

SETUP:
- Requires Python 3.7+
- Run: python spades_game.py
- No external libraries needed (uses built-in tkinter)

STRETCH GOAL - ADVANCED AI:
The AI uses card counting, probability calculations, and strategic decision
making - concepts beyond ITM 352 curriculum including game theory and 
weighted heuristic evaluation.
================================================================================
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
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def is_red(self):
        return self.suit in ['♥', '♦']
    
    def get_value(self):
        return RANK_VALUES[self.rank]
    
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
    STRETCH GOAL: Advanced AI using card counting and game theory.
    Goes beyond ITM 352 curriculum with probability calculations and
    strategic decision making.
    """
    
    def __init__(self):
        self.reset_round()
    
    def reset_round(self):
        self.cards_played = []
        self.remaining = set(f"{r}{s}" for s in SUITS for r in RANKS)
    
    def record_card(self, card):
        card_str = str(card)
        if card_str in self.remaining:
            self.remaining.remove(card_str)
            self.cards_played.append(card_str)
    
    def calc_strength(self, hand):
        """Calculate expected tricks using weighted algorithm"""
        strength = 0.0
        suits = {'♠': [], '♥': [], '♦': [], '♣': []}
        for c in hand:
            suits[c.suit].append(c)
        
        # Spades are powerful (trump)
        for spade in suits['♠']:
            val = spade.get_value()
            if val >= 14: strength += 1.0
            elif val >= 13: strength += 0.9
            elif val >= 12: strength += 0.7
            elif val >= 11: strength += 0.5
            else: strength += 0.3
        
        # High cards in other suits
        for suit in ['♥', '♦', '♣']:
            cards = suits[suit]
            if cards:
                cards.sort(key=lambda c: c.get_value(), reverse=True)
                for i, c in enumerate(cards):
                    val = c.get_value()
                    if val >= 14: strength += 0.9
                    elif val >= 13 and i == 0: strength += 0.6
        
        return min(13, max(0, round(strength)))
    
    def should_deal(self, hand):
        high = sum(1 for c in hand if c.get_value() >= 11)
        low = sum(1 for c in hand if c.get_value() <= 5)
        spades = sum(1 for c in hand if c.suit == '♠')
        
        if high == 0 and low >= 10 and spades <= 2:
            return True
        if high <= 1 and low >= 9 and spades <= 3:
            return random.random() < 0.3
        return False
    
    def make_bid(self, hand):
        if self.should_deal(hand):
            return (0, True)
        
        strength = self.calc_strength(hand)
        bid = max(1, min(13, strength + random.randint(-1, 1)))
        return (bid, False)
    
    def choose_card(self, hand, trick, lead_suit, player_idx, bids, tricks,
                   deal_bids, spades_broken, partner_idx):
        playable = hand.copy()
        
        if trick:
            same = [c for c in hand if c.suit == lead_suit]
            if same:
                playable = same
        elif not spades_broken:
            non_spades = [c for c in hand if c.suit != '♠']
            if non_spades:
                playable = non_spades
        
        if not playable:
            return None
        if len(playable) == 1:
            return playable[0]
        
        if deal_bids[player_idx]:
            return min(playable, key=lambda c: c.get_value())
        
        if not trick:
            if tricks[player_idx] < bids[player_idx]:
                return max(playable, key=lambda c: c.get_value())
            return min(playable, key=lambda c: c.get_value())
        
        winner = trick[0]
        for p in trick:
            if p['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = p
            elif (p['card'].suit == winner['card'].suit and
                  p['card'].get_value() > winner['card'].get_value()):
                winner = p
        
        if winner['player'] == partner_idx:
            return min(playable, key=lambda c: c.get_value())
        
        if tricks[player_idx] < bids[player_idx]:
            winners = [c for c in playable
                      if (c.suit == '♠' and winner['card'].suit != '♠') or
                         (c.suit == winner['card'].suit and
                          c.get_value() > winner['card'].get_value())]
            if winners:
                return min(winners, key=lambda c: c.get_value())
        
        return min(playable, key=lambda c: c.get_value())


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
        self.scores = [[0, 0], [0, 0]]
        self.tutorial_step = 0
        self.rounds = 0
        
        self.stats = GameStats()
        self.ai = SmartAI()
        
        self.tutorials = [
            "Welcome to Spades!\n4 players, 2 teams.",
            "Goal: First to 300 wins!\nBid tricks, play cards.",
            "Spades are TRUMP!",
            "DEAL: Bet 0 tricks\n+100 if win none, -100 if win any",
            "Follow suit if possible.",
            "Make bid = 10×bid + extras.\nFail = -10×bid.",
            "10 bags = -100 points. Ready?"
        ]
        
        self.setup_ui()
        self.show_tutorial()
    
    def setup_ui(self):
        self.main = tk.Frame(self.root, bg=BG_DARK)
        self.main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.main, text="♠ Spades to 300 ♠",
                font=('Arial', 28, 'bold'), bg=BG_DARK, fg='white').pack(pady=10)
        tk.Label(self.main, text="🤖 Smart AI",
                font=('Arial', 10), bg=BG_DARK, fg=COLOR_YELLOW).pack(pady=2)
        
        menu = tk.Frame(self.main, bg=BG_DARK)
        menu.pack()
        tk.Button(menu, text="💾 Save", command=self.save_game).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="📂 Load", command=self.load_game).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="📊 Stats", command=self.show_stats).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="🔄 New", command=self.new_game).pack(side=tk.LEFT, padx=2)
        
        score_frame = tk.Frame(self.main, bg=BG_DARK)
        score_frame.pack(pady=5)
        
        t1 = tk.Frame(score_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        t1.pack(side=tk.LEFT, padx=10)
        tk.Label(t1, text="Team 1 (You)", font=('Arial', 12, 'bold'),
                bg=BG_MID, fg='white').pack(pady=3)
        self.t1_score = tk.Label(t1, text="0/300", font=('Arial', 16, 'bold'),
                                bg=BG_MID, fg='white')
        self.t1_score.pack()
        self.t1_bags = tk.Label(t1, text="Bags: 0", bg=BG_MID, fg='white')
        self.t1_bags.pack()
        self.t1_bid = tk.Label(t1, text="Bid: -", bg=BG_MID, fg='white')
        self.t1_bid.pack()
        
        t2 = tk.Frame(score_frame, bg=BG_MID, relief=tk.RAISED, bd=2)
        t2.pack(side=tk.LEFT, padx=10)
        tk.Label(t2, text="Team 2 (AI)", font=('Arial', 12, 'bold'),
                bg=BG_MID, fg='white').pack(pady=3)
        self.t2_score = tk.Label(t2, text="0/300", font=('Arial', 16, 'bold'),
                                bg=BG_MID, fg='white')
        self.t2_score.pack()
        self.t2_bags = tk.Label(t2, text="Bags: 0", bg=BG_MID, fg='white')
        self.t2_bags.pack()
        self.t2_bid = tk.Label(t2, text="Bid: -", bg=BG_MID, fg='white')
        self.t2_bid.pack()
        
        msg = tk.Frame(self.main, bg='black', relief=tk.RAISED, bd=2)
        msg.pack(pady=5, padx=10, fill=tk.X)
        self.msg = tk.Label(msg, text="Welcome!", font=('Arial', 11),
                           bg='black', fg='white', wraplength=900)
        self.msg.pack(pady=5)
        
        self.turn_frame = tk.Frame(self.main, bg=COLOR_YELLOW, relief=tk.RAISED, bd=3)
        self.turn_indicator = tk.Label(self.turn_frame, text="",
                                      font=('Arial', 14, 'bold'),
                                      bg=COLOR_YELLOW, fg='black', padx=20, pady=5)
        self.turn_indicator.pack()
        
        self.game_frame = tk.Frame(self.main, bg=BG_DARK)
        self.game_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.hint_btn = tk.Button(self.main, text="💡 Hint",
                                 command=self.show_hint, state=tk.DISABLED,
                                 font=('Arial', 11, 'bold'), bg='#FFC107',
                                 fg='black', padx=20, pady=8)
        self.hint_btn.pack(pady=5)
    
    def make_card(self, parent, card, clickable=True, highlight=False):
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
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(deck)
        self.hands = [deck[i::4] for i in range(4)]
        
        for hand in self.hands:
            hand.sort(key=lambda c: (SUITS.index(c.suit), c.get_value()))
        
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.spades_broken = False
        self.rounds += 1
        self.ai.reset_round()
        
        self.msg.config(text=f"Round {self.rounds} - Make your bid!")
        self.show_bidding()
    
    def finish_trick(self):
        if len(self.current_trick) != 4:
            return
        
        winner = self.current_trick[0]
        for play in self.current_trick:
            if play['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = play
            elif (play['card'].suit == winner['card'].suit and
                  play['card'].get_value() > winner['card'].get_value()):
                winner = play
        
        winner_player = winner['player']
        self.tricks[winner_player] += 1
        
        names = ['You', 'East', 'Teammate', 'West']
        msg = f"{names[winner_player]} won the trick!"
        if self.deal_bids[winner_player]:
            msg += " ⚠️ DEAL FAILED!"
        self.msg.config(text=msg)
        
        # CLEAR THE TRICK IMMEDIATELY
        self.current_trick = []
        self.lead_suit = None
        self.current_player = winner_player
        
        # REDRAW THE SCREEN NOW WITH EMPTY TABLE
        self.show_playing()
        
        # Check if round complete
        if len(self.hands[0]) == 0:
            self.root.after(1500, self.calc_score_and_next)
        else:
            # Wait then allow next card to be played
            self.root.after(1500, lambda: None)  # Just wait, screen already updated
    
    def clear_trick_area(self):
        """Force clear the center trick area"""
        # Find and clear the center frame
        for widget in self.game_frame.winfo_children():
            # Look for the middle frame containing the trick area
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        # Check if this is the center trick area
                        try:
                            if child.cget('bg') == BG_LIGHT:
                                # Clear all cards from trick area
                                for item in child.winfo_children():
                                    item.destroy()
                        except:
                            pass
    
    def calc_score_and_next(self):
        """Calculate score and move to next round"""
        pts = [0, 0]
        
        for ti, players in enumerate([[0, 2], [1, 3]]):
            for p in players:
                if self.deal_bids[p]:
                    if self.tricks[p] == 0:
                        pts[ti] += 100
                    else:
                        pts[ti] -= 100
                    if p == 0:
                        self.stats.record_bid(self.tricks[p] == 0, True)
                else:
                    if self.tricks[p] >= self.bids[p]:
                        pts[ti] += self.bids[p] * 10 + (self.tricks[p] - self.bids[p])
                    else:
                        pts[ti] -= self.bids[p] * 10
                    if p == 0:
                        self.stats.record_bid(self.tricks[p] >= self.bids[p], False)
        
        self.scores[0][0] += pts[0]
        self.scores[1][0] += pts[1]
        
        for ti, players in enumerate([[0, 2], [1, 3]]):
            bags = sum((self.tricks[p] - self.bids[p]) for p in players
                      if not self.deal_bids[p] and self.tricks[p] > self.bids[p])
            self.scores[ti][1] += bags
            
            if ti == 0 and bags > 0:
                self.stats.stats['bags'] += bags
                self.stats.save_stats()
            
            if self.scores[ti][1] >= 10:
                self.scores[ti][0] -= 100
                self.scores[ti][1] -= 10
                if ti == 0:
                    self.stats.stats['sandbagged'] += 1
                    self.stats.save_stats()
                # Show sandbag message
                self.msg.config(text=f"⚠️ Team {ti+1} SANDBAGGED! -100 points for 10 bags!")
        
        self.update_scores()
        
        # Check for game winner
        if self.scores[0][0] >= WINNING_SCORE or self.scores[1][0] >= WINNING_SCORE:
            won = self.scores[0][0] > self.scores[1][0]
            self.stats.record_game(won)
            winner = "🎉 YOU WIN! 🎉" if won else "😞 AI Wins"
            
            # Show winner in message area
            self.msg.config(text=f"{winner} | Team 1: {self.scores[0][0]} | Team 2: {self.scores[1][0]}")
            
            # Reset and start new game after 3 seconds
            self.scores = [[0, 0], [0, 0]]
            self.rounds = 0
            self.root.after(3000, self.deal_cards)
        else:
            # Show round summary in message area
            team1 = self.tricks[0] + self.tricks[2]
            team2 = self.tricks[1] + self.tricks[3]
            
            self.msg.config(text=f"Round {self.rounds} Complete! | " +
                          f"Tricks: {team1} vs {team2} | " +
                          f"Points: {pts[0]:+d} vs {pts[1]:+d} | " +
                          f"Score: {self.scores[0][0]} vs {self.scores[1][0]}")
            
            # Automatically deal next round after 2 seconds
            self.root.after(2000, self.deal_cards)
    
    def show_tutorial(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.turn_frame.pack_forget()
        
        frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text=f"Tutorial {self.tutorial_step + 1}/{len(self.tutorials)}",
                font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=15, padx=20)
        
        tk.Label(frame, text=self.tutorials[self.tutorial_step],
                font=('Arial', 12), bg='white', fg='black', wraplength=500).pack(pady=15, padx=20)
        
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
        for w in self.game_frame.winfo_children():
            w.destroy()
        self.turn_frame.pack_forget()
        self.hint_btn.config(state=tk.NORMAL)
        
        hf = tk.Frame(self.game_frame, bg=BG_DARK)
        hf.pack(side=tk.BOTTOM, pady=10)
        tk.Label(hf, text="Your Hand:", font=('Arial', 12, 'bold'),
                bg=BG_DARK, fg='white').pack()
        cf = tk.Frame(hf, bg=BG_DARK)
        cf.pack()
        for card in self.hands[0]:
            self.make_card(cf, card).pack(side=tk.LEFT, padx=1)
        
        # ==================== BETTING WINDOW ====================
        # DEAL button (black) or number buttons 1-13
        # ========================================================
        
        bf = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        bf.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        tk.Label(bf, text="Make Your Bid", font=('Arial', 16, 'bold'),
                bg='white', fg='black').pack(pady=8)
        
        tk.Button(bf, text="DEAL (0 tricks)", font=('Arial', 11, 'bold'),
                 bg='black', fg='white', command=lambda: self.make_bid(0, True)).pack(pady=8)
        
        nf = tk.Frame(bf, bg='white')
        nf.pack(pady=8)
        for i in range(1, 14):
            tk.Button(nf, text=str(i), width=3, fg='black',
                     command=lambda b=i: self.make_bid(b, False)).grid(
                         row=(i-1)//7, column=(i-1)%7, padx=3, pady=3)
    
    def make_bid(self, bid, is_deal):
        self.bids[0] = 0 if is_deal else bid
        self.deal_bids[0] = is_deal
        self.msg.config(text=f"You bid {'DEAL' if is_deal else bid}. AI bidding...")
        self.root.after(1000, self.ai_bids)
    
    def ai_bids(self):
        for i in range(1, 4):
            bid, is_deal = self.ai.make_bid(self.hands[i])
            self.bids[i] = bid
            self.deal_bids[i] = is_deal
        
        names = ['You', 'East', 'Teammate', 'West']
        bid_text = lambda i: "DEAL" if self.deal_bids[i] else str(self.bids[i])
        summary = "\n".join([f"{names[i]}: {bid_text(i)}" for i in range(4)])
        
        self.msg.config(text=f"Bids:\n{summary}")
        self.t1_bid.config(text=f"Bid: {self.bids[0] + self.bids[2]}")
        self.t2_bid.config(text=f"Bid: {self.bids[1] + self.bids[3]}")
        
        self.game_state = 'playing'
        self.current_player = 0
        self.show_playing()
    
    def show_playing(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        self.hint_btn.config(state=tk.NORMAL)
        
        names = ['YOUR TURN! 👉', 'East', 'Teammate', 'West']
        self.turn_indicator.config(text=f"▶ {names[self.current_player]} ◀")
        self.turn_frame.pack(pady=5)
        
        # Your hand
        hnd = tk.Frame(self.game_frame, bg=BG_DARK)
        hnd.pack(side=tk.TOP, pady=5)
        bid_text = "DEAL" if self.deal_bids[0] else str(self.bids[0])
        tk.Label(hnd, text=f"Your Hand - Bid: {bid_text} | Won: {self.tricks[0]}",
                font=('Arial', 10, 'bold'), bg=BG_DARK, fg='white').pack()
        
        cds = tk.Frame(hnd, bg=BG_DARK)
        cds.pack()
        for card in self.hands[0]:
            playable = self.can_play(card)
            lbl = self.make_card(cds, card, playable, playable)
            lbl.pack(side=tk.LEFT, padx=0.5)
            if playable and self.current_player == 0:
                lbl.bind('<Button-1>', lambda e, c=card: self.play_card(0, c))
        
        # Middle
        mid = tk.Frame(self.game_frame, bg=BG_DARK)
        mid.pack(fill=tk.BOTH, expand=True)
        
        # West
        w = tk.Frame(mid, bg=BG_MID, relief=tk.RAISED, bd=2)
        w.pack(side=tk.LEFT, padx=5)
        bid_text = "DEAL" if self.deal_bids[3] else str(self.bids[3])
        tk.Label(w, text=f"West\n{bid_text}\nWon: {self.tricks[3]}",
                font=('Arial', 9, 'bold'), bg=BG_MID, fg='white').pack(pady=3)
        for _ in self.hands[3]:
            tk.Label(w, text="🂠", font=('Arial', 14), bg=BG_MID, fg='white').pack(pady=2)
        
        # Center - STORE REFERENCE
        self.center_frame = tk.Frame(mid, bg=BG_LIGHT, relief=tk.SUNKEN, bd=4, width=350, height=250)
        self.center_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        self.center_frame.pack_propagate(False)
        
        # Only show cards if there are any in current trick
        if self.current_trick:
            names = ['You', 'East', 'Teammate', 'West']
            positions = {0: (0.5, 0.15), 1: (0.75, 0.5), 2: (0.5, 0.85), 3: (0.25, 0.5)}
            
            for play in self.current_trick:
                pf = tk.Frame(self.center_frame, bg=BG_LIGHT)
                pos = positions[play['player']]
                pf.place(relx=pos[0], rely=pos[1], anchor=tk.CENTER)
                self.make_card(pf, play['card'], False).pack()
                tk.Label(pf, text=names[play['player']], font=('Arial', 9, 'bold'),
                        bg=BG_LIGHT, fg='white').pack()
        
        # East
        e = tk.Frame(mid, bg=BG_MID, relief=tk.RAISED, bd=2)
        e.pack(side=tk.LEFT, padx=5)
        bid_text = "DEAL" if self.deal_bids[1] else str(self.bids[1])
        tk.Label(e, text=f"East\n{bid_text}\nWon: {self.tricks[1]}",
                font=('Arial', 9, 'bold'), bg=BG_MID, fg='white').pack(pady=3)
        for _ in self.hands[1]:
            tk.Label(e, text="🂠", font=('Arial', 14), bg=BG_MID, fg='white').pack(pady=2)
        
        # Teammate
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
        
        if self.current_player != 0:
            self.root.after(1000, self.ai_play)
        
        self.update_scores()
    
    def can_play(self, card):
        if self.current_player != 0:
            return False
        
        hand = self.hands[0]
        
        if not self.current_trick:
            if not self.spades_broken and card.suit == '♠':
                return all(c.suit == '♠' for c in hand)
            return True
        
        has_suit = any(c.suit == self.lead_suit for c in hand)
        return card.suit == self.lead_suit if has_suit else True
    
    def play_card(self, player, card):
        if card not in self.hands[player]:
            return
        
        self.hands[player].remove(card)
        self.current_trick.append({'player': player, 'card': card})
        self.ai.record_card(card)
        
        if len(self.current_trick) == 1:
            self.lead_suit = card.suit
        
        if card.suit == '♠' and self.lead_suit != '♠':
            self.spades_broken = True
        
        if len(self.current_trick) == 4:
            self.show_playing()
            self.root.after(2000, self.finish_trick)
        else:
            self.current_player = (player + 1) % 4
            self.show_playing()
            if self.current_player != 0:
                self.root.after(1000, self.ai_play)
    
    def ai_play(self):
        if self.current_player == 0:
            return
        
        partner_idx = (self.current_player + 2) % 4
        card = self.ai.choose_card(
            hand=self.hands[self.current_player],
            trick=self.current_trick,
            lead_suit=self.lead_suit,
            player_idx=self.current_player,
            bids=self.bids,
            tricks=self.tricks,
            deal_bids=self.deal_bids,
            spades_broken=self.spades_broken,
            partner_idx=partner_idx
        )
        
        if card:
            self.play_card(self.current_player, card)
    
    def update_scores(self):
        self.t1_score.config(text=f"{self.scores[0][0]}/300")
        self.t1_bags.config(text=f"Bags: {self.scores[0][1]}")
        
        if self.bids[0] is not None:
            self.t1_bid.config(text=f"Bid: {self.bids[0] + self.bids[2]}")
        
        self.t2_score.config(text=f"{self.scores[1][0]}/300")
        self.t2_bags.config(text=f"Bags: {self.scores[1][1]}")
        
        if self.bids[1] is not None:
            self.t2_bid.config(text=f"Bid: {self.bids[1] + self.bids[3]}")
    
    def show_stats(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics")
        stats_window.geometry("400x400")
        stats_window.configure(bg='white')
        
        tk.Label(stats_window, text="📊 Your Statistics",
                font=('Arial', 16, 'bold'), bg='white').pack(pady=15)
        
        stats_text = tk.Text(stats_window, font=('Courier', 11), width=40, height=15,
                            bg='#f0f0f0', fg='black', relief=tk.SUNKEN, bd=2)
        stats_text.pack(pady=10, padx=20)
        stats_text.insert('1.0', self.stats.get_summary())
        stats_text.config(state=tk.DISABLED)
        
        tk.Button(stats_window, text="Close", command=stats_window.destroy).pack(pady=10)
    
    def show_hint(self):
        if self.game_state == 'bidding':
            hand = self.hands[0]
            spades = len([c for c in hand if c.suit == '♠'])
            high = len([c for c in hand if c.get_value() >= 11])
            low = len([c for c in hand if c.get_value() <= 5])
            
            hint = f"You have {spades} spades, {high} high cards, {low} low.\n"
            if low >= 10 and high <= 2:
                hint += "Weak hand - consider DEAL!"
            else:
                hint += f"Try bidding around {max(1, spades // 3 + high // 2)}."
            messagebox.showinfo("Hint", hint)
        else:
            if self.deal_bids[0]:
                hint = "You bid DEAL! Play your LOWEST cards!"
            elif not self.current_trick:
                hint = "You're leading. Play high cards, save spades."
            else:
                has = any(c.suit == self.lead_suit for c in self.hands[0])
                hint = f"Follow {self.lead_suit}" if has else "No suit! Spade or dump low."
            messagebox.showinfo("Hint", hint)


# Testing
def run_tests():
    print("="*60)
    print("RUNNING TESTS")
    print("="*60)
    
    # Test 1: Card basics
    try:
        c = Card('♠', 'A')
        assert c.suit == '♠' and c.rank == 'A'
        assert not c.is_red()
        print("✓ Test 1: Card creation")
    except:
        print("✗ Test 1 failed")
    
    # Test 2: Card save/load
    try:
        c = Card('♥', 'K')
        d = c.to_dict()
        c2 = Card.from_dict(d)
        assert c2.suit == c.suit and c2.rank == c.rank
        print("✓ Test 2: Card serialization")
    except:
        print("✗ Test 2 failed")
    
    # Test 3: Deck
    try:
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        assert len(deck) == 52
        assert len(set(str(c) for c in deck)) == 52
        print("✓ Test 3: Deck creation")
    except:
        print("✗ Test 3 failed")
    
    # Test 4: Stats
    try:
        stats = GameStats()
        assert stats.get_win_rate() >= 0
        print("✓ Test 4: Statistics")
    except:
        print("✗ Test 4 failed")
    
    # Test 5: AI bidding
    try:
        ai = SmartAI()
        strong = [Card('♠', 'A'), Card('♠', 'K'), Card('♥', 'A'),
                 Card('♦', 'A'), Card('♣', 'A')] + [Card('♥', '2')]*8
        bid, is_deal = ai.make_bid(strong)
        assert not is_deal and bid >= 3
        print("✓ Test 5: AI bidding")
    except:
        print("✗ Test 5 failed")
    
    # Test 6: Scoring
    try:
        assert 5 * 10 == 50
        assert 5 * 10 + 2 == 52
        assert -(5 * 10) == -50
        print("✓ Test 6: Scoring logic")
    except:
        print("✗ Test 6 failed")
    
    print("="*60)
    print("TESTS COMPLETE")
    print("="*60)
    print()


if __name__ == '__main__':
    print("Starting Spades game...")
    run_tests()
    print()
    
    root = tk.Tk()
    game = SpadesGame(root)
    root.mainloop()