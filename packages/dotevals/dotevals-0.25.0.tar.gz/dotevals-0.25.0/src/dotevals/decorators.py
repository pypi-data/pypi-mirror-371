"""
Decorators for evaluation functions.
"""

import asyncio
import functools
from collections.abc import Callable, Coroutine, Iterable
from typing import Any, TypeAlias

import pytest
from tenacity import AsyncRetrying, Retrying

from dotevals.concurrency import AsyncConcurrencyStrategy, SyncConcurrencyStrategy
from dotevals.executors.batch import BatchExecutor
from dotevals.executors.foreach import ForEachExecutor
from dotevals.executors.registry import executor_registry
from dotevals.models import EvaluationSummary
from dotevals.progress import BaseProgressManager
from dotevals.sessions import SessionManager

# Type aliases
ColumnSpec: TypeAlias = str
DatasetValue: TypeAlias = str | int | float | bool | None | dict | list
DatasetRow: TypeAlias = (
    tuple[DatasetValue, ...]
    | list[DatasetValue]
    | dict[str, DatasetValue]
    | DatasetValue
)


class ForEach:
    """Evaluator that processes each dataset item individually."""

    def __init__(
        self,
        retries: AsyncRetrying | Retrying | None = None,
        concurrency: SyncConcurrencyStrategy | AsyncConcurrencyStrategy | None = None,
    ) -> None:
        """Initialize ForEach decorator for individual item processing.

        ForEach processes each dataset item separately, calling your evaluation
        function once per item.

        For batch processing (calling your function with multiple items at once),
        use the `@batch` decorator instead.

        Args:
            retries: Optional retry configuration
            concurrency: Optional concurrency strategy (Sequential, Adaptive, etc.)

        Example:

            @foreach("question,answer", dataset)
            def eval_qa(question, answer, model):
                response = model.generate(question)  # One call per item
                return Result(exact_match(response, answer))
        """
        self.retries = retries
        self.concurrency = concurrency

    def __call__(
        self,
        column_spec: ColumnSpec,
        dataset: Iterable[DatasetRow],
        *,
        retries: AsyncRetrying | Retrying | None = None,
        concurrency: SyncConcurrencyStrategy | AsyncConcurrencyStrategy | None = None,
    ) -> Callable[[Callable], Callable]:
        """Create decorator for evaluation functions."""
        # Use passed kwargs or fall back to instance defaults
        return create_decorator(
            "foreach",
            column_spec,
            dataset,
            retries=retries or self.retries,
            concurrency=concurrency or self.concurrency,
        )

    def __getattr__(self, dataset_name: str) -> Callable:
        """Support dataset access via attribute syntax."""
        # Avoid conflicts with special methods that tools might probe for
        if dataset_name.startswith("__") and dataset_name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{dataset_name}'"
            )
        return create_dataset_decorator(
            "foreach", dataset_name, retries=self.retries, concurrency=self.concurrency
        )


foreach = ForEach()


class Batch:
    """Evaluator that processes dataset items in batches."""

    def __init__(
        self,
        retries: AsyncRetrying | Retrying | None = None,
    ) -> None:
        """Initialize `@batch` decorator for batch processing of multiple items at once.

        Batch processes multiple dataset items together, calling your evaluation
        function with lists/arrays of data.

        For individual item processing (calling your function once per item),
        use the `@foreach` decorator instead.

        Args:
            retries: Optional retry configuration

        Example:

            @batch("questions,answers", dataset, batch_size=32)
            def eval_qa_batch(questions, answers, model):
                # questions = ["Q1", "Q2", ..., "Q32"]
                # answers = ["A1", "A2", ..., "A32"]
                responses = model.batch_generate(questions)  # One call per batch
                return [Result(exact_match(r, a)) for r, a in zip(responses, answers)]
        """
        self.retries = retries

    def __call__(
        self,
        column_spec: ColumnSpec,
        dataset: Iterable[DatasetRow],
        *,
        batch_size: int | None = None,
        retries: AsyncRetrying | Retrying | None = None,
    ) -> Callable[[Callable], Callable]:
        """Create decorator for evaluation functions."""

        # Use passed kwargs or fall back to instance defaults
        return create_decorator(
            "batch",
            column_spec,
            dataset,
            retries=retries or self.retries,
            batch_size=batch_size,
        )

    def __getattr__(self, dataset_name: str) -> Callable:
        """Support dataset access via attribute syntax."""
        # Avoid conflicts with special methods that tools might probe for
        if dataset_name.startswith("__") and dataset_name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{dataset_name}'"
            )
        return create_dataset_decorator("batch", dataset_name, retries=self.retries)


def create_decorator(
    executor_type: str,
    column_spec: ColumnSpec,
    dataset: Iterable[DatasetRow],
    **kwargs: Any,
) -> Callable[[Callable], Callable]:
    """Create a decorator for evaluation functions.

    Args:
        executor_type: Type of executor to use ("foreach" or "batch")
        column_spec: Comma-separated list of column names
        dataset: Dataset to evaluate on
        **kwargs: Configuration kwargs to pass to the executor (e.g., retries, concurrency, batch_size)

    Returns:
        Decorator function
    """

    def decorator(
        eval_fn: Callable,
    ) -> Callable[..., EvaluationSummary | Coroutine[Any, Any, EvaluationSummary]]:
        # Mark for pytest
        eval_fn = pytest.mark.dotevals(eval_fn)  # type: ignore
        eval_fn._executor_type = executor_type  # type: ignore
        eval_fn._column_spec = column_spec  # type: ignore
        eval_fn._dataset = dataset  # type: ignore
        eval_fn._column_names = [col.strip() for col in column_spec.split(",")]  # type: ignore

        if asyncio.iscoroutinefunction(eval_fn):
            # Create async wrapper
            @functools.wraps(eval_fn)
            async def async_wrapper(
                session_manager: SessionManager,
                samples: int | None,
                progress_manager: BaseProgressManager | None = None,
                **runtime_kwargs: Any,
            ) -> EvaluationSummary:
                # Get executor from registry or create default
                executor = executor_registry.get(executor_type)
                if executor is None:
                    if executor_type == "foreach":
                        # Don't pass retries here - will be passed to execute()
                        executor = ForEachExecutor(
                            concurrency=kwargs.get("concurrency"),
                        )
                    elif executor_type == "batch":
                        # Don't pass retries here - will be passed to execute()
                        executor = BatchExecutor()
                    else:
                        raise RuntimeError(f"Unknown executor type: {executor_type}")

                # Extract samples and progress_manager from runtime kwargs if provided
                final_samples = runtime_kwargs.pop("samples", samples)
                final_progress_manager = runtime_kwargs.pop(
                    "progress_manager", progress_manager
                )
                final_retries = runtime_kwargs.pop("retries", kwargs.get("retries"))

                # Remove retries from kwargs since we're passing it explicitly
                decorator_kwargs = kwargs.copy()
                decorator_kwargs.pop("retries", None)

                # Merge remaining kwargs
                all_kwargs = {
                    **decorator_kwargs,  # Decorator-time kwargs (e.g., concurrency, batch_size)
                    **runtime_kwargs,  # Runtime kwargs override decorator kwargs
                }

                return await executor.execute(
                    eval_fn,
                    column_spec,
                    dataset,
                    session_manager,
                    samples=final_samples,
                    progress_manager=final_progress_manager,
                    retries=final_retries,
                    **all_kwargs,
                )

            return async_wrapper
        else:
            # Create sync wrapper that returns a coroutine
            @functools.wraps(eval_fn)
            def sync_wrapper(
                session_manager: SessionManager,
                samples: int | None,
                progress_manager: BaseProgressManager | None = None,
                **runtime_kwargs: Any,
            ) -> Coroutine[Any, Any, EvaluationSummary]:
                async def run() -> EvaluationSummary:
                    # Get executor from registry or create default
                    executor = executor_registry.get(executor_type)
                    if executor is None:
                        if executor_type == "foreach":
                            # Don't pass retries here - will be passed to execute()
                            executor = ForEachExecutor(
                                concurrency=kwargs.get("concurrency"),
                            )
                        elif executor_type == "batch":
                            # Don't pass retries here - will be passed to execute()
                            executor = BatchExecutor()
                        else:
                            raise RuntimeError(
                                f"Unknown executor type: {executor_type}"
                            )

                    # Extract samples and progress_manager from runtime kwargs if provided
                    final_samples = runtime_kwargs.pop("samples", samples)
                    final_progress_manager = runtime_kwargs.pop(
                        "progress_manager", progress_manager
                    )
                    final_retries = runtime_kwargs.pop("retries", kwargs.get("retries"))

                    # Remove retries from kwargs since we're passing it explicitly
                    decorator_kwargs = kwargs.copy()
                    decorator_kwargs.pop("retries", None)

                    # Merge remaining kwargs
                    all_kwargs = {
                        **decorator_kwargs,  # Decorator-time kwargs (e.g., concurrency, batch_size)
                        **runtime_kwargs,  # Runtime kwargs override decorator kwargs
                    }

                    return await executor.execute(
                        eval_fn,
                        column_spec,
                        dataset,
                        session_manager,
                        samples=final_samples,
                        progress_manager=final_progress_manager,
                        retries=final_retries,
                        **all_kwargs,
                    )

                # Always return the coroutine
                # The caller is responsible for awaiting or running it
                return run()

            return sync_wrapper

    return decorator


batch = Batch()


def create_dataset_decorator(
    executor_type: str,
    dataset_name: str,
    **kwargs: Any,
) -> Callable:
    """Create a decorator for dataset attribute access.

    Args:
        executor_type: Type of executor to use ("foreach" or "batch")
        dataset_name: Name of the dataset
        **kwargs: Configuration kwargs to pass to the executor (e.g., retries, concurrency, batch_size)

    Returns:
        Dataset decorator function
    """

    def dataset_decorator(
        split: str | None = None, **dataset_kwargs: Any
    ) -> Callable[[Callable], Callable]:
        from dotevals.datasets import _registry

        # Extract batch_size if present
        batch_size = dataset_kwargs.pop("batch_size", None)

        dataset_class = _registry.get_dataset_class(dataset_name)
        dataset_instance = (
            dataset_class(split, **dataset_kwargs)
            if split is not None
            else dataset_class(**dataset_kwargs)
        )
        column_spec = ",".join(dataset_class.columns)

        # Add batch_size to kwargs if it was provided
        if batch_size is not None:
            kwargs["batch_size"] = batch_size

        return create_decorator(executor_type, column_spec, dataset_instance, **kwargs)

    dataset_decorator._dataset_name = dataset_name  # type: ignore
    return dataset_decorator


def __getattr__(name: str) -> Any:
    """Dynamic attribute access for executor-based decorators.

    This allows importing decorators from plugins like:
        >>> from dotevals import async_batch  # If plugin installed

    It checks if there's a registered executor with this name and if so,
    tries to import the corresponding decorator from the plugin package.
    """
    # Check if there's an executor registered with this name
    from dotevals.executors.registry import executor_registry

    executor = executor_registry.get(name)
    if executor is not None:
        # Convention: plugins should provide a decorator with the same name as the executor
        package_name = f"dotevals_{name}"  # e.g., dotevals_async_batch

        import importlib

        try:
            package = importlib.import_module(package_name)
            if hasattr(package, name):
                return getattr(package, name)
            else:
                raise AttributeError(
                    f"Executor '{name}' is registered but package '{package_name}' "
                    f"does not provide a '{name}' decorator"
                )
        except ImportError:
            raise AttributeError(
                f"Executor '{name}' is registered but could not import decorator '{name}' "
                f"from package '{package_name}'. The package may not follow the expected "
                f"naming convention or may not export the decorator."
            )

    # Default behavior - attribute not found
    raise AttributeError(f"module 'dotevals.decorators' has no attribute '{name}'")
