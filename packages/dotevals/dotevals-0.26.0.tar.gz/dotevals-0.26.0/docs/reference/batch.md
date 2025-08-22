# The @batch Decorator

The `@batch` decorator transforms a regular Python function into an evaluation that processes multiple dataset items together in batches. It handles data iteration, error management, progress tracking, and session management.

**For individual item processing, see [`@foreach`](foreach.md) instead.**

## Basic Usage

```python
from dotevals import batch
from dotevals.models import Result
from dotevals.evaluators import exact_match

@batch("questions,answers", dataset, batch_size=32)
def eval_qa_batch(questions, answers, model):
    """Evaluate model on question-answer pairs in batches."""
    # questions = ["What is 2+2?", "What is 3+3?", ..., "What is 34+34?"]  # 32 items
    # answers = ["4", "6", ..., "68"]                                      # 32 items

    responses = model.batch_generate(questions)  # One API call for 32 items
    return [Result(exact_match(r, a)) for r, a in zip(responses, answers)]
```

## Batch Size Configuration

### Using batch_size parameter in decorator
```python
# Process 16 items at a time
@batch("prompts,expected", dataset, batch_size=16)
def eval_small_batch(prompts, expected, model):
    responses = model.batch_process(prompts)
    return [Result(score=len(r)) for r in responses]

# Process all items in one batch
@batch("prompts,expected", dataset)  # No batch_size parameter
def eval_all_at_once(prompts, expected, model):
    responses = model.batch_process(prompts)  # All items at once
    return [Result(score=len(r)) for r in responses]
```

## Return Values

Batch evaluation functions should return one `Result` instance per input item:

```python
@batch("texts,labels", dataset, batch_size=50)
def eval_classification_batch(texts, labels, model):
    predictions = model.batch_classify(texts)

    # Return one Result per input item
    results = []
    for text, pred, label in zip(texts, predictions, labels):
        score = exact_match(pred, label)
        results.append(Result(score, prompt=text, model_response=pred))

    return results
```


## Advanced Configuration

### Custom Retry Configuration

```python
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential
from dotevals import Batch

# Custom retry strategy for batch processing
batch_with_retries = Batch(
    retries=AsyncRetrying(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
)

@batch_with_retries("prompts,expected", dataset)
async def eval_with_retries(prompts, expected, api_client):
    """Batch evaluation with automatic retries."""
    responses = await api_client.batch_complete(prompts)
    return [Result(exact_match(r, e)) for r, e in zip(responses, expected)]
```

## See Also

### Core Concepts
- **[ForEach Decorator](foreach.md)** - Individual item processing alternative
- **[Evaluators](evaluators.md)** - Learn how to create and use evaluators within batch functions
- **[Experiments](experiments.md)** - Understand how batch evaluations create and manage experiments

### Integration Guides
- **[Running Evaluations](running-evaluations.md)** - Execute batch functions with pytest, CLI, and programmatic access
- **[Interactive API](../api/interactive.md)** - Use `run()` function with batch evaluations

### Advanced Usage
- **[Metrics](metrics.md)** - Configure custom metrics that aggregate results from batch evaluations
- **[Storage Backends](storage.md)** - Customize where batch evaluation results are stored

### Tutorials
- **[Performance Optimization](../tutorials/performance-optimization.md)** - When to choose batch vs individual processing
- **[Working with Large Datasets](../tutorials/03-working-with-real-datasets.md)** - Batch processing strategies for large datasets
