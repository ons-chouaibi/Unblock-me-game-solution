import time
from collections import deque
from src.models.vehicle import Vehicle
from src.core.state_storage import StateStorage
from src.models.game_state import GameState
from src.core.unblock_me import UnblockMe

class BFSSolver():
    """Breadth-First Search solver implementation."""
    def __init__(self, timeout: int = 600):
        """
        Initialize BFS solver.
        
        Args:
            timeout (int): Maximum solving time in seconds
        """
        self.timeout = timeout  # Timeout in seconds
        self.storage = StateStorage()  # Initialize storage for explored states



    def solve(self, filename):
        """
        Solves the UnblockMe puzzle using BFS.
        Returns the number of moves in the shortest solution and the solution path.
        """
        start_time = time.time()
        nodes_explored = 0
        # Read input file
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Parse input
        grid_size = int(lines[0])
        num_vehicles = int(lines[1])
        vehicles = []
        
        # Create initial vehicles
        for i in range(num_vehicles):
            label, orientation, length, x, y = lines[i + 2].strip().split()
            vehicle = Vehicle(int(label), orientation, int(length), int(x) - 1, int(y) - 1)
            vehicles.append(vehicle)
        
        # Create initial game state
        initial_game = UnblockMe(grid_size, vehicles)
        initial_state = GameState(vehicles, grid_size)
        
        # Initialize storage for explored states
        self.storage.add_state(initial_state)
        
        # Initialize queue for BFS
        queue = deque([(initial_game, initial_state, 0)])  # (game, state, moves)
        
        while queue:
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                print("Timeout reached!")
                return None, None, nodes_explored, elapsed_time  # Return None if timeout is reached
            
            nodes_explored += 1
            current_game, current_state, moves = queue.popleft()
            
            # Check if current state is a solution (red car can exit)
            red_car = next(v for v in current_game.vehicles if v.label == 1)
            if red_car.orientation == 'h' and red_car.x + red_car.length == current_game.grid_size:
                # Solution found!
                end_time = time.time()
                path = self.storage.get_path(current_state)
                return moves, path, nodes_explored, end_time - start_time
            
            # Get all possible moves from current state
            possible_moves = current_game.get_possible_moves()
            
            # Try each move
            for move in possible_moves:
                # Make the move
                new_game = current_game.make_move(move)
                new_state = GameState(new_game.vehicles, new_game.grid_size)
                
                # If this is a new state, add it to the queue
                if self.storage.add_state(new_state, current_state, move):
                    queue.append((new_game, new_state, moves + 1))
            
        end_time = time.time()

        return None, None, nodes_explored, end_time - start_time