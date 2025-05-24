#!/usr/bin/env python3
"""
Bridge Game - Main Entry Point

This module serves as the main entry point for the Bridge card game application.
It initializes the GUI and handles the main application loop.
"""

import os
import sys
import logging
import traceback
import tkinter as tk
from datetime import datetime

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}-log.txt")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("BridgeGame")

def main():
    """Main function to start the Bridge game application."""
    logger.info("Starting Bridge Game application")
    
    try:
        # Import here to avoid any potential circular imports
        from gui.main_window import BridgeGameWindow
        
        # Create and start the application
        app = BridgeGameWindow()
        logger.info("GUI initialized successfully")
        
        # Start the main event loop
        app.mainloop()
        
        logger.info("Application closed normally")
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        tk.messagebox.showerror("Import Error", 
                                f"Failed to load required modules.\n\nError: {e}\n\n"
                                "Make sure all dependencies are installed.")
        sys.exit(1)
        
    except tk.TclError as e:
        logger.error(f"Tkinter error: {e}")
        print(f"GUI Error: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        logger.critical(traceback.format_exc())
        
        # Try to show error dialog, but this might fail if the error is early
        try:
            tk.messagebox.showerror("Error", 
                                   f"An unexpected error occurred:\n\n{e}\n\n"
                                   f"Please check the log file at:\n{log_file}")
        except:
            print(f"Critical error: {e}")
            print(f"See log file for details: {log_file}")
            
        sys.exit(1)

if __name__ == "__main__":
    main()
