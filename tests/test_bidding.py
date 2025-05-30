#!/usr/bin/env python3
"""
Test script for bidding mechanics in the Bridge game.

This script tests:
1. Creating bids
2. Bid validation
3. Basic bidding sequence
4. Contract determination
"""

import sys
import os
import logging
from typing import List

# Add the parent directory to the path to allow importing the core modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the necessary modules
from core.game import BridgeGame, Bid, BidType

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BridgeTest")

def test_bid_creation():
    """Test creating various types of bids."""
    logger.info("\n=== TESTING BID CREATION ===")
    
    # Test creating normal bids
    one_club = Bid(BidType.NORMAL, 1, 'C')
    three_hearts = Bid(BidType.NORMAL, 3, 'H')
    seven_nt = Bid(BidType.NORMAL, 7, 'NT')
    
    # Test creating special bids
    pass_bid = Bid(BidType.PASS)
    double_bid = Bid(BidType.DOUBLE)
    redouble_bid = Bid(BidType.REDOUBLE)
    
    # Test string representation
    logger.info(f"One Club: {one_club}")
    logger.info(f"Three Hearts: {three_hearts}")
    logger.info(f"Seven NT: {seven_nt}")
    logger.info(f"Pass: {pass_bid}")
    logger.info(f"Double: {double_bid}")
    logger.info(f"Redouble: {redouble_bid}")
    
    # Test creating from string
    from_string_tests = [
        "1C", "2D", "3H", "4S", "5NT", "Pass", "Double", "Redouble"
    ]
    
    for bid_str in from_string_tests:
        bid = Bid.from_string(bid_str)
        logger.info(f"From string '{bid_str}': {bid}")

def test_bid_comparison():
    """Test bid comparison logic."""
    logger.info("\n=== TESTING BID COMPARISON ===")
    
    # Create some bids for comparison
    bids = [
        Bid(BidType.PASS),
        Bid(BidType.NORMAL, 1, 'C'),
        Bid(BidType.NORMAL, 1, 'D'),
        Bid(BidType.NORMAL, 1, 'H'),
        Bid(BidType.NORMAL, 1, 'S'),
        Bid(BidType.NORMAL, 1, 'NT'),
        Bid(BidType.NORMAL, 2, 'C'),
        Bid(BidType.DOUBLE),
        Bid(BidType.REDOUBLE)
    ]
    
    # Test bid ordering
    for i, bid1 in enumerate(bids):
        for j, bid2 in enumerate(bids):
            if i == j:
                assert bid1 == bid2, f"{bid1} should equal {bid2}"
            elif i < j and bid1.bid_type == BidType.NORMAL and bid2.bid_type == BidType.NORMAL:
                assert bid1 < bid2, f"{bid1} should be less than {bid2}"
                assert bid2 > bid1, f"{bid2} should be greater than {bid1}"
    
    logger.info("Bid comparison tests passed")

def test_bidding_sequence():
    """Test a basic bidding sequence."""
    logger.info("\n=== TESTING BIDDING SEQUENCE ===")
    
    # Create a new game
    game = BridgeGame()
    game.new_game()
    
    # Check initial state
    assert game.current_state == "bidding"
    assert game.current_bidder == 0  # South starts
    
    # Define a bidding sequence
    # Format: (player_index, bid_string)
    bidding_sequence = [
        (0, "1H"),      # South opens 1 Heart
        (1, "Pass"),    # West passes
        (2, "2H"),      # North raises to 2 Hearts
        (3, "Pass"),    # East passes
        (0, "4H"),      # South jumps to game
        (1, "Pass"),    # West passes
        (2, "Pass"),    # North passes
        (3, "Pass")     # East passes - bidding complete
    ]
    
    # Execute the bidding sequence
    for player_idx, bid_str in bidding_sequence:
        logger.info(f"Player {player_idx} bids {bid_str}")
        result = game.place_bid(player_idx, bid_str)
        assert result, f"Bid {bid_str} by player {player_idx} should be valid"
    
    # Check final state
    assert game.current_state == "playing"
    assert game.contract == "4H"
    
    # Verify declarer (should be South, who first bid Hearts)
    assert game.declarer == 0
    
    logger.info(f"Bidding sequence complete. Contract: {game.determine_final_contract()}")
    logger.info(f"Declarer: Player {game.declarer} ({['South', 'West', 'North', 'East'][game.declarer]})")
    logger.info(f"Dummy: Player {game.dummy} ({['South', 'West', 'North', 'East'][game.dummy]})")

def test_bid_validation():
    """Test bid validation rules."""
    logger.info("\n=== TESTING BID VALIDATION ===")
    
    game = BridgeGame()
    game.new_game()
    
    # Test 1: First bid - anything valid except Double/Redouble
    valid_first_bids = ["Pass", "1C", "1D", "1H", "1S", "1NT", "7NT"]
    invalid_first_bids = ["Double", "Redouble"]
    
    for bid_str in valid_first_bids:
        bid = Bid.from_string(bid_str)
        assert game.is_valid_bid(bid), f"{bid_str} should be valid as first bid"
    
    for bid_str in invalid_first_bids:
        bid = Bid.from_string(bid_str)
        assert not game.is_valid_bid(bid), f"{bid_str} should be invalid as first bid"
    
    # Test 2: After a bid, must be higher or Pass
    game.place_bid(0, "1H")  # South bids 1H
    
    valid_second_bids = ["Pass", "1S", "1NT", "2C", "7NT"]
    invalid_second_bids = ["1C", "1D", "1H"]
    
    for bid_str in valid_second_bids:
        bid = Bid.from_string(bid_str)
        assert game.is_valid_bid(bid), f"{bid_str} should be valid after 1H"
    
    for bid_str in invalid_second_bids:
        bid = Bid.from_string(bid_str)
        assert not game.is_valid_bid(bid), f"{bid_str} should be invalid after 1H"
    
    # Test 3: Double only valid for opponent's bid
    game = BridgeGame()
    game.new_game()
    
    game.place_bid(0, "1H")  # South bids 1H
    
    # West can double
    assert game.is_valid_bid(Bid(BidType.DOUBLE)), "West should be able to double South's bid"
    
    game.place_bid(1, "Double")  # West doubles
    
    # North can redouble (partner's bid was doubled)
    assert game.is_valid_bid(Bid(BidType.REDOUBLE)), "North should be able to redouble after West doubled"
    
    logger.info("Bid validation tests passed")

def test_all_pass():
    """Test when all players pass."""
    logger.info("\n=== TESTING ALL PASS ===")
    
    game = BridgeGame()
    game.new_game()
    
    # All players pass
    game.place_bid(0, "Pass")  # South passes
    game.place_bid(1, "Pass")  # West passes
    game.place_bid(2, "Pass")  # North passes
    game.place_bid(3, "Pass")  # East passes
    
    # Check final state
    assert game.current_state == "playing"
    assert game.contract is None
    
    logger.info("All pass test passed")

def test_complex_bidding():
    """Test a more complex bidding sequence with competition."""
    logger.info("\n=== TESTING COMPLEX BIDDING ===")
    
    game = BridgeGame()
    game.new_game()
    
    # Define a competitive bidding sequence
    bidding_sequence = [
        (0, "1NT"),     # South opens 1NT
        (1, "2H"),      # West overcalls 2H
        (2, "2S"),      # North bids 2S
        (3, "3H"),      # East raises to 3H
        (0, "3S"),      # South raises to 3S
        (1, "4H"),      # West bids 4H
        (2, "4S"),      # North bids 4S
        (3, "Double"),  # East doubles 4S
        (0, "Pass"),    # South passes
        (1, "Pass"),    # West passes
        (2, "Pass")     # North passes - bidding complete
    ]
    
    # Execute the bidding sequence
    for player_idx, bid_str in bidding_sequence:
        logger.info(f"Player {player_idx} bids {bid_str}")
        result = game.place_bid(player_idx, bid_str)
        assert result, f"Bid {bid_str} by player {player_idx} should be valid"
    
    # Check final state
    assert game.current_state == "playing"
    assert game.contract == "4SX"  # 4 Spades doubled
    
    # Verify declarer (should be North, who first bid Spades)
    assert game.declarer == 2
    
    logger.info(f"Complex bidding sequence complete. Contract: {game.determine_final_contract()}")
    logger.info(f"Declarer: Player {game.declarer} ({['South', 'West', 'North', 'East'][game.declarer]})")

def main():
    """Run all bidding tests."""
    logger.info("STARTING BIDDING TESTS")
    
    try:
        test_bid_creation()
        test_bid_comparison()
        test_bid_validation()
        test_bidding_sequence()
        test_all_pass()
        test_complex_bidding()
        
        logger.info("\nALL BIDDING TESTS PASSED")
    except AssertionError as e:
        logger.error(f"TEST FAILED: {e}")
    except Exception as e:
        logger.error(f"ERROR DURING TESTS: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()

