#!/usr/bin/env python3
"""
Bridge Game - Main Entry Point

This is the main entry point for the Bridge card game application.
It initializes the GUI and starts the game.
"""

import tkinter as tk
from gui.main_window import MainWindow
from core.game import BridgeGame


def main():
    """Initialize and start the bridge game application."""
    root = tk.Tk()
    root.title("Bridge Card Game")
    
    # Create game instance
    game = BridgeGame()
    
    # Create the main window and pass the game instance
    app = MainWindow(root, game)
    
    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()

