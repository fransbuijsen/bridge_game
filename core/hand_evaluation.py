"""
Hand evaluation module for Bridge card game.

This module provides functions for evaluating bridge hands
to determine appropriate bids based on high card points,
distribution, and other factors.
"""

import logging
from typing import List, Dict, Tuple
from core.deck import Card

# Set up logger
logger = logging.getLogger("BridgeGame.Core.HandEval")

# High card point values for each card rank
HCP_VALUES = {
    14: 4,  # Ace
    13: 3,  # King
    12: 2,  # Queen
    11: 1,  # Jack
    # All other cards are worth 0 points
}

def calculate_hcp(hand: List[Card]) -> int:
    """
    Calculate high card points for a hand.
    
    Args:
        hand: List of Card objects
        
    Returns:
        int: Total HCP (A=4, K=3, Q=2, J=1)
    """
    return sum(HCP_VALUES.get(card.value, 0) for card in hand)

def count_suit_length(hand: List[Card]) -> Dict[str, int]:
    """
    Count the number of cards in each suit.
    
    Args:
        hand: List of Card objects
        
    Returns:
        Dict: Mapping of suits to counts {'S': 3, 'H': 4, 'D': 3, 'C': 3}
    """
    suit_lengths = {'S': 0, 'H': 0, 'D': 0, 'C': 0}
    for card in hand:
        suit_lengths[card.suit] += 1
    return suit_lengths

def is_balanced(suit_lengths: Dict[str, int]) -> bool:
    """
    Check if a hand has balanced distribution (4-3-3-3, 4-4-3-2, or 5-3-3-2).
    
    Args:
        suit_lengths: Dict mapping suits to lengths
        
    Returns:
        bool: True if the hand is balanced
    """
    # Check if any suit has more than 5 cards or less than 2 cards
    if any(length > 5 or length < 2 for length in suit_lengths.values()):
        return False
    
    # Count how many suits have 4 or more cards
    suits_with_4_plus = sum(1 for length in suit_lengths.values() if length >= 4)
    
    # Balanced patterns are 4-3-3-3, 4-4-3-2, or 5-3-3-2
    if suits_with_4_plus > 2:
        return False
    
    # Check for 5-3-3-2 pattern
    if any(length == 5 for length in suit_lengths.values()):
        return list(sorted(suit_lengths.values(), reverse=True)) == [5, 3, 3, 2]
    
    # For 4-3-3-3 or 4-4-3-2 patterns
    return True

def get_longest_major(suit_lengths: Dict[str, int]) -> str:
    """
    Get the longest major suit, if any with 5+ cards.
    
    Args:
        suit_lengths: Dict mapping suits to lengths
        
    Returns:
        str: The longest major suit ('S' or 'H'), or None if no major with 5+ cards
    """
    if suit_lengths['S'] >= 5 and suit_lengths['S'] >= suit_lengths['H']:
        return 'S'
    elif suit_lengths['H'] >= 5:
        return 'H'
    return None

def get_longest_minor(suit_lengths: Dict[str, int]) -> str:
    """
    Get the longest minor suit.
    
    Args:
        suit_lengths: Dict mapping suits to lengths
        
    Returns:
        str: The longest minor suit ('D' or 'C')
    """
    if suit_lengths['D'] >= suit_lengths['C']:
        return 'D'
    else:
        return 'C'

def evaluate_distribution_points(suit_lengths: Dict[str, int]) -> int:
    """
    Calculate distribution points for a hand.
    
    Args:
        suit_lengths: Dict mapping suits to lengths
        
    Returns:
        int: Distribution points (1 for each void, doubleton, or singleton)
    """
    dist_points = 0
    for length in suit_lengths.values():
        if length == 0:  # Void
            dist_points += 3
        elif length == 1:  # Singleton
            dist_points += 2
        elif length == 2:  # Doubleton
            dist_points += 1
    return dist_points

def has_stopper(hand: List[Card], suit: str) -> bool:
    """
    Check if a hand has a stopper in a specific suit.
    
    A stopper is defined as:
    - Ace
    - King and at least one other card
    - Queen and at least two other cards
    - Jack and at least three other cards
    
    Args:
        hand: List of Card objects
        suit: The suit to check for stoppers
        
    Returns:
        bool: True if the hand has a stopper in the suit
    """
    suit_cards = [card for card in hand if card.suit == suit]
    
    if not suit_cards:
        return False
    
    # Check for Ace
    if any(card.value == 14 for card in suit_cards):
        return True
    
    # Check for King + another card
    if any(card.value == 13 for card in suit_cards) and len(suit_cards) >= 2:
        return True
    
    # Check for Queen + two other cards
    if any(card.value == 12 for card in suit_cards) and len(suit_cards) >= 3:
        return True
    
    # Check for Jack + three other cards
    if any(card.value == 11 for card in suit_cards) and len(suit_cards) >= 4:
        return True
    
    return False

def determine_opening_bid(hand: List[Card]) -> Tuple[str, str]:
    """
    Determine an appropriate opening bid based on hand evaluation.
    
    Args:
        hand: List of Card objects
        
    Returns:
        Tuple[str, str]: (bid, explanation)
    """
    hcp = calculate_hcp(hand)
    suit_lengths = count_suit_length(hand)
    balanced = is_balanced(suit_lengths)
    
    logger.info(f"Opening bid evaluation - HCP: {hcp}, Suit lengths: {suit_lengths}, Balanced: {balanced}")
    
    # Pass with less than 12 HCP
    if hcp < 12:
        return "Pass", f"Less than 12 HCP ({hcp})"
    
    # 1NT opening with balanced 15-17 HCP
    if balanced and 15 <= hcp <= 17:
        return "1NT", f"Balanced hand with {hcp} HCP"
    
    # 2NT opening with balanced 20-21 HCP
    if balanced and 20 <= hcp <= 21:
        return "2NT", f"Strong balanced hand with {hcp} HCP"
    
    # Standard 5-card major openings
    if suit_lengths['S'] >= 5 and hcp >= 12:
        return "1S", f"5+ spades with {hcp} HCP"
    
    if suit_lengths['H'] >= 5 and hcp >= 12:
        return "1H", f"5+ hearts with {hcp} HCP"
    
    # Open longest minor with 12+ HCP
    if hcp >= 12:
        # Better minor: with equal length minors, open 1D
        if suit_lengths['D'] >= suit_lengths['C']:
            return "1D", f"Longest/better minor with {hcp} HCP"
        else:
            return "1C", f"Longest minor with {hcp} HCP"
    
    # Default to Pass
    return "Pass", f"No suitable opening bid ({hcp} HCP)"

def determine_response(hand: List[Card], partner_bid: str, opponent_bid: str = None) -> Tuple[str, str]:
    """
    Determine an appropriate response to partner's bid.
    
    Args:
        hand: List of Card objects
        partner_bid: Partner's last bid
        opponent_bid: Opponent's last bid (if any)
        
    Returns:
        Tuple[str, str]: (bid, explanation)
    """
    hcp = calculate_hcp(hand)
    suit_lengths = count_suit_length(hand)
    balanced = is_balanced(suit_lengths)
    
    logger.info(f"Response evaluation - HCP: {hcp}, Suit lengths: {suit_lengths}, Partner bid: {partner_bid}")
    
    # Pass with less than 6 HCP (unless distributional)
    if hcp < 6 and max(suit_lengths.values()) < 6:
        return "Pass", f"Weak hand ({hcp} HCP)"
    
    # Responding to 1NT opening
    if partner_bid == "1NT":
        if hcp >= 8 and is_balanced(suit_lengths):
            if 8 <= hcp <= 9:
                return "2NT", f"Invitational with {hcp} HCP"
            else:  # 10+ HCP
                return "3NT", f"Game values with {hcp} HCP"
        elif hcp >= 8 and suit_lengths['S'] >= 5:
            return "2S", f"Transfer to spades ({suit_lengths['S']} cards)"
        elif hcp >= 8 and suit_lengths['H'] >= 5:
            return "2H", f"Transfer to hearts ({suit_lengths['H']} cards)"
        elif hcp >= 8 and (suit_lengths['C'] >= 5 or suit_lengths['D'] >= 5):
            # Stayman with 4+ card major
            if suit_lengths['H'] >= 4 or suit_lengths['S'] >= 4:
                return "2C", f"Stayman with {hcp} HCP"
        else:
            return "Pass", f"Nothing special to show ({hcp} HCP)"
    
    # Responding to 1 of a suit
    if partner_bid in ["1C", "1D", "1H", "1S"]:
        partner_suit = partner_bid[1]
        
        # New suit at 1-level with 6+ HCP
        if partner_bid in ["1C", "1D"] and hcp >= 6:
            if suit_lengths['H'] >= 4:
                return "1H", f"4+ hearts with {hcp} HCP"
            elif suit_lengths['S'] >= 4:
                return "1S", f"4+ spades with {hcp} HCP"
        
        # Raise partner's major with 3+ card support and 6-10 HCP
        if partner_suit in ["H", "S"] and suit_lengths[partner_suit] >= 3:
            if 6 <= hcp <= 10:
                return f"2{partner_suit}", f"Support for partner's {partner_suit} ({suit_lengths[partner_suit]} cards, {hcp} HCP)"
            elif 11 <= hcp <= 12:
                return f"3{partner_suit}", f"Invitational raise ({suit_lengths[partner_suit]} cards, {hcp} HCP)"
            elif hcp >= 13:
                return f"4{partner_suit}", f"Game values with support ({suit_lengths[partner_suit]} cards, {hcp} HCP)"
        
        # Raise partner's minor with 5+ card support and 10+ HCP
        if partner_suit in ["C", "D"] and suit_lengths[partner_suit] >= 5 and hcp >= 10:
            return f"3{partner_suit}", f"Strong raise in minor ({suit_lengths[partner_suit]} cards, {hcp} HCP)"
        
        # 1NT response with 6-10 HCP and balanced hand
        if 6 <= hcp <= 10 and is_balanced(suit_lengths):
            return "1NT", f"Balanced hand with {hcp} HCP"
        
        # 2NT response with 11-12 HCP and balanced hand
        if 11 <= hcp <= 12 and is_balanced(suit_lengths):
            return "2NT", f"Invitational balanced hand with {hcp} HCP"
        
        # 3NT response with 13-15 HCP and balanced hand
        if 13 <= hcp <= 15 and is_balanced(suit_lengths):
            return "3NT", f"Game values with {hcp} HCP"
        
        # New suit at 2-level with 10+ HCP
        if hcp >= 10:
            # Find a 4+ card suit to bid
            for suit in ["D", "C", "H", "S"]:
                if suit != partner_suit and suit_lengths[suit] >= 4:
                    # Check if the bid would be at the 2-level
                    if (partner_suit in ["C", "D"] and suit in ["H", "S"]) or \
                       (partner_suit == "C" and suit == "D") or \
                       (partner_suit in ["H", "S"] and suit not in ["H", "S"]):
                        return f"2{suit}", f"New suit with {suit_lengths[suit]} cards, {hcp} HCP"
    
    # Default to Pass if no suitable response
    return "Pass", f"No suitable response ({hcp} HCP)"

def determine_competitive_bid(hand: List[Card], partner_bid: str, opponent_bid: str) -> Tuple[str, str]:
    """
    Determine an appropriate bid in a competitive auction.
    
    Args:
        hand: List of Card objects
        partner_bid: Partner's last bid
        opponent_bid: Opponent's last bid
        
    Returns:
        Tuple[str, str]: (bid, explanation)
    """
    hcp = calculate_hcp(hand)
    suit_lengths = count_suit_length(hand)
    
    logger.info(f"Competitive bid evaluation - HCP: {hcp}, Suit lengths: {suit_lengths}")
    
    # Extract opponent's suit if they bid a suit
    opponent_suit = None
    if len(opponent_bid) == 2 and opponent_bid[1] in "CDHS":
        opponent_suit = opponent_bid[1]
    
    # Double with 13+ HCP and shortness in opponent's suit
    if opponent_bid != "Pass" and hcp >= 13:
        if opponent_suit and suit_lengths[opponent_suit] <= 2:
            return "Double", f"Takeout double with {hcp} HCP"
    
    # Overcall with 8-16 HCP and 5+ card suit
    if opponent_bid != "Pass" and 8 <= hcp <= 16:
        # Look for 5+ card suits to overcall with
        for suit in "SHDC":  # Check suits in order of priority
            if suit_lengths[suit] >= 5:
                # Check if the overcall is at an appropriate level
                if opponent_bid[0] == "1" and suit in "SH":
                    return f"1{suit}", f"Overcall with 5+ {suit} ({hcp} HCP)"
                elif opponent_bid[0] == "1":
                    return f"2{suit}", f"Overcall with 5+ {suit} ({hcp} HCP)"
    
    # Compete with a fit for partner's suit
    if partner_bid != "Pass" and partner_bid not in ["Double", "Redouble"]:
        partner_suit = partner_bid[-1]
        if partner_suit in "CDHS" and suit_lengths[partner_suit] >= 3:
            # Raise partner's suit competitively
            if 6 <= hcp <= 10:
                level = int(partner_bid[0]) + 1
                return f"{level}{partner_suit}", f"Competitive raise with {suit_lengths[partner_suit]} cards, {hcp} HCP"
    
    # Default to Pass in competitive situations
    return "Pass", f"No suitable competitive bid ({hcp} HCP)"

"""
Hand evaluation module for Bridge card game.

This module provides functions for evaluating bridge hands
to determine appropriate bids based on high card points,
distribution, and other factors.
"""

import logging
from typing import List, Dict, Tuple
from core.deck import Card

# Set up logger
logger = logging.getLogger("BridgeGame.Core.HandEval")

# High card point values for each card rank
HCP_VALUES = {
    14: 4,  # Ace
    13: 3,  # King
    12: 2,  # Queen
    11: 1,  # Jack
    # All other cards are worth 0 points
}

def calculate_hcp(hand: List[Card]) -> int:
    """
    Calculate high card points for a hand.
    
    Args:
        hand: List of Card objects
        
    Returns:
        int: Total HCP (A=4, K=3, Q=2, J=1)
    """
    return sum(HCP_VALUES.get(card.value, 0) for card in hand)

def count_suit_length(hand: List[Card]) -> Dict[str, int]:
    """
    Count the number of cards in each suit.
    
    Args:
        hand: List of Card objects
        
    Returns:
        Dict: Mapping of suits to counts {'S': 3, 'H': 4, 'D': 3, 'C': 3}
    """
    suit_lengths = {'S': 0, 'H': 0, 'D': 0, 'C': 0}
    for card in hand:
        suit_lengths[card.suit] += 1
    return suit_lengths

def is_balanced(suit_lengths: Dict[str, int]) -> bool:
    """
    Check if a hand has balanced distribution (4-3-3-3, 4-4-3-2, or 5-3-3-2).
    
    Args:
        suit_lengths: Dict mapping suits to lengths
        
    Returns:
        bool: True if the hand is balanced
    """
    # Check if any suit has more than 5 cards or less than 2 cards
    if any(length > 5 or length < 2 for length in suit_lengths.values()):
        return False
    
    # Count how many suits have 4 or more cards
    suits_with_4_plus = sum(1 for length in suit_lengths.values() if length >= 4)
    
    # Balanced patterns are 4-3-3-3, 4-4-3-2, or 5-3-3-2
    if suits_with_4_plus > 2:
        return False
    
    # Check for 5-3-3-2 pattern
    if any(length == 5 for length in suit_lengths.values()):
        return list(sorted(suit_lengths.values(), reverse=True)) == [5, 3, 3, 2]
    
    return True

def determine_opening_bid(hand: List[Card]) -> Tuple[str, str]:
    """
    Determine an appropriate opening bid based on hand evaluation.
    
    Args:
        hand: List of Card objects
        
    Returns:
        Tuple[str, str]: (bid, explanation)
    """
    hcp = calculate_hcp(hand)
    suit_lengths = count_suit_length(hand)
    balanced = is_balanced(suit_lengths)
    
    logger.info(f"Hand evaluation - HCP: {hcp}, Suit lengths: {suit_lengths}, Balanced: {balanced}")
    
    # Pass with less than 12 HCP
    if hcp < 12:
        return "Pass", f"Less than 12 HCP ({hcp})"
    
    # 1NT opening with balanced 15-17 HCP
    if balanced and 15 <= hcp <= 17:
        return "1NT", f"Balanced hand with {hcp} HCP"
    
    # Standard 5-card major openings
    if suit_lengths['S'] >= 5 and hcp >= 12:
        return "1S", f"5+ spades with {hcp} HCP"
    
    if suit_lengths['H'] >= 5 and hcp >= 12:
        return "1H", f"5+ hearts with {hcp} HCP"
    
    # Open longest minor with 12+ HCP
    if hcp >= 12:
        if suit_lengths['D'] >= suit_lengths['C']:
            return "1D", f"Longest minor with {hcp} HCP"
        else:
            return "1C", f"Longest minor with {hcp} HCP"
    
    # Default to Pass
    return "Pass", f"No suitable opening bid ({hcp} HCP)"

def determine_response(hand: List[Card], partner_bid: str, opponent_bid: str = None) -> Tuple[str, str]:
    """
    Determine an appropriate response to partner's bid.
    
    Args:
        hand: List of Card objects
        partner_bid: Partner's last bid
        opponent_bid: Opponent's last bid (if any)
        
    Returns:
        Tuple[str, str]: (bid, explanation)
    """
    hcp = calculate_hcp(hand)
    suit_lengths = count_suit_length(hand)
    
    logger.info(f"Response evaluation - HCP: {hcp}, Suit lengths: {suit_lengths}, Partner bid: {partner_bid}")
    
    # Pass with less than 6 HCP (unless distributional)
    if hcp < 6 and max(suit_lengths.values()) < 6:
        return "Pass", f"Weak hand ({hcp} HCP)"
    
    # Responding to 1NT opening
    if partner_bid == "1NT":
        if hcp >= 8 and is_balanced(suit_lengths):
            return "3NT", f"Balanced game values ({hcp} HCP)"
        elif hcp >= 8 and suit_lengths['S'] >= 5:
            return "2S", f"Transfer to spades ({suit_lengths['S']} cards)"
        elif hcp >= 8 and suit_lengths['H'] >= 5:
            return "2H", f"Transfer to hearts ({suit_lengths['H']} cards)"
        else:
            return "Pass", f"Nothing special to show ({hcp} HCP)"
    
    # Responding to 1 of a suit
    if partner_bid in ["1C", "1D", "1H", "1S"]:
        partner_suit = partner_bid[1]
        
        # New suit at 1-level with 6+ HCP
        if partner_bid in ["1C", "1D"] and hcp >= 6:
            if suit_lengths['H'] >= 4:
                return "1H", f"4+ hearts with {hcp} HCP"
            elif suit_lengths['S'] >= 4:
                return "1S", f"4+ spades with {hcp} HCP"
        
        # Raise partner's major with 3+ card support and 6-10 HCP
        if partner_suit in ["H", "S"] and suit_lengths[partner_suit] >= 3 and 6 <= hcp <= 10:
            return f"2{partner_suit}", f"Support for partner's {partner_suit} ({suit_lengths[partner_suit]} cards, {hcp} HCP)"
        
        # Jump to game with 13+ HCP and 4+ card support for partner's major
        if partner_suit in ["H", "S"] and suit_lengths[partner_suit] >= 4 and hcp >= 13:
            return f"4{partner_suit}", f"Game values with support ({suit_lengths[partner_suit]} cards, {hcp} HCP)"
        
        # 1NT response with 6-10 HCP and balanced hand
        if 6 <= hcp <= 10 and is_balanced(suit_lengths):
            return "1NT", f"Balanced hand with {hcp} HCP"
        
        # 2NT response with 11-12 HCP and balanced hand
        if 11 <= hcp <= 12 and is_balanced(suit_lengths):
            return "2NT", f"Invitational balanced hand with {hcp} HCP"
    
    # Default to Pass if no suitable response
    return "Pass", f"No suitable response ({hcp} HCP)"

def determine_competitive_bid(hand: List[Card], partner_bid: str, opponent_bid: str) -> Tuple[str, str]:
    """
    Determine an appropriate bid in a competitive auction.
    
    Args:
        hand: List of Card objects
        partner_bid: Partner's last bid
        opponent_bid: Opponent's last bid
        
    Returns:
        Tuple[str, str]: (bid, explanation)
    """
    hcp = calculate_hcp(hand)
    suit_lengths = count_suit_length(hand)
    
    logger.info(f"Competitive bid evaluation - HCP: {hcp}, Suit lengths: {suit_lengths}")
    
    # Extract opponent's suit if they bid a suit
    opponent_suit = None
    if len(opponent_bid) == 2 and opponent_bid[1] in "CDHS":
        opponent_suit = opponent_bid[1]
    
    # Double with 13+ HCP and shortness in opponent's suit
    if opponent_bid != "Pass" and hcp >= 13:
        if opponent_suit and suit_lengths[opponent_suit] <= 2:
            return "Double", f"Takeout double with {hcp} HCP"
    
    # Overcall with 8-16 HCP and 5+ card suit
    if opponent_bid != "Pass" and 8 <= hcp <= 16:
        # Look for 5+ card suits to overcall with
        for suit in "SHDC":  # Check suits in order of priority
            if suit_lengths[suit] >= 5:
                # Check if the overcall is at an appropriate level
                if opponent_bid[0] == "1" and suit in "SH":
                    return f"1{suit}", f"Overcall with 5+ {suit} ({hcp} HCP)"
                elif opponent_bid[0] == "1":
                    return f"2{suit}", f"Overcall with 5+ {suit} ({hcp} HCP)"
    
    # Default to Pass in competitive situations
    return "Pass", f"No suitable competitive bid ({hcp} HCP)"

