import os
import sys

def main():
    # Get the project root (parent of bin/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)

    # Import the main module and call its main() function
    from src.main import main as solver_main
    solver_main()

if __name__ == "__main__":
    main()