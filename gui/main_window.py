import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
from core.game import BridgeGame
from core.deck import Card

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
        self.trick_card_views = [None, None, None, None]  # Cards in current trick
        self.trick_frames = [None, None, None, None]  # Frames for trick cards
        self.ns_tricks = 0
        self.ew_tricks = 0
        self.current_player_highlight = None
        self.waiting_for_trick_end = False

        # Configure the main window
        self.title("Bridge Game")
        self.configure(bg='darkgreen')
        
        # Get screen dimensions and set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1400  # Increased width
        window_height = 900  # Increased height
        
        # Set minimum window size
        self.minsize(1000, 700)
        
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
                    spacer = tk.Label(frame, text=" ", bg='#004400', width=1)
                    if position in ['left', 'right']:
                        spacer.pack()
                    else:
                        spacer.pack(side=tk.LEFT)
                        
                current_suit = suit
                
                # Create card view with callback for clickable cards - allow all positions to be played
                card_view = CardView(frame, card=card, face_up=True, callback=self._on_card_click)
                
                # Store the player index in the card view for later reference
                card_view.player_idx = player_idx
                
                if position in ['left', 'right']:
                    card_view.pack(pady=1)  # Stack vertically for East/West
                else:
                    card_view.pack(side=tk.LEFT, padx=1)  # Stack horizontally for North/South
                
                # Store the card view for later reference
                self.card_views[player_idx].append(card_view)
        
        # Highlight current player
        self._highlight_current_player()

    def _new_game(self):
        """Start a new game"""
        # Initialize a new game
        self.game = BridgeGame()
        self.game.new_game()
        self.game.current_state = "playing"  # Skip bidding for now
        
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
        self.trick_label.config(text="Tricks: NS: 0 | EW: 0")
        self.status_bar.config(text="New game started - South to lead first trick")
        
        # Display hands
        self._display_hands()
    
    def _on_card_click(self, card_view):
        """Handle card click event"""
        if self.waiting_for_trick_end:
            return  # Ignore clicks while waiting for trick to end
            
        # Get the card object and player index
        card = card_view.card
        player_idx = card_view.player_idx
        
        self.logger.info(f"Card click: {self.POSITIONS[player_idx]} attempting to play {card}")
        
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
        
        # If continuing a trick, check if it's this player's turn
        if self.game.trick and player_idx != self.game.current_player:
            self.logger.info(f"Wrong player: {self.POSITIONS[player_idx]} tried to play but it's {self.POSITIONS[self.game.current_player]}'s turn")
            self.status_bar.config(text=f"It's {self.POSITIONS[self.game.current_player]}'s turn to play")
            return
        
        # If trick already has cards, show what's being followed
        if self.game.trick:
            led_suit = self.game.trick[0]["card"].suit
            self.logger.info(f"Current trick led with {led_suit}")
            
            # Check if player has cards of led suit
            player_hand = self.game.players[player_idx]["hand"]
            has_led_suit = any(c.suit == led_suit for c in player_hand)
            if has_led_suit:
                self.logger.info(f"{self.POSITIONS[player_idx]} has {led_suit} cards and must follow suit")
            else:
                self.logger.info(f"{self.POSITIONS[player_idx]} has no {led_suit} cards and can play anything")
        
        # We don't need to temporarily set the current player anymore since
        # the game.play_card will check if this is a valid play
        
        # Try to play the card
        if self.game.play_card(player_idx, card):
            # Card played successfully
            self.logger.info(f"Card played: {self.POSITIONS[player_idx]} played {card}")
            self._show_played_card(player_idx, card)
            
            # Remove card from display and refresh the player's hand
            self._refresh_player_hand(player_idx)
            
            # Check if trick is complete
            if len(self.game.trick) == 4:
                self.logger.info(f"Trick complete with 4 cards")
                self.waiting_for_trick_end = True
                self.after(1500, self._end_trick)  # Wait 1.5 seconds before ending trick
            else:
                # Update to next player in sequence
                next_player = (player_idx + 1) % 4
                self.game.current_player = next_player
                self.logger.info(f"Setting next player to: {next_player} ({self.POSITIONS[next_player]})")
                self._highlight_current_player()
                self.logger.info(f"Next player: {self.POSITIONS[self.game.current_player]}")
                self.status_bar.config(text=f"Next player: {self.POSITIONS[self.game.current_player]}")
        else:
            # Invalid play - provide feedback based on the context
            if not self.game.trick and self.game.last_trick_winner is not None and player_idx != self.game.last_trick_winner:
                # Wrong player trying to lead
                self.status_bar.config(text=f"{self.POSITIONS[self.game.last_trick_winner]} must lead to the next trick (as trick winner)")
            elif self.game.trick and player_idx != self.game.current_player:
                # Wrong player in the middle of a trick
                self.status_bar.config(text=f"It's {self.POSITIONS[self.game.current_player]}'s turn to play")
            
            # Get the led suit for better feedback
            led_suit = self.game.trick[0]["card"].suit if self.game.trick else None
            
            # Check if player has cards of the led suit
            player_hand = self.game.players[player_idx]["hand"]
            has_led_suit = any(c.suit == led_suit for c in player_hand) if led_suit else False
            
            # Provide more specific feedback
            if has_led_suit:
                self.status_bar.config(text=f"Invalid play from {self.POSITIONS[player_idx]}! Must follow {led_suit} suit.")
            else:
                # This case shouldn't happen with the fixed logic, but provide feedback just in case
                self.status_bar.config(text=f"Invalid play from {self.POSITIONS[player_idx]}! Please try another card.")
    
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
        # First, capture the complete trick before it's cleared
        complete_trick = self.game.trick.copy()
        
        # Determine winner
        winner_idx = self.game._determine_trick_winner()
        
        # Log detailed information about trick completion
        trick_cards = [(i, play["player"], play["card"]) for i, play in enumerate(complete_trick)]
        self.logger.info(f"Evaluating trick winner for trick: {trick_cards}")
        
        # Double-check the winner determination with our own calculation
        led_suit = complete_trick[0]["card"].suit
        highest_value = -1
        calculated_winner = None
        
        for play in complete_trick:
            card = play["card"]
            player = play["player"]
            if card.suit == led_suit and (highest_value == -1 or card.value > highest_value):
                highest_value = card.value
                calculated_winner = player
                
        if calculated_winner != winner_idx:
            self.logger.warning(f"Winner discrepancy! Game returned {winner_idx} but calculation gives {calculated_winner}")
            # Use the calculated winner as a fallback
            winner_idx = calculated_winner
        
        # Store the winner for the next trick
        self.trick_winner = winner_idx
        self.logger.info(f"Trick winner determined: {self.POSITIONS[winner_idx]} (player {winner_idx})")
        
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
        
        # Update trick count
        if winner_idx in [0, 2]:  # South and North (NS partnership)
            self.ns_tricks += 1
            self.logger.info(f"North-South won trick, now at {self.ns_tricks} tricks")
        else:  # West and East (EW partnership)
            self.ew_tricks += 1
            self.logger.info(f"East-West won trick, now at {self.ew_tricks} tricks")
        
        self.trick_label.config(text=f"Tricks: NS: {self.ns_tricks} | EW: {self.ew_tricks}")
        
        # Show winner with detailed reason
        status_text = f"Trick won by {self.POSITIONS[winner_idx]} with {winning_card}! ({reason})"
        self.logger.info(status_text)
        self.status_bar.config(text=status_text)
        
        # Highlight winning card
        if self.trick_card_views[winner_idx]:
            self.trick_card_views[winner_idx].config(bg='lightgreen')
        
        # Clear trick after delay
        self.after(1000, self._clear_trick)
    
    def _clear_trick(self):
        """Clear the current trick display"""
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
            # Set the winner as the next player to lead
            self.game.current_player = self.trick_winner
            self.game.last_trick_winner = self.trick_winner  # Ensure last_trick_winner is set
            
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
        messagebox.showinfo("Game Over", f"Game completed!\nFinal score:\nNorth-South: {self.ns_tricks}\nEast-West: {self.ew_tricks}")
        self.status_bar.config(text="Game over. North-South won the game!" if self.ns_tricks > self.ew_tricks else 
                              "Game over. East-West won the game!" if self.ew_tricks > self.ns_tricks else
                              "Game over. It's a tie!")
        
    def _ensure_visibility(self):
        """Final check to make sure window is visible and has focus"""
        self.logger.info("Performing final visibility check")
        # Update geometry info to ensure window is properly mapped
        self.update_idletasks()
        
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
                    spacer.pack()
                else:
                    spacer.pack(side=tk.LEFT)
                    
            current_suit = suit
            
            # Create card view with callback
            card_view = CardView(cards_frame, card=card, face_up=True, callback=self._on_card_click)
            
            # Store the player index in the card view
            card_view.player_idx = player_idx
            
            if position in ['left', 'right']:
                card_view.pack(pady=1)  # Stack vertically for East/West
            else:
                card_view.pack(side=tk.LEFT, padx=1)  # Stack horizontally for North/South
            
            # Store the card view for later reference
            self.card_views[player_idx].append(card_view)

    def _save_game(self):
        messagebox.showinfo("Save Game", "Game saving not implemented yet")
        self.status_bar.config(text="Game saved")

    def _load_game(self):
        messagebox.showinfo("Load Game", "Game loading not implemented yet")
        self.status_bar.config(text="Game loaded")
