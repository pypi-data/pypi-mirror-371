# AEA Optimizer Client SDK

This package provides a Python client for interacting with the AEA (Advanced Archipelago Evolution) Optimizer as a Service. It allows you to leverage the power of the AEA algorithm to solve complex, multi-objective optimization problems without exposing your proprietary evaluation logic.

## How It Works

The AEA Optimizer runs on a remote server, while your proprietary evaluation function (the `metrics_fn`) runs securely on your own machine. The client SDK facilitates this interaction through a secure callback mechanism:

1.  You define your optimization problem using `ObjectiveSpec` objects.
2.  You provide your `metrics_fn`, which takes a solution vector and returns a dictionary of performance metrics.
3.  When you call `client.optimize()`, the SDK starts a temporary, local web server (a "worker") that wraps your `metrics_fn`.
4.  The SDK sends the problem definition and the URL of your local worker to the AEA server.
5.  The AEA server runs the optimization, calling back to your worker to evaluate each candidate solution.
6.  Once complete, the SDK retrieves the final result and shuts down the local worker.

This ensures your intellectual property (the `metrics_fn`) never leaves your infrastructure.

## Installation

```bash
pip install aea-optimizer-client
```

## Quickstart Example

Here is a simple example of optimizing a 2D function.

```python
import numpy as np
from aea_client import AEAClient, ObjectiveSpec

# 1. Define your proprietary metrics function
def my_metrics_fn(x: np.ndarray) -> dict:
    # Objective 1: Minimize a sphere function
    cost = np.sum(x**2)
    # Objective 2: Maximize a linear function
    performance = np.sum(x)
    return {"cost": cost, "performance": performance}

# 2. Define your objectives for the API
objectives = [
    ObjectiveSpec(name="cost", weight=0.7, baseline=50.0, target=0.1, direction="min"),
    ObjectiveSpec(name="performance", weight=0.3, baseline=0.0, target=10.0, direction="max")
]

# 3. Initialize the client and run the optimization
# Replace with your production server URL
AEA_SERVER_URL = "http://api.your-aea-service.com"
client = AEAClient(server_url=AEA_SERVER_URL)

# Note: For cloud/Docker environments, you must provide your public IP
# via the `worker_host` argument.
final_result = client.optimize(
    objectives=objectives,
    metrics_fn=my_metrics_fn,
    dimension=2,
    bounds=(-5.0, 5.0),
    max_generations=50,
    pop_size=100
)

print(final_result)
```

### API Reference

#### `AEAClient(server_url: str)`

The main client class.

#### `client.optimize(...)`

Starts and manages an optimization job.

**Arguments:**

- `objectives` (List[ObjectiveSpec]): A list of `ObjectiveSpec` objects defining the problem.
- `metrics_fn` (Callable): Your evaluation function. Must accept a NumPy array and return a dictionary of metrics.
- `dimension` (int): The number of parameters in your solution vector.
- `bounds` (Tuple[float, float]): The `(min, max)` bounds for each parameter.
- `worker_port` (int, optional): The local port for the callback worker. Defaults to `8081`.
- `worker_host` (str, optional): The public IP or hostname of the machine running the client. **Required for non-local servers (e.g., cloud, Docker).** If `None`, a local IP is auto-detected.
- `pop_size`, `max_generations`, `n_islands`, `seed`: Standard parameters to configure the AEA optimizer.
- `poll_interval` (int, optional): Seconds to wait between polling for results. Defaults to `10`.

**Returns:**

A dictionary containing the final job status, best solution, and final metrics.
