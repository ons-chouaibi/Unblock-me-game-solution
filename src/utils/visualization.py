import os
import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

logger = logging.getLogger(__name__)

def setup_plotting_style():
    """Configure matplotlib style for consistent visualization."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

def save_figure(fig, filepath: str, file_format: str = 'png', dpi: int = 300):
    """Save a matplotlib figure with proper error handling."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the figure
        fig.savefig(filepath, format=file_format, dpi=dpi, bbox_inches='tight')
        logger.info(f"Saved figure to {filepath}")
        
    except Exception as e:
        logger.error(f"Failed to save figure to {filepath}: {str(e)}")
        raise

def plot_comparisons(
    df: pd.DataFrame, 
    save_dir: str = "results",
    file_format: str = "png",
    dpi: int = 300,
    show_progress: bool = True,
    heuristic_column: str = 'heuristic',
    time_column: str = 'time',
    nodes_column: str = 'nodes',
    puzzle_column: str = 'puzzle'
):
    """
    Create and save comparison plots for heuristic performance.
    
    Args:
        df: DataFrame containing the performance data
        save_dir: Directory to save the generated plots
        file_format: Format for saving plots (png, pdf, svg, etc.)
        dpi: Resolution for saved images
        show_progress: Whether to show a progress bar
        heuristic_column: Column name for heuristic identifier
        time_column: Column name for execution time
        nodes_column: Column name for nodes explored
        puzzle_column: Column name for puzzle identifier
    """
    
    # Validate inputs
    if df.empty:
        logger.warning("Empty DataFrame provided, no plots will be generated")
        return
    
    required_columns = [heuristic_column, time_column, nodes_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {missing_columns}")
    
    # Setup consistent style
    setup_plotting_style()
    
    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # List of plots to create
    plot_functions = [
        _plot_average_time,
        _plot_average_nodes,
        _plot_time_vs_nodes,
        _plot_performance_by_puzzle
    ]
    
    # Use tqdm if show_progress is True
    iterator = tqdm(plot_functions, desc="Generating plots") if show_progress else plot_functions
    
    # Generate and save each plot
    for plot_func in iterator:
        try:
            fig = plot_func(df, heuristic_column, time_column, nodes_column, puzzle_column)
            
            # Get the plot name from the function name
            plot_name = plot_func.__name__.replace('_plot_', '')
            filepath = os.path.join(save_dir, f"{plot_name}.{file_format}")
            
            save_figure(fig, filepath, file_format, dpi)
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Error generating plot with {plot_func.__name__}: {str(e)}")
            
    logger.info(f"All plots saved in '{save_dir}' directory")

def _plot_average_time(df, heuristic_col, time_col, nodes_col, puzzle_col):
    """Plot average execution time by heuristic."""
    fig, ax = plt.subplots()
    
    time_df = df.groupby(heuristic_col)[time_col].mean().sort_values()
    
    time_df.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Average Execution Time by Heuristic')
    ax.set_ylabel('Time (seconds)')
    ax.set_xlabel('Heuristic')
    
    # Add value labels on top of bars
    for i, v in enumerate(time_df):
        ax.text(i, v + 0.1, f"{v:.2f}s", ha='center', va='bottom', fontsize=9, rotation=0)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig

def _plot_average_nodes(df, heuristic_col, time_col, nodes_col, puzzle_col):
    """Plot average nodes explored by heuristic."""
    fig, ax = plt.subplots()
    
    nodes_df = df.groupby(heuristic_col)[nodes_col].mean().sort_values()
    
    nodes_df.plot(kind='bar', color='lightgreen', ax=ax)
    ax.set_title('Average Explored States by Heuristic')
    ax.set_ylabel('Number of Nodes')
    ax.set_xlabel('Heuristic')
    
    # Add value labels on top of bars
    for i, v in enumerate(nodes_df):
        ax.text(i, v + 1, f"{int(v)}", ha='center', va='bottom', fontsize=9, rotation=0)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig

def _plot_time_vs_nodes(df, heuristic_col, time_col, nodes_col, puzzle_col):
    """Plot time vs nodes with heuristics as different point types."""
    fig, ax = plt.subplots()
    
    # Using different colors for different heuristics
    unique_heuristics = df[heuristic_col].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_heuristics)))
    
    for i, heuristic in enumerate(unique_heuristics):
        subset = df[df[heuristic_col] == heuristic]
        ax.scatter(
            subset[time_col], 
            subset[nodes_col], 
            label=heuristic, 
            alpha=0.7,
            color=colors[i],
            edgecolor='w',
            s=60
        )
    
    ax.set_xlabel('Execution Time (seconds)')
    ax.set_ylabel('Explored States')
    ax.set_title('Performance Comparison: Time vs. Explored States')
    ax.legend(title='Heuristic')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return fig

def _plot_performance_by_puzzle(df, heuristic_col, time_col, nodes_col, puzzle_col):
    """Plot performance comparison across puzzles."""
    if puzzle_col not in df.columns:
        logger.warning(f"Cannot create puzzle comparison plot: '{puzzle_col}' column missing")
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"Cannot create plot: '{puzzle_col}' column not found", 
                ha='center', va='center')
        return fig
    
    # Extract puzzle numbers for better sorting
    df = df.copy()
    df['puzzle_num'] = df[puzzle_col].str.extract(r'(\d+)').astype(int)
    
    # Group by puzzle and heuristic, calculate mean time
    pivot_df = df.pivot_table(
        index='puzzle_num', 
        columns=heuristic_col, 
        values=time_col, 
        aggfunc='mean'
    ).sort_index()
    
    fig, ax = plt.subplots(figsize=(14, 8))
    pivot_df.plot(kind='bar', ax=ax)
    
    ax.set_title('Execution Time by Puzzle and Heuristic')
    ax.set_xlabel('Puzzle Number')
    ax.set_ylabel('Time (seconds)')
    ax.set_xticks(range(len(pivot_df)))
    ax.set_xticklabels([f'Puzzle {i}' for i in pivot_df.index], rotation=90)
    
    ax.legend(title='Heuristic')
    plt.tight_layout()
    
    return fig
