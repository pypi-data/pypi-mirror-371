"""Tests for ForEachExecutor implementation."""

import asyncio

import pytest
from tenacity import AsyncRetrying, Retrying, stop_after_attempt

from dotevals.concurrency import Adaptive, AsyncSequential
from dotevals.evaluators import exact_match
from dotevals.executors.foreach import ForEachExecutor
from dotevals.models import Result, Score
from dotevals.sessions import SessionManager


@pytest.fixture
def simple_dataset():
    """Basic 3-item dataset for testing."""
    return [("a", 1), ("b", 2), ("c", 3)]


@pytest.fixture
def large_dataset():
    """100-item dataset for sampling tests."""
    return [(str(i), i) for i in range(100)]


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


class TestForEachExecutor:
    """Tests for ForEachExecutor class."""

    @pytest.mark.asyncio
    async def test_executor_direct_call(self, simple_dataset, session_manager):
        """Test calling ForEachExecutor directly."""

        def eval_fn(text, number):
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        summary = await executor.execute(
            eval_fn, "text,number", simple_dataset, session_manager
        )

        assert len(summary.results) == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_with_samples(self, large_dataset, session_manager):
        """Test ForEachExecutor with samples parameter."""

        def eval_fn(text, number):
            return Result(exact_match(int(text), number))

        executor = ForEachExecutor()
        summary = await executor.execute(
            eval_fn, "text,number", large_dataset, session_manager, samples=5
        )

        assert len(summary.results) == 5

    @pytest.mark.asyncio
    async def test_executor_with_concurrency_strategy(
        self, simple_dataset, session_manager
    ):
        """Test ForEachExecutor with different concurrency strategies."""
        processed_order = []

        async def eval_fn(text, number):
            await asyncio.sleep(0.001)
            processed_order.append(number)
            return Result(exact_match(text, text))

        # Test with AsyncSequential
        executor = ForEachExecutor(concurrency=AsyncSequential())
        summary = await executor.execute(
            eval_fn, "text,number", simple_dataset, session_manager
        )

        assert len(summary.results) == 3
        assert processed_order == [1, 2, 3]  # Sequential order

        # Test with Adaptive
        processed_order.clear()
        executor = ForEachExecutor(concurrency=Adaptive(initial_concurrency=2))
        summary = await executor.execute(
            eval_fn, "text,number", simple_dataset, session_manager
        )

        assert len(summary.results) == 3
        # Order may vary with concurrent execution

    @pytest.mark.asyncio
    async def test_executor_with_retries(self, tmp_path):
        """Test ForEachExecutor with retry configuration."""
        executor = ForEachExecutor(retries=Retrying(stop=stop_after_attempt(3)))

        attempt_count = 0

        def eval_fn(text):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Retry me")
            return Result(exact_match(text, "a"))

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_retry_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        summary = await executor.execute(eval_fn, "text", [("a",)], session_manager)

        assert attempt_count == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_error_handling(self, simple_dataset, session_manager):
        """Test ForEachExecutor error handling."""
        call_count = 0

        def eval_fn(text, number):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError("Test error")
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        summary = await executor.execute(
            eval_fn, "text,number", simple_dataset, session_manager
        )

        # Check we have 3 total results: 2 successful and 1 error
        assert len(summary.results) == 3
        assert len([r for r in summary.results if not r.error]) == 2
        error_results = [r for r in summary.results if r.error]
        assert len(error_results) == 1
        assert "ValueError: Test error" in error_results[0].error

    @pytest.mark.asyncio
    async def test_executor_partial_failure(self, tmp_path):
        """Test handling partial failures in async evaluation."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_mgr = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        call_count = 0

        async def sometimes_failing(input):  # Parameter name must match column name
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError(f"Failed on item {call_count}")
            return Result(Score("test", True, []))

        dataset = [{"input": f"test_{i}"} for i in range(3)]

        executor = ForEachExecutor(concurrency=AsyncSequential())
        summary = await executor.execute(
            sometimes_failing,
            "input",
            dataset,
            session_mgr,
        )

        # Check that we have 2 successful results and 1 error
        assert len(summary.results) == 3
        successful = [r for r in summary.results if not r.error]
        errors = [r for r in summary.results if r.error]

        assert len(successful) == 2
        assert len(errors) == 1

        # The second item should have failed
        assert errors[0].dataset_row == {"input": "test_1"}
        assert "ValueError" in errors[0].error
        assert "Failed on item 2" in errors[0].error

    @pytest.mark.asyncio
    async def test_executor_concurrent_errors(self, tmp_path):
        """Test error handling with concurrent async evaluation."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_mgr = SessionManager(
            experiment_name=f"test_exp_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        async def evaluator_with_errors(id):  # Parameter name must match column name
            if id % 3 == 0:
                raise ValueError(f"Error on {id}")
            await asyncio.sleep(0.01)
            return Result(Score("test", id, []))

        dataset = [(i,) for i in range(10)]  # Use tuples for single column

        executor = ForEachExecutor(concurrency=Adaptive(initial_concurrency=3))
        summary = await executor.execute(
            evaluator_with_errors,
            "id",
            dataset,
            session_mgr,
        )

        # Check that we have both successful and error results
        successful = [r for r in summary.results if not r.error]
        errors = [r for r in summary.results if r.error]

        # IDs 0, 3, 6, 9 should have errors (multiples of 3)
        assert len(errors) == 4
        assert len(successful) == 6

        # Check error messages
        for error_result in errors:
            assert "ValueError" in error_result.error
            assert "Error on" in error_result.error

    @pytest.mark.asyncio
    async def test_executor_async_retry(self, tmp_path):
        """Test async evaluation with custom retry configuration."""
        executor = ForEachExecutor(retries=AsyncRetrying(stop=stop_after_attempt(5)))

        attempt_count = 0

        async def eval_fn(text):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Retry me")
            return Result(exact_match(text, "a"))

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_async_retry_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        summary = await executor.execute(eval_fn, "text", [("a",)], session_manager)

        assert attempt_count == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_no_retry(self, tmp_path):
        """Test async evaluation without retry on exceptions."""
        # Create a no-retry configuration (single attempt only)
        no_retry = AsyncRetrying(stop=stop_after_attempt(1))
        executor = ForEachExecutor(retries=no_retry)

        async def eval_fn(text):
            raise ConnectionError("Should not retry")

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_no_retry_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        # Should complete without retrying (error captured in result)
        summary = await executor.execute(eval_fn, "text", [("a",)], session_manager)

        # Verify error was captured in results
        assert len(summary.results) == 1
        assert summary.results[0].error is not None
        assert "ConnectionError" in summary.results[0].error

    @pytest.mark.asyncio
    async def test_executor_kwargs_handling(self, simple_dataset, session_manager):
        """Test that executor correctly handles additional kwargs."""
        captured_kwargs = []

        def eval_fn(text, number, custom_param=None, another_param=42):
            captured_kwargs.append(
                {"custom_param": custom_param, "another_param": another_param}
            )
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        await executor.execute(
            eval_fn,
            "text,number",
            simple_dataset,
            session_manager,
            custom_param="test_value",
            another_param=100,
        )

        assert len(captured_kwargs) == 3
        for kwargs in captured_kwargs:
            assert kwargs["custom_param"] == "test_value"
            assert kwargs["another_param"] == 100
