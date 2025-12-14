"""
Spades Card Game - Complete Implementation
Features: GUI, File I/O, Statistics, Error Handling, OOP
Author: [Your Name]
Date: December 2024
"""

import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import datetime

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i+2 for i, r in enumerate(RANKS)}
WINNING_SCORE = 300
STATS_FILE = 'spades_stats.json'
SAVE_FILE = 'spades_save.json'

class Card:
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
    def __init__(self):
        self.stats = self.load_stats()
    
    def load_stats(self):
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'games_played': 0, 'games_won': 0, 'bids_made': 0, 'bids_missed': 0, 
                'deals_successful': 0, 'deals_failed': 0, 'bags': 0, 'sandbagged': 0}
    
    def save_stats(self):
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
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
        gp = self.stats['games_played']
        return (self.stats['games_won'] / gp * 100) if gp > 0 else 0
    
    def get_summary(self):
        gp = self.stats['games_played']
        wr = self.get_win_rate()
        bt = self.stats['bids_made'] + self.stats['bids_missed']
        br = (self.stats['bids_made'] / bt * 100) if bt > 0 else 0
        return f"""Statistics:
Games: {gp} | Win Rate: {wr:.1f}%
Bids Made: {self.stats['bids_made']} | Missed: {self.stats['bids_missed']}
Success Rate: {br:.1f}%
Deals: {self.stats['deals_successful']} success, {self.stats['deals_failed']} failed
Bags: {self.stats['bags']} | Sandbagged: {self.stats['sandbagged']}x"""

class SpadesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Spades to 300")
        self.root.geometry("1000x750")
        self.root.configure(bg='#2d5016')
        
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
        self.team_wins = [0, 0]  # Track round wins for each team
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
        self.main = tk.Frame(self.root, bg='#2d5016')
        self.main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.main, text="♠ Spades to 300 ♠", font=('Arial', 28, 'bold'), 
                bg='#2d5016', fg='black').pack(pady=10)
        
        menu = tk.Frame(self.main, bg='#2d5016')
        menu.pack()
        tk.Button(menu, text="💾 Save", font=('Arial', 9), bg='#4caf50', fg='black',
                 command=self.save_game).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="📂 Load", font=('Arial', 9), bg='#2196f3', fg='black',
                 command=self.load_game).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="📊 Stats", font=('Arial', 9), bg='#ff9800', fg='black',
                 command=self.show_stats).pack(side=tk.LEFT, padx=2)
        tk.Button(menu, text="🔄 New", font=('Arial', 9), bg='#f44336', fg='black',
                 command=self.new_game).pack(side=tk.LEFT, padx=2)
        
        score_frame = tk.Frame(self.main, bg='#2d5016')
        score_frame.pack(pady=5)
        
        t1 = tk.Frame(score_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        t1.pack(side=tk.LEFT, padx=10)
        tk.Label(t1, text="Team 1 (You & Teammate)", font=('Arial', 12, 'bold'),
                bg='#1a3a0f', fg='black').pack(pady=3)
        self.t1_score = tk.Label(t1, text="0/300", font=('Arial', 16, 'bold'),
                                bg='#1a3a0f', fg='black')
        self.t1_score.pack()
        self.t1_bags = tk.Label(t1, text="Bags: 0", font=('Arial', 9),
                               bg='#1a3a0f', fg='black')
        self.t1_bags.pack()
        self.t1_bid = tk.Label(t1, text="Bid: -", font=('Arial', 9, 'bold'),
                              bg='#1a3a0f', fg='black')
        self.t1_bid.pack()
        self.t1_wins = tk.Label(t1, text="Rounds Won: 0", font=('Arial', 9),
                               bg='#1a3a0f', fg='black')
        self.t1_wins.pack(pady=3)
        
        t2 = tk.Frame(score_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        t2.pack(side=tk.LEFT, padx=10)
        tk.Label(t2, text="Team 2 (East & West)", font=('Arial', 12, 'bold'),
                bg='#1a3a0f', fg='black').pack(pady=3)
        self.t2_score = tk.Label(t2, text="0/300", font=('Arial', 16, 'bold'),
                                bg='#1a3a0f', fg='black')
        self.t2_score.pack()
        self.t2_bags = tk.Label(t2, text="Bags: 0", font=('Arial', 9),
                               bg='#1a3a0f', fg='black')
        self.t2_bags.pack()
        self.t2_bid = tk.Label(t2, text="Bid: -", font=('Arial', 9, 'bold'),
                              bg='#1a3a0f', fg='black')
        self.t2_bid.pack()
        self.t2_wins = tk.Label(t2, text="Rounds Won: 0", font=('Arial', 9),
                               bg='#1a3a0f', fg='black')
        self.t2_wins.pack(pady=3)
        
        msg = tk.Frame(self.main, bg='black', relief=tk.RAISED, bd=2)
        msg.pack(pady=5, padx=10, fill=tk.X)
        self.msg = tk.Label(msg, text="Welcome!", font=('Arial', 11),
                           bg='black', fg='white', wraplength=900)
        self.msg.pack(pady=5)
        
        self.game_frame = tk.Frame(self.main, bg='#2d5016')
        self.game_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.hint_btn = tk.Button(self.main, text="💡 Hint", font=('Arial', 10, 'bold'),
                                 bg='#2196f3', fg='black', command=self.show_hint,
                                 state=tk.DISABLED)
        self.hint_btn.pack(pady=3)
    
    def save_game(self):
        try:
            if self.game_state == 'tutorial':
                messagebox.showinfo("Cannot Save", "Start a game first!")
                return
            
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
            
            messagebox.showinfo("Saved", "Game saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    
    def load_game(self):
        try:
            if not os.path.exists(SAVE_FILE):
                messagebox.showinfo("No Save", "No saved game found!")
                return
            
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
            elif self.game_state == 'bidding':
                self.show_bidding()
            
            self.update_scores()
            messagebox.showinfo("Loaded", "Game loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Load failed: {e}")
    
    def show_stats(self):
        try:
            win = tk.Toplevel(self.root)
            win.title("Statistics")
            win.geometry("400x350")
            win.configure(bg='white')
            
            tk.Label(win, text="📊 Statistics", font=('Arial', 16, 'bold'),
                    bg='white').pack(pady=15)
            
            txt = tk.Text(win, font=('Courier', 11), width=40, height=12,
                         bg='#f0f0f0', relief=tk.SUNKEN, bd=2)
            txt.pack(pady=10, padx=20)
            txt.insert('1.0', self.stats.get_summary())
            txt.config(state=tk.DISABLED)
            
            tk.Button(win, text="Close", font=('Arial', 10), bg='#757575',
                     fg='white', command=win.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Stats error: {e}")
    
    def new_game(self):
        if self.game_state != 'tutorial':
            if messagebox.askyesno("New Game", "Start new game? Progress lost."):
                self.scores = [[0, 0], [0, 0]]
                self.rounds = 0
                self.team_wins = [0, 0]
                self.start_game()
        else:
            self.start_game()
    
    def show_tutorial(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        f = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        f.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(f, text=f"Tutorial {self.tutorial_step + 1}/{len(self.tutorials)}",
                font=('Arial', 16, 'bold'), bg='white', fg='black').pack(pady=15, padx=20)
        
        tk.Label(f, text=self.tutorials[self.tutorial_step], font=('Arial', 12),
                bg='white', fg='black', wraplength=500).pack(pady=15, padx=20)
        
        b = tk.Frame(f, bg='white')
        b.pack(pady=15)
        
        if self.tutorial_step > 0:
            tk.Button(b, text="Previous", font=('Arial', 11), bg='#757575',
                     fg='black', padx=15, pady=8,
                     command=lambda: self.change_tut(-1)).pack(side=tk.LEFT, padx=5)
        
        if self.tutorial_step < len(self.tutorials) - 1:
            tk.Button(b, text="Next", font=('Arial', 11), bg='#4caf50',
                     fg='black', padx=15, pady=8,
                     command=lambda: self.change_tut(1)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(b, text="Start Game!", font=('Arial', 12, 'bold'),
                     bg='#2196f3', fg='black', padx=20, pady=8,
                     command=self.start_game).pack(side=tk.LEFT, padx=5)
        
        tk.Button(b, text="Skip Tutorial", font=('Arial', 11), bg='#ff9800',
                 fg='black', padx=15, pady=8,
                 command=self.start_game).pack(side=tk.LEFT, padx=5)
    
    def change_tut(self, d):
        self.tutorial_step += d
        self.show_tutorial()
    
    def start_game(self):
        self.game_state = 'bidding'
        self.rounds = 0
        self.deal_cards()
    
    def deal_cards(self):
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        
        # Verify no duplicates in deck
        deck_strings = [str(c) for c in deck]
        assert len(deck) == len(set(deck_strings)), "Duplicate cards in deck!"
        
        random.shuffle(deck)
        
        self.hands = [deck[i::4] for i in range(4)]
        for h in self.hands:
            h.sort(key=lambda c: (SUITS.index(c.suit), RANK_VALUES[c.rank]))
        
        # Verify each player has exactly 13 cards
        card_counts = [len(h) for h in self.hands]
        print(f"Cards dealt - counts: {card_counts}")
        assert all(count == 13 for count in card_counts), f"Card deal error: {card_counts}"
        
        # Verify no duplicates across all hands
        all_cards = []
        for hand in self.hands:
            all_cards.extend([str(c) for c in hand])
        assert len(all_cards) == len(set(all_cards)), "Duplicate cards across hands!"
        print(f"✓ No duplicate cards found")
        
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.spades_broken = False
        self.deal_failed = [False, False, False, False]  # Reset DEAL failure tracking
        self.rounds += 1
        
        self.msg.config(text="Bid tricks you'll win, or bid DEAL!")
        self.show_bidding()
    
    def show_bidding(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        hf = tk.Frame(self.game_frame, bg='#2d5016')
        hf.pack(side=tk.BOTTOM, pady=10)
        tk.Label(hf, text="Your Hand:", font=('Arial', 12, 'bold'),
                bg='#2d5016', fg='white').pack()
        cf = tk.Frame(hf, bg='#2d5016')
        cf.pack()
        for card in self.hands[0]:
            self.make_card(cf, card).pack(side=tk.LEFT, padx=1)
        
        bf = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        bf.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        tk.Label(bf, text="Place Your Bid", font=('Arial', 16, 'bold'),
                bg='white', fg='black').pack(pady=8)
        
        tk.Button(bf, text="🤝 DEAL (+100 for 0 tricks, -100 if any)",
                 font=('Arial', 11, 'bold'), bg='#f44336', fg='black',
                 padx=15, pady=8, command=lambda: self.make_bid(0, True)).pack(pady=8)
        
        nf = tk.Frame(bf, bg='white')
        nf.pack(pady=8)
        for i in range(1, 14):
            tk.Button(nf, text=str(i), font=('Arial', 12, 'bold'),
                     bg='#2196f3', fg='black', width=3,
                     command=lambda b=i: self.make_bid(b, False)).grid(
                         row=(i-1)//7, column=(i-1)%7, padx=3, pady=3)
        
        self.hint_btn.config(state=tk.NORMAL)
    
    def make_bid(self, bid, is_deal):
        self.bids[0] = 0 if is_deal else bid
        self.deal_bids[0] = is_deal
        self.msg.config(text=f"You bid {'DEAL' if is_deal else bid}. AI bidding...")
        self.root.after(1000, self.ai_bids)
    
    def ai_bids(self):
        for i in range(1, 4):
            if random.random() < 0.15:
                self.bids[i] = 0
                self.deal_bids[i] = True
            else:
                self.bids[i] = random.randint(1, 5)
        
        # Show all bids
        names = ['You', 'East', 'Teammate', 'West']
        bid_summary = "\n".join([f"{names[i]}: {self.bid_txt(i)}" for i in range(4)])
        team1_total = self.bids[0] + self.bids[2]
        team2_total = self.bids[1] + self.bids[3]
        
        self.msg.config(text=f"Bids:\n{bid_summary}\nTeam 1 Total: {team1_total} | Team 2 Total: {team2_total}")
        
        # Update team bid displays
        self.t1_bid.config(text=f"Bid: {team1_total}")
        self.t2_bid.config(text=f"Bid: {team2_total}")
        
        self.game_state = 'playing'
        self.current_player = 0
        self.show_playing()
    
    def show_playing(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        # Your hand at TOP
        hnd = tk.Frame(self.game_frame, bg='#2d5016')
        hnd.pack(side=tk.TOP, pady=5)
        tk.Label(hnd, text=f"Your Hand - {self.bid_txt(0)} | Won: {self.tricks[0]} | Cards: {len(self.hands[0])}",
                font=('Arial', 10, 'bold'), bg='#2d5016', fg='white').pack()
        cds = tk.Frame(hnd, bg='#2d5016')
        cds.pack()
        
        for card in self.hands[0]:
            playable = self.can_play(card)
            lbl = self.make_card(cds, card, playable, playable)
            lbl.pack(side=tk.LEFT, padx=0.5)
            if playable and self.current_player == 0:
                lbl.bind('<Button-1>', lambda e, c=card: self.play_card(0, c))
        
        mid = tk.Frame(self.game_frame, bg='#2d5016')
        mid.pack(fill=tk.BOTH, expand=True)
        
        # West
        w = tk.Frame(mid, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        w.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        tk.Label(w, text=f"West\n{self.bid_txt(3)}\nWon: {self.tricks[3]}\nCards: {len(self.hands[3])}",
                font=('Arial', 9, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        for _ in self.hands[3]:
            tk.Label(w, text="🂠", font=('Arial', 14), bg='#1a3a0f', fg='white').pack(pady=2)
        
        # Center
        ctr = tk.Frame(mid, bg='#1a5016', relief=tk.SUNKEN, bd=4, width=350, height=250)
        ctr.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        ctr.pack_propagate(False)
        
        if self.current_trick:
            names = ['You', 'East', 'Teammate', 'West']
            
            # Display in order around center: You (top), West (left), Teammate (bottom), East (right)
            positions = {
                0: (0.5, 0.15),   # You - top center
                1: (0.75, 0.5),   # East - right middle  
                2: (0.5, 0.85),   # Teammate - bottom center
                3: (0.25, 0.5)    # West - left middle
            }
            
            # Display each card that has been played
            for play in self.current_trick:
                player_idx = play['player']
                pf = tk.Frame(ctr, bg='#1a5016')
                pos = positions[player_idx]
                pf.place(relx=pos[0], rely=pos[1], anchor=tk.CENTER)
                self.make_card(pf, play['card'], False).pack()
                tk.Label(pf, text=names[player_idx], font=('Arial', 9, 'bold'),
                        bg='#1a5016', fg='white').pack()
        
        # East
        e = tk.Frame(mid, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        e.pack(side=tk.LEFT, padx=5, anchor=tk.E)
        tk.Label(e, text=f"East\n{self.bid_txt(1)}\nWon: {self.tricks[1]}\nCards: {len(self.hands[1])}",
                font=('Arial', 9, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        for _ in self.hands[1]:
            tk.Label(e, text="🂠", font=('Arial', 14), bg='#1a3a0f', fg='white').pack(pady=2)
        
        # North at BOTTOM
        n = tk.Frame(self.game_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        n.pack(side=tk.BOTTOM, pady=5)
        tk.Label(n, text=f"Teammate - {self.bid_txt(2)} | Won: {self.tricks[2]} | Cards: {len(self.hands[2])}",
                font=('Arial', 10, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        nc = tk.Frame(n, bg='#1a3a0f')
        nc.pack()
        for _ in self.hands[2]:
            tk.Label(nc, text="🂠", font=('Arial', 16), bg='#1a3a0f', fg='white').pack(side=tk.LEFT, padx=2)
        
        if self.current_player != 0:
            self.root.after(1000, self.ai_play)
        
        self.update_scores()
    
    def bid_txt(self, p):
        return "DEAL" if self.deal_bids[p] else str(self.bids[p])
    
    def make_card(self, parent, card, clickable=True, highlight=False):
        # Card background colors by suit (darker colors)
        suit_colors = {
            '♠': '#c0c0c0',      # Darker gray for spades
            '♥': '#ffb0b0',      # Darker red for hearts
            '♦': '#b0d0ff',      # Darker blue for diamonds
            '♣': '#b0ffb0'       # Darker green for clubs
        }
        
        if highlight:
            bg = '#ffff00'  # Yellow highlight for playable cards
        else:
            bg = suit_colors.get(card.suit, 'white')
        
        f = tk.Frame(parent, bg=bg, relief=tk.RAISED, bd=2, width=42, height=62)
        f.pack_propagate(False)
        color = 'red' if card.is_red() else 'black'
        
        # Rank at top (smaller)
        tk.Label(f, text=card.rank, font=('Arial', 9, 'bold'), bg=bg, fg=color).pack(anchor=tk.NW, padx=2)
        
        # Suit in center (much larger)
        tk.Label(f, text=card.suit, font=('Arial', 28), bg=bg, fg=color).pack(expand=True)
        
        if not clickable:
            f.config(relief=tk.FLAT, bd=1)
        return f
    
    def can_play(self, card):
        if self.current_player != 0:
            return False
        hand = self.hands[0]
        if not self.current_trick:
            if not self.spades_broken and card.suit == '♠':
                return all(c.suit == '♠' for c in hand)
            return True
        has = any(c.suit == self.lead_suit for c in hand)
        return card.suit == self.lead_suit if has else True
    
    def play_card(self, player, card):
        # CRITICAL: Verify card is actually in hand before playing
        if card not in self.hands[player]:
            print(f"ERROR: Card {card} not in player {player}'s hand!")
            print(f"Player {player} hand: {self.hands[player]}")
            return
        
        # Verify we're not in a weird state
        if len(self.current_trick) >= 4:
            print(f"ERROR: Trick already has 4 cards! Not playing another.")
            return
        
        # Check if this card was already played this trick
        trick_cards = [p['card'] for p in self.current_trick]
        if any(str(c) == str(card) for c in trick_cards):
            print(f"ERROR: Card {card} already played this trick!")
            return
        
        # Remove card and add to trick
        self.hands[player].remove(card)
        self.current_trick.append({'player': player, 'card': card})
        
        print(f"Player {player} played {card}. Cards left: {len(self.hands[player])}")
        
        if len(self.current_trick) == 1:
            self.lead_suit = card.suit
        if card.suit == '♠' and self.lead_suit != '♠':
            self.spades_broken = True
        
        # Check if trick is complete
        if len(self.current_trick) == 4:
            # All 4 cards played - update display and finish trick
            self.show_playing()
            self.root.after(2000, self.finish_trick)
        else:
            # Not complete yet - move to next player
            self.current_player = (player + 1) % 4
            self.show_playing()
            
            # Only schedule AI if it's their turn
            if self.current_player != 0:
                self.root.after(1000, self.ai_play)
    
    def ai_play(self):
        # Safety check - make sure it's not player 0's turn
        if self.current_player == 0:
            return
        
        hand = self.hands[self.current_player]
        
        # Safety check - make sure AI has cards
        if not hand:
            print(f"ERROR: Player {self.current_player} has no cards!")
            return
        
        playable = hand.copy()
        
        if self.current_trick:
            same = [c for c in hand if c.suit == self.lead_suit]
            if same:
                playable = same
        elif not self.spades_broken:
            non = [c for c in hand if c.suit != '♠']
            if non:
                playable = non
        
        if playable:
            self.play_card(self.current_player, random.choice(playable))
        else:
            print(f"ERROR: Player {self.current_player} has no playable cards!")
    
    def finish_trick(self):
        winner = self.current_trick[0]
        for p in self.current_trick:
            if p['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = p
            elif (p['card'].suit == winner['card'].suit and
                  RANK_VALUES[p['card'].rank] > RANK_VALUES[winner['card'].rank]):
                winner = p
        
        self.tricks[winner['player']] += 1
        names = ['You', 'East', 'North', 'West']
        self.msg.config(text=f"{names[winner['player']]} won the trick!")
        
        self.current_trick = []
        self.lead_suit = None
        self.current_player = winner['player']
        
        if not self.hands[0]:
            self.calc_score()
        else:
            self.show_playing()
    
    def calc_score(self):
        prev_score1 = self.scores[0][0]
        prev_score2 = self.scores[1][0]
        
        pts = [0, 0]
        deal_results = []  # Track DEAL results for popup
        names = ['You', 'East', 'Teammate', 'West']
        
        for ti, players in enumerate([[0, 2], [1, 3]]):
            for p in players:
                made = (self.tricks[p] >= self.bids[p]) if not self.deal_bids[p] else (self.tricks[p] == 0)
                
                if p == 0:
                    self.stats.record_bid(made, self.deal_bids[p])
                
                if self.deal_bids[p]:
                    # Check if this player bid DEAL
                    if self.tricks[p] == 0:
                        # Success
                        pts[ti] += 100
                        deal_results.append((names[p], True, 0))
                        print(f"{names[p]} DEAL SUCCESS - won 0 tricks")
                    else:
                        # Failed
                        pts[ti] -= 100
                        deal_results.append((names[p], False, self.tricks[p]))
                        print(f"{names[p]} DEAL FAILED - won {self.tricks[p]} tricks")
                else:
                    if self.tricks[p] >= self.bids[p]:
                        pts[ti] += self.bids[p] * 10 + (self.tricks[p] - self.bids[p])
                    else:
                        pts[ti] -= self.bids[p] * 10
        
        # Show DEAL results popup if anyone bid DEAL
        if deal_results:
            print(f"Showing DEAL popup with {len(deal_results)} results")
            self.show_deal_results(deal_results)
        else:
            print("No DEAL results to show")
        
        self.scores[0][0] += pts[0]
        self.scores[1][0] += pts[1]
        
        for ti, players in enumerate([[0, 2], [1, 3]]):
            bags = sum((self.tricks[p] - self.bids[p]) for p in players
                      if not self.deal_bids[p] and self.tricks[p] > self.bids[p])
            self.scores[ti][1] += bags
            
            if ti == 0:
                self.stats.stats['bags'] += bags
            
            if self.scores[ti][1] >= 10:
                self.scores[ti][0] -= 100
                self.scores[ti][1] -= 10
                if ti == 0:
                    self.stats.stats['sandbagged'] += 1
                messagebox.showinfo("Sandbagged!", f"Team {ti+1}: -100 for 10 bags!")
        
        self.update_scores()
        
        # Determine round winner
        if self.scores[0][0] > prev_score1:
            round_pts1 = self.scores[0][0] - prev_score1
        else:
            round_pts1 = 0
        if self.scores[1][0] > prev_score2:
            round_pts2 = self.scores[1][0] - prev_score2
        else:
            round_pts2 = 0
        
        if round_pts1 > round_pts2:
            self.team_wins[0] += 1
        elif round_pts2 > round_pts1:
            self.team_wins[1] += 1
        
        if self.scores[0][0] >= WINNING_SCORE or self.scores[1][0] >= WINNING_SCORE:
            won = self.scores[0][0] > self.scores[1][0]
            self.stats.record_game(won)
            
            winner = "Team 1 (YOU WIN!)" if won else "Team 2"
            messagebox.showinfo("🏆 GAME OVER!",
                              f"{winner}\n\nTeam 1: {self.scores[0][0]}\nTeam 2: {self.scores[1][0]}")
            self.scores = [[0, 0], [0, 0]]
            self.rounds = 0
            self.deal_cards()
        else:
            messagebox.showinfo("Round Complete",
                              f"Your team: {self.tricks[0] + self.tricks[2]}\nOpponents: {self.tricks[1] + self.tricks[3]}")
            self.deal_cards()
    
    def show_deal_results(self, deal_results):
        """Show custom popup for DEAL results"""
        popup = tk.Toplevel(self.root)
        popup.title("DEAL Results")
        popup.geometry("450x350")
        popup.configure(bg='white')
        
        tk.Label(popup, text="🎲 DEAL RESULTS 🎲", font=('Arial', 18, 'bold'),
                bg='white', fg='black').pack(pady=15)
        
        for player_name, success, tricks_won in deal_results:
            result_frame = tk.Frame(popup, bg='white', relief=tk.RAISED, bd=3)
            result_frame.pack(pady=10, padx=20, fill=tk.X)
            
            if success:
                # Success - green background
                result_frame.config(bg='#90EE90')
                tk.Label(result_frame, text=f"✅ {player_name}", font=('Arial', 16, 'bold'),
                        bg='#90EE90', fg='darkgreen').pack(pady=5)
                tk.Label(result_frame, text="DEAL SUCCESS!", font=('Arial', 14, 'bold'),
                        bg='#90EE90', fg='darkgreen').pack()
                tk.Label(result_frame, text="Won 0 tricks", font=('Arial', 11),
                        bg='#90EE90', fg='darkgreen').pack()
                tk.Label(result_frame, text="+100 points", font=('Arial', 14, 'bold'),
                        bg='#90EE90', fg='darkgreen').pack(pady=5)
            else:
                # Failed - red background with bold message
                result_frame.config(bg='#FF6B6B')
                tk.Label(result_frame, text=f"❌ {player_name.upper()}", font=('Arial', 16, 'bold'),
                        bg='#FF6B6B', fg='white').pack(pady=5)
                tk.Label(result_frame, text="JUST FAILED A DEAL!", font=('Arial', 14, 'bold'),
                        bg='#FF6B6B', fg='white').pack()
                tk.Label(result_frame, text=f"Won {tricks_won} trick{'s' if tricks_won != 1 else ''}", 
                        font=('Arial', 11, 'bold'), bg='#FF6B6B', fg='white').pack()
                tk.Label(result_frame, text="-100 points", font=('Arial', 14, 'bold'),
                        bg='#FF6B6B', fg='white').pack(pady=5)
        
        tk.Button(popup, text="Continue", font=('Arial', 12, 'bold'),
                 bg='#2196f3', fg='white', padx=30, pady=10,
                 command=popup.destroy).pack(pady=15)
    
    def update_scores(self):
        self.t1_score.config(text=f"{self.scores[0][0]}/300")
        self.t1_bags.config(text=f"Bags: {self.scores[0][1]}")
        self.t1_wins.config(text=f"Rounds Won: {self.team_wins[0]}")
        
        # Update team bids if they exist
        if self.bids[0] is not None:
            team1_total = self.bids[0] + self.bids[2]
            self.t1_bid.config(text=f"Bid: {team1_total}")
        
        self.t2_score.config(text=f"{self.scores[1][0]}/300")
        self.t2_bags.config(text=f"Bags: {self.scores[1][1]}")
        self.t2_wins.config(text=f"Rounds Won: {self.team_wins[1]}")
        
        if self.bids[1] is not None:
            team2_total = self.bids[1] + self.bids[3]
            self.t2_bid.config(text=f"Bid: {team2_total}")
    
    def show_hint(self):
        if self.game_state == 'bidding':
            hand = self.hands[0]
            spades = len([c for c in hand if c.suit == '♠'])
            high = len([c for c in hand if RANK_VALUES[c.rank] >= 11])
            low = len([c for c in hand if RANK_VALUES[c.rank] <= 5])
            
            hint = f"You have {spades} spades, {high} high cards, {low} low.\n"
            if low >= 10 and high <= 2:
                hint += "Weak hand - consider DEAL!"
            else:
                hint += f"Try bidding {max(1, spades // 3 + high // 2)}."
            messagebox.showinfo("Hint", hint)
        else:
            if self.deal_bids[0]:
                hint = "You bid DEAL! Play LOWEST cards!"
            elif not self.current_trick:
                hint = "You're leading! Play high cards, save spades."
            else:
                has = any(c.suit == self.lead_suit for c in self.hands[0])
                hint = f"Follow suit ({self.lead_suit})" if has else "No suit! Spade to win or dump low."
            messagebox.showinfo("Hint", hint)

def run_tests():
    """Unit tests for game logic"""
    print("Running tests...")
    
    # Test 1: Card creation
    try:
        card = Card('♠', 'A')
        assert card.suit == '♠'
        assert card.rank == 'A'
        assert not card.is_red()
        print("✓ Card tests passed")
    except AssertionError:
        print("✗ Card tests failed")
    
    # Test 2: Card serialization
    try:
        card = Card('♥', 'K')
        d = card.to_dict()
        restored = Card.from_dict(d)
        assert restored.suit == card.suit
        assert restored.rank == card.rank
        print("✓ Serialization tests passed")
    except AssertionError:
        print("✗ Serialization tests failed")
    
    # Test 3: Deck creation
    try:
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        assert len(deck) == 52
        assert len(set(str(c) for c in deck)) == 52
        print("✓ Deck tests passed")
    except AssertionError:
        print("✗ Deck tests failed")
    
    # Test 4: Statistics
    try:
        stats = GameStats()
        assert stats.stats['games_played'] >= 0
        assert stats.get_win_rate() >= 0
        print("✓ Stats tests passed")
    except AssertionError:
        print("✗ Stats tests failed")
    
    print("Tests complete!\n")

if __name__ == '__main__':
    run_tests()
    print("Starting game...")
    root = tk.Tk()
    game = SpadesGame(root)
    root.mainloop()