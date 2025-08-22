"""Integration tests for complete dotevals workflows."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from dotevals import ForEach, Result, batch, foreach
from dotevals.evaluators import exact_match
from dotevals.models import Score
from dotevals.sessions import SessionManager, get_default_session_manager
from dotevals.storage.json import JSONStorage


def test_complete_evaluation_workflow():
    """Test the full user workflow end-to-end."""
    # Create temporary directory for test storage
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # Simple test dataset
        test_data = [
            ("What is 2+2?", "4"),
            ("What is 3+3?", "6"),
            ("What is 5+5?", "10"),
        ]

        # Create ForEach instance with storage
        foreach = ForEach()

        # Define evaluation function
        @foreach("question,answer", test_data)
        def eval_math(question, answer):
            # Create prompt
            prompt = f"Question: {question}"
            # Simulate some processing
            result = "4" if "2+2" in question else "wrong"
            # Return Result with prompt and scores
            return Result(exact_match(result, answer), prompt=prompt)

        # Run the evaluation with the new API
        session_manager = SessionManager(
            storage=f"json://{storage_path}",
            experiment_name="workflow_test",
            evaluation_name="eval_math",
        )
        coro = eval_math(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        # Verify results
        assert len(result.results) == 3
        assert (
            result.summary["exact_match"]["accuracy"] == 1 / 3
        )  # Only first item matches

        # Verify experiment was created and evaluation persisted
        experiments = session_manager.storage.list_experiments()
        assert "workflow_test" in experiments

        # Verify we can retrieve the evaluation results
        results = session_manager.storage.get_results("workflow_test", "eval_math")
        assert len(results) == 3


def test_session_persistence_across_runs():
    """Test that session state persists across multiple runs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1"), ("Q2", "A2")]

        # Create ForEach instance with storage
        foreach = ForEach()

        @foreach("question,answer", test_data)
        def eval_test(question, answer):
            prompt = f"Q: {question}"
            return Result(exact_match(answer, "A1"), prompt=prompt)

        # First run
        session_manager = SessionManager(
            storage=f"json://{storage_path}",
            experiment_name="persistence_test",
            evaluation_name="eval_test",
        )
        coro1 = eval_test(session_manager=session_manager, samples=None)
        result1 = asyncio.run(coro1)
        assert len(result1.results) == 2  # Verify first run processed items

        # Second run with new session manager (simulates new process)
        session_manager2 = SessionManager(
            storage=f"json://{storage_path}",
            experiment_name="persistence_test",
            evaluation_name="eval_test",
        )

        # Should be able to retrieve the same evaluation results
        results = session_manager2.storage.get_results("persistence_test", "eval_test")
        assert len(results) == 2

        # Experiments should be the same
        experiments = session_manager2.storage.list_experiments()
        assert "persistence_test" in experiments


def test_progress_tracker_with_errors():
    """Test progress tracking when some evaluations have errors."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create ForEach instance with isolated storage
        foreach_instance = ForEach()

        dataset = [("test1", "answer1"), ("test2", "answer2"), ("test3", "answer3")]

        error_on_item = "test2"

        @foreach_instance("input,expected", dataset)
        def eval_with_errors(input, expected):
            if input == error_on_item:
                raise ValueError(f"Intentional error on {input}")
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        # This should complete despite errors
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="error_test",
            evaluation_name="test_eval",
        )
        coro = eval_with_errors(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        # Should have 3 results, with one containing an error
        assert len(result.results) == 3
        error_results = [r for r in result.results if r.error]
        assert len(error_results) == 1
        assert "Intentional error on test2" in error_results[0].error


def test_progress_tracker_completion_count():
    """Test progress tracking with explicit completion count."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        dataset = [("test1", "answer1"), ("test2", "answer2")]

        @foreach_instance("input,expected", dataset)
        def eval_completion_count(input, expected):
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="completion_test",
            evaluation_name="test_eval",
        )
        coro = eval_completion_count(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        assert len(result.results) == 2


def test_sequential_runner_empty_items():
    """Test sequential runner with empty evaluation items."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        # Empty dataset
        dataset = []

        @foreach_instance("input,expected", dataset)
        def eval_empty(input, expected):
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="empty_test",
            evaluation_name="test_eval",
        )
        coro = eval_empty(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        assert len(result.results) == 0


def test_is_running_under_pytest():
    """Test the _is_running_under_pytest helper function."""
    from dotevals.progress import _is_running_under_pytest

    # Since we're running this in pytest, this should return True
    assert _is_running_under_pytest() is True


def test_concurrent_runner_with_empty_items():
    """Test concurrent runner behavior with empty evaluation items."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        # Empty dataset
        dataset = []

        @foreach_instance("input,expected", dataset)
        async def eval_empty_concurrent(input, expected):
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="empty_concurrent_test",
            evaluation_name="test_eval",
        )
        result = asyncio.run(
            eval_empty_concurrent(session_manager=session_manager, samples=None)
        )

        assert len(result.results) == 0


def test_concurrent_runner_multiple_async_evaluations():
    """Test concurrent runner with multiple async evaluations."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        dataset = [("test1", "test1"), ("test2", "test2"), ("test3", "test3")]

        @foreach_instance("input,expected", dataset)
        async def eval_concurrent_multi(input, expected):
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="concurrent_multi_test",
            evaluation_name="test_eval",
        )
        result = asyncio.run(
            eval_concurrent_multi(
                session_manager=session_manager,
                samples=None,
                max_concurrency=2,  # Force concurrent execution
            )
        )

        assert len(result.results) == 3


def test_sequential_runner_with_progress_finishing():
    """Test sequential runner progress finishing in finally block."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        dataset = [("test1", "answer1"), ("test2", "answer2")]

        @foreach_instance("input,expected", dataset)
        def eval_sequential_progress(input, expected):
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        # This should exercise the finally block in SequentialRunner
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="sequential_progress_test",
            evaluation_name="test_eval",
        )
        coro = eval_sequential_progress(session_manager=session_manager, samples=None)
        result = asyncio.run(coro)

        assert len(result.results) == 2


def test_concurrent_runner_with_progress_finishing():
    """Test concurrent runner progress finishing in finally block."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        dataset = [("test1", "test1"), ("test2", "test2")]

        @foreach_instance("input,expected", dataset)
        async def eval_concurrent_progress(input, expected):
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        # This should exercise the finally block in ConcurrentRunner
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="concurrent_progress_test",
            evaluation_name="test_eval",
        )
        result = asyncio.run(
            eval_concurrent_progress(
                session_manager=session_manager, samples=None, max_concurrency=2
            )
        )

        assert len(result.results) == 2


def test_concurrent_runner_task_creation():
    """Test concurrent runner task creation and evaluation processing."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        dataset = [
            ("item1", "expected1"),
            ("item2", "expected2"),
            ("item3", "expected3"),
        ]

        @foreach_instance("input,expected", dataset)
        async def eval_task_creation(input, expected):
            # Simulate some async work
            await asyncio.sleep(0.002)
            return Result(exact_match(input, expected), prompt=f"Processing: {input}")

        # This should exercise task creation, gathering, and progress management
        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="task_creation_test",
            evaluation_name="test_eval",
        )
        result = asyncio.run(
            eval_task_creation(
                session_manager=session_manager,
                samples=None,
                max_concurrency=3,  # Allow all tasks to run concurrently
            )
        )

        assert len(result.results) == 3


def test_concurrent_runner_single_evaluation_method():
    """Test the concurrent runner's single evaluation method."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach()

        dataset = [("single_test", "single_expected")]

        @foreach_instance("input,expected", dataset)
        async def eval_single_method(input, expected):
            # Test the run_single_evaluation method specifically
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Single eval: {input}")

        session_manager = SessionManager(
            storage=f"json://{temp_dir}",
            experiment_name="single_method_test",
            evaluation_name="test_eval",
        )
        result = asyncio.run(
            eval_single_method(
                session_manager=session_manager,
                samples=None,
                max_concurrency=1,  # Forces single evaluation path
            )
        )

        assert len(result.results) == 1


# Decorator Integration Tests
class TestForEachDecoratorIntegration:
    """Integration tests for @foreach decorator."""

    def test_foreach_basic_sync(self):
        """Test basic synchronous foreach evaluation."""
        dataset = [
            {"input": "hello", "expected": "HELLO"},
            {"input": "world", "expected": "WORLD"},
        ]

        @foreach("input,expected", dataset)
        def uppercase_eval(input: str, expected: str) -> Score:
            return Score(
                name="uppercase_match", value=input.upper() == expected, metrics=[]
            )

        # Run evaluation
        session_manager = get_default_session_manager()
        import asyncio

        coro = uppercase_eval(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 2
        assert all(r.result.scores[0].value for r in summary.results)

    def test_foreach_with_score(self):
        """Test foreach returning Score objects."""
        dataset = [
            {"text": "positive"},
            {"text": "negative"},
            {"text": "neutral"},
        ]

        @foreach("text", dataset)
        def sentiment_eval(text: str) -> Score:
            sentiment_scores = {
                "positive": 1.0,
                "negative": 0.0,
                "neutral": 0.5,
            }
            return Score(
                name="sentiment",
                value=sentiment_scores.get(text, 0.5),
                metrics=[],
            )

        session_manager = get_default_session_manager()
        import asyncio

        coro = sentiment_eval(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 3
        scores = [r.result.scores[0].value for r in summary.results]
        assert scores == [1.0, 0.0, 0.5]

    @pytest.mark.asyncio
    async def test_foreach_async(self):
        """Test asynchronous foreach evaluation."""
        dataset = [{"x": 1}, {"x": 2}, {"x": 3}]

        @foreach("x", dataset)
        async def async_double(x: int) -> Score:
            await asyncio.sleep(0.01)  # Simulate async work
            return Score(name="double", value=float(x * 2), metrics=[])

        session_manager = get_default_session_manager()
        summary = await async_double(session_manager, samples=None)

        assert len(summary.results) == 3
        values = sorted([r.result.scores[0].value for r in summary.results])
        assert values == [2.0, 4.0, 6.0]

    def test_foreach_error_handling(self):
        """Test foreach error handling."""
        dataset = [
            {"value": 10},
            {"value": 0},  # Will cause division by zero
            {"value": 5},
        ]

        @foreach("value", dataset)
        def divide_eval(value: int) -> Score:
            result = 100 / value
            return Score(name="division", value=result, metrics=[])

        session_manager = get_default_session_manager()
        import asyncio

        coro = divide_eval(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 3
        # First and third should succeed
        assert summary.results[0].result.scores[0].value == 10.0
        assert summary.results[2].result.scores[0].value == 20.0
        # Second should have error
        assert summary.results[1].error is not None
        assert "ZeroDivisionError" in summary.results[1].error


class TestBatchDecoratorIntegration:
    """Integration tests for @batch decorator."""

    def test_batch_basic_sync(self):
        """Test basic synchronous batch evaluation."""
        dataset = [
            {"value": 1},
            {"value": 2},
            {"value": 3},
            {"value": 4},
            {"value": 5},
        ]

        @batch("value", dataset, batch_size=2)
        def sum_batch(value: list[int]) -> list[Score]:
            # Process batch - receives lists
            return [Score(name="double", value=float(v * 2), metrics=[]) for v in value]

        session_manager = get_default_session_manager()
        import asyncio

        coro = sum_batch(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 5
        values = [r.result.scores[0].value for r in summary.results]
        assert values == [2.0, 4.0, 6.0, 8.0, 10.0]

    @pytest.mark.asyncio
    async def test_batch_async(self):
        """Test asynchronous batch evaluation."""
        dataset = [{"text": f"item_{i}"} for i in range(6)]

        @batch("text", dataset, batch_size=3)
        async def async_batch_process(text: list[str]) -> list[Result]:
            await asyncio.sleep(0.01)
            return [
                Result(
                    Score(name="uppercase", value=t.upper(), metrics=[]),
                    model_response=t.upper(),
                )
                for t in text
            ]

        session_manager = get_default_session_manager()
        summary = await async_batch_process(session_manager, samples=None)

        assert len(summary.results) == 6
        assert summary.results[0].result.model_response == "ITEM_0"
        assert summary.results[5].result.model_response == "ITEM_5"

    def test_batch_error_handling(self):
        """Test batch error handling."""
        dataset = [
            {"value": 2},
            {"value": 0},  # Will cause error in batch
            {"value": 3},
            {"value": 4},
        ]

        @batch("value", dataset, batch_size=2)
        def divide_batch(value: list[int]) -> list[Score]:
            return [Score(name="div", value=10 / v, metrics=[]) for v in value]

        session_manager = get_default_session_manager()
        import asyncio

        coro = divide_batch(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 4
        # First batch [2, 0] will fail entirely
        assert summary.results[0].error is not None
        assert summary.results[1].error is not None
        # Second batch [3, 4] should succeed
        assert summary.results[2].result.scores[0].value == 10 / 3
        assert summary.results[3].result.scores[0].value == 10 / 4


class TestDecoratorEdgeCases:
    """Test edge cases for decorators."""

    def test_empty_dataset(self):
        """Test decorators with empty dataset."""
        empty_dataset = []

        @foreach("value", empty_dataset)
        def empty_foreach(value: int) -> Score:
            return Score(name="test", value=value, metrics=[])

        @batch("value", empty_dataset, batch_size=10)
        def empty_batch(value: list[int]) -> list[Score]:
            return [Score(name="test", value=v, metrics=[]) for v in value]

        session_manager = get_default_session_manager()
        import asyncio

        foreach_coro = empty_foreach(session_manager, samples=None)
        foreach_summary = asyncio.run(foreach_coro)
        batch_coro = empty_batch(session_manager, samples=None)
        batch_summary = asyncio.run(batch_coro)

        assert len(foreach_summary.results) == 0
        assert len(batch_summary.results) == 0

    def test_large_dataset_batching(self):
        """Test batch with various batch sizes."""
        large_dataset = [{"n": i} for i in range(100)]

        # Test direct decorator syntax with batch_size
        @batch("n", large_dataset, batch_size=10)
        def batch_10(n: list[int]) -> list[Score]:
            return [Score(name="lt50", value=x < 50, metrics=[]) for x in n]

        @batch("n", large_dataset, batch_size=33)
        def batch_33(n: list[int]) -> list[Score]:
            return [Score(name="lt50", value=x < 50, metrics=[]) for x in n]

        session_manager = get_default_session_manager()
        import asyncio

        coro_10 = batch_10(session_manager, samples=None)
        summary_10 = asyncio.run(coro_10)
        coro_33 = batch_33(session_manager, samples=None)
        summary_33 = asyncio.run(coro_33)

        assert len(summary_10.results) == 100
        assert len(summary_33.results) == 100

        # Check results are correct regardless of batch size
        for summary in [summary_10, summary_33]:
            for i, record in enumerate(summary.results):
                assert record.result.scores[0].value == (i < 50)

    def test_with_session_manager(self):
        """Test decorators with explicit session manager."""
        import tempfile

        # Create temporary storage
        temp_dir = tempfile.mkdtemp()
        storage = JSONStorage(temp_dir)
        session_manager = SessionManager(
            storage=storage,
            experiment_name="test_experiment",
            evaluation_name="with_session",
        )

        dataset = [{"x": 1}, {"x": 2}]

        @foreach("x", dataset)
        def with_session(x: int) -> Score:
            return Score(name="triple", value=x * 3, metrics=[])

        import asyncio

        coro = with_session(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 2
        assert summary.results[0].result.scores[0].value == 3
        assert summary.results[1].result.scores[0].value == 6

        # Clean up
        import shutil

        shutil.rmtree(temp_dir)


class TestConcurrencyAndRetries:
    """Test concurrency and retry features."""

    @pytest.mark.asyncio
    async def test_foreach_with_concurrency(self):
        """Test foreach with different concurrency strategies."""
        from dotevals.concurrency import Adaptive, Sequential

        dataset = [{"x": i} for i in range(10)]

        # Test direct decorator syntax with concurrency
        @foreach("x", dataset, concurrency=Adaptive(max_concurrency=3))
        async def adaptive_eval(x: int) -> Score:
            await asyncio.sleep(0.01)
            return Score(name="double", value=x * 2, metrics=[])

        @foreach("x", dataset, concurrency=Sequential())
        async def sequential_eval(x: int) -> Score:
            await asyncio.sleep(0.01)
            return Score(name="double", value=x * 2, metrics=[])

        session_manager = get_default_session_manager()
        adaptive_summary = await adaptive_eval(session_manager, samples=None)
        sequential_summary = await sequential_eval(session_manager, samples=None)

        assert len(adaptive_summary.results) == 10
        assert len(sequential_summary.results) == 10

        # Results should be the same regardless of concurrency
        adaptive_values = sorted(
            r.result.scores[0].value for r in adaptive_summary.results
        )
        sequential_values = sorted(
            r.result.scores[0].value for r in sequential_summary.results
        )
        assert adaptive_values == sequential_values == [i * 2 for i in range(10)]

    def test_foreach_with_retries(self):
        """Test foreach with retry logic."""
        from tenacity import Retrying, stop_after_attempt, wait_fixed

        # Track attempts
        attempt_counts = {}

        dataset = [{"id": "a"}, {"id": "b"}, {"id": "c"}]

        # Test direct decorator syntax with retries
        @foreach(
            "id",
            dataset,
            retries=Retrying(stop=stop_after_attempt(3), wait=wait_fixed(0.01)),
        )
        def flaky_eval(id: str) -> Score:
            # Track attempts
            attempt_counts[id] = attempt_counts.get(id, 0) + 1

            # Fail first attempt for 'b'
            if id == "b" and attempt_counts[id] == 1:
                raise ValueError("Temporary failure")

            return Score(name="success", value=True, metrics=[])

        session_manager = get_default_session_manager()
        import asyncio

        coro = flaky_eval(session_manager, samples=None)
        summary = asyncio.run(coro)

        assert len(summary.results) == 3
        # All should eventually succeed
        assert all(r.result.scores[0].value for r in summary.results)
        # 'b' should have been retried
        assert attempt_counts["b"] == 2
        assert attempt_counts["a"] == 1
        assert attempt_counts["c"] == 1


class TestDecoratorSyntax:
    """Test the improved decorator syntax with keyword arguments."""

    def test_foreach_with_kwargs(self):
        """Test that @foreach accepts keyword arguments directly."""
        from tenacity import Retrying, stop_after_attempt

        from dotevals.concurrency import Adaptive

        dataset = [{"x": 1}, {"x": 2}]

        # Test with concurrency
        @foreach("x", dataset, concurrency=Adaptive(max_concurrency=2))
        def test1(x: int) -> Score:
            return Score(name="test", value=x * 2, metrics=[])

        # Test with retries
        @foreach("x", dataset, retries=Retrying(stop=stop_after_attempt(2)))
        def test2(x: int) -> Score:
            return Score(name="test", value=x * 3, metrics=[])

        # Test with both
        @foreach(
            "x",
            dataset,
            concurrency=Adaptive(max_concurrency=2),
            retries=Retrying(stop=stop_after_attempt(2)),
        )
        def test3(x: int) -> Score:
            return Score(name="test", value=x * 4, metrics=[])

        # All should work without errors
        session_manager = get_default_session_manager()
        import asyncio

        coro = test1(session_manager, samples=None)
        assert asyncio.run(coro).results is not None
        coro2 = test2(session_manager, samples=None)
        assert asyncio.run(coro2).results is not None
        coro3 = test3(session_manager, samples=None)
        assert asyncio.run(coro3).results is not None

    def test_batch_with_kwargs(self):
        """Test that @batch accepts keyword arguments directly."""
        from tenacity import Retrying, stop_after_attempt

        dataset = [{"x": i} for i in range(10)]

        # Test with batch_size
        @batch("x", dataset, batch_size=5)
        def test1(x: list[int]) -> list[Score]:
            return [Score(name="test", value=v, metrics=[]) for v in x]

        # Test with retries
        @batch("x", dataset, retries=Retrying(stop=stop_after_attempt(2)))
        def test2(x: list[int]) -> list[Score]:
            return [Score(name="test", value=v * 2, metrics=[]) for v in x]

        # Test with both
        @batch("x", dataset, batch_size=3, retries=Retrying(stop=stop_after_attempt(2)))
        def test3(x: list[int]) -> list[Score]:
            return [Score(name="test", value=v * 3, metrics=[]) for v in x]

        # All should work without errors
        session_manager = get_default_session_manager()
        import asyncio

        coro = test1(session_manager, samples=None)
        assert asyncio.run(coro).results is not None
        coro2 = test2(session_manager, samples=None)
        assert asyncio.run(coro2).results is not None
        coro3 = test3(session_manager, samples=None)
        assert asyncio.run(coro3).results is not None
