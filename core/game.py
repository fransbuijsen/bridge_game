"""
Game Module for Bridge Card Game

This module defines the main game logic for the Bridge card game.
"""

import logging
from enum import Enum, auto
from typing import List, Dict, Optional, Union, Tuple
from core.deck import Deck, Card

# Set up logger
logger = logging.getLogger("BridgeGame.Core")

class BidType(Enum):
    """Types of bids that can be made in bridge."""
    PASS = auto()
    NORMAL = auto()
    DOUBLE = auto()
    REDOUBLE = auto()

class Vulnerability(Enum):
    """Vulnerability states in bridge."""
    NONE = auto()
    NS = auto()
    EW = auto()
    BOTH = auto()

class Bid:
    """Representation of a bridge bid."""
    
    # Class constants for denominations
    DENOMINATIONS = {
        'C': {'name': 'Clubs', 'symbol': '♣', 'rank': 1},
        'D': {'name': 'Diamonds', 'symbol': '♦', 'rank': 2},
        'H': {'name': 'Hearts', 'symbol': '♥', 'rank': 3},
        'S': {'name': 'Spades', 'symbol': '♠', 'rank': 4},
        'NT': {'name': 'No Trump', 'symbol': 'NT', 'rank': 5}
    }
    
    def __init__(self, bid_type: BidType, level: int = None, denomination: str = None):
        """
        Initialize a bid.
        
        Args:
            bid_type: The type of bid (PASS, NORMAL, DOUBLE, REDOUBLE)
            level: The level of the bid (1-7) - required for NORMAL bids
            denomination: The denomination of the bid (C, D, H, S, NT) - required for NORMAL bids
        """
        self.bid_type = bid_type
        self.level = level
        self.denomination = denomination
        
        # Validate inputs
        if bid_type == BidType.NORMAL:
            if level is None or denomination is None:
                raise ValueError("Normal bids require both level and denomination")
            if level < 1 or level > 7:
                raise ValueError(f"Bid level must be between 1 and 7, got {level}")
            if denomination not in self.DENOMINATIONS:
                raise ValueError(f"Invalid denomination: {denomination}")
        elif bid_type != BidType.PASS and (level is not None or denomination is not None):
            logger.warning(f"Level and denomination ignored for {bid_type} bid")
    
    def __str__(self) -> str:
        """Return string representation of bid."""
        if self.bid_type == BidType.PASS:
            return "Pass"
        elif self.bid_type == BidType.DOUBLE:
            return "Double"
        elif self.bid_type == BidType.REDOUBLE:
            return "Redouble"
        else:  # NORMAL
            denom_symbol = self.DENOMINATIONS[self.denomination]['symbol']
            return f"{self.level}{denom_symbol}"
    
    def __repr__(self) -> str:
        """Return representation of bid."""
        if self.bid_type == BidType.PASS:
            return "Bid(BidType.PASS)"
        elif self.bid_type == BidType.DOUBLE:
            return "Bid(BidType.DOUBLE)"
        elif self.bid_type == BidType.REDOUBLE:
            return "Bid(BidType.REDOUBLE)"
        else:  # NORMAL
            return f"Bid(BidType.NORMAL, {self.level}, '{self.denomination}')"
    
    def __eq__(self, other) -> bool:
        """Compare bids for equality."""
        if not isinstance(other, Bid):
            return NotImplemented
        
        if self.bid_type != other.bid_type:
            return False
        
        if self.bid_type == BidType.NORMAL:
            return self.level == other.level and self.denomination == other.denomination
        
        return True  # Pass, Double, Redouble are equal to themselves
    
    def __lt__(self, other) -> bool:
        """Compare bids for less than."""
        if not isinstance(other, Bid):
            return NotImplemented
        
        # Pass is less than any other bid
        if self.bid_type == BidType.PASS:
            return other.bid_type != BidType.PASS
        
        # Double and Redouble are special cases
        if self.bid_type == BidType.DOUBLE or self.bid_type == BidType.REDOUBLE:
            # These aren't directly comparable to normal bids
            # but for completeness: Double < Redouble
            if other.bid_type == BidType.REDOUBLE:
                return self.bid_type == BidType.DOUBLE
            return False
        
        # Normal bid comparison
        if other.bid_type == BidType.NORMAL:
            # Compare levels first
            if self.level < other.level:
                return True
            if self.level > other.level:
                return False
            
            # Same level, compare denominations
            return self.DENOMINATIONS[self.denomination]['rank'] < self.DENOMINATIONS[other.denomination]['rank']
        
        # Normal bids are higher than Pass, but not directly comparable to Double/Redouble
        return False
    
    def __gt__(self, other) -> bool:
        """Compare bids for greater than."""
        if not isinstance(other, Bid):
            return NotImplemented
        
        return other < self and not self == other
    
    def get_rank(self) -> int:
        """
        Get the absolute rank of this bid for comparison.
        
        Returns:
            int: A number representing the bid's rank (higher = stronger bid)
                 Pass = 0
                 Normal bids = (level * 5) + denomination_rank
                 Double and Redouble are special cases and not included
        """
        if self.bid_type == BidType.PASS:
            return 0
        elif self.bid_type == BidType.NORMAL:
            denom_rank = self.DENOMINATIONS[self.denomination]['rank']
            return (self.level * 5) + denom_rank
        
        # Double and Redouble don't have a natural rank in this system
        return -1
    
    @classmethod
    def from_string(cls, bid_str: str) -> 'Bid':
        """
        Create a Bid object from a string representation.
        
        Args:
            bid_str: String representation of a bid (e.g., "1NT", "Pass", "Double")
            
        Returns:
            Bid: A new Bid object
        """
        bid_str = bid_str.strip()
        
        if bid_str.lower() == "pass":
            return cls(BidType.PASS)
        elif bid_str.lower() == "double":
            return cls(BidType.DOUBLE)
        elif bid_str.lower() == "redouble":
            return cls(BidType.REDOUBLE)
        else:
            # Normal bid like "1NT" or "3H"
            if len(bid_str) < 2:
                raise ValueError(f"Invalid bid string: {bid_str}")
            
            # Extract level and denomination
            level = int(bid_str[0])
            
            if bid_str[1:] == "NT":
                denomination = "NT"
            elif bid_str[1] in "CDHS":
                denomination = bid_str[1]
            else:
                # Try to convert symbols to letters
                symbol_to_letter = {'♣': 'C', '♦': 'D', '♥': 'H', '♠': 'S'}
                if bid_str[1] in symbol_to_letter:
                    denomination = symbol_to_letter[bid_str[1]]
                else:
                    raise ValueError(f"Invalid denomination in bid: {bid_str}")
            
            return cls(BidType.NORMAL, level, denomination)

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
        
        # Bidding-related fields
        self.bidding_history = []        # List of all bids made
        self.current_bidder = 0          # Player who is currently bidding
        self.last_bid = None             # Last non-pass bid made
        self.double_status = "none"      # none, doubled, redoubled
        self.vulnerability = Vulnerability.NONE  # Vulnerability state
        self.declarer = None             # Player who will play the hand
        self.dummy = None                # Partner of declarer who will be the dummy
        
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
        # Ensure players are initialized
        if not self.players or len(self.players) != 4:
            logger.info("Initializing players")
            self.initialize_players()
        
        # Reset game state
        self.deck = Deck()
        self.deck.shuffle()
        
        logger.info("Dealing cards for new game")
        # Deal cards
        self.deal_cards()
        
        # Log player hands for debugging
        for i, player in enumerate(self.players):
            cards_count = len(player["hand"])
            if cards_count != 13:
                logger.error(f"Player {i} has {cards_count} cards instead of 13!")
            
            hand_str = ", ".join(str(card) for card in sorted(player["hand"], key=lambda c: (c.suit, -c.value)))
            logger.info(f"Player {i} hand: {hand_str}")
        
        self.current_player = 0
        self.trick = []
        self.contract = None
        self.current_state = "bidding"
        self.game_history = []
        self.last_trick_winner = None
        
        # Reset bidding-related fields
        self.bidding_history = []
        self.current_bidder = 0  # Dealer starts bidding
        self.last_bid = None
        self.double_status = "none"
        
        # Log the state of the game
        logger.info(f"New game started - Current state: {self.current_state}, Current bidder: {self.current_bidder}")
        total_cards = sum(len(player["hand"]) for player in self.players)
        logger.info(f"Total cards dealt: {total_cards} (expected: 52)")
        
        # Note: vulnerability should be updated between hands based on score
    
    def deal_cards(self):
        """Deal cards to all players."""
        # Reset the deck with a completely new deck to ensure no issues
        self.deck = Deck()
        self.deck.shuffle()
        
        logger.info("Dealing new cards to all players")
        logger.info(f"Deck size before dealing: {len(self.deck.cards)}")
        
        # Clear existing hands
        for player in self.players:
            player["hand"] = []
        
        # Verify player array is initialized correctly
        if len(self.players) != 4:
            logger.error(f"Invalid number of players: {len(self.players)}")
            self.initialize_players()
        
        # Deal all 52 cards (13 to each player)
        dealt_cards = 0
        for player_idx in range(4):  # Ensure we go through players in order
            for _ in range(13):  # Each player gets 13 cards
                if len(self.deck.cards) == 0:
                    logger.error("Deck is empty before dealing all cards!")
                    break
                
                card = self.deck.deal_card()
                if card is None:
                    logger.error(f"Deck returned None when dealing card {dealt_cards+1}!")
                    break
                
                self.players[player_idx]["hand"].append(card)
                dealt_cards += 1
                
        logger.info(f"Total cards dealt: {dealt_cards}")
        logger.info(f"Deck size after dealing: {len(self.deck.cards)}")
        
        # Verify correct distribution
        total_cards = 0
        for player_idx, player in enumerate(self.players):
            hand_size = len(player["hand"])
            total_cards += hand_size
            if hand_size != 13:
                logger.warning(f"Player {player_idx} has {hand_size} cards instead of 13!")
        
        if total_cards != 52:
            logger.error(f"Total cards dealt: {total_cards}, expected 52!")
            
        # Log the hands for debugging
        for player_idx, player in enumerate(self.players):
            try:
                # Sort cards for more readable output
                sorted_hand = sorted(player["hand"], key=lambda c: (c.suit, -c.value))
                card_strs = [f"{card.value_name}{card.suit}" for card in sorted_hand]
                hand_str = ", ".join(card_strs)
                logger.info(f"Player {player_idx} was dealt: {hand_str}")
                
                # Log high card points for each hand
                from core.hand_evaluation import calculate_hcp, count_suit_length
                hcp = calculate_hcp(player["hand"])
                suit_lengths = count_suit_length(player["hand"])
                logger.info(f"Player {player_idx} hand - HCP: {hcp}, Distribution: {suit_lengths}")
            except Exception as e:
                logger.error(f"Error logging hand for player {player_idx}: {e}")
                logger.error(f"Raw hand: {player['hand']}")
    
    def start_bidding(self):
        """Start the bidding phase."""
        self.current_state = "bidding"
        self.current_bidder = 0  # South starts as dealer
        self.current_player = self.current_bidder  # Set current player to bidder
        self.bidding_history = []
        self.last_bid = None
        self.double_status = "none"
    
    def place_bid(self, player_idx: int, bid: Union[Bid, str]) -> bool:
        """
        Place a bid for the specified player.
        
        Args:
            player_idx: Index of the player making the bid
            bid: The bid being made, either a Bid object or a string (e.g., "1NT", "3H", "Pass")
            
        Returns:
            bool: Whether the bid was valid
        """
        if self.current_state != "bidding" or player_idx != self.current_bidder:
            logger.warning(f"Invalid bid attempt: wrong state or player. Current state: {self.current_state}, Expected player: {self.current_bidder}, Actual player: {player_idx}")
            return False
        
        # Convert string to Bid object if needed
        if isinstance(bid, str):
            try:
                bid = Bid.from_string(bid)
            except ValueError as e:
                logger.error(f"Invalid bid string: {str(e)}")
                return False
        
        # Check if the bid is valid in the current bidding sequence
        if not self.is_valid_bid(bid):
            logger.warning(f"Invalid bid: {bid} is not allowed in the current bidding sequence")
            return False
        
        # Update bidding state
        self.bidding_history.append({"player": player_idx, "bid": bid})
        
        # Update last_bid and double status if needed
        if bid.bid_type == BidType.NORMAL:
            self.last_bid = bid
            self.double_status = "none"
        elif bid.bid_type == BidType.DOUBLE:
            self.double_status = "doubled"
        elif bid.bid_type == BidType.REDOUBLE:
            self.double_status = "redoubled"
        
        # Check if bidding is complete
        if self._is_bidding_complete():
            self._finalize_contract()
            self.current_state = "playing"
        
        # Advance to next player
        self.current_bidder = (self.current_bidder + 1) % 4
        self.current_player = self.current_bidder  # Keep current_player in sync during bidding
        
        logger.info(f"Bid placed: Player {player_idx} bid {bid}")
        return True
    
    def is_valid_bid(self, bid: Bid) -> bool:
        """
        Check if a bid is valid in the current bidding sequence.
        
        Args:
            bid: The bid to check
            
        Returns:
            bool: Whether the bid is valid
        """
        # Pass is always valid
        if bid.bid_type == BidType.PASS:
            return True
        
        # Double is valid only if the last non-pass bid was made by an opponent
        # and it has not been doubled already
        if bid.bid_type == BidType.DOUBLE:
            if not self.last_bid:
                return False  # No bid to double
            
            # Find the player who made the last non-pass bid
            last_bidder = None
            for entry in reversed(self.bidding_history):
                if isinstance(entry["bid"], Bid) and entry["bid"].bid_type == BidType.NORMAL:
                    last_bidder = entry["player"]
                    break
            
            if last_bidder is None:
                return False  # No bid to double
            
            # Check if last bidder is an opponent
            current_partnership = self.current_bidder % 2
            last_bidder_partnership = last_bidder % 2
            
            if current_partnership == last_bidder_partnership:
                return False  # Can't double partner's bid
            
            # Check if already doubled
            return self.double_status == "none"
        
        # Redouble is valid only if the last non-pass bid was made by the current
        # partnership and it has been doubled by the opponents
        if bid.bid_type == BidType.REDOUBLE:
            if self.double_status != "doubled":
                return False  # Not doubled, can't redouble
            
            # Find the player who made the last non-pass bid
            last_bidder = None
            for entry in reversed(self.bidding_history):
                if isinstance(entry["bid"], Bid) and entry["bid"].bid_type == BidType.NORMAL:
                    last_bidder = entry["player"]
                    break
            
            if last_bidder is None:
                return False
            
            # Check if last bidder is from the same partnership
            current_partnership = self.current_bidder % 2
            last_bidder_partnership = last_bidder % 2
            
            return current_partnership == last_bidder_partnership
        
        # For normal bids, it must be higher than the last bid
        if self.last_bid:
            return bid > self.last_bid
        
        # First bid is always valid
        return True
    
    def get_valid_bids(self) -> List[Bid]:
        """
        Get a list of all valid bids for the current bidding situation.
        
        Returns:
            List[Bid]: List of valid Bid objects
        """
        valid_bids = [Bid(BidType.PASS)]  # Pass is always valid
        
        # Check if double is valid
        if self.last_bid and self.double_status == "none":
            # Find the player who made the last non-pass bid
            last_bidder = None
            for entry in reversed(self.bidding_history):
                if isinstance(entry["bid"], Bid) and entry["bid"].bid_type == BidType.NORMAL:
                    last_bidder = entry["player"]
                    break
            
            if last_bidder is not None:
                # Check if last bidder is an opponent
                current_partnership = self.current_bidder % 2
                last_bidder_partnership = last_bidder % 2
                
                if current_partnership != last_bidder_partnership:
                    valid_bids.append(Bid(BidType.DOUBLE))
        
        # Check if redouble is valid
        if self.double_status == "doubled":
            # Find the player who made the last non-pass bid
            last_bidder = None
            for entry in reversed(self.bidding_history):
                if isinstance(entry["bid"], Bid) and entry["bid"].bid_type == BidType.NORMAL:
                    last_bidder = entry["player"]
                    break
            
            if last_bidder is not None:
                # Check if last bidder is from the same partnership
                current_partnership = self.current_bidder % 2
                last_bidder_partnership = last_bidder % 2
                
                if current_partnership == last_bidder_partnership:
                    valid_bids.append(Bid(BidType.REDOUBLE))
        
        # Add all valid normal bids
        for level in range(1, 8):
            for denom in ['C', 'D', 'H', 'S', 'NT']:
                bid = Bid(BidType.NORMAL, level, denom)
                if not self.last_bid or bid > self.last_bid:
                    valid_bids.append(bid)
        
        return valid_bids
    
    def _is_bidding_complete(self) -> bool:
        """
        Check if bidding is complete.
        
        Returns:
            bool: Whether bidding is complete
        """
        # If we have less than 4 bids, bidding can't be complete
        if len(self.bidding_history) < 4:
            return False
        
        # Check if first round of bidding and all passes
        if len(self.bidding_history) == 4 and all(
            entry["bid"].bid_type == BidType.PASS for entry in self.bidding_history
        ):
            logger.info("Bidding complete: All players passed")
            return True
        
        # Check if last 3 bids are passes and there was at least one non-pass bid
        last_three_passes = all(
            entry["bid"].bid_type == BidType.PASS 
            for entry in self.bidding_history[-3:]
        )
        
        has_contract_bid = any(
            entry["bid"].bid_type != BidType.PASS 
            for entry in self.bidding_history
        )
        
        if last_three_passes and has_contract_bid:
            logger.info("Bidding complete: Last three bids were passes after a contract bid")
            return True
        
        return False
    
    def _finalize_contract(self) -> None:
        """Determine the final contract, declarer, and dummy from bidding history."""
        # Default: no contract (all passed)
        self.contract = None
        self.declarer = None
        self.dummy = None
        
        # Check if everyone passed
        if all(entry["bid"].bid_type == BidType.PASS for entry in self.bidding_history):
            logger.info("All players passed - no contract")
            return
        
        # Find the last non-pass bid (should be a normal bid)
        last_normal_bid = None
        last_normal_bidder = None
        
        for entry in reversed(self.bidding_history):
            if entry["bid"].bid_type == BidType.NORMAL:
                last_normal_bid = entry["bid"]
                last_normal_bidder = entry["player"]
                break
        
        if not last_normal_bid:
            logger.error("No normal bid found in bidding history")
            return
        
        # Determine the strain (denomination) of the contract
        strain = last_normal_bid.denomination
        
        # Determine the level
        level = last_normal_bid.level
        
        # Determine if the contract is doubled or redoubled
        contract_suffix = ""
        if self.double_status == "doubled":
            contract_suffix = "X"
        elif self.double_status == "redoubled":
            contract_suffix = "XX"
        
        # Create the contract string
        contract_str = f"{level}{strain}{contract_suffix}"
        
        # Find the declarer: first player of the partnership who bid the strain
        partnership = last_normal_bidder % 2  # 0 for N-S, 1 for E-W
        strain_bidders = []
        
        for entry in self.bidding_history:
            if (entry["player"] % 2 == partnership and  # Same partnership
                isinstance(entry["bid"], Bid) and
                entry["bid"].bid_type == BidType.NORMAL and
                entry["bid"].denomination == strain):
                strain_bidders.append(entry["player"])
        
        declarer = strain_bidders[0] if strain_bidders else last_normal_bidder
        
        # Determine dummy (partner of declarer)
        dummy = (declarer + 2) % 4
        
        # Set the game state
        self.contract = contract_str
        self.declarer = declarer
        self.dummy = dummy
        
        # The declarer's LHO (left-hand opponent) leads to the first trick
        self.current_player = (declarer + 1) % 4
        
        logger.info(f"Contract finalized: {contract_str}")
        logger.info(f"Declarer: Player {declarer} ({['South', 'West', 'North', 'East'][declarer]})")
        logger.info(f"Dummy: Player {dummy} ({['South', 'West', 'North', 'East'][dummy]})")
        logger.info(f"First lead: Player {self.current_player} ({['South', 'West', 'North', 'East'][self.current_player]})")
    
    def determine_final_contract(self) -> str:
        """
        Get the final contract as a formatted string.
        
        Returns:
            str: The contract (e.g., "3NT", "4♠X", "Pass")
        """
        if not self.contract:
            return "Pass"
        
        # Replace denomination letter with symbol for display
        if self.contract and len(self.contract) >= 2:
            level = self.contract[0]
            denom = self.contract[1]
            
            if denom in "CDHS":
                symbol = {"C": "♣", "D": "♦", "H": "♥", "S": "♠"}[denom]
                return level + symbol + self.contract[2:]
        
        return self.contract
    
    def determine_declarer(self) -> Optional[int]:
        """
        Get the index of the declarer.
        
        Returns:
            Optional[int]: The player index of the declarer, or None if no contract
        """
        return self.declarer
    
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
            if len(self.contract) >= 2 and self.contract[1] in "SHDC":
                trump_suit = self.contract[1]
            # Check for contract ending with X (doubled) or XX (redoubled)
            elif len(self.contract) >= 3 and self.contract[1] in "SHDC" and self.contract[2] in "X":
                trump_suit = self.contract[1]
        
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
