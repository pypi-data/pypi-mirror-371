"""Tests for @foreach and @batch decorators."""

import asyncio

import pytest

from dotevals import Batch, ForEach, batch, foreach
from dotevals.decorators import create_dataset_decorator, create_decorator
from dotevals.evaluators import exact_match
from dotevals.models import Result
from dotevals.sessions import SessionManager


@pytest.fixture
def simple_dataset():
    """Basic 3-item dataset for testing."""
    return [("a", 1), ("b", 2), ("c", 3)]


@pytest.fixture
def session_manager(tmp_path):
    """Session manager with JSON storage."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return SessionManager(
        evaluation_name=f"test_eval_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )


class TestForEachDecorator:
    """Tests for @foreach decorator functionality."""

    def test_foreach_decorator_sync_function(self, simple_dataset, session_manager):
        """Test @foreach decorator with synchronous function."""
        import asyncio

        @foreach("text,number", simple_dataset)
        def eval_fn(text, number):
            return Result(exact_match(text, text))

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)
        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    @pytest.mark.asyncio
    async def test_foreach_decorator_async_function(
        self, simple_dataset, session_manager
    ):
        """Test @foreach decorator with asynchronous function."""

        @foreach("text,number", simple_dataset)
        async def eval_fn(text, number):
            await asyncio.sleep(0)  # Simulate async work
            return Result(exact_match(text, text))

        summary = await eval_fn(session_manager, samples=None)
        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    def test_foreach_instance_with_retries(self, simple_dataset, tmp_path):
        """Test ForEach instance with custom retry configuration."""
        import asyncio

        from tenacity import Retrying, stop_after_attempt

        foreach_with_retry = ForEach(retries=Retrying(stop=stop_after_attempt(3)))

        @foreach_with_retry("text", [("a",)])
        def eval_fn(text):
            return Result(exact_match(text, "a"))

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_retry_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    def test_foreach_decorator_additional_kwargs(self, simple_dataset, session_manager):
        """Test that additional kwargs are passed through to the evaluation function."""
        import asyncio

        captured_kwargs = []

        @foreach("text,number", simple_dataset)
        def eval_fn(text, number, custom_param=None, another_param=42):
            captured_kwargs.append(
                {"custom_param": custom_param, "another_param": another_param}
            )
            return Result(exact_match(text, text))

        coro = eval_fn(
            session_manager, samples=None, custom_param="test_value", another_param=100
        )
        asyncio.run(coro)

        assert len(captured_kwargs) == 3
        for kwargs in captured_kwargs:
            assert kwargs["custom_param"] == "test_value"
            assert kwargs["another_param"] == 100

    def test_foreach_decorator_marks_pytest(self, simple_dataset):
        """Test that @foreach decorator adds pytest marks."""

        @foreach("text", simple_dataset)
        def eval_fn(text):
            return Result(exact_match(text, text))

        # Check that the function has the required attributes for pytest plugin
        assert hasattr(eval_fn, "_executor_type")
        assert eval_fn._executor_type == "foreach"
        assert hasattr(eval_fn, "_column_spec")
        assert eval_fn._column_spec == "text"
        assert hasattr(eval_fn, "_dataset")
        assert eval_fn._dataset == simple_dataset
        assert hasattr(eval_fn, "_column_names")
        assert eval_fn._column_names == ["text"]

    def test_foreach_dataset_attribute_access(self, session_manager):
        """Test ForEach dataset attribute access (e.g., @foreach.dataset_name)."""
        # This would normally use a registered dataset
        # For testing, we'll verify the mechanism works
        foreach_instance = ForEach()

        # Test that __getattr__ works
        with pytest.raises(Exception):  # Will fail because dataset not registered
            foreach_instance.nonexistent_dataset()


class TestBatchDecorator:
    """Tests for @batch decorator functionality."""

    def test_batch_decorator_sync_function(self, simple_dataset, session_manager):
        """Test @batch decorator with synchronous function."""
        import asyncio

        @batch("text,number", simple_dataset)
        def eval_fn(text, number):
            # In batch mode, text and number are lists
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)
        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    @pytest.mark.asyncio
    async def test_batch_decorator_async_function(
        self, simple_dataset, session_manager
    ):
        """Test @batch decorator with asynchronous function."""

        @batch("text,number", simple_dataset)
        async def eval_fn(text, number):
            await asyncio.sleep(0)  # Simulate async work
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        summary = await eval_fn(session_manager, samples=None)
        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    def test_batch_decorator_with_size_parameter(self, session_manager):
        """Test @batch decorator with explicit batch size."""
        import asyncio

        dataset = [(str(i), i) for i in range(10)]
        call_count = 0
        batch_sizes = []

        @batch("text,number", dataset, batch_size=3)
        def eval_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)

        # Should be called 4 times with batch sizes: 3, 3, 3, 1
        assert call_count == 4
        assert batch_sizes == [3, 3, 3, 1]
        assert len(summary.results) == 10

    def test_batch_instance_with_size(self, session_manager):
        """Test Batch instance with custom size."""
        import asyncio

        dataset = [(str(i), i) for i in range(7)]
        batch_instance = Batch()
        call_count = 0
        batch_sizes = []

        @batch_instance("text,number", dataset, batch_size=4)
        def eval_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)

        # Should be called 2 times with batch sizes: 4, 3
        assert call_count == 2
        assert batch_sizes == [4, 3]
        assert len(summary.results) == 7

    def test_batch_single_result_for_entire_batch(
        self, simple_dataset, session_manager
    ):
        """Test batch function returning a single result for the entire batch."""
        import asyncio

        @batch("text,number", simple_dataset)
        def eval_fn(text, number):
            # Return a single result for the entire batch
            return Result(exact_match(True, True))

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)

        # Should create 3 records (one for each item) with the same result
        assert len(summary.results) == 3
        assert all(r.result.scores[0].value for r in summary.results)
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    def test_batch_decorator_marks_pytest(self, simple_dataset):
        """Test that @batch decorator adds pytest marks."""

        @batch("text,number", simple_dataset)
        def eval_fn(text, number):
            return [Result(exact_match(t, t)) for t in text]

        # Check that the function has the required attributes for pytest plugin
        assert hasattr(eval_fn, "_executor_type")
        assert eval_fn._executor_type == "batch"
        assert hasattr(eval_fn, "_column_spec")
        assert eval_fn._column_spec == "text,number"
        assert hasattr(eval_fn, "_dataset")
        assert eval_fn._dataset == simple_dataset
        assert hasattr(eval_fn, "_column_names")
        assert eval_fn._column_names == ["text", "number"]


class TestDecoratorPluginLoading:
    """Test plugin and external executor loading through decorators."""

    def test_plugin_decorator_not_found(self):
        """Test handling when a registered executor's plugin doesn't exist."""
        from unittest.mock import MagicMock, patch

        from dotevals.decorators import __getattr__ as decorators_getattr

        # Mock the registry to return a fake executor
        with patch("dotevals.executors.registry.executor_registry.get") as mock_get:
            mock_executor = MagicMock()
            mock_executor.name = "test_executor"
            mock_get.return_value = mock_executor

            # This should raise AttributeError when the package doesn't exist
            with pytest.raises(AttributeError, match="could not import decorator"):
                decorators_getattr("test_executor")

    def test_plugin_decorator_missing_attribute(self):
        """Test when plugin package exists but doesn't have the decorator."""
        from unittest.mock import MagicMock, patch

        from dotevals.decorators import __getattr__ as decorators_getattr

        with patch("dotevals.executors.registry.executor_registry.get") as mock_get:
            mock_executor = MagicMock()
            mock_get.return_value = mock_executor

            # Mock the import to succeed but not have the attribute
            with patch("importlib.import_module") as mock_import:
                mock_module = MagicMock()
                del mock_module.test_executor  # Ensure attribute doesn't exist
                mock_import.return_value = mock_module

                with pytest.raises(
                    AttributeError, match="does not provide a 'test_executor' decorator"
                ):
                    decorators_getattr("test_executor")

    def test_getattr_nonexistent_decorator(self):
        """Test __getattr__ with non-existent decorator."""
        from dotevals.decorators import __getattr__ as decorators_getattr

        with pytest.raises(AttributeError, match="has no attribute"):
            decorators_getattr("completely_nonexistent_decorator")


class TestDecoratorHelpers:
    """Tests for decorator helper functions."""

    def test_create_decorator_foreach_type(self):
        """Test create_decorator with foreach type."""

        dataset = [("a",), ("b",)]
        decorator = create_decorator("foreach", "text", dataset)

        @decorator
        def eval_fn(text):
            return Result(exact_match(text, text))

        assert hasattr(eval_fn, "_executor_type")
        assert eval_fn._executor_type == "foreach"

    def test_create_decorator_batch_type(self):
        """Test create_decorator with batch type."""

        dataset = [("a",), ("b",)]
        decorator = create_decorator("batch", "text", dataset)

        @decorator
        def eval_fn(text):
            return [Result(exact_match(t, t)) for t in text]

        assert hasattr(eval_fn, "_executor_type")
        assert eval_fn._executor_type == "batch"

    def test_create_dataset_decorator(self):
        """Test create_dataset_decorator function."""

        # This will fail for non-existent dataset but tests the mechanism
        decorator_func = create_dataset_decorator("foreach", "test_dataset")
        assert hasattr(decorator_func, "_dataset_name")
        assert decorator_func._dataset_name == "test_dataset"
