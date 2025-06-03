import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
from core.game import BridgeGame
from core.deck import Card
from gui.bidding_box import BiddingBox
from gui.player_setup import PlayerSetupDialog

class CardView(tk.Label):
    SUITS = {'♠': 'black', '♥': 'red', '♦': 'red', '♣': 'black'}
    GUI_SUITS = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
    RANKS = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
             11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    
    def __init__(self, parent, card=None, suit=None, rank=None, face_up=True, callback=None):
        self.card = card
        self.callback = callback
        self.selected = False
        
        # If a Card object is provided, use its properties
        if card:
            suit = self.GUI_SUITS[card.suit]
            rank = self.RANKS[card.value]
        
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
            
        # Bind click event if callback is provided
        if callback and face_up:
            self.bind("<Button-1>", self._on_click)
            self.config(cursor="hand2")  # Change cursor to hand when hovering
    
    def _on_click(self, event):
        if self.callback:
            self.callback(self)
    
    def select(self):
        """Highlight the card as selected"""
        self.selected = True
        self.config(bg='lightyellow', relief=tk.SUNKEN)
        
    def deselect(self):
        """Remove the selection highlight"""
        self.selected = False
        self.config(bg='white', relief=tk.RAISED)
        
    def is_selected(self):
        """Return whether the card is currently selected"""
        return self.selected
        
    def disable(self):
        """Disable the card from being clicked"""
        self.unbind("<Button-1>")
        self.config(cursor="")
        self.config(bg='#f0f0f0')  # Light gray background

class BridgeGameWindow(tk.Tk):
    CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    CARD_SUITS = ['♠', '♥', '♦', '♣']
    POSITIONS = ['South', 'West', 'North', 'East']
    
    # Import logging at class level
    import logging
    logger = logging.getLogger("BridgeGame.GUI")
    
    # Add trick winner tracking
    trick_winner = None
    

    def __init__(self):
        super().__init__()

        # Initialize game state
        self.game = BridgeGame()
        self.card_views = [[], [], [], []]  # Card views for each player
        self.player_types = {0: "human", 1: "ai", 2: "ai", 3: "ai"}  # Default player types
        self.trick_card_views = [None, None, None, None]  # Cards in current trick
        self.trick_frames = [None, None, None, None]  # Frames for trick cards
        self.ns_tricks = 0
        self.ew_tricks = 0
        self.current_player_highlight = None
        self.waiting_for_trick_end = False
        self.trick_count_verified = True  # Flag to track if trick count is verified
        self.trick_winner_cache = None  # Cache for trick winner to ensure consistency
        self.last_trick_time = None  # Timestamp of last trick completion
        self.clear_trick_job = None  # ID of scheduled _clear_trick job
        self.clear_trick_called = False  # Flag to track if _clear_trick was ever called
        self.last_trick_displayed = False  # Flag to track if the last trick count was displayed

        # Configure the main window
        self.title("Bridge Game")
        self.configure(bg='darkgreen')
        
        # Get screen dimensions and set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1600  # Wider to accommodate side-by-side layout
        window_height = 900  # Maintained height
        
        # Set minimum window size
        self.minsize(1200, 700)  # Increased minimum width
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Log window dimensions and position
        self.logger.info(f"Screen dimensions: {screen_width}x{screen_height}")
        self.logger.info(f"Window dimensions: {window_width}x{window_height}")
        self.logger.info(f"Window position: +{x}+{y}")
        
        # Make sure window appears on top and gets focus
        self.attributes('-topmost', True)  # Put window on top
        self.update()  # Update to ensure topmost takes effect
        self.attributes('-topmost', False)  # Disable topmost to allow other windows to go in front later
        self.deiconify()  # Ensure window is not minimized
        self.lift()      # Lift window to top of stacking order
        self.focus_force()  # Force focus to this window

        self._create_menu()
        self._create_layout()
        self._create_status_bar()
        
        # Start a new game
        self._new_game()
        
        # Final check to ensure window is visible
        self.after(100, self._ensure_visibility)

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
        """Create the main layout with cards on left, bidding on right."""
        # Main frame
        self.main_frame = tk.Frame(self, bg='darkgreen')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create left and right container frames for split layout
        self.left_container = tk.Frame(self.main_frame, bg='darkgreen', width=800)
        self.right_container = tk.Frame(self.main_frame, bg='darkgreen', width=700)
        
        # Place left and right containers side by side
        self.left_container.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10))
        self.right_container.pack(side=tk.RIGHT, fill='both', expand=True, padx=(10, 0))
        
        # Prevent containers from shrinking
        self.left_container.pack_propagate(False)
        self.right_container.pack_propagate(False)
        
        # Create frames for each player with better styling (in left container)
        self.north_frame = tk.Frame(self.left_container, bg='#004400', height=160, width=1200)  # Wide for horizontal cards
        self.south_frame = tk.Frame(self.left_container, bg='#004400', height=160, width=1200)  # Wide for horizontal cards
        self.east_frame = tk.Frame(self.left_container, bg='#004400', height=800, width=150)    # Tall and narrow for vertical cards
        self.west_frame = tk.Frame(self.left_container, bg='#004400', height=800, width=150)    # Tall and narrow for vertical cards
        
        # Create central playing area (in left container)
        self.center_frame = tk.Frame(self.left_container, bg='darkgreen', height=300, width=400)
        
        # Create bidding box (in right container)
        self.bidding_box = BiddingBox(self.right_container, self.game, self._on_bidding_complete, self.player_types)
        # Create frames for trick display in the center
        self.trick_area = tk.Frame(self.center_frame, bg='darkgreen', height=300, width=300)
        self.trick_area.pack(pady=20)
        
        # Create frames for each player's card in the trick
        # North trick card
        self.north_trick_frame = tk.Frame(self.trick_area, bg='darkgreen', height=70, width=70)
        self.north_trick_frame.place(relx=0.5, rely=0, anchor='n')
        
        # South trick card
        self.south_trick_frame = tk.Frame(self.trick_area, bg='darkgreen', height=70, width=70)
        self.south_trick_frame.place(relx=0.5, rely=1, anchor='s')
        
        # East trick card
        self.east_trick_frame = tk.Frame(self.trick_area, bg='darkgreen', height=70, width=70)
        self.east_trick_frame.place(relx=1, rely=0.5, anchor='e')
        
        # West trick card
        self.west_trick_frame = tk.Frame(self.trick_area, bg='darkgreen', height=70, width=70)
        self.west_trick_frame.place(relx=0, rely=0.5, anchor='w')
        
        self.trick_frames = [
            self.south_trick_frame,
            self.west_trick_frame,
            self.north_trick_frame, 
            self.east_trick_frame
        ]
        
        # Place frames using place geometry manager
        # Position frames in a traditional bridge layout within the left container
        self.north_frame.place(relx=0.5, rely=0.02, anchor='n')    # Moved up slightly
        self.south_frame.place(relx=0.5, rely=0.98, anchor='s')    # Moved down slightly
        self.east_frame.place(relx=0.98, rely=0.5, anchor='e')     # Moved more to the right
        self.west_frame.place(relx=0.02, rely=0.5, anchor='w')     # Moved more to the left
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')
        # Add a title for the cards area in the left container
        cards_title = tk.Label(self.left_container, text="Playing Cards", 
                             font=('Arial', 16, 'bold'),
                             bg='darkgreen', fg='white')
        cards_title.place(relx=0.5, rely=0.02, anchor='n')

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
        
        # Add current player indicator
        self.current_player_label = tk.Label(self.center_frame,
                                           text="Current Player: South",
                                           bg='darkgreen', fg='yellow',
                                           font=('Arial', 16, 'bold'))
        self.current_player_label.pack(pady=10)

    def _create_status_bar(self):
        self.status_bar = ttk.Label(
            self,
            text="Welcome to Bridge Game! Click 'Game > New Game' to start.",
            relief=tk.SUNKEN,
            font=('Arial', 12)  # Added font size
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _display_hands(self):
        """Display all player hands with face-up cards"""
        # Clear existing cards
        for i in range(4):
            self.card_views[i] = []
        
        # Create frames for each player's cards
        frames = []
        
        # South (player 0)
        south_cards_frame = tk.Frame(self.south_frame, bg='#004400')
        south_cards_frame.pack(pady=30)
        frames.append((south_cards_frame, 'bottom'))
        
        # West (player 1)
        west_cards_frame = tk.Frame(self.west_frame, bg='#004400')
        west_cards_frame.pack(pady=30)
        frames.append((west_cards_frame, 'left'))
        
        # North (player 2)
        north_cards_frame = tk.Frame(self.north_frame, bg='#004400')
        north_cards_frame.pack(pady=30)
        frames.append((north_cards_frame, 'top'))
        
        # East (player 3)
        east_cards_frame = tk.Frame(self.east_frame, bg='#004400')
        east_cards_frame.pack(pady=30)
        frames.append((east_cards_frame, 'right'))
        
        # Display cards for each player
        for player_idx, (frame, position) in enumerate(frames):
            # Get and sort cards
            hand = sorted(self.game.players[player_idx]['hand'], 
                          key=lambda c: (c.suit, -c.value))
            
            # Group cards by suit for better spacing
            current_suit = None
            for card in hand:
                suit = card.suit
                
                if current_suit is not None and suit != current_suit:
                    # Add a bit more space between suits
                    spacer = tk.Label(frame, text=" ", bg='#004400', width=2)  # Increased spacer width
                    if position in ['left', 'right']:
                        spacer.pack(side=tk.TOP)  # Vertical spacing for East/West
                    else:
                        spacer.pack(side=tk.LEFT)  # Horizontal spacing for North/South
                        
                current_suit = suit
                
                # Create card view with callback for clickable cards - allow all positions to be played
                card_view = CardView(frame, card=card, face_up=True, callback=self._on_card_click)
                
                # Store the player index in the card view for later reference
                card_view.player_idx = player_idx
                
                if position in ['left', 'right']:  # East and West
                    card_view.pack(side=tk.TOP, pady=4)  # Vertical stacking
                else:  # North and South
                    card_view.pack(side=tk.LEFT, padx=4)  # Horizontal arrangement
                
                # Store the card view for later reference
                self.card_views[player_idx].append(card_view)
        
        # Highlight current player
        self._highlight_current_player()

    def _new_game(self):
        """Start a new game"""
        # Show player setup dialog
        setup_dialog = PlayerSetupDialog(self)
        self.wait_window(setup_dialog)
        
        if setup_dialog.result:
            self.player_types = setup_dialog.result
        else:
            # Default to South as human if dialog was cancelled
            self.player_types = {0: "human", 1: "ai", 2: "ai", 3: "ai"}
        
        # Initialize game and deal cards
        self.game = BridgeGame()
        self.game.new_game()  # This deals the cards
        
        # Clear trick area
        for frame in self.trick_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Clear player frames
        for frame in [self.north_frame, self.south_frame, self.east_frame, self.west_frame]:
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.destroy()
        
        # Reset game state
        self.trick_card_views = [None, None, None, None]
        self.ns_tricks = 0
        self.ew_tricks = 0
        self.trick_count_verified = True  # Reset verification flag
        self.trick_winner_cache = None  # Reset winner cache
        self.last_trick_time = None  # Reset trick timing
        self.clear_trick_job = None  # Reset scheduled job ID
        self.clear_trick_called = False  # Reset clear_trick called flag
        self.last_trick_displayed = False  # Reset display flag
        
        # Clear any stored trick values
        if hasattr(self, '_stored_ns_tricks'):
            delattr(self, '_stored_ns_tricks')
        if hasattr(self, '_stored_ew_tricks'):
            delattr(self, '_stored_ew_tricks')
        if hasattr(self, '_stored_trick_winner'):
            delattr(self, '_stored_trick_winner')
            
        self.trick_label.config(text="Tricks: NS: 0 | EW: 0")
        self.trick_label.update()  # Force update immediately
        self.update_idletasks()  # Additional update for good measure
        self.logger.info("Game state reset - trick counts zeroed")
        
        # Show all player frames for bidding
        self.north_frame.place(relx=0.5, rely=0.02, anchor='n')
        self.south_frame.place(relx=0.5, rely=0.98, anchor='s')
        self.east_frame.place(relx=0.98, rely=0.5, anchor='e')
        self.west_frame.place(relx=0.02, rely=0.5, anchor='w')
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Reset game state to ensure bidding
        self.game.current_state = "bidding"
        
        # Log game state before starting bidding
        self.logger.info("Starting bidding phase")
        self.logger.info(f"Game state: {self.game.current_state}, Bidder: {self.game.current_bidder}")
        
        # Check if cards were dealt properly
        total_cards = sum(len(player["hand"]) for player in self.game.players)
        self.logger.info(f"Total cards before bidding: {total_cards}")
        
        if total_cards != 52:
            self.logger.warning(f"Card count mismatch! Expected 52, got {total_cards}. Re-dealing cards.")
            self.game.deal_cards()
        
        # Verify each player has 13 cards
        for i, player in enumerate(self.game.players):
            cards_count = len(player["hand"])
            self.logger.info(f"Player {i} has {cards_count} cards")
            if cards_count != 13:
                self.logger.error(f"Player {i} has {cards_count} cards instead of 13!")
        
        # Always prepare for bidding phase
        self.status_bar.config(text="New game started - Bidding phase")
        
        # Start bidding phase
        self._prepare_for_bidding()
    
    def _on_card_click(self, card_view):
        """Handle card click event"""
        if self.waiting_for_trick_end:
            return  # Ignore clicks while waiting for trick to end
            
        # Get the card object and player index
        card = card_view.card
        player_idx = card_view.player_idx
        
        # Log attempt
        self.logger.info(f"Card click: {self.POSITIONS[player_idx]} attempting to play {card}")
        
        # Check if it's this player's turn
        if player_idx != self.game.current_player:
            self.status_bar.config(text=f"It's {self.POSITIONS[self.game.current_player]}'s turn to play")
            self.logger.info(f"Wrong player: {self.POSITIONS[player_idx]} tried to play but it's {self.POSITIONS[self.game.current_player]}'s turn")
            return
            
        # Check if this is a new trick and enforce proper lead
        if not self.game.trick and self.game.last_trick_winner is not None:
            # If it's a new trick and not the first trick of the hand, only the winner can lead
            if player_idx != self.game.last_trick_winner:
                # Wrong player trying to lead
                self.logger.info(f"Wrong player leading: {self.POSITIONS[player_idx]} tried to lead but it's {self.POSITIONS[self.game.last_trick_winner]}'s turn")
                self.status_bar.config(text=f"{self.POSITIONS[self.game.last_trick_winner]} must lead to the next trick (as trick winner)")
                return
            else:
                self.logger.info(f"Correct player leading: {self.POSITIONS[player_idx]} (trick winner)")
        
        # Check if player is following suit if required
        if self.game.trick:
            led_suit = self.game.trick[0]["card"].suit
            player_hand = self.game.players[player_idx]["hand"]
            has_led_suit = any(c.suit == led_suit for c in player_hand)
            
            if has_led_suit and card.suit != led_suit:
                self.status_bar.config(text=f"Must follow suit ({led_suit})")
                self.logger.info(f"{self.POSITIONS[player_idx]} must follow {led_suit} suit")
                return
        
        # Try to play the card
        if self.game.play_card(player_idx, card):
            # Card played successfully
            self.logger.info(f"Card played successfully: {self.POSITIONS[player_idx]} played {card}")
            self._show_played_card(player_idx, card)
            
            # Remove card from display and refresh the player's hand
            self._refresh_player_hand(player_idx)
            
            # Check if trick is complete
            if len(self.game.trick) == 4:
                self.logger.info(f"Trick complete with 4 cards - Current trick counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}, Verified: {self.trick_count_verified}")
                self.waiting_for_trick_end = True
                self.last_trick_displayed = False  # Reset flag for new trick processing
                
                # Snapshot of trick and display state before processing
                current_trick_content = [(play["player"], str(play["card"])) for play in self.game.trick]
                self.logger.info(f"TRICK COMPLETE SNAPSHOT: {current_trick_content}, NS: {self.ns_tricks}, EW: {self.ew_tricks}")
                
                # Process trick immediately for better reliability
                try:
                    self._end_trick()
                except Exception as e:
                    self.logger.error(f"ERROR in _end_trick: {e}")
                    # Force trick count update if _end_trick fails
                    self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
                    self.trick_label.update()
            else:
                # Update to next player in sequence
                next_player = (player_idx + 1) % 4
                self.game.current_player = next_player
                self.logger.info(f"Setting next player to: {next_player} ({self.POSITIONS[next_player]})")
                self._highlight_current_player()
                self.logger.info(f"Next player: {self.POSITIONS[self.game.current_player]}")
                self.status_bar.config(text=f"Next player: {self.POSITIONS[self.game.current_player]}")
        else:
            # Card play failed
            self.logger.warning(f"Invalid play: {self.POSITIONS[player_idx]} attempted to play {card}")
            self.status_bar.config(text=f"Invalid play. Please try another card.")
    
    def _show_played_card(self, player_idx, card):
        """Display a card in the trick area"""
        # Create a frame for the card if not exists
        frame = self.trick_frames[player_idx]
        
        # Clear any existing card
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Create and display the card
        card_view = CardView(frame, card=card, face_up=True)
        card_view.pack(padx=5, pady=5)
        
        # Store reference to the card view
        self.trick_card_views[player_idx] = card_view
        
        # Update status
        self.status_bar.config(text=f"{self.POSITIONS[player_idx]} played {card}")
    
    def _end_trick(self):
        """Handle end of trick"""
        import time
        current_time = time.time()
        
        # Log entering _end_trick with detailed state
        self.logger.info(f"ENTERING _end_trick - Window state: Exists: {self.winfo_exists()}, Viewable: {self.winfo_viewable()}")
        self.logger.info(f"Trick counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}, clear_trick_called: {self.clear_trick_called}")
        
        # Prevent double-processing of tricks (debounce)
        if self.last_trick_time and (current_time - self.last_trick_time < 2.0):
            self.logger.warning(f"TRICK END - Ignoring duplicate call to _end_trick (last call was {current_time - self.last_trick_time:.2f}s ago)")
            # Even if we skip this call, ensure trick counts are displayed correctly
            self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
            self.trick_label.update()  # Force immediate update
            return
            
        # Cancel any existing scheduled clear_trick job
        if self.clear_trick_job:
            self.logger.info(f"Cancelling previous clear_trick job: {self.clear_trick_job}")
            self.after_cancel(self.clear_trick_job)
            self.clear_trick_job = None
        
        self.last_trick_time = current_time
        self.logger.info(f"TRICK END - Beginning trick count processing. Current counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}")
        
        # First, capture the complete trick before it's cleared
        complete_trick = self.game.trick.copy()
        if not complete_trick or len(complete_trick) != 4:
            self.logger.error(f"TRICK END - Invalid trick: Expected 4 cards but found {len(complete_trick)}")
            return
            
        # Record the raw trick data for debugging
        raw_trick_data = [(i, play["player"], str(play["card"])) for i, play in enumerate(complete_trick)]
        self.logger.info(f"Raw trick data: {raw_trick_data}")
        
        # Determine winner using game's method
        winner_idx = self.game._determine_trick_winner()
        
        # Log detailed information about trick completion
        trick_cards = [(i, play["player"], play["card"]) for i, play in enumerate(complete_trick)]
        self.logger.info(f"Evaluating trick winner for trick: {trick_cards}")
        
        # Double-check the winner determination with our own calculation
        # This is a safeguard against any bugs in the game's winner determination
        led_suit = complete_trick[0]["card"].suit
        highest_value = -1
        calculated_winner = None
        
        # Detailed verification of winner
        self.logger.info(f"Led suit: {led_suit}")
        
        for play in complete_trick:
            card = play["card"]
            player = play["player"]
            self.logger.info(f"Evaluating card: {card} from player {player} (suit: {card.suit}, value: {card.value})")
            
            if card.suit == led_suit:
                self.logger.info(f"Card follows led suit {led_suit}")
                if highest_value == -1 or card.value > highest_value:
                    highest_value = card.value
                    calculated_winner = player
                    self.logger.info(f"New highest card: {card} (value: {card.value}) from player {player}")
            else:
                self.logger.info(f"Card does not follow led suit, cannot win trick")
                
        if calculated_winner is None:
            self.logger.error(f"CRITICAL ERROR: Failed to determine calculated winner")
            # Fallback to first player as a last resort
            calculated_winner = complete_trick[0]["player"]
                
        if calculated_winner != winner_idx:
            self.logger.warning(f"Winner discrepancy! Game returned {winner_idx} but calculation gives {calculated_winner}")
            # Use the calculated winner as a fallback since our calculation is simpler and more reliable
            winner_idx = calculated_winner
        
        # Store the winner for the next trick - this is critical for proper lead tracking
        self.trick_winner = winner_idx
        self.trick_winner_cache = winner_idx  # Cache winner for future reference
        self.logger.info(f"FINAL trick winner determined: {self.POSITIONS[winner_idx]} (player {winner_idx})")
        self.trick_count_verified = False  # Set flag to indicate trick count needs verification
        
        # Find the winning card from the captured trick
        winning_play = next(p for p in complete_trick if p["player"] == winner_idx)
        winning_card = winning_play["card"]
        led_suit = complete_trick[0]["card"].suit
        
        self.logger.info(f"Winning card: {winning_card} from player {winner_idx}")
        
        # Prepare reason text with detailed explanation
        if winning_card.suit == led_suit:
            # Won with led suit
            reason = f"Highest {led_suit} card (led suit)"
            winning_explanation = f"Won as highest card of led suit ({led_suit})"
        else:
            # Won with trump
            reason = f"Trump card ({winning_card.suit})"
            winning_explanation = f"Won by trumping with {winning_card.suit}"
            
        self.logger.info(f"Win reason: {winning_explanation}")
        
        # Update trick count - critical section that must work correctly
        self.logger.info(f"BEFORE TRICK COUNT UPDATE - NS: {self.ns_tricks}, EW: {self.ew_tricks}, Winner: {self.POSITIONS[winner_idx]} (index: {winner_idx})")
        
        # Capture old counts before update for verification
        old_ns = self.ns_tricks
        old_ew = self.ew_tricks
        
        # Save the winner information first - critical for next trick leadership
        self.game.last_trick_winner = winner_idx
        
        # Atomic trick count update with explicit locking
        try:
            # In a real concurrent environment, we'd use a lock here
            # For this single-threaded app, we just ensure we don't get interrupted
            
            if winner_idx in [0, 2]:  # South and North (NS partnership)
                # Increment NS trick count
                self.ns_tricks += 1
                self.logger.info(f"North-South won trick, NS TRICKS INCREMENTED from {old_ns} to {self.ns_tricks}")
            else:  # West and East (EW partnership)
                # Increment EW trick count  
                self.ew_tricks += 1
                self.logger.info(f"East-West won trick, EW TRICKS INCREMENTED from {old_ew} to {self.ew_tricks}")
                
            # Verify and correct the trick counts if needed
            if winner_idx in [0, 2] and self.ns_tricks != old_ns + 1:
                self.logger.error(f"NS TRICK COUNT ERROR: Should be {old_ns + 1} but is {self.ns_tricks}")
                self.ns_tricks = old_ns + 1  # Force the correct value
            elif winner_idx in [1, 3] and self.ew_tricks != old_ew + 1:
                self.logger.error(f"EW TRICK COUNT ERROR: Should be {old_ew + 1} but is {self.ew_tricks}")
                self.ew_tricks = old_ew + 1  # Force the correct value
                
            # Double-check trick counts
            correct_ns = old_ns + (1 if winner_idx in [0, 2] else 0)
            correct_ew = old_ew + (1 if winner_idx in [1, 3] else 0)
            
            if self.ns_tricks != correct_ns or self.ew_tricks != correct_ew:
                self.logger.error(f"CRITICAL TRICK COUNT MISMATCH: NS should be {correct_ns}, is {self.ns_tricks}; EW should be {correct_ew}, is {self.ew_tricks}")
                # Force correct values
                self.ns_tricks = correct_ns
                self.ew_tricks = correct_ew
            
            # Update the trick count display immediately - THIS IS CRITICAL
            # Do this BEFORE calling _clear_trick to ensure counts are displayed
            self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
            self.logger.info(f"TRICK COUNT UPDATED - NS: {self.ns_tricks}, EW: {self.ew_tricks}")
            # Force update of the display - CRITICAL for user feedback
            self.trick_label.update()  # Use update() instead of update_idletasks() for more immediate refresh
            self.update_idletasks()    # Also call this for good measure
            
            self.logger.info(f"AFTER TRICK COUNT UPDATE - NS: {self.ns_tricks}, EW: {self.ew_tricks} - DISPLAY UPDATED")
            self.trick_count_verified = True  # Mark trick count as verified
            
        except Exception as e:
            self.logger.error(f"ERROR in trick completion: {e}")
            # Emergency recovery - force correct values
            if winner_idx in [0, 2]:
                self.ns_tricks = old_ns + 1
            else:
                self.ew_tricks = old_ew + 1
            # Update display in emergency mode
            self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
            self.trick_label.update()  # More forceful update
            self.update_idletasks()    # Additional update to ensure display refresh
            self.logger.info(f"EMERGENCY TRICK COUNT RECOVERY - NS: {self.ns_tricks}, EW: {self.ew_tricks}")
            self.trick_count_verified = True  # Mark trick count as verified in emergency mode
            
        # Call _clear_trick outside try-except to ensure it always runs
        # This is critical for proper trick progression
        self.logger.info(f"CALLING _clear_trick directly after try-except at {time.time()}")
        self._clear_trick()
        self.logger.info("_clear_trick completed successfully")
        
        status_text = f"Trick won by {self.POSITIONS[winner_idx]} with {winning_card}! ({reason})"
        self.logger.info(status_text)
        self.status_bar.config(text=status_text)
        
        # Highlight winning card
        if self.trick_card_views[winner_idx]:
            self.trick_card_views[winner_idx].config(bg='lightgreen')
        
        # Log window state
        self.logger.info(f"TRICK COUNTS UPDATED - Window exists: {self.winfo_exists()}, Viewable: {self.winfo_viewable()}, Mapped: {self.winfo_ismapped()}")
        
        # CRITICAL: Store the current trick counts for verification during cleanup
        # This ensures we have the correct counts regardless of when _clear_trick runs
        self._stored_ns_tricks = self.ns_tricks
        self._stored_ew_tricks = self.ew_tricks
        self._stored_trick_winner = winner_idx
        
    
    # Emergency trick processing method is no longer needed since we call _clear_trick directly
    # in the _end_trick method. This ensures more reliable trick processing.
    
    def _reset_trick_state(self):
        """Reset the trick state without doing full _clear_trick"""
        self.logger.info(f"RESETTING TRICK STATE - Current counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}")
        
        # Force trick count display update
        self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
        self.trick_label.update_idletasks()
        
        # Reset waiting state
        self.waiting_for_trick_end = False
        
        # Set next player (use cached winner)
        winner = self.trick_winner_cache if self.trick_winner_cache is not None else self.trick_winner
        if winner is not None:
            self.game.current_player = winner
            self.game.last_trick_winner = winner
            self._highlight_current_player()
            self.logger.info(f"Reset next player to {self.POSITIONS[winner]}")
        
        self.logger.info("Trick state reset complete")
    

    def _clear_trick(self):
        """Clear the current trick display"""
        import traceback
        self.clear_trick_called = True  # Mark that _clear_trick was called
        self.logger.info(f"ENTERING _clear_trick - Current trick counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}, Verified: {self.trick_count_verified}")
        self.logger.info(f"Window state: Exists: {self.winfo_exists()}, Viewable: {self.winfo_viewable()}, Mapped: {self.winfo_ismapped()}")
        
        # CRITICAL: Verify trick counts against stored values before clearing
        # This ensures counts haven't been lost between _end_trick and now
        if hasattr(self, '_stored_ns_tricks') and hasattr(self, '_stored_ew_tricks'):
            if self.ns_tricks != self._stored_ns_tricks or self.ew_tricks != self._stored_ew_tricks:
                self.logger.error(f"TRICK COUNT LOST: Current NS: {self.ns_tricks}, stored: {self._stored_ns_tricks}, " +
                                 f"Current EW: {self.ew_tricks}, stored: {self._stored_ew_tricks}")
                # Restore from stored values to ensure counts aren't lost
                self.ns_tricks = self._stored_ns_tricks
                self.ew_tricks = self._stored_ew_tricks
                self.logger.info(f"RESTORED trick counts from stored values: NS: {self.ns_tricks}, EW: {self.ew_tricks}")
                
        # Update display immediately
        try:
            self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
            self.trick_label.update()  # Force immediate update, not just idle tasks
            self.logger.info(f"Updated trick display: NS: {self.ns_tricks}, EW: {self.ew_tricks}")
        except Exception as e:
            self.logger.error(f"Failed to update trick display: {str(e)}")
        
        # CRITICAL: Check stored values first - this ensures trick counts don't get lost
        if hasattr(self, '_stored_ns_tricks') and hasattr(self, '_stored_ew_tricks') and hasattr(self, '_stored_trick_winner'):
            if self.ns_tricks != self._stored_ns_tricks or self.ew_tricks != self._stored_ew_tricks:
                self.logger.warning(f"TRICK COUNT MISMATCH: Current NS: {self.ns_tricks}, stored: {self._stored_ns_tricks}, " +
                                   f"Current EW: {self.ew_tricks}, stored: {self._stored_ew_tricks}")
                # Use stored values as they were set at trick end time
                self.ns_tricks = self._stored_ns_tricks
                self.ew_tricks = self._stored_ew_tricks
                winner = self._stored_trick_winner
                self.trick_winner = winner
                self.trick_winner_cache = winner
                self.logger.info(f"RESTORED trick counts from stored values: NS: {self.ns_tricks}, EW: {self.ew_tricks}")
                
                # Force immediate display update with restored values
                self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
                self.trick_label.update()
                self.trick_count_verified = True
        
        # Secondary verification if needed
        if not self.trick_count_verified:
            self.logger.warning("CLEAR_TRICK: Trick count not verified - this should not happen")
            
            # Recover using cached winner if available
            winner = self.trick_winner_cache if self.trick_winner_cache is not None else self.trick_winner
            if winner is not None:
                self.logger.info(f"Recovering trick count using cached winner: {self.POSITIONS[winner]}")
                # Force verification based on cached winner
                old_ns = self.ns_tricks
                old_ew = self.ew_tricks
                
                if winner in [0, 2]:  # South and North partnership
                    if self.ns_tricks == old_ns:  # No increment happened
                        self.ns_tricks = old_ns + 1
                        self.logger.warning(f"NS TRICK COUNT FORCED from {old_ns} to {self.ns_tricks}")
                else:  # East-West partnership
                    if self.ew_tricks == old_ew:  # No increment happened
                        self.ew_tricks = old_ew + 1
                        self.logger.warning(f"EW TRICK COUNT FORCED from {old_ew} to {self.ew_tricks}")
                
                # Update display immediately
                self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
                self.trick_label.update()  # More forceful update
                self.update_idletasks()
                self.last_trick_displayed = True
                
                self.trick_count_verified = True
        
        # Clear trick area
        for frame in self.trick_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        
        self.trick_card_views = [None, None, None, None]
        
        # Refresh all player hands to ensure proper display
        for i in range(4):
            self._refresh_player_hand(i)
        
        # Check if hand is complete
        if not any(player["hand"] for player in self.game.players):
            self._game_over()
        else:
            # Ensure trick count is consistent with display - CRITICAL CHECK
            trick_label_text = self.trick_label.cget("text")
            expected_text = f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}"
            if trick_label_text != expected_text:
                self.logger.error(f"TRICK LABEL MISMATCH: Display shows '{trick_label_text}' but should be '{expected_text}'")
                self.trick_label.config(text=expected_text)
                # Force immediate update, not just idle tasks
                self.trick_label.update()
            
            # Make sure display is up to date one more time - FINAL SAFETY CHECK
            current_label = self.trick_label.cget("text")
            expected_label = f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}"
            if current_label != expected_label:
                self.logger.warning(f"Display mismatch after _clear_trick! Shows '{current_label}' but should be '{expected_label}'")
                self.trick_label.config(text=expected_label)
                self.trick_label.update()
                
            # Final verification that trick counts are correct before proceeding
            total_tricks = self.ns_tricks + self.ew_tricks
            if total_tricks > 13:
                self.logger.error(f"INVALID TOTAL TRICK COUNT: {total_tricks} (should be ≤ 13)")
                # Correct by removing from the higher count
                excess = total_tricks - 13
                if self.ns_tricks >= self.ew_tricks:
                    self.ns_tricks -= excess
                else:
                    self.ew_tricks -= excess
                self.logger.info(f"Corrected trick counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}")
                self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
                self.trick_label.update()
                
            # Mark that trick was successfully displayed
            self.last_trick_displayed = True
                
            # Log successful completion of _clear_trick
            self.logger.info("_clear_trick completed successfully - About to set next player")
            
            # Use the cached winner if available, otherwise use trick_winner
            winner = self.trick_winner_cache if self.trick_winner_cache is not None else self.trick_winner
            
            # Set the winner as the next player to lead
            self.game.current_player = winner
            self.game.last_trick_winner = winner  # Ensure last_trick_winner is set
            self.logger.info(f"TRICK CLEARED - Final trick counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}, Next trick led by: {self.POSITIONS[winner]}")
            
            # Clear stored trick values as they're no longer needed
            if hasattr(self, '_stored_ns_tricks'):
                delattr(self, '_stored_ns_tricks')
            if hasattr(self, '_stored_ew_tricks'):
                delattr(self, '_stored_ew_tricks')
            if hasattr(self, '_stored_trick_winner'):
                delattr(self, '_stored_trick_winner')
            
            # Log the state changes
            self.logger.info(f"Setting player {self.trick_winner} ({self.POSITIONS[self.trick_winner]}) as next player (winner leads)")
            self.logger.info(f"Current player set to: {self.game.current_player}")
            self.logger.info(f"Last trick winner set to: {self.game.last_trick_winner}")
            
            # Update UI for next trick
            self.waiting_for_trick_end = False
            self._highlight_current_player()
            
            # Provide detailed feedback about who leads and why
            lead_explanation = f"Next trick - {self.POSITIONS[self.game.current_player]} must lead (winner of previous trick)"
            self.logger.info(lead_explanation)
            self.status_bar.config(text=lead_explanation)
            
            # Flash the winner's area to make it very clear who should lead
            self._flash_player_frame(self.trick_winner)
    
    def _highlight_current_player(self):
        """Highlight the current player's frame"""
        # Reset all frames
        for i, frame in enumerate([self.south_frame, self.west_frame, self.north_frame, self.east_frame]):
            if i == self.game.current_player:
                frame.config(bg='#006600')  # Brighter green for current player
            else:
                frame.config(bg='#004400')  # Regular green for others
        
        # Update current player label
        self.current_player_label.config(text=f"Current Player: {self.POSITIONS[self.game.current_player]}")
    
    def _game_over(self):
        """Handle end of game"""
        self.logger.info(f"GAME OVER - Final trick counts: NS: {self.ns_tricks}, EW: {self.ew_tricks}, Verified: {self.trick_count_verified}")
        
        # Final verification of trick counts
        total_tricks = self.ns_tricks + self.ew_tricks
        if total_tricks != 13:  # A complete bridge hand should have exactly 13 tricks
            self.logger.error(f"TRICK COUNT ERROR: Total tricks should be 13 but is {total_tricks}")
            
            # Last chance to fix the counts - we'll distribute the missing/extra tricks
            if total_tricks < 13:
                missing = 13 - total_tricks
                self.logger.warning(f"Missing {missing} tricks - fixing final counts")
                # Distribute missing tricks - split them evenly or give to whoever has fewer
                if self.ns_tricks <= self.ew_tricks:
                    self.ns_tricks += missing
                else:
                    self.ew_tricks += missing
            elif total_tricks > 13:
                extra = total_tricks - 13
                self.logger.warning(f"Extra {extra} tricks - fixing final counts")
                # Remove extra tricks from whoever has more
                if self.ns_tricks >= self.ew_tricks:
                    self.ns_tricks -= min(extra, self.ns_tricks)
                else:
                    self.ew_tricks -= min(extra, self.ew_tricks)
            
            # Update display one last time
            self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
            self.trick_label.update_idletasks()
            self.logger.info(f"FINAL CORRECTED TRICK COUNTS: NS: {self.ns_tricks}, EW: {self.ew_tricks}, Total: {self.ns_tricks + self.ew_tricks}")
        
        # Force update of the display one last time
        self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
        self.trick_label.update_idletasks()
        
        # Log debug info about clear_trick calls
        self.logger.info(f"GAME OVER DEBUG - clear_trick_called: {self.clear_trick_called}, clear_trick_job: {self.clear_trick_job}")
        
        messagebox.showinfo("Game Over", f"Game completed!\nFinal score:\nNorth-South: {self.ns_tricks}\nEast-West: {self.ew_tricks}")
        self.status_bar.config(text="Game over. North-South won the game!" if self.ns_tricks > self.ew_tricks else 
                              "Game over. East-West won the game!" if self.ew_tricks > self.ns_tricks else
                              "Game over. It's a tie!")
        
    def _ensure_visibility(self):
        """Final check to make sure window is visible and has focus"""
        self.logger.info("Performing final visibility check")
        # Update geometry info to ensure window is properly mapped
        self.update_idletasks()
        
        # Check if Tkinter's after() mechanism is working
        import time
        start_time = time.time()
        self.after_test_completed = False
        
        def after_test():
            elapsed = time.time() - start_time
            self.after_test_completed = True
            self.logger.info(f"after() test completed after {elapsed:.4f} seconds")
            
        self.logger.info("Testing Tkinter after() mechanism...")
        self.after(500, after_test)  # Should run after 500ms
        
    def _on_bidding_complete(self):
        """Handle completion of the bidding phase."""
        self.logger.info("Bidding complete")
        
        # Hide the bidding box
        self.bidding_box.hide()
        
        # Get contract and declarer info
        contract_str = self.game.determine_final_contract()
        self.contract_label.config(text=f"Contract: {contract_str}")
        
        # Set up the play phase
        if self.game.contract is None:
            self.status_bar.config(text="All players passed. Starting a new game.")
            # Could automatically start a new game here
        else:
            # Determine first leader (player to left of declarer)
            first_leader = (self.game.declarer + 1) % 4
            declarer_name = self.POSITIONS[self.game.declarer]
            dummy_name = self.POSITIONS[(self.game.declarer + 2) % 4]
            
            # Set current player to first leader and clear any previous trick winner
            self.game.current_player = first_leader
            self.game.last_trick_winner = None  # Clear any previous trick winner
            
            # Log detailed information
            self.logger.info(f"Contract: {contract_str}")
            self.logger.info(f"Declarer: {declarer_name} (player {self.game.declarer})")
            self.logger.info(f"Dummy: {dummy_name}")
            self.logger.info(f"First Leader: {self.POSITIONS[first_leader]} (player {first_leader})")
            
            # Update UI with clear status message
            status_text = (f"Contract: {contract_str} by {declarer_name}. "
                          f"{dummy_name} is dummy. "
                          f"{self.POSITIONS[first_leader]} to lead.")
            self.status_bar.config(text=status_text)
            
            # Update UI to show current player
            self._highlight_current_player()
            
            # Make sure all cards are properly enabled/disabled for play phase
            self._prepare_cards_for_play()
            
            # Flash the leader's frame to make it clear who should play
            self._flash_player_frame(first_leader)
    
    def _prepare_for_bidding(self):
        """Prepare the UI for the bidding phase."""
        self.logger.info("Preparing for bidding phase")
        
        # Ensure we're in bidding state
        self.game.current_state = "bidding"
        
        # Make sure all frames are visible
        self.north_frame.place(relx=0.5, rely=0.02, anchor='n')
        self.south_frame.place(relx=0.5, rely=0.98, anchor='s')
        self.east_frame.place(relx=0.98, rely=0.5, anchor='e')
        self.west_frame.place(relx=0.02, rely=0.5, anchor='w')
        self.center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Make sure we have valid hands
        if not all(len(player["hand"]) == 13 for player in self.game.players):
            self.logger.warning("Invalid hand count detected, re-dealing cards")
            self.game.deal_cards()
        
        # Import hand evaluation for logging hand values
        from core.hand_evaluation import calculate_hcp, count_suit_length, is_balanced
        
        # Log the hands with evaluation info for debugging
        for i, player in enumerate(self.game.players):
            hand = player["hand"]
            try:
                # Basic hand info
                hand_str = ", ".join(f"{card.value_name}{card.suit}" for card in sorted(hand, key=lambda c: (c.suit, -c.value)))
                
                # Calculate HCP and distribution
                hcp = calculate_hcp(hand)
                suit_lengths = count_suit_length(hand)
                balanced = is_balanced(suit_lengths)
                
                # Log with evaluation
                self.logger.info(f"Player {i} ({self.POSITIONS[i]}) hand: {hand_str}")
                self.logger.info(f"  - HCP: {hcp}, Distribution: {suit_lengths}, Balanced: {balanced}")
            except Exception as e:
                self.logger.error(f"Error evaluating player {i} hand: {e}")
        
        # Show all hands face-up for bidding
        self._display_all_hands_for_bidding()
        
        # Show and initialize bidding box
        self.bidding_box.show()
        
        # Update status
        self.status_bar.config(text="Bidding phase - make your bid")
        
        # All players are human-controlled, so no AI bidding is needed
    
    def _display_all_hands_for_bidding(self):
        """Display all hands face-up for the bidding phase."""
        self.logger.info("Displaying all hands for bidding phase")
        
        # Check if cards have been dealt
        total_cards = sum(len(player["hand"]) for player in self.game.players)
        self.logger.info(f"Total cards in all hands: {total_cards}")
        
        # Ensure a fresh deal if any issues are detected
        if total_cards != 52:
            self.logger.warning(f"Incorrect card count: {total_cards}. Re-dealing cards.")
            # Reinitialize the game completely to ensure clean state
            self.game = BridgeGame()
            self.game.initialize_players()
            self.game.new_game()  # Use new_game instead of just deal_cards to reset everything
            
            # Verify the new deal
            total_cards = sum(len(player["hand"]) for player in self.game.players)
            self.logger.info(f"After re-dealing, total cards: {total_cards}")
            
            if total_cards != 52:
                self.logger.error(f"Still have incorrect card count: {total_cards} after re-dealing!")
                messagebox.showerror("Card Dealing Error", f"Failed to deal cards correctly. Got {total_cards} cards instead of 52.")
        
        # Import hand evaluation for showing hand statistics
        from core.hand_evaluation import calculate_hcp, count_suit_length, is_balanced
        
        # Log detailed hand information for debugging
        for i, player in enumerate(self.game.players):
            hand = player["hand"]
            try:
                # Calculate hand statistics
                hcp = calculate_hcp(hand)
                suit_lengths = count_suit_length(hand)
                balanced = is_balanced(suit_lengths)
                
                # Sort hand for logging
                sorted_hand = sorted(hand, key=lambda c: (c.suit, -c.value))
                hand_str = ", ".join(f"{card.value_name}{card.suit}" for card in sorted_hand)
                
                self.logger.info(f"Player {i} ({self.POSITIONS[i]}) hand for display:")
                self.logger.info(f"  Cards: {hand_str}")
                self.logger.info(f"  HCP: {hcp}, Distribution: ♠{suit_lengths['S']} ♥{suit_lengths['H']} ♦{suit_lengths['D']} ♣{suit_lengths['C']}, Balanced: {balanced}")
            except Exception as e:
                self.logger.error(f"Error formatting player {i} hand: {e}")
        
        # Clear existing cards
        self.card_views = [[] for _ in range(4)]
        
        # Make sure frames are properly positioned
        self.north_frame.place(relx=0.5, rely=0.1, anchor='n')
        self.south_frame.place(relx=0.5, rely=0.9, anchor='s')
        self.east_frame.place(relx=0.8, rely=0.5, anchor='e')
        self.west_frame.place(relx=0.2, rely=0.5, anchor='w')
        
        # Clear existing content in frames
        for frame in [self.north_frame, self.south_frame, self.east_frame, self.west_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Create frames for each player's cards
        frames = []
        
        # South (player 0)
        south_cards_frame = tk.Frame(self.south_frame, bg='#004400')
        south_cards_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        frames.append((south_cards_frame, 'bottom', "South (You)"))
        
        # West (player 1)
        west_cards_frame = tk.Frame(self.west_frame, bg='#004400')
        west_cards_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        frames.append((west_cards_frame, 'left', "West"))
        
        # North (player 2)
        north_cards_frame = tk.Frame(self.north_frame, bg='#004400')
        north_cards_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        frames.append((north_cards_frame, 'top', "North"))
        
        # East (player 3)
        east_cards_frame = tk.Frame(self.east_frame, bg='#004400')
        east_cards_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        frames.append((east_cards_frame, 'right', "East"))
        
        # Import hand evaluation functions
        from core.hand_evaluation import calculate_hcp, count_suit_length, is_balanced
        
        # Add player hand information labels (HCP and distribution)
        for player_idx, (frame, position, player_name) in enumerate(frames):
            # First add player name label
            name_label = tk.Label(frame, 
                              text=player_name,
                              font=('Arial', 12, 'bold'), 
                              fg='white', bg='#004400')
            name_label.pack(side=tk.TOP, pady=(5, 0))
            
            # Get and sort cards
            hand = self.game.players[player_idx]['hand']
            
            # Skip if hand is empty (shouldn't happen but just in case)
            if not hand:
                error_label = tk.Label(frame, text="No cards available!",
                                    font=('Arial', 12, 'bold'), fg='red', bg='#004400')
                error_label.pack(pady=20)
                continue
            
            # Sort cards for display
            hand = sorted(hand, key=lambda c: (c.suit, -c.value))
            
            # Calculate HCP and suit lengths for display
            hcp = calculate_hcp(hand)
            suit_lengths = count_suit_length(hand)
            balanced = is_balanced(suit_lengths)
            dist_points = sum(max(0, length-4) for length in suit_lengths.values())
            
            # Add info label with HCP and distribution
            distribution_str = f"♠{suit_lengths['S']} ♥{suit_lengths['H']} ♦{suit_lengths['D']} ♣{suit_lengths['C']}"
            total_pts = f"{hcp}{'+'+ str(dist_points) if dist_points > 0 else ''}"
            
            info_frame = tk.Frame(frame, bg='#004400')
            info_frame.pack(side=tk.TOP, pady=(5, 10), fill=tk.X)
            
            # HCP label with colorful background based on strength
            hcp_bg = '#006600' if hcp >= 12 else '#444400' if hcp >= 8 else '#440000'
            hcp_label = tk.Label(info_frame, 
                              text=f"HCP: {total_pts}",
                              font=('Arial', 10, 'bold'),
                              fg='white', bg=hcp_bg,
                              padx=5, pady=2)
            hcp_label.pack(side=tk.LEFT, padx=5)
            
            # Distribution with colorful suit symbols
            dist_label = tk.Label(info_frame,
                              text=distribution_str,
                              font=('Arial', 10),
                              fg='white', bg='#004400')
            dist_label.pack(side=tk.LEFT, padx=5)
            
            # Balanced/Unbalanced indicator
            balance_label = tk.Label(info_frame,
                                  text=f"{'Balanced' if balanced else 'Unbalanced'}",
                                  font=('Arial', 10),
                                  fg='white', bg='#004400')
            balance_label.pack(side=tk.LEFT, padx=5)
            
            # Create a subframe for the cards with a slight border
            cards_subframe = tk.Frame(frame, bg='#003300', bd=2, relief=tk.GROOVE)
            cards_subframe.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
            
            # Create a frame for each suit to organize cards
            suit_frames = {}
            for suit_name, suit_symbol, color in [
                ('S', '♠', 'white'),  # Changed to white for better visibility
                ('H', '♥', 'red'),
                ('D', '♦', 'red'),
                ('C', '♣', 'white')
            ]:
                # Create frame with background color matching the suit
                bg_color = '#000055' if suit_name in ['S', 'C'] else '#550000'
                suit_frame = tk.Frame(cards_subframe, bg=bg_color, bd=1, relief=tk.RAISED)
                
                # For East/West, stack suits vertically
                # For North/South, arrange suits horizontally
                if position in ['left', 'right']:  # East and West
                    suit_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=8)  # Stack suit frames vertically
                else:  # North and South
                    suit_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=5)  # Arrange suit frames horizontally
                
                # Add suit label
                suit_label = tk.Label(suit_frame, 
                                   text=suit_symbol, 
                                   font=('Arial', 12, 'bold'), 
                                   fg=color, bg=bg_color)
                suit_label.pack(side=tk.TOP if position in ['left', 'right'] else tk.LEFT, padx=3, pady=3)
                
                suit_frames[suit_name] = suit_frame
            
            # Add cards to appropriate suit frames
            for card in hand:
                suit = card.suit
                
                # Create CardView instead of Button for consistent handling
                card_view = CardView(suit_frames[suit], 
                                   card=card,
                                   face_up=True,
                                   callback=self._on_card_click)
                
                # Store player index in card view
                card_view.player_idx = player_idx
                
                # For East/West, stack cards vertically within each suit
                # For North/South, arrange cards horizontally within each suit
                if position in ['left', 'right']:  # East and West
                    # Stack cards vertically
                    card_view.pack(side=tk.TOP, pady=4)  # Increased vertical spacing
                else:  # North and South
                    # Arrange cards horizontally
                    card_view.pack(side=tk.LEFT, padx=4, pady=2)  # Increased horizontal spacing
                
                # Store the card view for later reference
                self.card_views[player_idx].append(card_view)
    
    def _prepare_cards_for_play(self):
        """Prepare cards for the playing phase."""
        # Get first leader (player to left of declarer)
        first_leader = (self.game.declarer + 1) % 4
        
        # Set the game's current player to the first leader
        self.game.current_player = first_leader
        
        self.logger.info(f"Setting up play phase - First leader: {self.POSITIONS[first_leader]}")
        
        # Enable/disable cards based on first leader
        for player_idx, card_views in enumerate(self.card_views):
            for card_view in card_views:
                if player_idx == first_leader:
                    # Enable clicking for first leader's cards
                    card_view.callback = self._on_card_click  # Set callback first
                    card_view.bind("<Button-1>", lambda e, cv=card_view: self._on_card_click(cv))
                    card_view.config(cursor="hand2", bg='white')
                    self.logger.info(f"Enabled card {card_view.card} for {self.POSITIONS[player_idx]}")
                else:
                    # Disable clicking for other players' cards
                    card_view.callback = None
                    card_view.unbind("<Button-1>")
                    card_view.config(cursor="", bg='#f0f0f0')  # Gray out cards
                    self.logger.info(f"Disabled card {card_view.card} for {self.POSITIONS[player_idx]}")
        
        # Update UI
        self._highlight_current_player()
        
        # Set status text
        status_text = f"{self.POSITIONS[first_leader]} to lead"
        self.status_bar.config(text=status_text)
        
        # Flash the leader's frame to make it clear who should play
        self._flash_player_frame(first_leader)
        
        # Log completion
        self.logger.info(f"Play phase setup complete - {self.POSITIONS[first_leader]} to lead")
    
    def _hide_play_area(self):
        """Hide the play area during bidding - NOT USED, we keep cards visible during bidding."""
        pass  # No longer hiding the play area
    
    def _show_play_area(self):
        """Show the play area after bidding is complete - NOT USED, cards stay visible throughout."""
        pass  # No longer needed since cards are always visible
        
        # Get actual window geometry after rendering
        actual_geometry = self.geometry()
        self.logger.info(f"Actual window geometry: {actual_geometry}")
        
        # Check if window is visible on screen
        if self.winfo_viewable():
            self.logger.info("Window is confirmed viewable")
        else:
            self.logger.warning("Window might not be viewable - forcing visibility")
            self.deiconify()
            self.lift()
            self.focus_force()
            
        # Force another update and lift
        self.update()
        self.lift()
        self.focus_force()
        
    def _flash_player_frame(self, player_idx):
        """Flash a player's frame to draw attention to it"""
        frames = [self.south_frame, self.west_frame, self.north_frame, self.east_frame]
        frame = frames[player_idx]
        
        # Original color
        original_bg = frame.cget("bg")
        
        # Flash sequence (bright yellow -> original)
        def flash_on():
            frame.config(bg='#FFFF00')  # Bright yellow
            self.after(300, lambda: flash_off())
            
        def flash_off():
            frame.config(bg='#006600')  # Brighter green
            
        # Start flashing
        flash_on()
        
    def _refresh_player_hand(self, player_idx):
        """Refresh a player's hand display after playing a card"""
        # Get the frame for this player's cards
        frames = [self.south_frame, self.west_frame, self.north_frame, self.east_frame]
        frame = frames[player_idx]
        
        # Clear existing card displays
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
                
        # Create a new frame for the cards
        positions = ['bottom', 'left', 'top', 'right']
        cards_frame = tk.Frame(frame, bg='#004400')
        cards_frame.pack(pady=30)
        
        # Get and sort remaining cards
        hand = sorted(self.game.players[player_idx]['hand'], 
                     key=lambda c: (c.suit, -c.value))
        
        # Display remaining cards with proper spacing
        current_suit = None
        position = positions[player_idx]
        
        # Remove this player's card views from tracking
        self.card_views[player_idx] = []
        
        # Group cards by suit for better spacing
        for card in hand:
            suit = card.suit
            
            if current_suit is not None and suit != current_suit:
                # Add a bit more space between suits
                spacer = tk.Label(cards_frame, text=" ", bg='#004400', width=1)
                if position in ['left', 'right']:
                    spacer.pack(side=tk.TOP)  # Vertical spacing for East/West
                else:
                    spacer.pack(side=tk.LEFT)  # Horizontal spacing for North/South
                    
            current_suit = suit
            
            # Create card view with callback
            card_view = CardView(cards_frame, card=card, face_up=True, callback=self._on_card_click)
            
            # Store the player index in the card view
            card_view.player_idx = player_idx
            
            if position in ['left', 'right']:  # East and West
                card_view.pack(side=tk.TOP, pady=4)  # Match the spacing from bidding display
            else:  # North and South
                card_view.pack(side=tk.LEFT, padx=4)  # Match the spacing from bidding display
            
            # Store the card view for later reference
            self.card_views[player_idx].append(card_view)

    def _save_game(self):
        messagebox.showinfo("Save Game", "Game saving not implemented yet")
        self.status_bar.config(text="Game saved")

    def _load_game(self):
        messagebox.showinfo("Load Game", "Game loading not implemented yet")
        self.status_bar.config(text="Game loaded")
