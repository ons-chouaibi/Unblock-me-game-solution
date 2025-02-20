from src.core.unblock_me import UnblockMe
from src.models.vehicle import Vehicle

# Registry for storing heuristic functions
REGISTERED_HEURISTICS = {}

def register_heuristic(name: str) :
    """
    Decorator to register heuristic functions.
    
    Args:
        name (str): Name of the heuristic
        
    Returns:
        Callable: Decorator function
    """
    def decorator(func):
        REGISTERED_HEURISTICS[name] = func
        return func
    return decorator

@register_heuristic("blocking")
def blocking_heuristic(game: UnblockMe) -> int:
    """
    Computes the heuristic value for a given game state.
    This heuristic counts the number of blocking vehicles between the red car and the exit.
    """
    red_car = next(v for v in game.vehicles if v.label == 1)
    blocking_count = 0
    
    # Check all cells between red car and exit
    for x in range(red_car.x + red_car.length, game.grid_size):
        if game.grid[red_car.y][x] != 0:
            blocking_count += 1
            
    return blocking_count

@register_heuristic("manhattan")
def manhattan_heuristic(game: UnblockMe) -> float:
    """
    Manhattan distance heuristic considering blocking vehicles.
    
    Args:
        game (UnblockMe): Current game state
        
    Returns:
        float: Heuristic value based on Manhattan distances
    """
    red_car = next(v for v in game.vehicles if v.label == 1)
    total_cost = 0
    blocking_vehicles = set()
    
    # Find blocking vehicles
    for x in range(red_car.x + red_car.length, game.grid_size):
        vehicle_id = game.grid[red_car.y][x]
        if vehicle_id != 0:
            blocking_vehicles.add(vehicle_id)
    
    # Calculate minimum moves needed for each blocking vehicle
    for vehicle in game.vehicles:
        if vehicle.label in blocking_vehicles:
            if vehicle.orientation == 'v':
                # Vertical vehicle needs to move either up or down to clear path
                moves_up = vehicle.length if vehicle.y + vehicle.length > red_car.y else 0
                moves_down = vehicle.length if vehicle.y < red_car.y else 0
                total_cost += min(moves_up, moves_down) if (moves_up or moves_down) else 1
            else:
                # Horizontal vehicle needs to move left or right
                total_cost += 1
    
    return total_cost

@register_heuristic("critical_path")
def critical_path_heuristic(game: UnblockMe) -> int:
    """
    Critical path heuristic.
    
    Args:
        game (UnblockMe): Current game state
        
    Returns:
        int: Depth of the deepest blocking chain
    """
    def get_blockers_depth(vehicle: Vehicle, depth: int = 0, visited: set = None) -> int:
        if visited is None:
            visited = set()
            
        if vehicle.label in visited:
            return depth
            
        visited.add(vehicle.label)
        max_depth = depth
        
        # Find vehicles blocking this vehicle
        if vehicle.orientation == 'v':
            # Check positions above and below
            positions = [(vehicle.x, vehicle.y - 1), (vehicle.x, vehicle.y + vehicle.length)]
        else:
            # Check positions left and right
            positions = [(vehicle.x - 1, vehicle.y), (vehicle.x + vehicle.length, vehicle.y)]
            
        for x, y in positions:
            if 0 <= x < game.grid_size and 0 <= y < game.grid_size:
                if game.grid[y][x] != 0:
                    blocking_vehicle = next(v for v in game.vehicles if v.label == game.grid[y][x])
                    max_depth = max(max_depth, get_blockers_depth(blocking_vehicle, depth + 1, visited))
                    
        return max_depth
    
    red_car = next(v for v in game.vehicles if v.label == 1)
    return get_blockers_depth(red_car)

@register_heuristic("blocking_mobility")
def blocking_mobility_heuristic(game: UnblockMe) -> float:
    """
    Blocking mobility heuristic considering movement freedom.
    
    Args:
        game (UnblockMe): Current game state
        
    Returns:
        float: Heuristic value based on blocking vehicles' mobility
    """
    def get_blocking_vehicles(game):
        """Get all vehicles blocking the red car's path to exit"""
        red_car = next(v for v in game.vehicles if v.label == 1)
        blockers = []
        
        # Check all positions from red car to exit
        for x in range(red_car.x + red_car.length, game.grid_size):
            if game.grid[red_car.y][x] != 0:
                blocker = next(v for v in game.vehicles if v.label == game.grid[red_car.y][x])
                if blocker not in blockers:
                    blockers.append(blocker)
        return blockers
    
    def count_free_direction(game, vehicle, direction):
        """Count free spaces in a given direction"""
        if direction == 'up':
            y = vehicle.y - 1
            x = vehicle.x
            while y >= 0 and game.grid[y][x] == 0:
                y -= 1
            return vehicle.y - (y + 1)
        elif direction == 'down':
            y = vehicle.y + vehicle.length
            x = vehicle.x
            while y < game.grid_size and game.grid[y][x] == 0:
                y += 1
            return (y - 1) - (vehicle.y + vehicle.length - 1)
        elif direction == 'left':
            x = vehicle.x - 1
            y = vehicle.y
            while x >= 0 and game.grid[y][x] == 0:
                x -= 1
            return vehicle.x - (x + 1)
        else:  # right
            x = vehicle.x + vehicle.length
            y = vehicle.y
            while x < game.grid_size and game.grid[y][x] == 0:
                x += 1
            return (x - 1) - (vehicle.x + vehicle.length - 1)



    blockers = get_blocking_vehicles(game)
    total_moves = 0
    
    for blocker in blockers:
        if blocker.orientation == 'v':
            up = count_free_direction(game, blocker, 'up')
            down = count_free_direction(game, blocker, 'down')
            total_moves += min(up, down) + 1
        else:
            left = count_free_direction(game, blocker, 'left')
            right = count_free_direction(game, blocker, 'right')
            total_moves += min(left, right) + 1
    return total_moves

def is_solved(game):
    """Check if the puzzle is solved"""
    red_car = next(v for v in game.vehicles if v.label == 1)
    return red_car.x + red_car.length == game.grid_size

def two_step_heuristic(game, base_heuristic=blocking_mobility_heuristic):
    """Two-Step Lookahead Heuristic"""
    if is_solved(game):
        return 0
        
    min_h = float('inf')
    for move in game.get_possible_moves():
        new_game = game.make_move(move)
        h_val = base_heuristic(new_game)
        if h_val < min_h:
            min_h = h_val
    return min_h + 1


def get_heuristic(name: str) :
    """
    Get registered heuristic function by name.
    
    Args:
        name (str): Name of the heuristic
        
    Returns:
        Callable: Heuristic function
        
    Raises:
        ValueError: If heuristic name is not registered
    """
    if name not in REGISTERED_HEURISTICS:
        raise ValueError(f"Heuristic '{name}' not found. Available heuristics: {list(REGISTERED_HEURISTICS.keys())}")
    return REGISTERED_HEURISTICS[name]


