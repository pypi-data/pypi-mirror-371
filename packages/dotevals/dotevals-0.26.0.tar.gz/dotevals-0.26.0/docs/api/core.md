# Core Module

The core module contains the fundamental components of dotevals, including the `@foreach` decorator and essential evaluation functions.

## @foreach Decorator

The main decorator that transforms functions into evaluations. This is the primary entry point for most users.

**Usage**: `@foreach("param1,param2", dataset)`

::: dotevals.foreach

## @batch Decorator

Batch processing - your function is called with lists/arrays of data.

**Usage**: `@batch("prompts,expected", dataset, batch_size=32)`

**Example**:
```python
@batch("questions,answers", dataset, batch_size=32)
def eval_qa_batch(questions, answers, model):
    # questions = ["Q1", "Q2", ..., "Q32"]
    # answers = ["A1", "A2", ..., "A32"]
    responses = model.batch_generate(questions)  # Called once per batch
    return [Result(exact_match(r, a)) for r, a in zip(responses, answers)]
```

::: dotevals.batch

## ForEach Class

The configurable version of the foreach decorator that allows custom retry strategies, concurrency, and storage backends.

::: dotevals.ForEach

## Batch Class

The configurable version of the batch decorator.

::: dotevals.ForEach
