"""split_data node for ML Pipeline."""

from core.state import PipelineState, update_state, mark_node_completed


def split_data_node(state: PipelineState) -> PipelineState:
    """
    Split data into train/test sets

    Args:
        state: Current pipeline state

    Returns:
        Updated pipeline state
    """
    node_name = "split_data"

    try:
        # TODO: Implement split_data logic

        updated_state = update_state(
            state,
            current_node=node_name,
        )

        return mark_node_completed(updated_state, node_name)

    except Exception as e:
        from core.state import add_error
        return add_error(state, node_name, e)
