"""
Game Module for Bridge Card Game

This module defines the main game logic for the Bridge card game.
"""

from core.deck import Deck
from ai.player import AIPlayer


class BridgeGame:
    """Main game class for Bridge card game."""
    
    def __init__(self):
        """Initialize the game."""
        self.deck = Deck()
        self.players = []
        self.current_player = 0
        self.trick = []
        self.score = {"north-south": 0, "east-west": 0}
        self.contract = None
        self.current_state = "bidding"  # States: bidding, playing, game_over
        self.game_history = []
        
        # Initialize AI players
        self.initialize_players()
    
    def initialize_players(self):
        """Initialize the four players (1 human, 3 AI)."""
        # Player positions: 0=South (human), 1=West, 2=North, 3=East
        self.players = [
            {"name": "Player", "hand": [], "type": "human"},
            {"name": "West", "hand": [], "type": "ai", "ai": AIPlayer("West")},
            {"name": "North", "hand": [], "type": "ai", "ai": AIPlayer("North")},
            {"name": "East", "hand": [], "type": "ai", "ai": AIPlayer("East")}
        ]
    
    def new_game(self):
        """Start a new game."""
        # Reset game state
        self.deck = Deck()
        self.deck.shuffle()
        self.deal_cards()
        self.current_player = 0
        self.trick = []
        self.contract = None
        self.current_state = "bidding"
        self.game_history = []
    
    def deal_cards(self):
        """Deal cards to all players."""
        # Clear existing hands
        for player in self.players:
            player["hand"] = []
        
        # Deal 13 cards to each player
        for _ in range(13):
            for player in self.players:
                player["hand"].append(self.deck.deal_card())
    
    def start_bidding(self):
        """Start the bidding phase."""
        self.current_state = "bidding"
        self.current_player = 0
        # Initialize bidding history
        self.bidding_history = []
    
    def place_bid(self, player_idx, bid):
        """
        Place a bid for the specified player.
        
        Args:
            player_idx: Index of the player making the bid
            bid: The bid being made (e.g., "1NT", "3H", "Pass")
            
        Returns:
            bool: Whether the bid was valid
        """
        if self.current_state != "bidding" or player_idx != self.current_player:
            return False
        
        # Add bid to history
        self.bidding_history.append({"player": player_idx, "bid": bid})
        
        # Check if bidding is complete (4 consecutive passes or after a bid is made)
        if self._is_bidding_complete():
            self._finalize_contract()
            self.current_state = "playing"
        
        # Advance to next player
        self.current_player = (self.current_player + 1) % 4
        return True
    
    def _is_bidding_complete(self):
        """Check if bidding is complete."""
        # If we have less than 4 bids, bidding can't be complete
        if len(self.bidding_history) < 4:
            return False
        
        # Check if last 3 bids are passes and there was at least one non-pass bid
        last_three_passes = all(bid["bid"] == "Pass" for bid in self.bidding_history[-3:])
        has_contract_bid = any(bid["bid"] != "Pass" for bid in self.bidding_history)
        
        return last_three_passes and has_contract_bid
    
    def _finalize_contract(self):
        """Determine the final contract from bidding history."""
        # Find the last non-pass bid
        for bid in reversed(self.bidding_history):
            if bid["bid"] != "Pass":
                self.contract = bid["bid"]
                self.declarer = bid["player"]
                break
    
    def play_card(self, player_idx, card):
        """
        Play a card from the specified player.
        
        Args:
            player_idx: Index of the player playing the card
            card: The card being played
            
        Returns:
            bool: Whether the play was valid
        """
        if self.current_state != "playing" or player_idx != self.current_player:
            return False
        
        # Check if card is in player's hand
        if card not in self.players[player_idx]["hand"]:
            return False
        
        # Check if card follows suit if required
        if not self._is_valid_play(player_idx, card):
            return False
        
        # Remove card from player's hand and add to current trick
        self.players[player_idx]["hand"].remove(card)
        self.trick.append({"player": player_idx, "card": card})
        
        # Record the play in game history
        self.game_history.append({
            "player": player_idx,
            "card": card,
            "trick": len(self.game_history) // 4
        })
        
        # If trick is complete (4 cards), determine winner
        if len(self.trick) == 4:
            winner = self._determine_trick_winner()
            self.current_player = winner
            self.trick = []
            
            # Check if hand is complete
            if not any(player["hand"] for player in self.players):
                self._score_hand()
                self.current_state = "game_over"
        else:
            # Move to next player
            self.current_player = (self.current_player + 1) % 4
        
        return True
    
    def _is_valid_play(self, player_idx, card):
        """Check if the played card follows the rules."""
        # If this is the first card in the trick, any card is valid
        if not self.trick:
            return True
        
        # Get the suit of the first card in the trick
        led_suit = self.trick[0]["card"].suit
        
        # If player has a card of the led suit, they must play it
        player_hand = self.players[player_idx]["hand"]
        has_led_suit = any(c.suit == led_suit for c in player_hand)
        
        # If player has the led suit but played card is not of that suit, invalid
        if has_led_suit and card.suit != led_suit:
            return False
            
        return True
    
    def _determine_trick_winner(self):
        """Determine which player won the current trick."""
        if not self.trick or len(self.trick) != 4:
            return None
            
        trump_suit = None
        if self.contract:
            # Extract trump suit from contract, if any
            if self.contract[-1] in "SHDC":
                trump_suit = self.contract[-1]
        
        # Get the led suit (first card played)
        led_suit = self.trick[0]["card"].suit
        
        # Find highest card of led suit or trump
        highest_value = -1
        winner = None
        
        for play in self.trick:
            card = play["card"]
            
            # If this is a trump and we're not already looking at a trump
            if trump_suit and card.suit == trump_suit and (highest_value == -1 or 
                                                        self.trick[winner]["card"].suit != trump_suit):
                highest_value = card.value
                winner = play["player"]
            # If this is the led suit and we haven't found a trump yet
            elif card.suit == led_suit and (highest_value == -1 or 
                                          self.trick[winner]["card"].suit == led_suit):
                if card.value > highest_value:
                    highest_value = card.value
                    winner = play["player"]
        
        return winner
    
    def _score_hand(self):
        """Calculate the score for the completed hand."""
        # Basic scoring - count tricks won by each partnership
        ns_tricks = 0
        ew_tricks = 0
        
        for i in range(0, len(self.game_history), 4):
            trick = self.game_history[i:i+4]
            if not trick or len(trick) < 4:
                continue
                
            winner = self._determine_trick_winner()
            if winner in

