import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class CardView(tk.Label):
    SUITS = {'♠': 'black', '♥': 'red', '♦': 'red', '♣': 'black'}
    
    def __init__(self, parent, suit, rank, face_up=True):
        # Calculate width based on rank
        width = 4 if rank == '10' else 3
        
        if face_up:
            super().__init__(
                parent,
                text=f"{rank}{suit}",
                font=('Arial', 14),  # Increased font size
                fg=self.SUITS[suit],
                bg='white',
                width=width,
                relief=tk.RAISED,
                padx=2,
                pady=2,
                borderwidth=2
            )
        else:
            super().__init__(
                parent,
                text="🂠",  # Card back symbol
                font=('Arial', 14),
                fg='navy',
                bg='lightblue',
                width=3,
                relief=tk.RAISED,
                padx=2,
                pady=2,
                borderwidth=2
            )

class BridgeGameWindow(tk.Tk):
    CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    CARD_SUITS = ['♠', '♥', '♦', '♣']

    def __init__(self):
        super().__init__()

        # Configure the main window
        self.title("Bridge Game")
        self.configure(bg='darkgreen')
        
        # Get screen dimensions and set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1400  # Increased width
        window_height = 900  # Increased height
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        self._create_menu()
        self._create_layout()
        self._create_status_bar()
        
        # Add sample hands
        self._add_sample_hands()

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self._new_game)
        game_menu.add_command(label="Save Game", command=self._save_game)
        game_menu.add_command(label="Load Game", command=self._load_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.quit)

    def _create_layout(self):
        # Create main frame
        self.main_frame = tk.Frame(self, bg='darkgreen')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Create frames for each player with better styling
        self.north_frame = tk.Frame(self.main_frame, bg='#004400', height=180, width=700)  # Increased sizes
        self.south_frame = tk.Frame(self.main_frame, bg='#004400', height=180, width=700)
        self.east_frame = tk.Frame(self.main_frame, bg='#004400', height=500, width=180)
        self.west_frame = tk.Frame(self.main_frame, bg='#004400', height=500, width=180)
        
        # Create central playing area
        self.center_frame = tk.Frame(self.main_frame, bg='darkgreen', height=400, width=400)
        
        # Place frames using place geometry manager
        self.north_frame.place(relx=0.5, rely=0, anchor='n')
        self.south_frame.place(relx=0.5, rely=1, anchor='s')
        self.east_frame.place(relx=1, rely=0.5, anchor='e')
        self.west_frame.place(relx=0, rely=0.5, anchor='w')
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Prevent frames from shrinking
        for frame in [self.north_frame, self.south_frame, self.east_frame, 
                     self.west_frame, self.center_frame]:
            frame.pack_propagate(False)

        # Add labels for player positions with better styling
        style = {'bg': '#004400', 'fg': 'white', 'font': ('Arial', 14, 'bold')}  # Increased font size
        tk.Label(self.north_frame, text="North", **style).pack(pady=5)
        tk.Label(self.south_frame, text="South (You)", **style).pack(pady=5)
        tk.Label(self.east_frame, text="East", **style).pack(pady=5)
        tk.Label(self.west_frame, text="West", **style).pack(pady=5)
        
        # Add trick counter and contract display in center
        self.trick_label = tk.Label(self.center_frame, 
                                  text="Tricks: NS: 0 | EW: 0",
                                  bg='darkgreen', fg='white',
                                  font=('Arial', 14))  # Increased font size
        self.trick_label.pack(pady=10)
        
        self.contract_label = tk.Label(self.center_frame,
                                     text="Contract: Not set",
                                     bg='darkgreen', fg='white',
                                     font=('Arial', 14))  # Increased font size
        self.contract_label.pack(pady=10)

    def _create_status_bar(self):
        self.status_bar = ttk.Label(
            self,
            text="Welcome to Bridge Game! Click 'Game > New Game' to start.",
            relief=tk.SUNKEN,
            font=('Arial', 12)  # Added font size
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _add_sample_hands(self):
        # Sample complete hand for South (visible cards)
        south_cards_frame = tk.Frame(self.south_frame, bg='#004400')
        south_cards_frame.pack(pady=30)
        
        sample_south_hand = [
            ('♠', 'A'), ('♠', 'K'), ('♠', '10'), ('♠', '2'),
            ('♥', 'Q'), ('♥', 'J'), ('♥', '9'),
            ('♦', 'K'), ('♦', '8'), ('♦', '7'),
            ('♣', 'A'), ('♣', '10'), ('♣', '5')
        ]
        
        # Sort the hand by suit and rank
        def card_sort_key(card):
            suit, rank = card
            suit_index = self.CARD_SUITS.index(suit)
            rank_index = self.CARD_RANKS.index(rank)
            return (suit_index, -rank_index)  # Negative rank_index to sort high to low
        
        sample_south_hand.sort(key=card_sort_key)
        
        # Group cards by suit for better spacing
        current_suit = None
        for suit, rank in sample_south_hand:
            if current_suit is not None and suit != current_suit:
                # Add a bit more space between suits
                spacer = tk.Label(south_cards_frame, text=" ", bg='#004400', width=1)
                spacer.pack(side=tk.LEFT)
            current_suit = suit
            
            card = CardView(south_cards_frame, suit, rank, face_up=True)
            card.pack(side=tk.LEFT, padx=1)

        # Add face-down cards for other players
        for frame, position in [(self.north_frame, 'top'), 
                              (self.east_frame, 'right'), 
                              (self.west_frame, 'left')]:
            cards_frame = tk.Frame(frame, bg='#004400')
            cards_frame.pack(pady=30)
            
            # Create 13 face-down cards for each other player
            for i in range(13):
                card = CardView(cards_frame, '♠', 'A', face_up=False)
                if position in ['left', 'right']:
                    card.pack(pady=1)  # Stack vertically for East/West
                else:
                    card.pack(side=tk.LEFT, padx=1)  # Stack horizontally for North
                    # Add slight spacing every 4 cards for North
                    if i in [3, 7, 11]:
                        spacer = tk.Label(cards_frame, text=" ", bg='#004400', width=1)
                        spacer.pack(side=tk.LEFT)

    def _new_game(self):
        messagebox.showinfo("New Game", "Starting new game...")
        self.status_bar.config(text="New game started")

    def _save_game(self):
        messagebox.showinfo("Save Game", "Game saving not implemented yet")
        self.status_bar.config(text="Game saved")

    def _load_game(self):
        messagebox.showinfo("Load Game", "Game loading not implemented yet")
        self.status_bar.config(text="Game loaded")
