# Run Batch Inference with Local Models

Learn how to use the `@batch` decorator with HuggingFace Transformers for efficient local model evaluation. This guide shows you how to process multiple dataset items together, reducing overhead and maximizing throughput.

## Setup Requirements

Install the required dependencies:

```bash
pip install transformers torch dotevals
```

## Text Classification with Batching

Process multiple texts at once using Transformers pipelines:

```python title="eval_sentiment_batch.py"
import pytest
from transformers import pipeline
from dotevals import batch, Result
from dotevals.evaluators import exact_match

@pytest.fixture(scope="session")
def sentiment_pipeline():
    """Load sentiment analysis model once per test session."""
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1  # Use GPU if available
    )

# Test dataset
sentiment_data = [
    ("I love this product!", "positive"),
    ("This is terrible", "negative"),
    ("It's okay", "neutral"),
    ("Amazing quality!", "positive"),
    ("Completely broken", "negative"),
    ("Works as expected", "positive"),
    ("Could be better", "negative"),
    ("Perfect for my needs", "positive"),
] * 50  # 400 items total

@batch("texts,expected", sentiment_data, batch_size=32)
def eval_sentiment_batch(texts, expected, sentiment_pipeline):
    """Evaluate sentiment classification in batches."""

    # Process entire batch in one call
    predictions = sentiment_pipeline(texts, batch_size=32)

    # Extract labels and normalize
    results = []
    for pred, exp in zip(predictions, expected):
        label = pred['label'].lower()
        results.append(Result(exact_match(label, exp)))

    return results
```

Run the evaluation:

```bash
pytest eval_sentiment_batch.py --experiment sentiment_batch_test -v
```

## Text Generation with Batching

For generative models, use the model and tokenizer directly for better control:

```python title="eval_generation_batch.py"
import pytest
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from dotevals import batch, Result
from dotevals.evaluators import exact_match

@pytest.fixture(scope="session")
def generation_model():
    """Load generation model once per test session."""
    model_name = "microsoft/DialoGPT-medium"  # Fast, reasonably sized model

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )

    # Set padding token
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id

    return model, tokenizer

# Simple Q&A dataset
qa_data = [
    ("What is 2+2?", "4"),
    ("What color is the sky?", "blue"),
    ("What is the capital of France?", "Paris"),
    ("How many days in a week?", "7"),
    ("What is H2O?", "water"),
    ("What is the largest planet?", "Jupiter"),
    ("What is 10-5?", "5"),
    ("What language is this?", "English"),
] * 25  # 200 items total

@batch("questions,answers", qa_data, batch_size=8)
def eval_generation_batch(questions, answers, generation_model):
    """Evaluate text generation in batches."""
    model, tokenizer = generation_model

    # Tokenize all questions at once
    inputs = tokenizer(
        questions,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )

    # Move to GPU if available
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    # Generate responses for entire batch
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=20,
            temperature=0.1,  # Low temperature for more deterministic outputs
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=inputs['attention_mask']
        )

    # Decode all outputs at once
    generated_texts = tokenizer.batch_decode(
        outputs,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )

    # Extract only the new tokens (remove input)
    responses = []
    for i, (question, generated) in enumerate(zip(questions, generated_texts)):
        # Remove the input question from generated text
        response = generated[len(question):].strip()
        responses.append(response)

    # Return one Result per input
    results = []
    for response, answer in zip(responses, answers):
        # Simple matching - check if expected answer is in response
        score = 1.0 if answer.lower() in response.lower() else 0.0
        results.append(Result(score, model_response=response))

    return results
```

## See Also

- **[Batch Decorator Reference](../reference/batch.md)** - Complete API documentation
- **[ForEach vs Batch Comparison](../api/core.md)** - Choosing the right approach
- **[Pytest Fixtures Guide](../tutorials/06-pytest-fixtures-and-resource-pooling.md)** - Managing model resources
