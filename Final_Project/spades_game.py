import tkinter as tk
from tkinter import messagebox
import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i+2 for i, r in enumerate(RANKS)}
WINNING_SCORE = 300

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        return f"{self.rank}{self.suit}"
    
    def is_red(self):
        return self.suit in ['♥', '♦']

class SpadesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Spades to 300")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2d5016')
        
        self.game_state = 'tutorial'
        self.hands = [[], [], [], []]
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.current_player = 0
        self.lead_suit = None
        self.spades_played = False
        self.scores = [[0, 0], [0, 0]]
        self.tutorial_step = 0
        
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
        self.main_frame = tk.Frame(self.root, bg='#2d5016')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.main_frame, text="♠ Spades to 300 ♠", 
                font=('Arial', 28, 'bold'), bg='#2d5016', fg='black').pack(pady=10)
        
        score_frame = tk.Frame(self.main_frame, bg='#2d5016')
        score_frame.pack(pady=5)
        
        # Team 1 Score
        team1_frame = tk.Frame(score_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        team1_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(team1_frame, text="Team 1 (You & North)", 
                font=('Arial', 12, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        self.team1_score = tk.Label(team1_frame, text="0/300", 
                                    font=('Arial', 16, 'bold'), bg='#1a3a0f', fg='black')
        self.team1_score.pack()
        self.team1_bags = tk.Label(team1_frame, text="Bags: 0", 
                                   font=('Arial', 9), bg='#1a3a0f', fg='black')
        self.team1_bags.pack(pady=3)
        
        # Team 2 Score
        team2_frame = tk.Frame(score_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        team2_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(team2_frame, text="Team 2 (East & West)", 
                font=('Arial', 12, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        self.team2_score = tk.Label(team2_frame, text="0/300", 
                                    font=('Arial', 16, 'bold'), bg='#1a3a0f', fg='black')
        self.team2_score.pack()
        self.team2_bags = tk.Label(team2_frame, text="Bags: 0", 
                                   font=('Arial', 9), bg='#1a3a0f', fg='black')
        self.team2_bags.pack(pady=3)
        
        # Message area
        msg_frame = tk.Frame(self.main_frame, bg='#ffeb3b', relief=tk.RAISED, bd=2)
        msg_frame.pack(pady=5, padx=10, fill=tk.X)
        self.msg_label = tk.Label(msg_frame, text="Welcome!", 
                                  font=('Arial', 11), bg='#ffeb3b', wraplength=900)
        self.msg_label.pack(pady=5, padx=5)
        
        self.game_frame = tk.Frame(self.main_frame, bg='#2d5016')
        self.game_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.hint_btn = tk.Button(self.main_frame, text="💡 Hint (-5pts)", 
                                 font=('Arial', 10, 'bold'), bg='#2196f3', fg='white',
                                 command=self.show_hint, state=tk.DISABLED)
        self.hint_btn.pack(pady=3)
    
    def show_tutorial(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text=f"Tutorial {self.tutorial_step + 1}/{len(self.tutorials)}", 
                font=('Arial', 16, 'bold'), bg='white').pack(pady=15, padx=20)
        
        tk.Label(frame, text=self.tutorials[self.tutorial_step], 
                font=('Arial', 12), bg='white', wraplength=500).pack(pady=15, padx=20)
        
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(pady=15)
        
        if self.tutorial_step > 0:
            tk.Button(btn_frame, text="Previous", font=('Arial', 11), bg='#757575', 
                     fg='white', padx=15, pady=8, 
                     command=lambda: self.change_tutorial(-1)).pack(side=tk.LEFT, padx=5)
        
        if self.tutorial_step < len(self.tutorials) - 1:
            tk.Button(btn_frame, text="Next", font=('Arial', 11), bg='#4caf50', 
                     fg='white', padx=15, pady=8,
                     command=lambda: self.change_tutorial(1)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="Start Game!", font=('Arial', 12, 'bold'), 
                     bg='#2196f3', fg='white', padx=20, pady=8,
                     command=self.start_game).pack(side=tk.LEFT, padx=5)
    
    def change_tutorial(self, direction):
        self.tutorial_step += direction
        self.show_tutorial()
    
    def start_game(self):
        self.game_state = 'bidding'
        self.deal_cards()
    
    def deal_cards(self):
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(deck)
        
        self.hands = [deck[i::4] for i in range(4)]
        for hand in self.hands:
            hand.sort(key=lambda c: (SUITS.index(c.suit), RANK_VALUES[c.rank]))
        
        self.bids = [None] * 4
        self.deal_bids = [False] * 4
        self.tricks = [0] * 4
        self.current_trick = []
        self.spades_played = False
        
        self.msg_label.config(text="Bid tricks you'll win, or bid DEAL!")
        self.show_bidding()
    
    def show_bidding(self):
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        # Show hand
        hand_frame = tk.Frame(self.game_frame, bg='#2d5016')
        hand_frame.pack(side=tk.BOTTOM, pady=10)
        tk.Label(hand_frame, text="Your Hand:", font=('Arial', 12, 'bold'), 
                bg='#2d5016', fg='black').pack()
        cards_frame = tk.Frame(hand_frame, bg='#2d5016')
        cards_frame.pack()
        for card in self.hands[0]:
            self.make_card(cards_frame, card).pack(side=tk.LEFT, padx=1)
        
        # Bid options
        bid_frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=4)
        bid_frame.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        tk.Label(bid_frame, text="Place Your Bid", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=8)
        
        tk.Button(bid_frame, text="🤝 DEAL (+100 for 0 tricks, -100 if any)", 
                 font=('Arial', 11, 'bold'), bg='#f44336', fg='white', 
                 padx=15, pady=8, command=lambda: self.make_bid(0, True)).pack(pady=8)
        
        num_frame = tk.Frame(bid_frame, bg='white')
        num_frame.pack(pady=8)
        for i in range(1, 14):
            tk.Button(num_frame, text=str(i), font=('Arial', 12, 'bold'), 
                     bg='#2196f3', fg='white', width=3,
                     command=lambda b=i: self.make_bid(b, False)).grid(
                         row=(i-1)//7, column=(i-1)%7, padx=3, pady=3)
        
        self.hint_btn.config(state=tk.NORMAL)
    
    def make_bid(self, bid, is_deal):
        self.bids[0] = 0 if is_deal else bid
        self.deal_bids[0] = is_deal
        self.msg_label.config(text=f"You bid {'DEAL' if is_deal else bid}. AI bidding...")
        self.root.after(1000, self.ai_bids)
    
    def ai_bids(self):
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
        for w in self.game_frame.winfo_children():
            w.destroy()
        
        # North player
        north = tk.Frame(self.game_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        north.pack(side=tk.TOP, pady=5)
        tk.Label(north, text=f"North - {self.bid_text(2)} | Won: {self.tricks[2]}", 
                font=('Arial', 10, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        nc = tk.Frame(north, bg='#1a3a0f')
        nc.pack()
        for _ in self.hands[2]:
            tk.Label(nc, text="🂠", font=('Arial', 16), bg='#1a3a0f', fg='black').pack(side=tk.LEFT)
        
        # Middle section
        mid = tk.Frame(self.game_frame, bg='#2d5016')
        mid.pack(fill=tk.BOTH, expand=True)
        
        # West player
        west = tk.Frame(mid, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        west.pack(side=tk.LEFT, padx=5, anchor=tk.W)
        tk.Label(west, text=f"West\n{self.bid_text(3)}\n{self.tricks[3]}", 
                font=('Arial', 9, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        for _ in self.hands[3]:
            tk.Label(west, text="🂠", font=('Arial', 14), bg='#1a3a0f', fg='black').pack()
        
        # Center trick area
        center = tk.Frame(mid, bg='#1a5016', relief=tk.SUNKEN, bd=4, width=350, height=250)
        center.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        center.pack_propagate(False)
        
        if self.current_trick:
            trick = tk.Frame(center, bg='#1a5016')
            trick.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            names = ['You', 'East', 'North', 'West']
            for play in self.current_trick:
                cf = tk.Frame(trick, bg='#1a5016')
                cf.pack(side=tk.LEFT, padx=8)
                self.make_card(cf, play['card'], False).pack()
                tk.Label(cf, text=names[play['player']], 
                        font=('Arial', 9), bg='#1a5016', fg='black').pack()
        
        # East player
        east = tk.Frame(mid, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        east.pack(side=tk.LEFT, padx=5, anchor=tk.E)
        tk.Label(east, text=f"East\n{self.bid_text(1)}\n{self.tricks[1]}", 
                font=('Arial', 9, 'bold'), bg='#1a3a0f', fg='black').pack(pady=3)
        for _ in self.hands[1]:
            tk.Label(east, text="🂠", font=('Arial', 14), bg='#1a3a0f', fg='black').pack()
        
        # Your hand
        hand = tk.Frame(self.game_frame, bg='#2d5016')
        hand.pack(side=tk.BOTTOM, pady=5)
        tk.Label(hand, text=f"Your Hand - {self.bid_text(0)} | Won: {self.tricks[0]}", 
                font=('Arial', 11, 'bold'), bg='#2d5016', fg='black').pack()
        cards = tk.Frame(hand, bg='#2d5016')
        cards.pack()
        
        for card in self.hands[0]:
            playable = self.can_play(card)
            lbl = self.make_card(cards, card, playable, playable)
            lbl.pack(side=tk.LEFT, padx=1)
            if playable and self.current_player == 0:
                lbl.bind('<Button-1>', lambda e, c=card: self.play_card(0, c))
        
        if self.current_player != 0:
            self.root.after(1000, self.ai_play)
        
        self.update_scores()
    
    def bid_text(self, player):
        return "DEAL" if self.deal_bids[player] else str(self.bids[player])
    
    def make_card(self, parent, card, clickable=True, highlight=False):
        bg = '#ffff00' if highlight else 'white'
        frame = tk.Frame(parent, bg=bg, relief=tk.RAISED, bd=2, width=50, height=70)
        frame.pack_propagate(False)
        color = 'red' if card.is_red() else 'black'
        tk.Label(frame, text=card.rank, font=('Arial', 12, 'bold'), bg=bg, fg=color).pack(anchor=tk.NW)
        tk.Label(frame, text=card.suit, font=('Arial', 16), bg=bg, fg=color).pack(expand=True)
        if not clickable:
            frame.config(relief=tk.FLAT, bd=1)
        return frame
    
    def can_play(self, card):
        if self.current_player != 0:
            return False
        hand = self.hands[0]
        if not self.current_trick:
            if not self.spades_played and card.suit == '♠':
                return all(c.suit == '♠' for c in hand)
            return True
        has_suit = any(c.suit == self.lead_suit for c in hand)
        return card.suit == self.lead_suit if has_suit else True
    
    def play_card(self, player, card):
        self.hands[player].remove(card)
        self.current_trick.append({'player': player, 'card': card})
        
        if len(self.current_trick) == 1:
            self.lead_suit = card.suit
        if card.suit == '♠' and self.lead_suit != '♠':
            self.spades_played = True
        
        if len(self.current_trick) == 4:
            self.root.after(1500, self.finish_trick)
        else:
            self.current_player = (player + 1) % 4
            self.show_playing()
    
    def ai_play(self):
        hand = self.hands[self.current_player]
        playable = hand.copy()
        
        if self.current_trick:
            same_suit = [c for c in hand if c.suit == self.lead_suit]
            if same_suit:
                playable = same_suit
        elif not self.spades_played:
            non_spades = [c for c in hand if c.suit != '♠']
            if non_spades:
                playable = non_spades
        
        self.play_card(self.current_player, random.choice(playable))
    
    def finish_trick(self):
        winner = self.current_trick[0]
        for play in self.current_trick:
            if play['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = play
            elif (play['card'].suit == winner['card'].suit and 
                  RANK_VALUES[play['card'].rank] > RANK_VALUES[winner['card'].rank]):
                winner = play
        
        self.tricks[winner['player']] += 1
        names = ['You', 'East', 'North', 'West']
        self.msg_label.config(text=f"{names[winner['player']]} won the trick!")
        
        self.current_trick = []
        self.lead_suit = None
        self.current_player = winner['player']
        
        if not self.hands[0]:
            self.calc_score()
        else:
            self.show_playing()
    
    def calc_score(self):
        pts = [0, 0]
        for team_idx, players in enumerate([[0, 2], [1, 3]]):
            for p in players:
                if self.deal_bids[p]:
                    pts[team_idx] += 100 if self.tricks[p] == 0 else -100
                else:
                    if self.tricks[p] >= self.bids[p]:
                        pts[team_idx] += self.bids[p] * 10 + (self.tricks[p] - self.bids[p])
                    else:
                        pts[team_idx] -= self.bids[p] * 10
        
        self.scores[0][0] += pts[0]
        self.scores[1][0] += pts[1]
        
        for team_idx, players in enumerate([[0, 2], [1, 3]]):
            bags = sum((self.tricks[p] - self.bids[p]) for p in players 
                      if not self.deal_bids[p] and self.tricks[p] > self.bids[p])
            self.scores[team_idx][1] += bags
            if self.scores[team_idx][1] >= 10:
                self.scores[team_idx][0] -= 100
                self.scores[team_idx][1] -= 10
                messagebox.showinfo("Sandbagged!", f"Team {team_idx+1}: -100 for 10 bags!")
        
        self.update_scores()
        
        if self.scores[0][0] >= WINNING_SCORE or self.scores[1][0] >= WINNING_SCORE:
            winner = "Team 1" if self.scores[0][0] > self.scores[1][0] else "Team 2"
            messagebox.showinfo("🏆 GAME OVER!", 
                              f"{winner} WINS!\n\nTeam 1: {self.scores[0][0]}\nTeam 2: {self.scores[1][0]}")
            self.scores = [[0, 0], [0, 0]]
            self.deal_cards()
        else:
            messagebox.showinfo("Round Complete", 
                              f"Your team: {self.tricks[0] + self.tricks[2]}\nOpponents: {self.tricks[1] + self.tricks[3]}")
            self.deal_cards()
    
    def update_scores(self):
        self.team1_score.config(text=f"{self.scores[0][0]}/300")
        self.team1_bags.config(text=f"Bags: {self.scores[0][1]}")
        self.team2_score.config(text=f"{self.scores[1][0]}/300")
        self.team2_bags.config(text=f"Bags: {self.scores[1][1]}")
    
    def show_hint(self):
        self.scores[0][0] -= 5
        self.update_scores()
        
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
            messagebox.showinfo("Hint (-5pts)", hint)
        else:
            if self.deal_bids[0]:
                hint = "You bid DEAL! Play LOWEST cards!"
            elif not self.current_trick:
                hint = "You're leading! Play high cards, save spades."
            else:
                has_suit = any(c.suit == self.lead_suit for c in self.hands[0])
                hint = f"Follow suit ({self.lead_suit})" if has_suit else "No suit! Spade to win or dump low."
            messagebox.showinfo("Hint (-5pts)", hint)

if __name__ == '__main__':
    root = tk.Tk()
    game = SpadesGame(root)
    root.mainloop()