# DeepRails Python SDK

Official Python SDK for interacting with the DeepRails API. [DeepRails](https://deeprails.com) is a powerful developer tool with a comprehesive set of adaptive guardrails to protect against LLM hallucinations - deploy our Evaluate, Monitor, and Defend APIs in <15 mins for the best out-of-the-box guardrails in the market.

Supports DeepRails API Version v2.0

## Installation

```bash
pip install deeprails
```

## Quick Start

```python
from deeprails import DeepRails

# Initialize with your API token
client = DeepRails(token="YOUR_API_KEY")

# Create an evaluation
evaluation = client.create_evaluation(
    model_input={"user_prompt": "Prompt used to generate completion"},
    model_output="Generated output",
    model_used="gpt-4o-mini",
    guardrail_metrics=["correctness", "completeness"]
)
print(f"Evaluation created with ID: {evaluation.eval_id}")

# Create a monitor
monitor = client.create_monitor(
    name="Production Assistant Monitor",
    description="Tracking our production assistant quality"
)
print(f"Monitor created with ID: {monitor.monitor_id}")
```

## Features

- **Simple API**: Just a few lines of code to integrate evaluation into your workflow
- **Comprehensive Metrics**: Evaluate outputs on correctness, completeness, and more
- **Real-time Progress**: Track evaluation progress in real-time
- **Detailed Results**: Get detailed scores and rationales for each metric
- **Continuous Monitoring**: Create monitors to track AI system performance over time

## Authentication

All API requests require authentication using your DeepRails API key. Your API key is a sensitive credential that should be kept secure.

```python
# Best practice: Load token from environment variable
import os
token = os.environ.get("DEEPRAILS_API_KEY")
client = DeepRails(token=token)
```

## Evaluation Service

### Creating Evaluations

```python
try:
    evaluation = client.create_evaluation(
        model_input={"user_prompt": "Prompt used to generate completion"},
        model_output="Generated output",
        model_used="gpt-4o-mini",
        guardrail_metrics=["correctness", "completeness"]
    )
    print(f"ID: {evaluation.eval_id}")
    print(f"Status: {evaluation.evaluation_status}")
    print(f"Progress: {evaluation.progress}%")
except Exception as e:
    print(f"Error: {e}")
```

#### Parameters

- `model_input`: Dictionary containing the prompt and any context (must include `user_prompt`)
- `model_output`: The generated output to evaluate
- `model_used`: (Optional) The model that generated the output
- `run_mode`: (Optional) Evaluation run mode - defaults to "smart"
- `guardrail_metrics`: (Optional) List of metrics to evaluate
- `nametag`: (Optional) Custom identifier for this evaluation
- `webhook`: (Optional) URL to receive completion notifications

### Retrieving Evaluations

```python
try:
    eval_id = "eval-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    evaluation = client.get_evaluation(eval_id)
    
    print(f"Status: {evaluation.evaluation_status}")
    
    if evaluation.evaluation_result:
        print("\nResults:")
        for metric, result in evaluation.evaluation_result.items():
            score = result.get('score', 'N/A')
            print(f"  {metric}: {score}")
except Exception as e:
    print(f"Error: {e}")
```

## Monitor Service

### Creating Monitors

```python
try:
    # Create a monitor
    monitor = client.create_monitor(
        name="Production Chat Assistant Monitor",
        description="Monitoring our production chatbot responses"
    )
    
    print(f"Monitor created with ID: {monitor.monitor_id}")
except Exception as e:
    print(f"Error: {e}")
```

### Logging Monitor Events

```python
try:
    # Add an event to the monitor
    event = client.create_monitor_event(
        monitor_id="mon-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        model_input={"user_prompt": "Tell me about renewable energy"},
        model_output="Renewable energy comes from natural sources...",
        model_used="gpt-4o-mini",
        guardrail_metrics=["correctness", "completeness", "comprehensive_safety"]
    )
    
    print(f"Monitor event created with ID: {event.event_id}")
    print(f"Associated evaluation ID: {event.evaluation_id}")
except Exception as e:
    print(f"Error: {e}")
```

### Retrieving Monitor Data

```python
try:
    # Get monitor details
    monitor = client.get_monitor("mon-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    print(f"Monitor name: {monitor.name}")
    print(f"Status: {monitor.monitor_status}")
    
    # Get monitor events
    events = client.get_monitor_events(
        monitor_id="mon-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", 
        limit=10
    )
    
    for event in events:
        print(f"Event ID: {event.event_id}")
        print(f"Evaluation ID: {event.evaluation_id}")
        
    # List all monitors with filtering
    monitors = client.get_monitors(
        limit=5,
        monitor_status=["active"],
        sort_by="created_at",
        sort_order="desc"
    )
    
    print(f"Total monitors: {monitors.pagination.total_count}")
    for m in monitors.monitors:
        print(f"{m.name}: {m.event_count} events")
except Exception as e:
    print(f"Error: {e}")
```

## Available Metrics

- `correctness`: Measures factual accuracy by evaluating whether each claim in the output is true and verifiable.
- `completeness`: Assesses whether the response addresses all necessary parts of the prompt with sufficient detail and relevance.
- `instruction_adherence`: Checks whether the AI followed the explicit instructions in the prompt and system directives.
- `context_adherence`: Determines whether each factual claim is directly supported by the provided context.
- `ground_truth_adherence`: Measures how closely the output matches a known correct answer (gold standard).
- `comprehensive_safety`: Detects and categorizes safety violations across areas like PII, CBRN, hate speech, self-harm, and more.

## Error Handling

The SDK throws `DeepRailsAPIError` for API-related errors, with status code and detailed message.

```python
from deeprails import DeepRailsAPIError

try:
    # SDK operations
except DeepRailsAPIError as e:
    print(f"API Error: {e.status_code} - {e.error_detail}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Support

For questions or support, please contact support@deeprails.ai.