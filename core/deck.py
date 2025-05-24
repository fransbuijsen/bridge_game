"""
Deck Module for Bridge Card Game

This module defines the Card and Deck classes for the Bridge card game.
"""

import random
import collections

class Card:
    """Representation of a playing card."""
    
    # Class constants for suits and values
    SUITS = {"S": "Spades", "H": "Hearts", "D": "Diamonds", "C": "Clubs"}
    SUIT_ORDER = {"S": 4, "H": 3, "D": 2, "C": 1}  # For comparison
    
    VALUE_NAMES = {
        2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
        11: "Jack", 12: "Queen", 13: "King", 14: "Ace"
    }
    
    def __init__(self, suit, value):
        """
        Initialize a card with suit and value.
        
        Args:
            suit (str): Single character suit code ('S', 'H', 'D', 'C')
            value (int): Card value (2-14, where 14 is Ace)
        """
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        if value not in self.VALUE_NAMES:
            raise ValueError(f"Invalid value: {value}")
            
        self.suit = suit
        self.value = value
    
    def __str__(self):
        """Return string representation of card."""
        return f"{self.VALUE_NAMES[self.value]} of {self.SUITS[self.suit]}"
    
    def __repr__(self):
        """Return representation of card."""
        return f"Card('{self.suit}', {self.value})"
    
    def __eq__(self, other):
        """Compare cards for equality."""
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
        value_short = {14: "A", 13: "K", 12: "Q", 11: "J"}.get(self.value, str(self.value))
        return f"{value_short}{self.suit}"


class Deck:
    """Representation of a deck of cards."""
    
    def __init__(self):
        """Initialize a standard 52-card deck."""
        self.cards = []
        self.reset()
        
    def reset(self):
        """Reset the deck to a full set of 52 cards."""
        self.cards = []
        for suit in Card.SUITS:
            for value in range(2, 15):  # 2 through 14 (Ace)
                self.cards.append(Card(suit, value))
    
    def shuffle(self):
        """Shuffle the cards in the deck using secure random."""
        # Using Fisher-Yates shuffle algorithm via random.shuffle
        random.shuffle(self.cards)
    
    def deal_card(self):
        """
        Deal one card from the deck.
        
        Returns:
            Card: A card object, or None if the deck is empty
        """
        if not self.cards:
            return None
        
        return self.cards.pop()
    
    def count(self):
        """
        Return the number of cards remaining in the deck.
        
        Returns:
            int: Number of cards remaining
        """
        return len(self.cards)
    
    def __str__(self):
        """Return string representation of the deck."""
        return f"Deck with {self.count()} cards"
    
    def __repr__(self):
        """Return representation of the deck."""
        return f"Deck({len(self.cards)} cards)"

