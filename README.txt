# UnblockMe Puzzle Solver

This project implements various solving algorithms and heuristics for the UnblockMe puzzle game.

## Project Structure

```
unblock-me/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── vehicle.py        # Vehicle class
│   │   └── game_state.py     # GameState class
│   ├── core/
│   │   ├── __init__.py
│   │   ├── unblock_me.py     # UnblockMe class - core game logic
│   │   └── state_storage.py  # StateStorage class
│   ├── solvers/
│   │   ├── __init__.py
│   │   ├── bfs_solver.py     # BFS implementation
│   │   └── astar_solver.py   # A* implementation
│   ├── heuristics/
│   │   ├── __init__.py
│   │   └── heuristic_functions.py  # All heuristic functions
│   ├── utils/
│   │   ├── __init__.py
│   │   └── visualization.py  # Plotting and visualization functions
│   ├── main.py              # Main script to run experiments
│   └── __init__.py
    
├── data/                    # Directory for puzzle input files
│   ├── GameP01.txt
│   ├── GameP02.txt
│   └── ...
├── results/                 # Directory for output files
├── lib/
│   └── requirements.txt      # Dependencies list
├── bin/
│   └── run.py  # Cross-platform launcher script
└── README.md                 # This file
```

## Setup Instructions

1. First, copy your puzzle files (GameP01.txt, GameP02.txt, etc.) to the `data/` directory.

2. Install the required dependencies:
   ```
   pip install -r lib/requirements.txt
   ```

## Running the Solver
Standard execution:
python bin/run.py

This will launch an interactive menu:

UnblockMe Puzzle Solver
1. Run BFS solver on all puzzles
2. Run A* with Blocking Vehicles heuristic
3. Run A* with Manhattan Distance heuristic
4. Run A* with Critical Path heuristic
5. Run A* with Blocking Mobility heuristic
6. Run A* with Two-Step Lookahead heuristic
7. Compare all heuristics
0. Exit

Advanced options:

Run specific solver directly:
python -m src.main --solver bfs --puzzle GameP01.txt

The solver will generate:
1. Individual solution files for each puzzle for each solver
2. A CSV file with comparison data for all heuristics
3. Plots comparing the performance of different heuristics

Check the `results/` directory for these outputs.

## Customization
Add new puzzles: Create new .txt files in data/ following existing format

Add heuristics: Implement new functions in src/heuristics/heuristic_functions.py