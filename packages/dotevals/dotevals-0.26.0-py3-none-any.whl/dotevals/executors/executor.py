"""Base class for executor plugins."""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import Any, TypedDict

from tenacity import AsyncRetrying, Retrying

from dotevals.exceptions import InvalidResultError
from dotevals.models import EvaluationSummary, Record, Result, Score
from dotevals.progress import BaseProgressManager, SingleProgress, get_dataset_info
from dotevals.sessions import SessionManager


class DatasetInfo(TypedDict, total=False):
    """Type for dataset information dictionary."""

    name: str
    total_rows: int | None


class Executor(ABC):
    """Abstract base class for evaluation executor plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this executor (e.g., 'foreach', 'batch')."""
        ...

    async def execute(
        self,
        eval_fn: Callable,
        column_spec: str,
        dataset: Iterable,
        session_manager: SessionManager,
        samples: int | None = None,
        progress_manager: BaseProgressManager | None = None,
        retries: AsyncRetrying | Retrying | None = None,
        **kwargs: Any,
    ) -> EvaluationSummary:
        """Execute the evaluation using this strategy.

        Args:
            eval_fn: The evaluation function to execute
            column_spec: Comma-separated column names
            dataset: Dataset to evaluate
            session_manager: Session manager for tracking results
            samples: Optional number of samples to process
            progress_manager: Optional progress manager for tracking
            retries: Optional retry configuration
            **kwargs: Additional arguments for execution

        Returns:
            EvaluationSummary containing all results
        """

        # Start evaluation
        session_manager.start_evaluation()

        columns = [col.strip() for col in column_spec.split(",")]
        dataset_info = get_dataset_info(dataset)

        # Get completed items and prepare for retry
        completed_items = session_manager.storage.completed_items(
            session_manager.current_experiment, session_manager.current_evaluation
        )
        completed_ids = set(completed_items)

        # Remove error results for items that will be retried
        self._remove_error_results_for_retry(session_manager, completed_ids)

        # Prepare dataset items (filtering completed ones)
        dataset_items = self._prepare_dataset_items(
            dataset, columns, completed_ids, samples
        )

        # No progress manager is passed in interactive mode
        if progress_manager is None:
            progress_manager = SingleProgress()

        # Delegate to sync or async execution
        if asyncio.iscoroutinefunction(eval_fn):
            await self._execute_async(
                eval_fn,
                columns,
                dataset_items,
                retries,
                session_manager,
                progress_manager,
                dataset_info,
                **kwargs,
            )
        else:
            self._execute_sync(
                eval_fn,
                columns,
                dataset_items,
                retries,
                session_manager,
                progress_manager,
                dataset_info,
                **kwargs,
            )

        # Finish the evaluation
        session_manager.finish_evaluation()

        # Create and return summary
        results = session_manager.get_results()
        return EvaluationSummary(results)

    def _remove_error_results_for_retry(
        self, session_manager: SessionManager, completed_ids: set[int]
    ) -> None:
        """Remove error results for items that will be retried.

        Args:
            session_manager: Session manager with storage and current evaluation info
            completed_ids: Set of item IDs that have been successfully completed
        """
        all_results = session_manager.get_results()
        all_item_ids = {r.item_id for r in all_results}
        items_to_retry = all_item_ids - completed_ids

        # Batch remove error results for retry
        if items_to_retry:
            session_manager.storage.remove_error_results_batch(
                session_manager.current_experiment,
                session_manager.current_evaluation,
                list(items_to_retry),
            )

    def _prepare_dataset_items(
        self,
        dataset: Iterable,
        columns: list[str],
        completed_ids: set[int],
        samples: int | None,
    ) -> list[tuple[int, dict[str, Any] | Exception]]:
        """Prepare dataset items for processing.

        Args:
            dataset: Raw dataset iterable
            columns: Column names
            completed_ids: Set of already completed item IDs
            samples: Optional sample limit

        Returns:
            List of (item_id, row_dict_or_error) tuples ready for processing
        """
        dataset_items: list[tuple[int, dict[str, Any] | Exception]] = []
        for item_id, row_data in enumerate(dataset):
            if item_id not in completed_ids:
                try:
                    formatted_data = format_data(row_data, columns)
                    dataset_items.append((item_id, formatted_data))
                except ValueError as e:
                    # Store the error to be converted to error record later
                    dataset_items.append((item_id, e))

        # Limit the dataset to samples
        if samples is not None:
            dataset_items = dataset_items[:samples]

        return dataset_items

    @abstractmethod
    def _execute_sync(
        self,
        eval_fn: Callable,
        columns: list[str],
        dataset_items: list[tuple[int, dict[str, Any] | Exception]],
        retries: AsyncRetrying | Retrying | None,
        session_manager: SessionManager,
        progress_manager: BaseProgressManager,
        dataset_info: DatasetInfo,
        **kwargs: Any,
    ) -> None:
        """Execute synchronous evaluation.

        Args:
            eval_fn: Synchronous evaluation function
            columns: Column names
            dataset_items: Prepared dataset items
            retries: Retry configuration
            session_manager: Session manager
            progress_manager: Progress manager
            dataset_info: Dataset metadata
            **kwargs: Additional arguments to pass to eval_fn
        """
        ...

    @abstractmethod
    async def _execute_async(
        self,
        eval_fn: Callable,
        columns: list[str],
        dataset_items: list[tuple[int, dict[str, Any] | Exception]],
        retries: AsyncRetrying | Retrying | None,
        session_manager: SessionManager,
        progress_manager: BaseProgressManager,
        dataset_info: DatasetInfo,
        **kwargs: Any,
    ) -> None:
        """Execute asynchronous evaluation.

        Args:
            eval_fn: Asynchronous evaluation function
            columns: Column names
            dataset_items: Prepared dataset items
            retries: Retry configuration
            session_manager: Session manager
            progress_manager: Progress manager
            dataset_info: Dataset metadata
            **kwargs: Additional arguments to pass to eval_fn
        """
        ...

    def _create_error_record(
        self, item_id: int, row_dict: dict[str, Any], error: Exception
    ) -> Record:
        """Create an error record from an exception.

        Args:
            item_id: Item ID that caused the error
            row_dict: Row data that caused the error
            error: The exception that occurred

        Returns:
            Record with error information
        """
        return Record(
            result=Result(Score(name="error", value=0.0, metrics=[])),
            item_id=item_id,
            dataset_row=row_dict,
            error=f"{type(error).__name__}: {error}",
        )

    def _process_result(self, result: Any) -> Result:
        """Process evaluation result into a standardized Result object.

        Args:
            result: Raw result from evaluation function

        Returns:
            Standardized Result object
        """
        if isinstance(result, Result):
            return result
        elif isinstance(result, Score):
            return Result(result)
        else:
            raise InvalidResultError("eval_fn", type(result))


def format_data(row_data: Any, columns: list[str]) -> dict[str, Any]:
    """Format dataset row into a dictionary.

    Args:
        row_data: Raw row data (tuple, list, dict, or single value)
        columns: Column names to map to

    Returns:
        Dictionary mapping column names to values
    """
    if isinstance(row_data, dict):
        # If dict, use columns as keys to extract values
        # This allows the dict to have extra keys that aren't needed
        return {col: row_data.get(col) for col in columns}
    elif isinstance(row_data, tuple | list):
        # If tuple/list, zip with column names
        if len(row_data) < len(columns):
            # Not enough values - this is an error
            raise ValueError(
                f"Row has {len(row_data)} values but {len(columns)} columns specified"
            )
        # If there are extra values, just ignore them (take only what we need)
        return dict(zip(columns, row_data[: len(columns)]))
    else:
        # Single value - must have single column
        if len(columns) != 1:
            raise ValueError(
                f"Single value provided but {len(columns)} columns specified"
            )
        return {columns[0]: row_data}
