"""Logistic Regression node for ML Pipeline."""

from sklearn.linear_model import LogisticRegression
from core.state import PipelineState, update_state, mark_node_completed, AlgorithmResult
from tuning.grid_search import GridSearchWrapper


def logistic_regression_node(state: PipelineState) -> PipelineState:
    """
    Train Logistic Regression with hyperparameter tuning.

    Args:
        state: Current pipeline state

    Returns:
        Updated pipeline state with algorithm results
    """
    node_name = "logistic_regression"
    algorithm_name = "logistic_regression"

    try:
        # Check if this algorithm was selected
        selected_algorithms = state.get("selected_algorithms", [])
        if algorithm_name not in selected_algorithms:
            return state  # Skip if not selected

        X_train = state["X_train"]
        X_test = state["X_test"]
        y_train = state["y_train"]
        y_test = state["y_test"]

        # TODO: Define parameter grid
        param_grid = {}

        # Train with GridSearchCV
        tuner = GridSearchWrapper(
            estimator=LogisticRegression(),
            param_grid=param_grid,
            cv=state["pipeline_config"]["tuning"]["cv_folds"]
        )

        result = tuner.fit_predict(X_train, y_train, X_test, y_test)

        # Store results
        algorithm_results = state.get("algorithm_results", {})
        algorithm_results[algorithm_name] = result

        updated_state = update_state(
            state,
            algorithm_results=algorithm_results,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        from core.state import add_error
        return add_error(state, node_name, e)
