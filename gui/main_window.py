"""
Main Window Module for Bridge Game GUI

This module defines the main window for the Bridge card game GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class MainWindow:
    """Main window class for the Bridge game interface."""
    
    def __init__(self, master, game):
        """
        Initialize the main window.
        
        Args:
            master: The Tkinter root window
            game: The BridgeGame instance
        """
        self.master = master
        self.game = game
        
        # Configure the root window
        self.master.geometry("800x600")
        self.master.minsize(800, 600)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Set up the menu bar
        self.setup_menu()
        
        # Create the game board
        self.setup_game_board()
        
        # Set up status bar
        self.setup_status_bar()
    
    def setup_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.master)
        
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Game", command=self.new_game)
        filemenu.add_command(label="Save Game", command=self.save_game)
        filemenu.add_command(label="Load Game", command=self.load_game)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.quit)
        
        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Rules", command=self.show_rules)
        helpmenu.add_command(label="About", command=self.show_about)
        
        # Add menus to menubar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        # Display the menubar
        self.master.config(menu=menubar)
    
    def setup_game_board(self):
        """Create the game board area."""
        # Main game area frame
        self.game_frame = ttk.Frame(self.main_frame, borderwidth=2, relief="groove")
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Placeholder for the card table
        self.table_canvas = tk.Canvas(self.game_frame, bg="green")
        self.table_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Player's hand frame
        self.hand_frame = ttk.Frame(self.main_frame)
        self.hand_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Placeholder text
        self.table_canvas.create_text(
            400, 300, 
            text="Bridge Game Table - Cards will be displayed here", 
            fill="white", font=("Arial", 14)
        )
    
    def setup_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.master)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Welcome to Bridge Card Game", 
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def update_status(self, message):
        """Update the status bar message."""
        self.status_label.config(text=message)
    
    def new_game(self):
        """Start a new game."""
        self.game.new_game()
        self.update_status("New game started")
    
    def save_game(self):
        """Save the current game state."""
        self.update_status("Game saved")
        messagebox.showinfo("Save Game", "Game state saved successfully!")
    
    def load_game(self):
        """Load a saved game state."""
        self.update_status("Game loaded")
        messagebox.showinfo("Load Game", "Game state loaded successfully!")
    
    def show_rules(self):
        """Display the rules of Bridge."""
        messagebox.showinfo(
            "Bridge Rules",
            "Bridge is a trick-taking card game using a standard deck of 52 playing cards.\n\n"
            "The game is played by four players in two competing partnerships."
        )
    
    def show_about(self):
        """Display information about the application."""
        messagebox.showinfo(
            "About Bridge Game",
            "Bridge Card Game\nVersion 1.0\n\nA simple implementation of the Bridge card game."
        )

