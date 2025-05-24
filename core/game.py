"""
Game Module for Bridge Card Game

This module defines the main game logic for the Bridge card game.
"""

import logging
from core.deck import Deck

# Set up logger
logger = logging.getLogger("BridgeGame.Core")

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
        self.last_trick_winner = None  # Track the winner of the last trick
        self.last_complete_trick = None  # Store the last complete trick for reference
        
        # Initialize AI players
        self.initialize_players()
    
    def initialize_players(self):
        """Initialize the four players (1 human, 3 simulated)."""
        # Player positions: 0=South (human), 1=West, 2=North, 3=East
        self.players = [
            {"name": "Player", "hand": [], "type": "human"},
            {"name": "West", "hand": [], "type": "simulated"},
            {"name": "North", "hand": [], "type": "simulated"},
            {"name": "East", "hand": [], "type": "simulated"}
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
        self.last_trick_winner = None
    
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
        if self.current_state != "playing":
            return False
            
        # If starting a new trick, only the last trick winner can lead
        # (except for the first trick of the hand)
        if not self.trick and self.last_trick_winner is not None and player_idx != self.last_trick_winner:
            logger.info(f"Invalid lead: Player {player_idx} tried to lead but it's Player {self.last_trick_winner}'s turn to lead")
            return False
            
        # For continuation of trick, must be the current player
        if self.trick and player_idx != self.current_player:
            logger.info(f"Invalid play: Not Player {player_idx}'s turn")
            return False
        
        # Check if card is in player's hand
        if card not in self.players[player_idx]["hand"]:
            return False
        
        # Check if card follows suit if required
        if not self._is_valid_play(player_idx, card):
            logger.info(f"Invalid play: Player {player_idx} tried to play {card} but must follow suit")
            return False
        
        # Remove card from player's hand and add to current trick
        self.players[player_idx]["hand"].remove(card)
        self.trick.append({"player": player_idx, "card": card})
        
        # Log the play
        player_names = ["South", "West", "North", "East"]
        logger.info(f"Player {player_names[player_idx]} played {card}")
        
        # Record the play in game history
        self.game_history.append({
            "player": player_idx,
            "card": card,
            "trick": len(self.game_history) // 4
        })
        
        # If trick is complete (4 cards), determine winner
        if len(self.trick) == 4:
            # Print the complete trick for debugging
            trick_log = [(i, p["player"], p["card"]) for i, p in enumerate(self.trick)]
            logger.info(f"Trick complete: {trick_log}")
            
            winner = self._determine_trick_winner()
            
            # Find the winning card for logging
            winning_play = next(p for p in self.trick if p["player"] == winner)
            logger.info(f"Trick winner: Player {player_names[winner]} with {winning_play['card']}")
            
            self.current_player = winner
            self.last_trick_winner = winner  # Store the trick winner for next lead
            
            # Create a deep copy of the trick before clearing it (for GUI reference)
            self.last_complete_trick = self.trick.copy()
            self.trick = []
            
            logger.info(f"Next lead: Player {player_names[winner]} (trick winner) - current_player and last_trick_winner set to {winner}")
            
            # Check if hand is complete
            if not any(player["hand"] for player in self.players):
                self._score_hand()
                self.current_state = "game_over"
                logger.info("Hand complete - game over")
        else:
            # Move to next player
            self.current_player = (self.current_player + 1) % 4
            logger.info(f"Next player: {player_names[self.current_player]}")
        
        return True
    
    def _is_valid_play(self, player_idx, card):
        """Check if the played card follows the rules."""
        # If this is the first card in the trick, any card is valid
        if not self.trick:
            return True
        
        # Get the suit of the first card in the trick
        led_suit = self.trick[0]["card"].suit
        
        # Check if player has any cards of led suit
        player_hand = self.players[player_idx]["hand"]
        has_led_suit = any(c.suit == led_suit for c in player_hand)
        
        # If player has led suit, they must play it
        if has_led_suit:
            return card.suit == led_suit
            
        # If player has no cards of led suit, they can play anything
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
        
        # First, handle the case with no trumps (focus on this for now)
        if not trump_suit:
            # Find highest card of led suit
            highest_value = -1
            winner = None
            
            # Create a string representation of the trick for debugging
            trick_str = ", ".join([f"Player {p['player']}: {p['card']}" for p in self.trick])
            logger.info(f"Trick to evaluate: {trick_str}")
            logger.info(f"Led suit: {led_suit}")
            
            for i, play in enumerate(self.trick):
                card = play["card"]
                player = play["player"]
                
                # Log each card being evaluated
                logger.info(f"Evaluating card {i+1}/4: {card} from player {player}")
                
                # Only cards of the led suit can win
                if card.suit == led_suit:
                    logger.info(f"Card is led suit ({led_suit})")
                    if highest_value == -1 or card.value > highest_value:
                        highest_value = card.value
                        winner = player
                        logger.info(f"New highest card: {card} from player {player} (value={card.value})")
                else:
                    logger.info(f"Card is not led suit, cannot win: {card}")
            
            # Verify the winner card
            winning_card = self.trick[self.trick.index(next(p for p in self.trick if p["player"] == winner))]["card"]
            
            # Log the winner determination
            logger.info(f"Winner: Player {winner} with highest {led_suit} card: {winning_card} (value={highest_value})")
            return winner
        else:
            # With trumps - to be fully implemented later
            # Find highest trump, or if no trump, highest of led suit
            highest_trump_value = -1
            highest_led_value = -1
            trump_winner = None
            led_suit_winner = None
            
            for play in self.trick:
                card = play["card"]
                player = play["player"]
                
                # Check for trump
                if card.suit == trump_suit:
                    if card.value > highest_trump_value:
                        highest_trump_value = card.value
                        trump_winner = player
                # Check for led suit
                elif card.suit == led_suit:
                    if card.value > highest_led_value:
                        highest_led_value = card.value
                        led_suit_winner = player
            
            # Trump wins if any were played, otherwise highest of led suit
            return trump_winner if trump_winner is not None else led_suit_winner
    
    def _score_hand(self):
        """Calculate the score for the completed hand."""
        # Basic scoring - count tricks won by each partnership
        ns_tricks = 0
        ew_tricks = 0
        
        for i in range(0, len(self.game_history), 4):
            trick = self.game_history[i:i+4]
            if not trick or len(trick) < 4:
                continue
            
            # Extract the winner from the trick data
            # Assuming each trick entry includes a 'winner' field
            # If not, we need to determine the winner using the trick data
            winner = None
            for play in trick:
                if play.get('winner', False):
                    winner = play['player']
                    break
            
            # If winner couldn't be determined from the data, skip this trick
            if winner is None:
                continue
                
            # Count tricks for each partnership
            if winner in [0, 2]:  # South and North (NS partnership)
                ns_tricks += 1
            else:  # West and East (EW partnership)
                ew_tricks += 1
        
        # Calculate final score based on tricks won and contract
        # This can be expanded with more complex bridge scoring rules
        self.scores = {
            'NS': ns_tricks,
            'EW': ew_tricks
        }
        
        return self.scores
