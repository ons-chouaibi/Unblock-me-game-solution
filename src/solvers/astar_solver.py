import heapq

import time
from src.models.vehicle import Vehicle
from src.models.game_state import GameState, PrioritizedState
from src.core.unblock_me import UnblockMe
from src.core.state_storage import StateStorage

class AStarSolver():
    """A* search algorithm implementation."""
    
    def __init__(self, heuristic_func, timeout: int = 600):
        """
        Initialize A* solver.
        
        Args:
            heuristic_func (Callable): Heuristic function to estimate cost to goal
            timeout (int): Maximum solving time in seconds
        """
        self.timeout = timeout  # Timeout in seconds
        self.heuristic_func = heuristic_func
        self.storage = StateStorage()
        

    def solve(self, filename) :
        """
        Solves the puzzle using A* search with the specified heuristic.
        Returns moves, path, nodes_explored, and execution_time.
        """
        start_time = time.time()
        nodes_explored = 0
        # Read and initialize puzzle same as before
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        grid_size = int(lines[0])
        num_vehicles = int(lines[1])
        vehicles = []
        
        for i in range(num_vehicles):
            label, orientation, length, x, y = lines[i + 2].strip().split()
            vehicle = Vehicle(int(label), orientation, int(length), int(x) - 1, int(y) - 1)
            vehicles.append(vehicle)
        
        initial_game = UnblockMe(grid_size, vehicles)
        initial_state = GameState(vehicles, grid_size)
        
        # Initialize storage
        self.storage.add_state(initial_state)
        
        # Initialize priority queue for A* search
        # Priority queue items: (priority, PrioritizedState)
        initial_h = self.heuristic_func(initial_game)
        pq = [(initial_h, PrioritizedState(initial_game, initial_state, 0, initial_h))]
        
        while pq:
            nodes_explored += 1
            _, current = heapq.heappop(pq)
            

            # Check if current state is a solution
            red_car = next(v for v in current.game.vehicles if v.label == 1)
            if red_car.orientation == 'h' and red_car.x + red_car.length == current.game.grid_size:
                end_time = time.time()
                return (current.moves, self.storage.get_path(current.state), 
                    nodes_explored, end_time - start_time)
            
            # Generate successors
            possible_moves = current.game.get_possible_moves()
            
            for move in possible_moves:
                new_game = current.game.make_move(move)
                new_state = GameState(new_game.vehicles, new_game.grid_size)
                
                if self.storage.add_state(new_state, current.state, move):
                    h = self.heuristic_func(new_game)
                    prioritized_state = PrioritizedState(new_game, new_state, 
                                                    current.moves + 1, h)
                    heapq.heappush(pq, (prioritized_state.priority, prioritized_state))
        
        end_time = time.time()
        return None, None, nodes_explored, end_time - start_time

    
    def get_state_storage(self) :
        """Get the state storage instance."""
        return self.storage

