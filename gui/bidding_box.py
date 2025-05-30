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
    
    def __init__(self, parent, game, on_bidding_complete):
        """
        Initialize the BiddingBox.
        
        Args:
            parent: The parent widget
            game: The BridgeGame instance
            on_bidding_complete: Callback function when bidding is complete
        """
        super().__init__(parent, bg='darkgreen')
        
        self.parent = parent
        self.game = game
        self.on_bidding_complete = on_bidding_complete
        
        # Bidding state
        self.ai_thinking = False
        self.ai_bid_job = None
        
        # Create UI components
        self._create_layout()
        
        self.logger.info("BiddingBox initialized")
    
    def _create_layout(self):
        """Create the main layout for the bidding box."""
        # Main container with title
        title_label = tk.Label(self, text="Bidding Phase", 
                              font=('Arial', 16, 'bold'),
                              bg='darkgreen', fg='white')
        title_label.pack(pady=(10, 20))
        
        # Create two columns: bidding grid on left, history on right
        content_frame = tk.Frame(self, bg='darkgreen')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left column - bidding controls
        self.bid_frame = tk.Frame(content_frame, bg='darkgreen')
        self.bid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
        
        # Right column - bidding history
        history_frame = tk.Frame(content_frame, bg='#004400', bd=2, relief=tk.GROOVE)
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(20, 0))
        
        # History title
        tk.Label(history_frame, text="Bidding History", 
                font=('Arial', 14), bg='#004400', fg='white').pack(pady=10)
        
        # Bidding history display
        self.history_text = tk.Text(history_frame, width=30, height=20, 
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
        self.pack(fill=tk.BOTH, expand=True)
        
        # Reset bidding history
        self.clear_history()
        
        # Update current bidder display
        self.update_current_bidder()
        
        # Update button states
        self.update_button_states()
        
        # Start AI bidding if it's an AI's turn
        if self.game.current_bidder != 0:  # Not the human player (South)
            self.schedule_ai_bid()
    
    def hide(self):
        """Hide the bidding box."""
        # Cancel any pending AI bid
        if self.ai_bid_job:
            self.after_cancel(self.ai_bid_job)
            self.ai_bid_job = None
        
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
        
        # Highlight differently for human vs AI
        if current_bidder_idx == 0:  # Human player (South)
            self.current_bidder_label.config(fg='yellow')
        else:  # AI player
            self.current_bidder_label.config(fg='#AAAAFF')  # Light blue
    
    def update_button_states(self):
        """Enable/disable buttons based on valid bids."""
        valid_bids = self.game.get_valid_bids()
        
        # First disable all buttons
        for button in self.bid_buttons.values():
            button.config(state=tk.DISABLED)
        
        self.pass_button.config(state=tk.DISABLED)
        self.double_button.config(state=tk.DISABLED)
        self.redouble_button.config(state=tk.DISABLED)
        
        # If it's not human player's turn, disable all buttons
        if self.game.current_bidder != 0:
            return
        
        # Enable valid bid buttons
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
        if self.game.current_bidder != 0 or self.ai_thinking:
            # Not human player's turn or AI is thinking
            return
        
        self.logger.info(f"Bid button clicked: {level}{denomination}")
        
        # Create a bid and place it
        bid = Bid(BidType.NORMAL, level, denomination)
        success = self.game.place_bid(0, bid)
        
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
                # Schedule AI bid
                self.schedule_ai_bid()
        else:
            self.logger.warning(f"Invalid bid: {bid}")
    
    def _on_special_bid_click(self, bid_type):
        """Handle a click on a special bid button (Pass, Double, Redouble)."""
        if self.game.current_bidder != 0 or self.ai_thinking:
            # Not human player's turn or AI is thinking
            return
        
        self.logger.info(f"Special bid button clicked: {bid_type}")
        
        # Place the bid
        success = self.game.place_bid(0, bid_type)
        
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
                # Schedule AI bid
                self.schedule_ai_bid()
        else:
            self.logger.warning(f"Invalid special bid: {bid_type}")
    
    def schedule_ai_bid(self):
        """Schedule an AI bid after a short delay."""
        if self.game.current_bidder == 0 or self.ai_thinking:
            # Human player's turn or AI is already thinking
            return
        
        self.ai_thinking = True
        
        # Show thinking indicator
        current_bidder_idx = self.game.current_bidder
        player_name = self.POSITIONS[current_bidder_idx]
        self.current_bidder_label.config(text=f"{player_name} (thinking...)")
        
        # Schedule AI bid after delay (simulate thinking)
        delay = 1000  # 1 second
        self.ai_bid_job = self.after(delay, self.make_ai_bid)
    
    def make_ai_bid(self):
        """Make a bid for the current AI player."""
        current_bidder = self.game.current_bidder
        position = self.POSITIONS[current_bidder]
        self.ai_thinking = True
        
        try:
            # Skip if human player
            if current_bidder == 0:  # Human player
                self.ai_thinking = False
                return
                
            self.logger.info(f"AI player {position} is making a bid")
            
            # Import the hand evaluation module
            from core.hand_evaluation import (
                calculate_hcp, 
                count_suit_length, 
                is_balanced,
                evaluate_distribution_points,
                determine_opening_bid,
                determine_response,
                determine_competitive_bid
            )
            
            # Get AI's hand with improved error handling
            try:
                # Direct access to player dictionary
                player = self.game.players[current_bidder]
                
                # Debug log of player data structure
                self.logger.info(f"Player type: {type(player)}")
                self.logger.info(f"Player data: {player}")
                
                # Access hand directly
                hand = player["hand"]
                
                if not hand:
                    self.logger.error(f"Empty hand for {position}")
                    self.logger.info(f"Player data: {player}")
                    raise ValueError(f"Empty hand list for {position}")
                
                # Log found cards for verification
                self.logger.info(f"Successfully found {len(hand)} cards for {position}")
                
                # Additional debug - print first few cards
                card_sample = ', '.join(str(card) for card in hand[:3]) + "..." if hand else "None"
                self.logger.info(f"Card sample: {card_sample}")
            except KeyError as ke:
                self.logger.error(f"KeyError accessing hand: {ke}")
                self.logger.error(f"Game players structure: {self.game.players}")
                raise ValueError(f"Cannot access hand for {position}: {ke}")
            except Exception as e:
                self.logger.error(f"Error accessing hand: {e}")
                raise ValueError(f"Hand access error for {position}: {e}")
            
            # Evaluate hand
            hcp = calculate_hcp(hand)
            suit_lengths = count_suit_length(hand)
            balanced = is_balanced(suit_lengths)
            dist_points = evaluate_distribution_points(suit_lengths)
            total_points = hcp + dist_points
            
            # Log hand details for debugging
            sorted_hand = sorted(hand, key=lambda c: (c.suit, -c.value))
            card_str = ", ".join(f"{card.value_name}{card.suit}" for card in sorted_hand)
            dist_str = f"♠{suit_lengths['S']} ♥{suit_lengths['H']} ♦{suit_lengths['D']} ♣{suit_lengths['C']}"
            pattern = "-".join(str(count) for count in sorted(suit_lengths.values(), reverse=True))
            
            self.logger.info(f"AI {position} cards: {card_str}")
            self.logger.info(f"HCP: {hcp}, Total points: {total_points}, Distribution: {dist_str}, Pattern: {pattern}, Balanced: {balanced}")
            
            # Get valid bids
            valid_bids = self.game.get_valid_bids()
            valid_bid_strs = [str(bid) for bid in valid_bids]
            self.logger.info(f"Valid bids: {', '.join(valid_bid_strs)}")
            
            # Analyze bidding context
            partner_idx = (current_bidder + 2) % 4  # Partner sits across
            partner_bid = "Pass"
            right_opponent_bid = "Pass"
            left_opponent_bid = "Pass"
            
            # Extract previous bids
            recent_bids = []
            for entry in reversed(self.game.bidding_history):
                player_idx = entry["player"]
                bid_str = str(entry["bid"])
                position_name = self.POSITIONS[player_idx]
                recent_bids.append(f"{position_name}: {bid_str}")
                
                if player_idx == partner_idx and partner_bid == "Pass":
                    partner_bid = bid_str
                elif player_idx == (current_bidder + 1) % 4 and right_opponent_bid == "Pass":
                    right_opponent_bid = bid_str
                elif player_idx == (current_bidder + 3) % 4 and left_opponent_bid == "Pass":
                    left_opponent_bid = bid_str
            
            # Determine the auction type
            opening_auction = all(
                isinstance(entry["bid"], Bid) and entry["bid"].bid_type == BidType.PASS 
                for entry in self.game.bidding_history
            )
            
            if recent_bids:
                self.logger.info(f"Recent bids (newest first): {', '.join(recent_bids[:4])}")
            self.logger.info(f"Bidding context - Opening: {opening_auction}, Partner: {partner_bid}, Opponents: {left_opponent_bid}/{right_opponent_bid}")
            
            # Make bidding decision based on hand evaluation and auction context
            bid_str = "Pass"  # Default to Pass
            explanation = "Default pass"
            
            if opening_auction:
                # This is an opening bid
                bid_str, explanation = determine_opening_bid(hand)
                self.logger.info(f"Opening decision: {bid_str} ({explanation})")
                
                # Enhanced opening logic for borderline hands
                if bid_str == "Pass" and total_points >= 11:
                    # Light opening with shape
                    if suit_lengths['S'] >= 5:
                        bid_str = "1S"
                        explanation = f"Light opening with {hcp} HCP + {dist_points} distribution points and 5+ spades"
                    elif suit_lengths['H'] >= 5:
                        bid_str = "1H"
                        explanation = f"Light opening with {hcp} HCP + {dist_points} distribution points and 5+ hearts"
            
            elif partner_bid != "Pass" and partner_bid not in ["Double", "Redouble"]:
                # Responding to partner's bid
                bid_str, explanation = determine_response(hand, partner_bid, right_opponent_bid)
                self.logger.info(f"Response decision: {bid_str} ({explanation})")
                
                # Enhanced response logic for borderline hands
                if bid_str == "Pass" and hcp >= 6:
                    if partner_bid[1] in "SH" and suit_lengths[partner_bid[1]] >= 3:
                        # Support partner's major with 3+ cards
                        bid_str = f"2{partner_bid[1]}"
                        explanation = f"Support with {hcp} HCP and {suit_lengths[partner_bid[1]]} cards"
                    elif partner_bid[0] == "1" and balanced and 6 <= hcp <= 10:
                        # Standard 1NT response with balanced hand
                        bid_str = "1NT"
                        explanation = f"Balanced hand with {hcp} HCP"
            
            elif left_opponent_bid != "Pass" or right_opponent_bid != "Pass":
                # Competitive auction
                opponent_bid = right_opponent_bid if right_opponent_bid != "Pass" else left_opponent_bid
                bid_str, explanation = determine_competitive_bid(hand, partner_bid, opponent_bid)
                self.logger.info(f"Competitive decision: {bid_str} ({explanation})")
                
                # Enhanced competitive logic
                if bid_str == "Pass" and hcp >= 8:
                    # Consider overcalling with good suit
                    for suit in "SHDC":
                        if suit_lengths[suit] >= 5 and opponent_bid[0] == "1":
                            bid_str = f"1{suit}" if suit in "SH" and opponent_bid[1] not in suit else f"2{suit}"
                            explanation = f"Competitive overcall with {hcp} HCP and 5+ {suit}"
                            break
            
            else:
                # Default to Pass if no context matches
                bid_str = "Pass"
                explanation = "No appropriate context"
            
            # Validate that the bid is actually allowed
            if bid_str != "Pass" and bid_str not in valid_bid_strs:
                self.logger.warning(f"Selected bid {bid_str} not valid in current auction")
                bid_str = "Pass"  # Default to Pass if invalid
                explanation += " (defaulted to Pass - invalid bid)"
            
            self.logger.info(f"FINAL DECISION: {bid_str} - {explanation}")
            
            # Find the corresponding Bid object
            selected_bid = None
            for bid in valid_bids:
                if str(bid) == bid_str:
                    selected_bid = bid
                    break
            
            # Default to Pass if no matching bid found
            if not selected_bid:
                for bid in valid_bids:
                    if bid.bid_type == BidType.PASS:
                        selected_bid = bid
                        break
            
            # Place the bid
            if selected_bid:
                success = self.game.place_bid(current_bidder, selected_bid)
                
                if success:
                    self.logger.info(f"AI bid placed: {selected_bid} - {explanation}")
                    
                    # Update UI
                    self.update_history()
                    self.update_current_bidder()
                    self.update_button_states()
                    
                    # Check if bidding is complete
                    if self.game.current_state == "playing":
                        self.logger.info("Bidding complete")
                        self.on_bidding_complete()
                    else:
                        # Schedule next AI bid if needed
                        self.ai_thinking = False
                        if self.game.current_bidder != 0:
                            self.schedule_ai_bid()
                else:
                    self.logger.error(f"AI bid failed: {selected_bid}")
                    self._emergency_pass(current_bidder)
            else:
                self.logger.error("No valid bid found for AI")
                self._emergency_pass(current_bidder)
                
        except Exception as e:
            self.logger.error(f"Error in AI bidding: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._emergency_pass(current_bidder)
        
        finally:
            self.ai_thinking = False
            self.ai_bid_job = None
    
    def _emergency_pass(self, player_idx):
        """Emergency fallback to place a Pass bid when normal bidding fails."""
        try:
            self.logger.info(f"Emergency Pass for player {self.POSITIONS[player_idx]}")
            
            # Find Pass bid
            pass_bid = None
            for bid in self.game.get_valid_bids():
                if bid.bid_type == BidType.PASS:
                    pass_bid = bid
                    break
            
            if pass_bid:
                success = self.game.place_bid(player_idx, pass_bid)
                if success:
                    self.logger.info("Emergency Pass bid placed successfully")
                    self.update_history()
                    self.update_current_bidder()
                    self.update_button_states()
                    
                    # Check if bidding is complete
                    if self.game.current_state == "playing":
                        self.ai_thinking = False
                        self.on_bidding_complete()
                    else:
                        # If it's another AI's turn, schedule next AI bid
                        self.ai_thinking = False
                        if self.game.current_bidder != 0:
                            self.schedule_ai_bid()
                else:
                    self.logger.error("Emergency Pass bid failed")
            else:
                self.logger.error("Could not find Pass bid in valid bids")
        except Exception as e:
            self.logger.error(f"Emergency Pass recovery failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

