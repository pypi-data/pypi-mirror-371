# Spimind

English | [中文](README.md)

Event stream logging system designed for Spiking Neural Networks, using TinyDB as the storage backend.

## Features

- **Lightweight API**: One line to initialize, one line to log, one line to close
- **Event-stream First**: Centered around `log_event` rather than traditional "step" concept
- **Hookable**: Support for attaching hook functions at key points
- **TinyDB Storage**: Structured data storage with support for complex queries

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import spimind

# Initialize logger
logger = spimind.init(project="spimind-sim")

# Log spike event
logger.log_event(event="spike", event_time=12.3, neuron="LIF_23")

# Close logger
logger.close()
```

## Usage Examples

### Basic Usage

```python
import spimind

logger = spimind.init(project="test")
logger.log_event(event="spike", event_time=1.0, neuron="neuron_1")
logger.close()
```

### Context Manager

```python
with spimind.init(project="test") as logger:
    logger.log_event(event="spike", event_time=1.0, neuron="neuron_1")
```

### Hook Functionality

```python
def spike_monitor(event_data):
    if event_data['event'] == 'spike':
        print(f"Spike detected: {event_data['neuron']}")

logger = spimind.init(project="test")
logger.add_hook(spike_monitor)
logger.log_event(event="spike", event_time=1.0, neuron="LIF_1")
```

## Example Code

Check the `example/` directory for more usage examples:

- `basic_usage.py` - Basic usage example
- `hook_example.py` - Hook functionality example
- `context_manager_example.py` - Context manager example

## API

### spimind.init()

Initialize logger

**Parameters:**
- `project` (str): Project name
- `run_name` (str, optional): Run name, auto-generated if None
- `**kwargs`: Specific parameters passed to backend

### logger.log_event()

Log event

**Parameters:**
- `event` (str): Event type
- `event_time` (float): Event timestamp
- `**kwargs`: Event-related data

### logger.add_hook()

Add event processing hook

**Parameters:**
- `hook_func` (callable): Function to process events

### logger.close()

Close logger

## License

This project is licensed under the [MIT](LICENSE) License.
