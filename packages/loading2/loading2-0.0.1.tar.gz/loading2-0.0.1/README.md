# Loading2 🔄

A simple and elegant Python library for adding loading animations to your functions with a decorator.

## Features

- ✨ Easy-to-use decorator pattern
- 🎨 Customizable loading messages
- ⚡ Lightweight with no external dependencies
- 🔄 Smooth spinning animation
- 📦 Thread-safe implementation

## Installation

```bash
# Clone the repository
git clone https://github.com/r1cardohj/loading2.git
cd loading2

# Or download the loading2.py file directly
```

## Quick Start

```python
from loading2 import loading
import time

@loading()
def long_running_task():
    time.sleep(3)  # Simulate some work
    return "Task completed!"

# Run the function - you'll see a spinning animation
result = long_running_task()
# you will see this in your command line
# \ Loading...
# when long_running_task function return, you will see
# OK
```

## Usage

### Basic Usage

```python
from loading2 import loading

@loading()
def my_function():
    # Your code here
    pass
```

### Custom Messages

```python
@loading(
    msg="Processing data...",
    ok="✅ Data processed successfully!",
    err="❌ Processing failed:"
)
def process_data():
    # Your processing logic
    pass
```

### Real-world Example

```python
import requests
from loading2 import loading

@loading(
    msg="Fetching data from API...",
    ok="✅ API request completed!",
    err="❌ API request failed:"
)
def fetch_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

# Usage
user_data = fetch_user_data(123)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `msg` | `str` | `"Loading..."` | Message displayed during loading |
| `ok` | `str` | `"OK"` | Message displayed on success |
| `err` | `str` | `"Failed"` | Message displayed on error |

## How It Works

The library uses Python's threading module to run a spinning animation in a separate thread while your function executes. The animation automatically stops when your function completes or raises an exception.

## Requirements

- Python 3.10+
- No external dependencies

## Examples

### CPU-intensive Task

```python
@loading(msg="Calculating...", ok="🎉 Calculation done!")
def cpu_bound_task():
    return sum(i * i for i in range(100_000_000))

result = cpu_bound_task()
```

### File Operations

```python
@loading(msg="Reading large file...", ok="📁 File loaded!")
def read_large_file(filename):
    with open(filename, 'r') as f:
        return f.read()

content = read_large_file('big_data.txt')
```

### Database Operations

```python
@loading(msg="Querying database...", ok="🗄️ Query completed!")
def fetch_records():
    # Database query logic here
    pass
```

## Inspiration

The spinning animation implementation is inspired by the examples in "Fluent Python" by Luciano Ramalho.

## Support

If you find this library helpful, please consider giving it a ⭐ on GitHub!

---

Made with ❤️ by [r1cardohj]
