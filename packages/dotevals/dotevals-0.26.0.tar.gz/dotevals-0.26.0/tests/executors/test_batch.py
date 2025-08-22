"""Tests for BatchExecutor implementation."""

import asyncio

import pytest
from tenacity import AsyncRetrying, Retrying, stop_after_attempt

from dotevals.evaluators import exact_match
from dotevals.executors.batch import BatchExecutor
from dotevals.models import Result
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
        evaluation_name=f"test_batch_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )


class TestBatchExecutor:
    """Tests for BatchExecutor class."""

    @pytest.mark.asyncio
    async def test_executor_direct_call(self, simple_dataset, session_manager):
        """Test calling BatchExecutor directly."""

        def eval_batch_fn(text, number):
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            simple_dataset,
            session_manager,
            samples=None,
        )

        assert len(summary.results) == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_with_batch_size(self, session_manager):
        """Test BatchExecutor with specific batch size."""
        dataset = [(str(i), i) for i in range(10)]
        call_count = 0
        batch_sizes = []

        def eval_batch_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            dataset,
            session_manager,
            batch_size=3,
        )

        # Should be called 4 times with batch sizes: 3, 3, 3, 1
        assert call_count == 4
        assert batch_sizes == [3, 3, 3, 1]
        assert len(summary.results) == 10
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_no_batch_size(self, session_manager):
        """Test BatchExecutor without batch size processes all items in one batch."""
        dataset = [(str(i), i) for i in range(5)]
        call_count = 0
        batch_sizes = []

        def eval_batch_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()  # No batch_size
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            dataset,
            session_manager,
        )

        # Should be called 1 time with all 5 items
        assert call_count == 1
        assert batch_sizes == [5]
        assert len(summary.results) == 5

    @pytest.mark.asyncio
    async def test_executor_single_result(self, simple_dataset, session_manager):
        """Test BatchExecutor when function returns single result for entire batch."""

        def eval_batch_fn(text, number):
            # Return a single result for the entire batch
            return Result(exact_match(True, True))

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            simple_dataset,
            session_manager,
        )

        # Should create 3 records (one for each item) with the same result
        assert len(summary.results) == 3
        assert all(r.result.scores[0].value for r in summary.results)
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_with_samples(self, large_dataset, session_manager):
        """Test BatchExecutor with samples parameter."""

        def eval_batch_fn(text, number):
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            large_dataset,
            session_manager,
            samples=25,
            batch_size=10,
        )

        assert len(summary.results) == 25

    @pytest.mark.asyncio
    async def test_executor_error_handling(self, simple_dataset, session_manager):
        """Test BatchExecutor error handling."""

        def eval_batch_fn(text, number):
            raise ValueError("Test batch error")

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            simple_dataset,
            session_manager,
        )

        # Check we have 3 error results (one for each item in the batch)
        assert len(summary.results) == 3
        error_results = [r for r in summary.results if r.error]
        assert len(error_results) == 3
        assert all("ValueError: Test batch error" in r.error for r in error_results)

    @pytest.mark.asyncio
    async def test_executor_with_retries(self, tmp_path):
        """Test BatchExecutor with retry configuration."""
        executor = BatchExecutor(retries=Retrying(stop=stop_after_attempt(5)))

        attempt_count = 0

        def eval_batch_fn(text):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Retry me")
            return [Result(exact_match(text[0], "a"))]

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_batch_retry_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        summary = await executor.execute(
            eval_batch_fn, "text", [("a",)], session_manager
        )

        assert attempt_count == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_async_evaluation(self, simple_dataset, session_manager):
        """Test BatchExecutor with async evaluation function."""

        async def eval_batch_fn(text, number):
            await asyncio.sleep(0.001)  # Simulate async work
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            simple_dataset,
            session_manager,
        )

        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    @pytest.mark.asyncio
    async def test_executor_async_retry(self, tmp_path):
        """Test BatchExecutor with async retry configuration."""
        executor = BatchExecutor(retries=AsyncRetrying(stop=stop_after_attempt(3)))

        attempt_count = 0

        async def eval_batch_fn(text):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ConnectionError("Retry me")
            return [Result(exact_match(text[0], "a"))]

        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_async_retry_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        await executor.execute(eval_batch_fn, "text", [("a",)], session_manager)

        assert attempt_count == 2


class TestBatchExecutorErrorHandling:
    """Test error handling edge cases in batch executor."""

    def test_batch_with_error_in_evaluation(self, tmp_path):
        """Test batch processing when evaluation function raises error."""
        executor = BatchExecutor()

        def eval_batch_with_error(value):
            # Simulate error during batch processing
            if 0 in value:
                raise ValueError("Cannot process zero")
            return [Result(exact_match(v, v)) for v in value]

        dataset = [(0,), (1,), (2,)]

        session_manager = SessionManager(
            experiment_name="test_errors",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        # This should handle the error gracefully
        summary = asyncio.run(
            executor.execute(
                eval_fn=eval_batch_with_error,
                column_spec="value",
                dataset=dataset,
                session_manager=session_manager,
                batch_size=3,
            )
        )

        # Should have error records
        assert summary is not None
        assert len(summary.results) == 3
        # All should have errors since the batch failed
        assert all(r.error is not None for r in summary.results)

    def test_batch_empty_dataset(self, tmp_path):
        """Test batch executor with empty dataset."""
        executor = BatchExecutor()

        def eval_batch(value):
            return [Result(exact_match(v, v)) for v in value]

        session_manager = SessionManager(
            experiment_name="test_empty",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        summary = asyncio.run(
            executor.execute(
                eval_fn=eval_batch,
                column_spec="value",
                dataset=[],
                session_manager=session_manager,
                batch_size=10,
            )
        )

        assert summary is not None
        assert len(summary.results) == 0

    def test_batch_with_different_batch_sizes(self, tmp_path):
        """Test batch executor with different batch sizes."""
        executor = BatchExecutor()

        call_count = 0
        batch_sizes_seen = []

        def eval_batch(value):
            nonlocal call_count, batch_sizes_seen
            call_count += 1
            batch_sizes_seen.append(len(value))
            return [Result(exact_match(v, v)) for v in value]

        dataset = [(i,) for i in range(10)]

        session_manager = SessionManager(
            experiment_name="test_batch_size",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        # Test with batch size 3
        summary = asyncio.run(
            executor.execute(
                eval_fn=eval_batch,
                column_spec="value",
                dataset=dataset,
                session_manager=session_manager,
                batch_size=3,
            )
        )

        assert summary is not None
        assert len(summary.results) == 10
        # Should have been called 4 times: 3, 3, 3, 1
        assert call_count == 4
        assert batch_sizes_seen == [3, 3, 3, 1]

    @pytest.mark.asyncio
    async def test_executor_kwargs_handling(self, simple_dataset, session_manager):
        """Test that executor correctly handles additional kwargs."""

        def eval_batch_fn(text, number, custom_param=None, another_param=42):
            assert custom_param == "test_value"
            assert another_param == 100
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        executor = BatchExecutor()
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            simple_dataset,
            session_manager,
            custom_param="test_value",
            another_param=100,
        )

        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    @pytest.mark.asyncio
    async def test_executor_empty_dataset(self, session_manager):
        """Test BatchExecutor with empty dataset."""

        def eval_batch_fn(text):
            return []

        executor = BatchExecutor()
        summary = await executor.execute(eval_batch_fn, "text", [], session_manager)

        assert summary.summary == {}
        assert len(summary.results) == 0

    @pytest.mark.asyncio
    async def test_executor_batch_size_from_kwargs(self, session_manager):
        """Test BatchExecutor picks up batch_size from kwargs."""
        dataset = [(str(i), i) for i in range(7)]
        call_count = 0
        batch_sizes = []

        def eval_batch_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()  # No batch_size in constructor
        summary = await executor.execute(
            eval_batch_fn,
            "text,number",
            dataset,
            session_manager,
            batch_size=4,  # Pass batch_size via kwargs
        )

        # Should be called 2 times with batch sizes: 4, 3
        assert call_count == 2
        assert batch_sizes == [4, 3]
        assert len(summary.results) == 7
