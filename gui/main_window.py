import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class CardView(tk.Label):
    SUITS = {'♠': 'black', '♥': 'red', '♦': 'red', '♣': 'black'}
    
    def __init__(self, parent, suit, rank):
        super().__init__(
            parent,
            text=f"{rank}{suit}",
            font=('Arial', 14),
            fg=self.SUITS[suit],
            bg='white',
            width=4,
            relief=tk.RAISED,
            padx=5,
            pady=5
        )

class BridgeGameWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure the main window
        self.title("Bridge Game")
        self.configure(bg='darkgreen')
        
        # Get screen dimensions and set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1200
        window_height = 800
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        self._create_menu()
        self._create_layout()
        self._create_status_bar()
        
        # Add some sample cards for visualization
        self._add_sample_cards()

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
        self.north_frame = tk.Frame(self.main_frame, bg='#004400', height=150, width=500)
        self.south_frame = tk.Frame(self.main_frame, bg='#004400', height=150, width=500)
        self.east_frame = tk.Frame(self.main_frame, bg='#004400', height=400, width=150)
        self.west_frame = tk.Frame(self.main_frame, bg='#004400', height=400, width=150)
        
        # Create central playing area
        self.center_frame = tk.Frame(self.main_frame, bg='darkgreen', height=300, width=300)
        
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
        style = {'bg': '#004400', 'fg': 'white', 'font': ('Arial', 12, 'bold')}
        tk.Label(self.north_frame, text="North", **style).pack(pady=5)
        tk.Label(self.south_frame, text="South", **style).pack(pady=5)
        tk.Label(self.east_frame, text="East", **style).pack(pady=5)
        tk.Label(self.west_frame, text="West", **style).pack(pady=5)
        
        # Add trick counter and contract display in center
        self.trick_label = tk.Label(self.center_frame, 
                                  text="Tricks: NS: 0 | EW: 0",
                                  bg='darkgreen', fg='white',
                                  font=('Arial', 12))
        self.trick_label.pack(pady=10)
        
        self.contract_label = tk.Label(self.center_frame,
                                     text="Contract: Not set",
                                     bg='darkgreen', fg='white',
                                     font=('Arial', 12))
        self.contract_label.pack(pady=10)

    def _create_status_bar(self):
        self.status_bar = ttk.Label(
            self,
            text="Welcome to Bridge Game! Click 'Game > New Game' to start.",
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _add_sample_cards(self):
        # Add some sample cards to South position
        south_cards_frame = tk.Frame(self.south_frame, bg='#004400')
        south_cards_frame.pack(pady=30)
        
        sample_cards = [
            ('♠', 'A'), ('♥', 'K'), ('♦', 'Q'), ('♣', 'J'),
            ('♠', '10'), ('♥', '9'), ('♦', '8'), ('♣', '7')
        ]
        
        for suit, rank in sample_cards:
            card = CardView(south_cards_frame, suit, rank)
            card.pack(side=tk.LEFT, padx=2)

    def _new_game(self):
        messagebox.showinfo("New Game", "Starting new game...")
        self.status_bar.config(text="New game started")

    def _save_game(self):
        messagebox.showinfo("Save Game", "Game saving not implemented yet")
        self.status_bar.config(text="Game saved")

    def _load_game(self):
        messagebox.showinfo("Load Game", "Game loading not implemented yet")
        self.status_bar.config(text="Game loaded")
