"""Script to run the ML Pipeline."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from core import create_initial_state, compile_pipeline


def main():
    """Run the ML Pipeline."""
    print("Starting Enhanced ML Pipeline...")

    # Load configuration
    config = load_config()
    print(f"Loaded configuration: {config.mlflow.experiment_name}")

    # Create initial state
    initial_state = create_initial_state(config.to_dict())

    # Compile and run pipeline
    pipeline = compile_pipeline()
    result = pipeline.invoke(initial_state)

    print(f"\nPipeline Status: {result.get('pipeline_status', 'unknown')}")
    print(f"Completed Nodes: {len(result.get('completed_nodes', []))}")
    print(f"Best Model: {result.get('best_model_name', 'N/A')}")


if __name__ == "__main__":
    main()
