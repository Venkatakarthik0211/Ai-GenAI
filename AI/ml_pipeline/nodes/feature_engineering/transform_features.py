"""transform_features node for ML Pipeline."""

from core.state import PipelineState, update_state, mark_node_completed


def transform_features_node(state: PipelineState) -> PipelineState:
    """
    Transform features

    Args:
        state: Current pipeline state

    Returns:
        Updated pipeline state
    """
    node_name = "transform_features"

    try:
        # TODO: Implement transform_features logic

        updated_state = update_state(
            state,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        from core.state import add_error
        return add_error(state, node_name, e)
