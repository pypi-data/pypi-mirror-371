# LLMEvaluationFramework

**LLMEvaluationFramework** is a Python package for **evaluating, testing, and benchmarking Large Language Models (LLMs)**.  
It provides tools for model inference, automated suggestions, model registry management, and synthetic dataset generation — all in one package.

---

## Features

- **Model Inference Engine** — Evaluate prompts against different LLMs.
- **Auto Suggestion Engine** — Generate intelligent suggestions for prompts.
- **Model Registry** — Manage and register multiple LLM configurations.
- **Test Dataset Generator** — Create synthetic datasets for evaluation.
- **Extensible** — Easily integrate with new models and datasets.
- **Testable** — Designed with 100% test coverage in mind.

### New Features
- **Async Inference Engine** — Run multiple model evaluations concurrently for faster benchmarking.
- **Custom Scoring Strategies** — Define and plug in your own evaluation metrics.
- **Persistent Storage** — Save and load model configurations, datasets, and results using JSON or database backends.
- **CLI Support** — Run evaluations, manage models, and generate datasets directly from the command line.
- **Enhanced Logging** — Detailed logs for debugging and performance tracking.

---

## Installation

From PyPI:
```bash
pip install llm-evaluation-framework
```

From source:
```bash
git clone https://github.com/isathish/LLMEvaluationFramework.git
cd LLMEvaluationFramework
pip install -e .[dev]
```

---

## Quick Start

### Model Inference
```python
from llm_evaluation_framework import ModelInferenceEngine

engine = ModelInferenceEngine(model_name="gpt-4")
result = engine.evaluate("What is the capital of France?")
print(result)
```

### Auto Suggestions
```python
from llm_evaluation_framework import AutoSuggestionEngine

suggestion_engine = AutoSuggestionEngine(model_name="gpt-4")
suggestions = suggestion_engine.suggest("Write a poem about the ocean.")
print(suggestions)
```

### Model Registry
```python
from llm_evaluation_framework import ModelRegistry

ModelRegistry.register("gpt-4", {"provider": "OpenAI", "max_tokens": 4096})
print(ModelRegistry.list_models())
```

### Test Dataset Generation
```python
from llm_evaluation_framework import TestDatasetGenerator

generator = TestDatasetGenerator()
dataset = generator.generate(num_samples=5, topic="math problems")
print(dataset)
```

---

## Documentation

Full documentation is available in the [`docs/`](docs/) folder:

- [Getting Started](docs/getting-started.md)
- [Usage Guide](docs/usage.md)
- [Contributing Guide](docs/contributing.md)

---

## Contributing

We welcome contributions! Please read the [Contributing Guide](docs/contributing.md) for details.

---

## License

This project is licensed under the MIT License.
