import tkinter as tk
from tkinter import ttk
import time
import logging
from core.game import BridgeGame, Bid, BidType

class BiddingBox(tk.Frame):
    """
    Bidding interface for Bridge game.
    
    This class provides a graphical interface for the bidding phase of a Bridge game,
    including a grid of bid buttons, Pass/Double/Redouble buttons, and a bidding history display.
    """
    
    # Card suits and denominations
    SUITS = {'C': '♣', 'D': '♦', 'H': '♥', 'S': '♠', 'NT': 'NT'}
    SUIT_COLORS = {'♣': 'black', '♦': 'red', '♥': 'red', '♠': 'black', 'NT': 'blue'}
    POSITIONS = ['South', 'West', 'North', 'East']
    
    # Set up logger
    logger = logging.getLogger("BridgeGame.GUI.BiddingBox")
    
    def __init__(self, parent, game, on_bidding_complete, player_types):
        """
        Initialize the BiddingBox.
        
        Args:
            parent: The parent widget
            game: The BridgeGame instance
            on_bidding_complete: Callback function when bidding is complete
            player_types: Dictionary mapping player indices to their types (human/ai)
        """
        super().__init__(parent, bg='darkgreen')
        
        self.parent = parent
        self.game = game
        self.on_bidding_complete = on_bidding_complete
        self.player_types = player_types  # Store player types directly in the bidding box
        
        # Create UI components
        self._create_layout()
        
        self.logger.info("BiddingBox initialized")
    
    def _create_layout(self):
        """Create the main layout for the bidding box."""
        # Main container with title
        title_label = tk.Label(self, text="Bidding", 
                              font=('Arial', 16, 'bold'),
                              bg='darkgreen', fg='white')
        title_label.pack(pady=(10, 20))
        
        # Create two columns: bidding grid on left, history on right
        content_frame = tk.Frame(self, bg='darkgreen')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Bidding controls frame - now stacked vertically
        self.bid_frame = tk.Frame(content_frame, bg='darkgreen')
        self.bid_frame.pack(fill=tk.X, expand=True)  # Changed to fill X
        
        # Current bidder indicator
        self.bidder_frame = tk.Frame(self.bid_frame, bg='darkgreen')
        self.bidder_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(self.bidder_frame, text="Current Bidder:", 
                font=('Arial', 14), bg='darkgreen', fg='white').pack(side=tk.LEFT, padx=10)
        
        self.current_bidder_label = tk.Label(self.bidder_frame, text="South", 
                                            font=('Arial', 14, 'bold'), 
                                            bg='darkgreen', fg='yellow')
        self.current_bidder_label.pack(side=tk.LEFT, padx=10)
        
        # Create the bidding grid
        self._create_bidding_grid()
        
        # Create special bid buttons
        self._create_special_bid_buttons()
        
        # History frame - now below the bidding frame
        history_frame = tk.Frame(content_frame, bg='#004400', bd=2, relief=tk.GROOVE)
        history_frame.pack(fill=tk.X, pady=(20, 0))  # Changed to fill X with top padding
        
        # History title
        tk.Label(history_frame, text="Bidding History", 
                font=('Arial', 14), bg='#004400', fg='white').pack(pady=10)
        
        # Bidding history display - adjusted height for new layout
        self.history_text = tk.Text(history_frame, height=10,  # Reduced height
                                   font=('Courier', 12), bg='#002200', fg='white')
        self.history_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add scrollbar to history
        scrollbar = tk.Scrollbar(self.history_text, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
        
        # Initialize history with header
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"{'Player':<10} {'Bid':<10}\n")
        self.history_text.insert(tk.END, "-" * 20 + "\n")
        self.history_text.config(state=tk.DISABLED)
    
    def _create_bidding_grid(self):
        """Create the grid of bid buttons (7 levels × 5 denominations)."""
        # Frame for the bidding grid
        grid_frame = tk.Frame(self.bid_frame, bg='darkgreen')
        grid_frame.pack(pady=10)
        
        # Store bid buttons for later enabling/disabling
        self.bid_buttons = {}
        
        # Create column headers (denominations)
        for col, denom in enumerate(['♣', '♦', '♥', '♠', 'NT']):
            label = tk.Label(grid_frame, text=denom, font=('Arial', 14, 'bold'),
                           fg=self.SUIT_COLORS[denom], bg='darkgreen')
            label.grid(row=0, column=col+1, padx=5, pady=5)
        
        # Create row headers (levels) and buttons
        for row in range(7):
            level = 7 - row  # Start with 7 at the top
            
            # Level label
            level_label = tk.Label(grid_frame, text=str(level), font=('Arial', 14, 'bold'),
                                 fg='white', bg='darkgreen')
            level_label.grid(row=row+1, column=0, padx=10, pady=5)
            
            # Bid buttons for this level
            for col, (letter_denom, symbol_denom) in enumerate(zip(['C', 'D', 'H', 'S', 'NT'], 
                                                                 ['♣', '♦', '♥', '♠', 'NT'])):
                bid_text = f"{level}{symbol_denom}"
                button = tk.Button(grid_frame, text=bid_text, width=4, height=1,
                                 font=('Arial', 12),
                                 fg=self.SUIT_COLORS[symbol_denom],
                                 command=lambda l=level, d=letter_denom: self._on_bid_click(l, d))
                button.grid(row=row+1, column=col+1, padx=3, pady=3)
                
                # Store the button for later enabling/disabling
                self.bid_buttons[(level, letter_denom)] = button
    
    def _create_special_bid_buttons(self):
        """Create the Pass, Double, and Redouble buttons."""
        special_frame = tk.Frame(self.bid_frame, bg='darkgreen')
        special_frame.pack(pady=15)
        
        # Pass button
        self.pass_button = tk.Button(special_frame, text="Pass", width=10, height=2,
                                  font=('Arial', 12, 'bold'), bg='#CCFFCC', fg='green',
                                  command=lambda: self._on_special_bid_click("Pass"))
        self.pass_button.pack(side=tk.LEFT, padx=10)
        
        # Double button
        self.double_button = tk.Button(special_frame, text="Double", width=10, height=2,
                                    font=('Arial', 12, 'bold'), bg='#FFCCCC', fg='red',
                                    command=lambda: self._on_special_bid_click("Double"))
        self.double_button.pack(side=tk.LEFT, padx=10)
        
        # Redouble button
        self.redouble_button = tk.Button(special_frame, text="Redouble", width=10, height=2,
                                      font=('Arial', 12, 'bold'), bg='#CCCCFF', fg='blue',
                                      command=lambda: self._on_special_bid_click("Redouble"))
        self.redouble_button.pack(side=tk.LEFT, padx=10)
    
    def show(self):
        """Show the bidding box and start the bidding phase."""
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Reset bidding history
        self.clear_history()
        
        # Update current bidder display
        self.update_current_bidder()
        
        # Update button states
        self.update_button_states()
    
    def hide(self):
        """Hide the bidding box."""
        self.pack_forget()
    
    def clear_history(self):
        """Clear the bidding history display."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.insert(tk.END, f"{'Player':<10} {'Bid':<10}\n")
        self.history_text.insert(tk.END, "-" * 20 + "\n")
        self.history_text.config(state=tk.DISABLED)
    
    def update_history(self):
        """Update the bidding history display with the current bidding sequence."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        # Add header
        self.history_text.insert(tk.END, f"{'Player':<10} {'Bid':<10}\n")
        self.history_text.insert(tk.END, "-" * 20 + "\n")
        
        # Add each bid with color coding
        for entry in self.game.bidding_history:
            player_idx = entry["player"]
            player_name = self.POSITIONS[player_idx]
            bid_str = str(entry["bid"])
            
            # Determine color based on player position
            if player_idx in [0, 2]:  # North-South
                text_color = "lightblue"
            else:  # East-West
                text_color = "lightgreen"
            
            # Insert player name
            self.history_text.insert(tk.END, f"{player_name:<10} ", (f"p{player_idx}",))
            
            # Insert bid with appropriate color for suit symbols
            if len(bid_str) >= 2 and bid_str[1] in "♣♦♥♠":
                # Split the bid into level and denomination
                level = bid_str[0]
                denom = bid_str[1]
                
                # Insert level
                self.history_text.insert(tk.END, level)
                
                # Insert denomination with appropriate color
                if denom == "♣":
                    self.history_text.insert(tk.END, denom, ("club",))
                elif denom == "♦":
                    self.history_text.insert(tk.END, denom, ("diamond",))
                elif denom == "♥":
                    self.history_text.insert(tk.END, denom, ("heart",))
                elif denom == "♠":
                    self.history_text.insert(tk.END, denom, ("spade",))
                
                # Add newline
                self.history_text.insert(tk.END, "\n")
            else:
                # For Pass, Double, Redouble, or NT bids
                self.history_text.insert(tk.END, f"{bid_str}\n")
        
        # Configure text tags for colors
        self.history_text.tag_configure("p0", foreground="lightblue")
        self.history_text.tag_configure("p1", foreground="lightgreen")
        self.history_text.tag_configure("p2", foreground="lightblue")
        self.history_text.tag_configure("p3", foreground="lightgreen")
        
        self.history_text.tag_configure("club", foreground="black")
        self.history_text.tag_configure("diamond", foreground="red")
        self.history_text.tag_configure("heart", foreground="red")
        self.history_text.tag_configure("spade", foreground="black")
        
        self.history_text.config(state=tk.DISABLED)
        
        # Scroll to the bottom
        self.history_text.see(tk.END)
    
    def update_current_bidder(self):
        """Update the current bidder display."""
        current_bidder_idx = self.game.current_bidder
        player_name = self.POSITIONS[current_bidder_idx]
        
        self.current_bidder_label.config(text=player_name)
        # All players are human, so always use yellow
        self.current_bidder_label.config(fg='yellow')
    
    def update_button_states(self):
        """Enable/disable buttons based on valid bids."""
        valid_bids = self.game.get_valid_bids()
        current_player = self.game.current_bidder
        
        # First disable all buttons
        for button in self.bid_buttons.values():
            button.config(state=tk.DISABLED)
        
        self.pass_button.config(state=tk.DISABLED)
        self.double_button.config(state=tk.DISABLED)
        self.redouble_button.config(state=tk.DISABLED)
        
        # Enable valid bid buttons for current player (all players are human)
        for bid in valid_bids:
            if bid.bid_type == BidType.PASS:
                self.pass_button.config(state=tk.NORMAL)
            elif bid.bid_type == BidType.DOUBLE:
                self.double_button.config(state=tk.NORMAL)
            elif bid.bid_type == BidType.REDOUBLE:
                self.redouble_button.config(state=tk.NORMAL)
            elif bid.bid_type == BidType.NORMAL:
                button_key = (bid.level, bid.denomination)
                if button_key in self.bid_buttons:
                    self.bid_buttons[button_key].config(state=tk.NORMAL)
    
    def _on_bid_click(self, level, denomination):
        """Handle a click on a normal bid button."""
        current_bidder = self.game.current_bidder
        
        self.logger.info(f"Bid button clicked: {level}{denomination}")
        
        # Create a bid and place it
        bid = Bid(BidType.NORMAL, level, denomination)
        success = self.game.place_bid(current_bidder, bid)
        
        if success:
            self.logger.info(f"Bid placed: {bid}")
            
            # Update UI
            self.update_history()
            self.update_current_bidder()
            self.update_button_states()
            
            # Check if bidding is complete
            if self.game.current_state == "playing":
                self.logger.info("Bidding complete")
                self.on_bidding_complete()
        else:
            self.logger.warning(f"Invalid bid: {bid}")
    
    def _on_special_bid_click(self, bid_type):
        """Handle a click on a special bid button (Pass, Double, Redouble)."""
        current_bidder = self.game.current_bidder
        
        self.logger.info(f"Special bid button clicked: {bid_type}")
        
        # Place the bid
        success = self.game.place_bid(current_bidder, bid_type)
        
        if success:
            self.logger.info(f"Special bid placed: {bid_type}")
            
            # Update UI
            self.update_history()
            self.update_current_bidder()
            self.update_button_states()
            
            # Check if bidding is complete
            if self.game.current_state == "playing":
                self.logger.info("Bidding complete")
                self.on_bidding_complete()
        else:
            self.logger.warning(f"Invalid special bid: {bid_type}")
    
    # AI bidding methods removed for human-only play

