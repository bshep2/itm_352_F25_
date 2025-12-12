import tkinter as tk
from tkinter import messagebox
import random

# Constants
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
}
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
        self.root.title("Spades to 300 - Learn & Play")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2d5016')
        
        # Game state
        self.game_state = 'tutorial'
        self.hands = [[], [], [], []]
        self.bids = [None, None, None, None]
        self.deal_bids = [False, False, False, False]
        self.tricks = [0, 0, 0, 0]
        self.current_trick = []
        self.current_player = 0
        self.lead_suit = None
        self.spades_played = False
        self.scores = [[0, 0], [0, 0]]
        self.tutorial_step = 0
        self.hints_used = 0
        
        self.tutorial_steps = [
            "Welcome to Spades! Play with 4 players in 2 teams.\nYou and North are partners against East and West.",
            "Goal: First team to 300 points wins! Play multiple rounds.\nBid tricks you'll win each round. Spades are always trump!",
            "Each player gets 13 cards. You'll see your cards at the bottom.",
            "First, everyone bids (1-13). Your team's bids are added together.",
            "Special bid: 'DEAL' - Bet you won't win ANY tricks!\nSuccess = +100 points, Failure = -100 points. Use with bad hands!",
            "After bidding, follow suit if possible. If you can't, play any card.",
            "Spades beat any other suit! But can't lead spades until\n'broken' (played when you couldn't follow suit).",
            "Highest card of led suit wins, unless spade played.\nHighest spade wins the trick!",
            "Scoring: Make bid = 10 × bid + overtricks. Fail = -10 × bid.\n10 overtricks = -100 points (sandbagging penalty)!",
            "Play multiple rounds until a team reaches 300 points to win!"
        ]
        
        self.setup_ui()
        self.show_tutorial()
    
    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg='#2d5016')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.title_label = tk.Label(
            self.main_frame,
            text="♠ Spades to 300 ♠",
            font=('Arial', 32, 'bold'),
            bg='#2d5016',
            fg='white'
        )
        self.title_label.pack(pady=10)
        
        self.score_frame = tk.Frame(self.main_frame, bg='#2d5016')
        self.score_frame.pack(pady=10)
        
        self.team1_frame = tk.Frame(self.score_frame, bg='#1a3a0f', relief=tk.RAISED, bd=3)
        self.team1_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(self.team1_frame, text="👥 Team 1 (You & North)", 
                 font=('Arial', 14, 'bold'), bg='#1a3a0f', fg='white').pack(pady=5)
        self.team1_score_label = tk.Label(self.team1_frame, text="0 / 300", 
                                          font=('Arial', 20, 'bold'), bg='#1a3a0f', fg='yellow')
        self.team1_score_label.pack()
        self.team1_bags_label = tk.Label(self.team1_frame, text="Bags: 0", 
                                         font=('Arial', 10), bg='#1a3a0f', fg='white')
        self.team1_bags_label.pack(pady=5)
        
        self.team2_frame = tk.Frame(self.score_frame, bg='#1a3a0f', relief=tk.RAISED, bd=3)
        self.team2_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(self.team2_frame, text="👥 Team 2 (East & West)", 
                 font=('Arial', 14, 'bold'), bg='#1a3a0f', fg='white').pack(pady=5)
        self.team2_score_label = tk.Label(self.team2_frame, text="0 / 300", 
                                          font=('Arial', 20, 'bold'), bg='#1a3a0f', fg='yellow')
        self.team2_score_label.pack()
        self.team2_bags_label = tk.Label(self.team2_frame, text="Bags: 0", 
                                         font=('Arial', 10), bg='#1a3a0f', fg='white')
        self.team2_bags_label.pack(pady=5)
        
        self.message_frame = tk.Frame(self.main_frame, bg='#ffeb3b', relief=tk.RAISED, bd=3)
        self.message_frame.pack(pady=10, padx=20, fill=tk.X)
        self.message_label = tk.Label(
            self.message_frame,
            text="Welcome!",
            font=('Arial', 12),
            bg='#ffeb3b',
            wraplength=1000,
            justify=tk.LEFT
        )
        self.message_label.pack(pady=10, padx=10)
        
        self.game_frame = tk.Frame(self.main_frame, bg='#2d5016')
        self.game_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.hint_button = tk.Button(
            self.main_frame,
            text="💡 Get Hint (-5 points)",
            font=('Arial', 12, 'bold'),
            bg='#2196f3',
            fg='white',
            command=self.get_hint,
            state=tk.DISABLED
        )
        self.hint_button.pack(pady=5)
    
    def show_tutorial(self):
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        tutorial_frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=5)
        tutorial_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(
            tutorial_frame,
            text=f"📖 Tutorial - Step {self.tutorial_step + 1} of {len(self.tutorial_steps)}",
            font=('Arial', 18, 'bold'),
            bg='white'
        ).pack(pady=20, padx=30)
        
        tk.Label(
            tutorial_frame,
            text=self.tutorial_steps[self.tutorial_step],
            font=('Arial', 14),
            bg='white',
            wraplength=600,
            justify=tk.LEFT
        ).pack(pady=20, padx=30)
        
        button_frame = tk.Frame(tutorial_frame, bg='white')
        button_frame.pack(pady=20)
        
        if self.tutorial_step > 0:
            tk.Button(
                button_frame,
                text="Previous",
                font=('Arial', 12),
                bg='#757575',
                fg='white',
                padx=20,
                pady=10,
                command=self.prev_tutorial
            ).pack(side=tk.LEFT, padx=10)
        
        if self.tutorial_step < len(self.tutorial_steps) - 1:
            tk.Button(
                button_frame,
                text="Next",
                font=('Arial', 12),
                bg='#4caf50',
                fg='white',
                padx=20,
                pady=10,
                command=self.next_tutorial
            ).pack(side=tk.LEFT, padx=10)
        else:
            tk.Button(
                button_frame,
                text="Start Game!",
                font=('Arial', 14, 'bold'),
                bg='#2196f3',
                fg='white',
                padx=30,
                pady=10,
                command=self.start_game
            ).pack(side=tk.LEFT, padx=10)
    
    def next_tutorial(self):
        self.tutorial_step += 1
        self.show_tutorial()
    
    def prev_tutorial(self):
        self.tutorial_step -= 1
        self.show_tutorial()
    
    def start_game(self):
        self.game_state = 'bidding'
        self.deal_cards()
    
    def create_deck(self):
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append(Card(suit, rank))
        random.shuffle(deck)
        return deck
    
    def deal_cards(self):
        deck = self.create_deck()
        self.hands = [[], [], [], []]
        
        for i in range(52):
            player = i % 4
            self.hands[player].append(deck[i])
        
        for hand in self.hands:
            hand.sort(key=lambda c: (SUITS.index(c.suit), RANK_VALUES[c.rank]))
        
        self.bids = [None, None, None, None]
        self.deal_bids = [False, False, False, False]
        self.tricks = [0, 0, 0, 0]
        self.current_trick = []
        self.spades_played = False
        
        self.message_label.config(text="Time to bid! Look at your cards. Bid tricks you'll win, or bid DEAL!")
        self.show_bidding()
    
    def show_bidding(self):
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        hand_frame = tk.Frame(self.game_frame, bg='#2d5016')
        hand_frame.pack(side=tk.BOTTOM, pady=20)
        
        tk.Label(hand_frame, text="Your Hand:", font=('Arial', 14, 'bold'), 
                bg='#2d5016', fg='white').pack()
        
        cards_frame = tk.Frame(hand_frame, bg='#2d5016')
        cards_frame.pack()
        
        for card in self.hands[0]:
            self.create_card_label(cards_frame, card).pack(side=tk.LEFT, padx=2)
        
        bid_frame = tk.Frame(self.game_frame, bg='white', relief=tk.RAISED, bd=5)
        bid_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        tk.Label(bid_frame, text="Place Your Bid", font=('Arial', 18, 'bold'), 
                bg='white').pack(pady=10)
        tk.Label(bid_frame, text="How many tricks will you win?", 
                font=('Arial', 12), bg='white').pack(pady=5)
        
        tk.Button(
            bid_frame,
            text="🤝 Bid DEAL\n(+100 if you win 0 tricks, -100 if you win any)",
            font=('Arial', 12, 'bold'),
            bg='#f44336',
            fg='white',
            padx=20,
            pady=10,
            command=lambda: self.make_bid(0, True)
        ).pack(pady=10)
        
        numbers_frame = tk.Frame(bid_frame, bg='white')
        numbers_frame.pack(pady=10)
        
        for i in range(1, 14):
            row = (i - 1) // 7
            col = (i - 1) % 7
            
            btn = tk.Button(
                numbers_frame,
                text=str(i),
                font=('Arial', 14, 'bold'),
                bg='#2196f3',
                fg='white',
                width=4,
                height=2,
                command=lambda bid=i: self.make_bid(bid, False)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        self.hint_button.config(state=tk.NORMAL)
    
    def make_bid(self, bid, is_deal):
        self.bids[0] = 0 if is_deal else bid
        self.deal_bids[0] = is_deal
        
        if is_deal:
            self.message_label.config(text="You bid DEAL! Try not to win any tricks. AI players bidding...")
        else:
            self.message_label.config(text=f"You bid {bid} tricks. AI players bidding...")
        
        self.root.after(1000, self.ai_bids)
    
    def ai_bids(self):
        for i in range(1, 4):
            should_deal = random.random() < 0.15
            if should_deal:
                self.bids[i] = 0
                self.deal_bids[i] = True
            else:
                self.bids[i] = random.randint(1, 5)
                self.deal_bids[i] = False
        
        team1_bid = "Double DEAL!" if self.deal_bids[0] and self.deal_bids[2] else \
                    f"DEAL + {self.bids[2]}" if self.deal_bids[0] else \
                    f"{self.bids[0]} + DEAL" if self.deal_bids[2] else \
                    str(self.bids[0] + self.bids[2])
        
        self.message_label.config(text=f"Bidding complete! Your team: {team1_bid}. You lead!")
        self.game_state = 'playing'
        self.current_player = 0
        self.show_playing()
    
    def show_playing(self):
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        north_frame = tk.Frame(self.game_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        north_frame.pack(side=tk.TOP, pady=10)
        tk.Label(north_frame, text=f"North (Partner) - Bid: {self.get_bid_text(2)} | Won: {self.tricks[2]}", 
                font=('Arial', 11, 'bold'), bg='#1a3a0f', fg='white').pack(pady=5)
        north_cards = tk.Frame(north_frame, bg='#1a3a0f')
        north_cards.pack()
        for _ in self.hands[2]:
            tk.Label(north_cards, text="🂠", font=('Arial', 20), bg='#1a3a0f').pack(side=tk.LEFT, padx=1)
        
        middle_frame = tk.Frame(self.game_frame, bg='#2d5016')
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        west_frame = tk.Frame(middle_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        west_frame.pack(side=tk.LEFT, padx=10, anchor=tk.W)
        tk.Label(west_frame, text=f"West\nBid: {self.get_bid_text(3)}\nWon: {self.tricks[3]}", 
                font=('Arial', 10, 'bold'), bg='#1a3a0f', fg='white').pack(pady=5)
        for _ in self.hands[3]:
            tk.Label(west_frame, text="🂠", font=('Arial', 16), bg='#1a3a0f').pack(pady=1)
        
        center_frame = tk.Frame(middle_frame, bg='#1a5016', relief=tk.SUNKEN, bd=5, 
                               width=400, height=300)
        center_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=20)
        center_frame.pack_propagate(False)
        
        if self.current_trick:
            trick_display = tk.Frame(center_frame, bg='#1a5016')
            trick_display.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            for play in self.current_trick:
                player_names = ['You', 'East', 'North', 'West']
                card_frame = tk.Frame(trick_display, bg='#1a5016')
                card_frame.pack(side=tk.LEFT, padx=10)
                self.create_card_label(card_frame, play['card'], clickable=False).pack()
                tk.Label(card_frame, text=player_names[play['player']], 
                        font=('Arial', 10), bg='#1a5016', fg='white').pack()
        
        east_frame = tk.Frame(middle_frame, bg='#1a3a0f', relief=tk.RAISED, bd=2)
        east_frame.pack(side=tk.LEFT, padx=10, anchor=tk.E)
        tk.Label(east_frame, text=f"East\nBid: {self.get_bid_text(1)}\nWon: {self.tricks[1]}", 
                font=('Arial', 10, 'bold'), bg='#1a3a0f', fg='white').pack(pady=5)
        for _ in self.hands[1]:
            tk.Label(east_frame, text="🂠", font=('Arial', 16), bg='#1a3a0f').pack(pady=1)
        
        hand_frame = tk.Frame(self.game_frame, bg='#2d5016')
        hand_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Label(hand_frame, text=f"Your Hand - Bid: {self.get_bid_text(0)} | Tricks Won: {self.tricks[0]}", 
                font=('Arial', 12, 'bold'), bg='#2d5016', fg='white').pack()
        
        cards_frame = tk.Frame(hand_frame, bg='#2d5016')
        cards_frame.pack()
        
        for card in self.hands[0]:
            playable = self.is_card_playable(card)
            card_label = self.create_card_label(cards_frame, card, clickable=playable, highlight=playable)
            card_label.pack(side=tk.LEFT, padx=2)
            if playable and self.current_player == 0:
                card_label.bind('<Button-1>', lambda e, c=card: self.play_card(0, c))
        
        if self.current_player != 0:
            self.root.after(1000, lambda: self.ai_play())
        
        self.update_scores()
    
    def get_bid_text(self, player):
        if self.deal_bids[player]:
            return "DEAL"
        return str(self.bids[player])
    
    def create_card_label(self, parent, card, clickable=True, highlight=False):
        bg_color = 'white'
        if highlight:
            bg_color = '#ffff00'
        
        card_frame = tk.Frame(parent, bg=bg_color, relief=tk.RAISED, bd=3, 
                             width=60, height=85)
        card_frame.pack_propagate(False)
        
        color = 'red' if card.is_red() else 'black'
        
        tk.Label(card_frame, text=card.rank, font=('Arial', 14, 'bold'), 
                bg=bg_color, fg=color).pack(anchor=tk.NW, padx=2)
        tk.Label(card_frame, text=card.suit, font=('Arial', 18), 
                bg=bg_color, fg=color).pack(expand=True)
        
        if not clickable:
            card_frame.config(relief=tk.FLAT, bd=1)
        
        return card_frame
    
    def is_card_playable(self, card):
        if self.current_player != 0:
            return False
        
        hand = self.hands[0]
        
        if len(self.current_trick) == 0:
            if not self.spades_played and card.suit == '♠':
                return all(c.suit == '♠' for c in hand)
            return True
        
        have_lead_suit = any(c.suit == self.lead_suit for c in hand)
        if have_lead_suit:
            return card.suit == self.lead_suit
        
        return True
    
    def play_card(self, player, card):
        self.hands[player] = [c for c in self.hands[player] if c != card]
        
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
        player = self.current_player
        hand = self.hands[player]
        playable = hand.copy()
        
        if len(self.current_trick) > 0:
            has_suit = any(c.suit == self.lead_suit for c in hand)
            if has_suit:
                playable = [c for c in hand if c.suit == self.lead_suit]
        else:
            if not self.spades_played:
                non_spades = [c for c in hand if c.suit != '♠']
                if non_spades:
                    playable = non_spades
        
        card = random.choice(playable)
        self.play_card(player, card)
    
    def finish_trick(self):
        winner = self.current_trick[0]
        
        for play in self.current_trick:
            if play['card'].suit == '♠' and winner['card'].suit != '♠':
                winner = play
            elif (play['card'].suit == winner['card'].suit and 
                  RANK_VALUES[play['card'].rank] > RANK_VALUES[winner['card'].rank]):
                winner = play
        
        self.tricks[winner['player']] += 1
        
        player_names = ['You', 'East', 'North', 'West']
        message = f"{player_names[winner['player']]} won the trick!"
        
        if self.deal_bids[winner['player']]:
            message += f" ({player_names[winner['player']]} bid DEAL - bad!)"
        
        self.message_label.config(text=message)
        
        self.current_trick = []
        self.lead_suit = None
        self.current_player = winner['player']
        
        if len(self.hands[0]) == 0:
            self.calculate_round_score()
        else:
            self.show_playing()
    
    def calculate_round_score(self):
        team1_points = 0
        team2_points = 0
        
        if self.deal_bids[0]:
            team1_points += 100 if self.tricks[0] == 0 else -100
        else:
            if self.tricks[0] >= self.bids[0]:
                team1_points += self.bids[0] * 10 + (self.tricks[0] - self.bids[0])
            else:
                team1_points -= self.bids[0] * 10
        
        if self.deal_bids[2]:
            team1_points += 100 if self.tricks[2] == 0 else -100
        else:
            if self.tricks[2] >= self.bids[2]:
                team1_points += self.bids[2] * 10 + (self.tricks[2] - self.bids[2])
            else:
                team1_points -= self.bids[2] * 10
        
        if self.deal_bids[1]:
            team2_points += 100 if self.tricks[1] == 0 else -100
        else:
            if self.tricks[1] >= self.bids[1]:
                team2_points += self.bids[1] * 10 + (self.tricks[1] - self.bids[1])
            else:
                team2_points -= self.bids[1] * 10
        
        if self.deal_bids[3]:
            team2_points += 100 if self.tricks[3] == 0 else -100
        else:
            if self.tricks[3] >= self.bids[3]:
                team2_points += self.bids[3] * 10 + (self.tricks[3] - self.bids[3])
            else:
                team2_points -= self.bids[3] * 10
        
        self.scores[0][0] += team1_points
        self.scores[1][0] += team2_points
        
        team1_bags = 0
        team2_bags = 0
        
        if not self.deal_bids[0] and self.tricks[0] > self.bids[0]:
            team1_bags += self.tricks[0] - self.bids[0]
        if not self.deal_bids[2] and self.tricks[2] > self.bids[2]:
            team1_bags += self.tricks[2] - self.bids[2]
        if not self.deal_bids[1] and self.tricks[1] > self.bids[1]:
            team2_bags += self.tricks[1] - self.bids[1]
        if not self.deal_bids[3] and self.tricks[3] > self.bids[3]:
            team2_bags += self.tricks[3] - self.bids[3]
        
        self.scores[0][1] += team1_bags
        self.scores[1][1] += team2_bags
        
        if self.scores[0][1] >= 10:
            self.scores[0][0] -= 100
            self.scores[0][1] -= 10
            messagebox.showinfo("Sandbagged!", "Team 1 sandbagged! -100 points for 10 bags!")
        if self.scores[1][1] >= 10:
            self.scores[1][0] -= 100
            self.scores[1][1] -= 10
        
        self.update_scores()
        
        if self.scores[0][0] >= WINNING_SCORE or self.scores[1][0] >= WINNING_SCORE:
            winner = "Team 1 (You & North)" if self.scores[0][0] > self.scores[1][0] else "Team 2 (East & West)"
            messagebox.showinfo("🏆 Game Over!", 
                              f"{winner} WINS!\n\nFinal Score:\nTeam 1: {self.scores[0][0]}\nTeam 2: {self.scores[1][0]}")
            self.scores = [[0, 0], [0, 0]]
            self.hints_used = 0
            self.deal_cards()
        else:
            result = f"Round over! "
            if self.deal_bids[0]:
                result += f"You bid DEAL and {'SUCCESS (+100)' if self.tricks[0] == 0 else 'FAILED (-100)'}!"
            self.message_label.config(text=result)
            messagebox.showinfo("Round Complete", 
                              f"Round complete!\n\nYour team: {self.tricks[0] + self.tricks[2]} tricks\nOpponents: {self.tricks[1] + self.tricks[3]} tricks\n\nNext round starting...")
            self.deal_cards()
    
    def update_scores(self):
        self.team1_score_label.config(text=f"{self.scores[0][0]} / {WINNING_SCORE}")
        self.team1_bags_label.config(text=f"Bags: {self.scores[0][1]}")
        self.team2_score_label.config(text=f"{self.scores[1][0]} / {WINNING_SCORE}")
        self.team2_bags_label.config(text=f"Bags: {self.scores[1][1]}")
    
    def get_hint(self):
        if self.game_state == 'bidding':
            hand = self.hands[0]
            spades = [c for c in hand if c.suit == '♠']
            high_cards = [c for c in hand if RANK_VALUES[c.rank] >= 11]
            low_cards = [c for c in hand if RANK_VALUES[c.rank] <= 5]
            suggested = len(spades) // 3 + len(high_cards) // 2
            
            hint = f"Bidding Tip: You have {len(spades)} spades, {len(high_cards)} high cards, {len(low_cards)} low cards. "
            
            if len(low_cards) >= 10 and len(high_cards) <= 2:
                hint += "Hand is weak - consider DEAL for +100 points!"
            else:
                hint += f"Consider bidding around {max(1, suggested)} tricks."
            
            messagebox.showinfo("Hint (-5 points)", hint)
        
        elif self.game_state == 'playing':
            hand = self.hands[0]
            
            if self.deal_bids[0]:
                hint = "You bid DEAL! Play your LOWEST cards to avoid winning tricks."
            elif len(self.current_trick) == 0:
                hint = "You're leading! Lead with high cards in suits you're strong in. Save spades!"
            else:
                have_suit = any(c.suit == self.lead_suit for c in hand)