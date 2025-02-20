import os
import sys
import argparse

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)



import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from src.models import Vehicle, GameState
from src.core import UnblockMe, StateStorage
from src.solvers import BFSSolver, AStarSolver
from src.heuristics import (
    blocking_heuristic,
    manhattan_heuristic,
    critical_path_heuristic,
    blocking_mobility_heuristic,
    two_step_heuristic
)
from src.utils import plot_comparisons

# Define data directories
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")

def ensure_directories():
    """Ensure that data and results directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)


def run_solver(solver_type, heuristic_func=None, heuristic_name=None,specific_file=None):
    """
    Runs either BFS or A* solver on all puzzle files and saves results in a folder.

    Args:
        solver_type (str): "bfs" for BFS, "astar" for A*.
        heuristic_func (callable, optional): Heuristic function for A*.
        heuristic_name (str, optional): Name of the heuristic (used in output folder name).
        pecific_file (str): Optional specific puzzle file to process
    """
    if specific_file:
        test_files = [DATA_DIR / specific_file]
    else:
        test_files = sorted(DATA_DIR.glob("GameP*.txt"))
    
    if not test_files:
        print(f"No puzzle files found in {DATA_DIR}. Make sure to copy them there.")
        return
    
    # Determine results folder based on solver type
    if solver_type == "bfs":
        solver = BFSSolver()
        results_folder = RESULTS_DIR / "results_with_bfs"
    elif solver_type == "astar":
        if heuristic_func is None or heuristic_name is None:
            raise ValueError("A* requires a heuristic function and a heuristic name.")
        solver = AStarSolver(heuristic_func)
        results_folder = RESULTS_DIR / f"results_with_{heuristic_name.lower().replace(' ', '_')}"
    else:
        raise ValueError("Invalid solver type. Use 'bfs' or 'astar'.")
    
    results_folder.mkdir(parents=True, exist_ok=True)  # ✅ Create folder if it doesn't exist
    print(f"Found {len(test_files)} puzzle files: {[f.name for f in test_files]}")
    
    unsolved_puzzles = []  # List to track unsolved puzzles

    for file_path in test_files:
        print(f"\nSolving puzzle: {file_path.name}")
        
        moves, path, nodes_explored, execution_time = solver.solve(file_path)
        
        # Create a separate file for each puzzle inside the results folder
        output_path = results_folder / f"solution_{file_path.name}"
        
        with open(output_path, "w") as f:
            f.write(f"Solving puzzle: {file_path.name}\n")
            f.write(f"Execution time: {execution_time:.2f} seconds\n")
            f.write(f"Nodes explored: {nodes_explored}\n")

            if moves is not None and path is not None:
                # Solution found
                f.write(f"Solution found in {moves} moves\n")
                f.write("Solution path:\n")
                for i, move in enumerate(path, 1):
                    f.write(f"Move {i}: Vehicle {move[0]} to position ({move[1]}, {move[2]})\n")
            else:
                # No solution found
                f.write("No solution found\n")
                unsolved_puzzles.append(file_path.name)

        print(f"Solution saved to {output_path}")

    # Print a summary of unsolved puzzles
    if unsolved_puzzles:
        print("\nThe following puzzles could not be solved:")
        for puzzle in unsolved_puzzles:
            print(f"- {puzzle}")
    else:
        print("\nAll puzzles were successfully solved!")


def compare_all_heuristics():
    """Compare performance of all heuristics"""
    test_files = list(sorted(DATA_DIR.glob("GameP*.txt")))
    if not test_files:
        print(f"No puzzle files found in {DATA_DIR}. Make sure to copy them there.")
        return
    
    heuristics = {
        "Blocking Vehicles": blocking_heuristic,
        "Manhattan Distance": manhattan_heuristic,
        "Critical Path": critical_path_heuristic,
        "Blocking Mobility": blocking_mobility_heuristic,
        "Two-Step Lookahead": two_step_heuristic
    }
    
    results = []
    
    for file_path in test_files:
        print(f"\nProcessing puzzle: {file_path.name}")
        
        for heuristic_name, heuristic_func in heuristics.items():
            solver = AStarSolver(heuristic_func)
            moves, path, nodes_explored, execution_time = solver.solve(file_path)
            
            if moves is not None and path is not None:
                results.append({
                    'puzzle': file_path.name,
                    'heuristic': heuristic_name,
                    'time': execution_time,
                    'nodes': nodes_explored,
                    'moves': moves
                })
                
                print(f"  {heuristic_name}: {moves} moves in {execution_time:.2f}s "
                      f"({nodes_explored} nodes explored)")
            else:
                print(f"  {heuristic_name}: No solution found")
    
    # Convert results to DataFrame and save
    if results:
        df = pd.DataFrame(results)
        csv_path = RESULTS_DIR / "heuristics_comparison.csv"
        df.to_csv(csv_path, index=False)
        print(f"Results saved to {csv_path}")
        
        # Generate comparison plots
        plot_comparisons(df, save_dir=RESULTS_DIR)
        print(f"Plots saved in {RESULTS_DIR} directory")
    else:
        print("No results collected. Check puzzle files and heuristics.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="UnblockMe Puzzle Solver")
    parser.add_argument('--solver', choices=['bfs', 'astar'], help='Solver algorithm')
    parser.add_argument('--puzzle', help='Specific puzzle filename')
    parser.add_argument('--all', action='store_true', help='Process all puzzles')
    parser.add_argument('--heuristic', choices=[
        'blocking', 'manhattan', 'critical', 'mobility', 'two-step'
    ], help='Heuristic for A*')
    return parser.parse_args()

def handle_arguments(args):
    if not args.solver:
        print("Error: --solver argument required")
        return

    heuristic_map = {
        'blocking': (blocking_heuristic, 'Blocking Vehicles'),
        'manhattan': (manhattan_heuristic, 'Manhattan Distance'),
        'critical': (critical_path_heuristic, 'Critical Path'),
        'mobility': (blocking_mobility_heuristic, 'Blocking Mobility'),
        'two-step': (two_step_heuristic, 'Two-Step Lookahead')
    }

    if args.puzzle and not (DATA_DIR / args.puzzle).exists():
        print(f"Error: Puzzle file {args.puzzle} not found in {DATA_DIR}")
        return

    if args.solver == 'astar' and not args.heuristic:
        print("Error: --heuristic required for A*")
        return

    heuristic = heuristic_map.get(args.heuristic, (None, None)) if args.solver == 'astar' else (None, None)
    
    unsolved = run_solver(
        solver_type=args.solver,
        heuristic_func=heuristic[0],
        heuristic_name=heuristic[1],
        specific_file=args.puzzle
    )
    
    if unsolved:
        print("\nUnsolved puzzles:")
        for puzzle in unsolved:
            print(f"- {puzzle}")


def main_menu():
    
    while True:  # Keeps prompting until user exits
        print("\nUnblockMe Puzzle Solver")
        print("1. Run BFS solver on all puzzles")
        print("2. Run A* with Blocking Vehicles heuristic")
        print("3. Run A* with Manhattan Distance heuristic")
        print("4. Run A* with Critical Path heursistic")
        print("5. Run A* with Blocking Mobility heuristic")
        print("6. Run A* with Two-Step Lookahead heuristic")
        print("7. Compare all heuristics")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            run_solver("bfs")  
        elif choice == '2':
            run_solver("astar", blocking_heuristic, "Blocking Vehicles")  
        elif choice == '3':
            run_solver("astar", manhattan_heuristic, "Manhattan Distance")
        elif choice == '4':
            run_solver("astar", critical_path_heuristic, "Critical Path")
        elif choice == '5':
            run_solver("astar", blocking_mobility_heuristic, "Blocking Mobility")
        elif choice == '6':
            run_solver("astar", two_step_heuristic, "Two Step Lookahead")
        elif choice == '7':
            compare_all_heuristics()
        elif choice == '0':
            print("Exiting...")
            break  # exits the loop cleanly
        else:
            print("Invalid choice. Please try again.")  #Re-prompts instead of exiting immediately

def main():
    """Main entry point for the application"""
    ensure_directories()
    args = parse_arguments()

    # Run in appropriate mode based on arguments
    if any(vars(args).values()):
        handle_arguments(args)
    else:
        main_menu()

if __name__ == "__main__":
    main()