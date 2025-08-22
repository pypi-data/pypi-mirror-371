"""ForEach executor implementation."""

from collections.abc import Callable, Generator
from functools import partial
from typing import Any

from tenacity import AsyncRetrying, Retrying

from dotevals.concurrency import (
    Adaptive,
    AsyncConcurrencyStrategy,
    Sequential,
    SyncConcurrencyStrategy,
)
from dotevals.executors.executor import DatasetInfo, Executor
from dotevals.executors.registry import executor_registry
from dotevals.models import Record
from dotevals.progress import BaseProgressManager
from dotevals.retry import create_default_async_retrying, create_default_sync_retrying
from dotevals.sessions import SessionManager


class ForEachExecutor(Executor):
    """Default ForEach executor plugin."""

    @property
    def name(self) -> str:
        return "foreach"

    def __init__(
        self,
        retries: AsyncRetrying | Retrying | None = None,
        concurrency: SyncConcurrencyStrategy | AsyncConcurrencyStrategy | None = None,
    ) -> None:
        """Initialize ForEach executor.

        Args:
            retries: Optional retry configuration
            concurrency: Optional concurrency strategy (Sequential, Adaptive, etc.)
        """
        self.retries = retries
        self.concurrency = concurrency

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
        """Execute synchronous evaluation for each item."""
        concurrency = kwargs.pop("concurrency", self.concurrency)

        # Default concurrency strategy
        if concurrency is None or not isinstance(concurrency, SyncConcurrencyStrategy):
            concurrency = Sequential()

        if retries is None:
            retries = create_default_sync_retrying()

        def process_item(item_id: int, row_data: dict[str, Any] | Exception) -> Record:
            """Process a single dataset item."""
            if isinstance(row_data, Exception):
                return self._create_error_record(item_id, {}, row_data)

            try:
                # Run evaluation with retries
                for attempt in retries:
                    with attempt:
                        result = eval_fn(**row_data, **kwargs)

                # Process the result
                result = self._process_result(result)

                return Record(
                    result=result,
                    item_id=item_id,
                    dataset_row=row_data,
                    error=result.error,  # Propagate error from Result to Record
                )
            except Exception as e:
                # Convert exceptions to error records
                return self._create_error_record(item_id, row_data, e)

        def create_tasks() -> Generator[Callable[[], Record], None, None]:
            """Create a task for each dataset item."""
            for item_id, row_data in dataset_items:
                yield partial(process_item, item_id, row_data)

        total_items = len(dataset_items)

        progress_manager.start_evaluation(
            dataset_info.get("name", "dataset"), total_items, dataset_info
        )

        # Execute all tasks using the concurrency strategy
        for result in concurrency.execute(create_tasks()):
            session_manager.add_results([result])
            progress_manager.update_evaluation_progress(
                dataset_info.get("name", "dataset"), result=result
            )

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
        """Execute asynchronous evaluation for each item."""
        concurrency = kwargs.pop("concurrency", self.concurrency)

        # Default concurrency strategy for async
        if concurrency is None or not isinstance(concurrency, AsyncConcurrencyStrategy):
            concurrency = Adaptive()

        if retries is None:
            retries = create_default_async_retrying()

        async def process_item(
            item_id: int, row_data: dict[str, Any] | Exception
        ) -> Record:
            """Process a single dataset item."""
            if isinstance(row_data, Exception):
                return self._create_error_record(item_id, {}, row_data)

            try:
                # Run evaluation with retries (create fresh instance for each task)
                task_retries = retries.copy() if retries else retries
                async for attempt in task_retries:
                    with attempt:
                        result = await eval_fn(**row_data, **kwargs)

                # Process the result
                result = self._process_result(result)

                return Record(
                    result=result,
                    item_id=item_id,
                    dataset_row=row_data,
                    error=result.error,  # Propagate error from Result to Record
                )
            except Exception as e:
                # Convert exceptions to error records
                return self._create_error_record(item_id, row_data, e)

        def create_tasks() -> Generator[Callable[[], Any], None, None]:
            """Create an async task for each dataset item."""
            for item_id, row_data in dataset_items:
                yield partial(process_item, item_id, row_data)

        total_items = len(dataset_items)

        progress_manager.start_evaluation(
            dataset_info.get("name", "dataset"), total_items, dataset_info
        )

        # Execute all tasks using the async concurrency strategy
        async for result in concurrency.execute(create_tasks()):
            session_manager.add_results([result])
            progress_manager.update_evaluation_progress(
                dataset_info.get("name", "dataset"), result=result
            )


# Register with the global registry
executor_registry.register("foreach", ForEachExecutor())
