# Bridge Game

A Python-based implementation of the card game Bridge, featuring a graphical user interface built with Tkinter.

## Current Features

- Full graphical interface showing a bridge table
- Card display for all four players (North, South, East, West)
- Proper card representation with suits (♠♥♦♣) and ranks
- Card sorting and organization
- Basic game state display (tricks, contract)
- Menu system for game management

## Requirements

- Python 3.13 or higher
- Tkinter (usually comes with Python)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fransbuijsen/bridge_game.git
   cd bridge_game
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python3 main.py
```

## Project Structure

- `main.py`: Main entry point
- `gui/`: GUI components
- `core/`: Game logic (in development)
- `ai/`: AI player logic (in development)
- `data/`: Save game storage (in development)

## Future Development

- Bidding interface
- Card dealing functionality
- Trick-taking mechanics
- AI player implementation
- Game state persistence (save/load)

## License

[MIT License](LICENSE)
