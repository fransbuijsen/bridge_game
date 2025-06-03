import tkinter as tk
from tkinter import ttk

class PlayerSetupDialog(tk.Toplevel):
    """Dialog for selecting which positions are played by humans or AI."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Player Setup")
        self.resizable(False, False)
        
        # Dictionary to store results
        self.player_types = {
            0: "human",  # South
            1: "ai",    # West
            2: "ai",    # North
            3: "ai"     # East
        }
        
        self.result = None
        
        # Create the main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add title label with better styling
        ttk.Label(main_frame, text="Select player types:", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, 
                                                columnspan=2, pady=(0, 10))
        
        # Create player selection controls
        positions = ["South", "West", "North", "East"]
        self.player_vars = {}
        
        for i, pos in enumerate(positions):
            ttk.Label(main_frame, text=f"{pos}:").grid(row=i+1, column=0, padx=5, pady=5)
            var = tk.StringVar(value="Human" if i == 0 else "AI")
            self.player_vars[i] = var
            ttk.Combobox(main_frame, textvariable=var, values=["Human", "AI"], 
                        state="readonly", width=15).grid(row=i+1, column=1, padx=5, pady=5)
        
        # Create OK button
        ttk.Button(main_frame, text="OK", command=self._on_ok).grid(row=5, column=0, 
                                                                   columnspan=2, pady=10)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Handle window close button
        self.protocol("WM_DELETE_WINDOW", self._on_ok)
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
    
    def _on_ok(self):
        """Handle OK button click."""
        # Store the results
        for pos, var in self.player_vars.items():
            self.player_types[pos] = "human" if var.get() == "Human" else "ai"
        
        self.result = self.player_types
        self.destroy()

