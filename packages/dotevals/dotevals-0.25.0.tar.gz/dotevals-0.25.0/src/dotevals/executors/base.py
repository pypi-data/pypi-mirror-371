"""Base protocol for executor plugins."""

from collections.abc import Callable, Iterable
from typing import Any, Protocol

from dotevals.models import EvaluationSummary
from dotevals.sessions import SessionManager


class ExecutorPlugin(Protocol):
    """Protocol that all evaluation executor plugins must implement."""

    @property
    def name(self) -> str:
        """Unique name for this executor (e.g., 'foreach', 'batch')."""
        ...

    async def execute(
        self,
        eval_fn: Callable,
        column_spec: str,
        dataset: Iterable,
        session_manager: SessionManager,
        **kwargs: Any,
    ) -> EvaluationSummary | Any:
        """Execute the evaluation using this strategy.

        Args:
            eval_fn: The evaluation function to execute
            column_spec: Comma-separated column names
            dataset: Dataset to evaluate
            session_manager: Session manager for tracking results
            **kwargs: Additional arguments for execution

        Returns:
            EvaluationSummary for immediate executors
            Custom handle/results for async executors (e.g., AsyncBatchResultsHandle)
        """
        ...
