"""Tests for ForEach decorator with custom strategies."""

import asyncio

import pytest
from tenacity import AsyncRetrying, Retrying, stop_after_attempt, wait_fixed

from dotevals import ForEach
from dotevals.concurrency import Sequential, SlidingWindow
from dotevals.evaluators import exact_match
from dotevals.models import Result


class TestForEachWithStrategies:
    """Test ForEach decorator with custom retry and concurrency strategies."""

    def test_foreach_with_custom_retries(self):
        """Test ForEach with custom retry configuration."""
        custom_retries = AsyncRetrying(
            stop=stop_after_attempt(5),
            wait=wait_fixed(0.1),
        )

        foreach = ForEach(retries=custom_retries)

        # Test data
        dataset = [("input1",), ("input2",)]

        @foreach("text", dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # The function should use the custom retries
        assert foreach.retries == custom_retries

    def test_foreach_with_custom_concurrency_sync(self):
        """Test ForEach with custom concurrency for sync functions."""
        sequential_strategy = Sequential()
        foreach = ForEach(concurrency=sequential_strategy)

        dataset = [(f"input{i}",) for i in range(5)]

        @foreach("text", dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # The function should use the sequential strategy
        assert foreach.concurrency == sequential_strategy

    @pytest.mark.asyncio
    async def test_foreach_with_custom_concurrency_async(self):
        """Test ForEach with custom concurrency for async functions."""
        sliding_strategy = SlidingWindow(max_concurrency=3)
        foreach = ForEach(concurrency=sliding_strategy)

        dataset = [(f"input{i}",) for i in range(5)]

        @foreach("text", dataset)
        async def evaluate(text):
            await asyncio.sleep(0.001)
            return Result(exact_match(text, text), prompt=text)

        # The function should use the sliding window strategy
        assert foreach.concurrency == sliding_strategy

    def test_foreach_initialization_basic(self):
        """Test basic ForEach initialization and decoration."""
        foreach = ForEach()
        dataset = [("input1",), ("input2",)]

        @foreach("text", dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # Verify function is properly decorated
        assert hasattr(evaluate, "_column_names")
        assert evaluate._column_names == ["text"]

    def test_foreach_initialization_with_name(self):
        """Test ForEach initialization without name (name parameter removed)."""
        foreach = ForEach()
        dataset = [("input1",), ("input2",)]

        # Dataset is provided in decorator call
        @foreach("text", dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # Name is no longer a parameter of ForEach
        assert hasattr(evaluate, "_column_names")

    def test_foreach_with_dataset(self):
        """Test that decorator properly uses the provided dataset."""
        decorator_dataset = [("dec1",), ("dec2",)]

        foreach = ForEach()

        @foreach("text", decorator_dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # The function should have column spec
        assert hasattr(evaluate, "_column_names")
        assert evaluate._column_names == ["text"]

    def test_foreach_missing_dataset_error(self):
        """Test error when no dataset is provided."""
        foreach = ForEach()

        with pytest.raises(
            TypeError, match="missing 1 required positional argument: 'dataset'"
        ):

            @foreach("text")
            def evaluate(text):
                return Result(exact_match(text, text), prompt=text)

    def test_foreach_with_async_strategy_on_sync_function(self):
        """Test that async strategy works with sync function (executor handles it)."""
        sliding_strategy = SlidingWindow()
        foreach = ForEach(concurrency=sliding_strategy)

        dataset = [("input1",)]

        @foreach("text", dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # The executor now handles this gracefully - no error expected
        import tempfile

        from dotevals.sessions import SessionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager = SessionManager(
                storage=f"json://{temp_dir}",
                experiment_name="test_exp",
                evaluation_name="test_eval",
            )
            coro = evaluate(
                session_manager=session_manager,
                samples=None,
            )
            summary = asyncio.run(coro)

            # Should complete successfully
            assert len(summary.results) == 1
            assert summary.results[0].error is None

    @pytest.mark.asyncio
    async def test_foreach_with_sync_strategy_on_async_function(self):
        """Test that sync strategy works with async function (executor handles it)."""

        sequential_strategy = Sequential()
        foreach = ForEach(concurrency=sequential_strategy)

        dataset = [("input1",)]

        @foreach("text", dataset)
        async def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        # The executor now handles this gracefully - no error expected
        import tempfile

        from dotevals.sessions import SessionManager

        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager = SessionManager(
                storage=f"json://{temp_dir}",
                experiment_name="test_exp",
                evaluation_name="test_eval",
            )
            summary = await evaluate(
                session_manager=session_manager,
                samples=None,
            )

            # Should complete successfully
            assert len(summary.results) == 1
            assert summary.results[0].error is None

    def test_foreach_with_all_parameters(self):
        """Test ForEach with all parameters specified."""
        dataset = [("input1",), ("input2",)]
        custom_retries = Retrying(stop=stop_after_attempt(10))
        custom_concurrency = Sequential()

        foreach = ForEach(
            retries=custom_retries,
            concurrency=custom_concurrency,
        )

        @foreach("text", dataset)
        def evaluate(text):
            return Result(exact_match(text, text), prompt=text)

        assert foreach.retries == custom_retries
        assert foreach.concurrency == custom_concurrency
