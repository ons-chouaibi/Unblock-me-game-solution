from src.models.vehicle import Vehicle
from src.models.game_state import GameState
import sys



class UnblockMe:
    """
    Manages the game grid and vehicle movements.
    
    Attributes:
        grid_size (int): Size of the square grid
        vehicles (List[Vehicle]): List of vehicles on the grid
        grid (List[List[int]]): 2D grid representation of the game state
    """
    def __init__(self, grid_size: int, vehicles):
        self.grid_size = grid_size
        self.grid = [[0] * grid_size for _ in range(grid_size)]
        self.vehicles = []
        self.initialize_game(vehicles)

    def initialize_game(self, vehicles) :
        """
        Initialize the game by validating and placing vehicles.
        
        Args:
            vehicles: List of Vehicle objects to place on the grid
            
        Raises:
            UnblockMeError: If vehicle placement is invalid
        """
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]  # Clear grid first
        for vehicle in vehicles:
            if not self.is_within_bounds(vehicle):
                raise ValueError(f"Vehicle {vehicle.label} is out of grid bounds.")
            if not self.does_not_overlap(vehicle):
                raise ValueError(f"Vehicle {vehicle.label} overlaps with another vehicle.")
            self.vehicles.append(vehicle)
            self.place_vehicle(vehicle)


    def is_valid_placement(self, vehicle: Vehicle) -> bool:
        """Check if a vehicle can be placed at its position"""
        if not self.is_within_bounds(vehicle):
            return False
        return self.does_not_overlap(vehicle)

    def is_within_bounds(self, vehicle: Vehicle) -> bool:
        """Check if a vehicle fits within the grid boundaries"""
        if vehicle.orientation == 'h':  # Horizontal
            return 0 <= vehicle.x < self.grid_size and 0 <= vehicle.y < self.grid_size and (vehicle.x + vehicle.length-1) <= self.grid_size
        elif vehicle.orientation == 'v':  # Vertical
            return 0 <= vehicle.x < self.grid_size and 0 <= vehicle.y < self.grid_size and (vehicle.y + vehicle.length-1) <= self.grid_size
        return False

    def does_not_overlap(self, vehicle: Vehicle) -> bool:
        """Check if a vehicle overlaps with any existing vehicles"""
        x, y = vehicle.x, vehicle.y
        for i in range(vehicle.length):
            if vehicle.orientation == 'h':  # Horizontal
                if self.grid[y][x + i] != 0:
                    return False
            elif vehicle.orientation == 'v':  # Vertical
                if self.grid[y + i][x] != 0:
                    return False
        return True
    
    def place_vehicle(self, vehicle):
        """Place a vehicle on the grid."""
        x, y = vehicle.x, vehicle.y
        for i in range(vehicle.length):
            if vehicle.orientation == 'h':  # Horizontal
                self.grid[y][x + i] = vehicle.label
            elif vehicle.orientation == 'v':  # Vertical
                self.grid[y + i][x] = vehicle.label

    def get_possible_moves(self) :
        """Returns all possible moves for the current state.
        Each move is represented as a tuple (vehicle_label, new_x, new_y)."""
        possible_moves = []
        
        for vehicle in self.vehicles:
            current_x, current_y = vehicle.x, vehicle.y
            
            if vehicle.orientation == 'h':  # Horizontal vehicle
                # Check moves to the left
                x = current_x
                while x > 0:  # Try moving left until hitting the edge or another vehicle
                    x -= 1
                    if self.grid[current_y][x] != 0:  # Hit another vehicle
                        break
                    possible_moves.append((vehicle.label, x, current_y))
                
                # Check moves to the right
                x = current_x
                while x + vehicle.length < self.grid_size:  # Try moving right
                    x += 1
                    if self.grid[current_y][x + vehicle.length - 1] != 0:  # Hit another vehicle
                        break
                    possible_moves.append((vehicle.label, x, current_y))
                    
            else:  # Vertical vehicle
                # Check moves upward
                y = current_y
                while y > 0:  # Try moving up
                    y -= 1
                    if self.grid[y][current_x] != 0:  # Hit another vehicle
                        break
                    possible_moves.append((vehicle.label, current_x, y))
                
                # Check moves downward
                y = current_y
                while y + vehicle.length < self.grid_size:  # Try moving down
                    y += 1
                    if self.grid[y + vehicle.length - 1][current_x] != 0:  # Hit another vehicle
                        break
                    possible_moves.append((vehicle.label, current_x, y))
        
        return possible_moves


    def make_move(self, move):
        """Apply a move to the current state and return a new state.
        move is a tuple (vehicle_label, new_x, new_y)"""
        vehicle_label, new_x, new_y = move
        
        # Create new list of vehicles with updated position
        new_vehicles = []
        for vehicle in self.vehicles:
            if vehicle.label == vehicle_label:
                # Create new vehicle with updated position
                new_vehicle = Vehicle(
                    label=vehicle.label,
                    orientation=vehicle.orientation,
                    length=vehicle.length,
                    x=new_x,
                    y=new_y
                )
            else:
                # Create new vehicle with same position
                new_vehicle = Vehicle(
                    label=vehicle.label,
                    orientation=vehicle.orientation,
                    length=vehicle.length,
                    x=vehicle.x,
                    y=vehicle.y
                )
            new_vehicles.append(new_vehicle)
        
        # Create new game state with updated vehicles
        new_state = UnblockMe(self.grid_size, [])  # Create empty state
        new_state.vehicles = new_vehicles  # Set vehicles directly
        
        # Rebuild the grid
        new_state.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        for vehicle in new_vehicles:
            new_state.place_vehicle(vehicle)
            
        return new_state
    

    def is_solved(self) :
        """Check if the puzzle is solved (red car can exit)"""
        red_car = next((v for v in self.vehicles if v.label == 1), None)
        if not red_car:
            return False
        return (red_car.orientation == 'h' and 
                red_car.x + red_car.length == self.grid_size)

    def to_game_state(self):
        """Convert current game to GameState for storage"""
        return GameState(
            vehicles=[v.copy() for v in self.vehicles],
            grid_size=self.grid_size
        )

    def __str__(self):
        """String representation of the game grid"""
        return "\n".join(" ".join(map(str, row)) for row in self.grid)
   