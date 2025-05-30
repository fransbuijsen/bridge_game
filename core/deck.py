"""
Deck module for Bridge card game.

This module defines the Card and Deck classes for a standard 52-card deck.
"""

import random
import logging
from typing import List, Optional

# Set up logger
logger = logging.getLogger("BridgeGame.Core.Deck")

class Card:
    """
    Card class representing a playing card.
    
    Attributes:
        suit: The suit of the card (S, H, D, C)
        value: The value of the card (2-14, where 14 is Ace)
    """
    
    # Constants for card values
    ACE = 14
    KING = 13
    QUEEN = 12
    JACK = 11
    
    # Map of value to name
    VALUE_NAMES = {
        14: 'A',
        13: 'K',
        12: 'Q',
        11: 'J',
        10: '10',
        9: '9',
        8: '8',
        7: '7',
        6: '6',
        5: '5',
        4: '4',
        3: '3',
        2: '2'
    }
    
    # Map of suit to symbol
    SUIT_SYMBOLS = {
        'S': '♠',
        'H': '♥',
        'D': '♦',
        'C': '♣'
    }
    
    # Class constants for suit ordering
    SUIT_ORDER = {"S": 4, "H": 3, "D": 2, "C": 1}  # For comparison
    
    def __init__(self, suit: str, value: int):
        """
        Initialize a card.
        
        Args:
            suit: The suit of the card (S, H, D, C)
            value: The value of the card (2-14, where 14 is Ace)
        """
        if suit not in self.SUIT_SYMBOLS:
            raise ValueError(f"Invalid suit: {suit}")
        if value not in self.VALUE_NAMES:
            raise ValueError(f"Invalid value: {value}")
            
        self.suit = suit
        self.value = value
        
    @property
    def value_name(self) -> str:
        """Get the string representation of the card's value."""
        return self.VALUE_NAMES.get(self.value, str(self.value))
    
    @property
    def suit_symbol(self) -> str:
        """Get the symbol for the card's suit."""
        return self.SUIT_SYMBOLS.get(self.suit, self.suit)
    
    def __str__(self) -> str:
        """String representation of the card."""
        return f"{self.value_name}{self.suit_symbol}"
    
    def __repr__(self) -> str:
        """Representation of the card."""
        return f"Card('{self.suit}', {self.value})"
    
    def __eq__(self, other) -> bool:
        """
        Compare two cards for equality.
        
        Args:
            other: Another card to compare to
            
        Returns:
            bool: True if the cards have the same suit and value
        """
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.value == other.value
    
    def __lt__(self, other):
        """Compare cards for less than."""
        if not isinstance(other, Card):
            return NotImplemented
        # For bridge comparison, only compare values within the same suit
        if self.suit == other.suit:
            return self.value < other.value
        # For general comparison across suits
        return self.SUIT_ORDER[self.suit] < self.SUIT_ORDER[other.suit]
    
    def __gt__(self, other):
        """Compare cards for greater than."""
        if not isinstance(other, Card):
            return NotImplemented
        # For bridge comparison, only compare values within the same suit
        if self.suit == other.suit:
            return self.value > other.value
        # For general comparison across suits
        return self.SUIT_ORDER[self.suit] > self.SUIT_ORDER[other.suit]
    
    def get_short_name(self):
        """Return short representation (e.g., 'AS' for Ace of Spades)."""
        return f"{self.value_name}{self.suit}"

class Deck:
    """
    Deck class representing a standard 52-card deck.
    
    Attributes:
        cards: List of Card objects
    """
    
    def __init__(self):
        """Initialize a new deck with 52 cards."""
        self.cards = []
        self.reset()
        logger.info("New deck initialized")
    
    def reset(self):
        """Reset the deck to a full 52-card deck."""
        self.cards = []
        for suit in ['S', 'H', 'D', 'C']:
            for value in range(2, 15):  # 2-14 (Ace is 14)
                self.cards.append(Card(suit, value))
        logger.info(f"Deck reset with {len(self.cards)} cards")
    
    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)
        logger.info("Deck shuffled")
    
    def deal_card(self) -> Optional[Card]:
        """
        Deal a card from the deck.
        
        Returns:
            Card: The top card from the deck, or None if deck is empty
        """
        if not self.cards:
            logger.warning("Attempted to deal from an empty deck")
            return None
        
        card = self.cards.pop()
        return card
    
    def __len__(self) -> int:
        """
        Get the number of cards left in the deck.
        
        Returns:
            int: Number of cards
        """
        return len(self.cards)
    
    def __str__(self) -> str:
        """String representation of the deck."""
        return f"Deck with {len(self.cards)} cards"

# The duplicate Card and Deck classes have been removed

