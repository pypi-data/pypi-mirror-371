
# SpeedSense

SpeedSense is a Python package that automatically analyzes and determines the time complexity of Python functions. It uses static code analysis and curve fitting techniques to provide accurate complexity estimates with optional visualization capabilities.

## Features

- **Automatic Complexity Analysis**: Analyzes Python functions and determines their time complexity
- **Visualization Support**: Optional plotting of complexity curves with smooth interpolation
- **Multiple Complexity Models**: Supports O(1), O(log n), O(n), O(n log n), O(n²), and O(n³) analysis
- **Code Instrumentation**: Automatically instruments loops to count iterations
- **Flexible Input**: Works with both function objects and source code strings

## Limitations

Currently, the library works with:
1. **Single-variable input functions** (functions that take one parameter)
2. **Non-recursive functions** (no recursive calls)
3. **Basic loop structures** (for and while loops)
4. **Simple arithmetic operations**

**Note**: Built-in library functions and complex data structures may not be fully supported yet.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable) to install speedsense:

```bash
pip install speedsense
```

## Usage

### Basic Usage

```python
from speedsense.tc_estimator import get_time_complexity
import inspect

def my_function(n):
    for i in range(n):
        for j in range(n):
            pass  # Some operation

# Method 1: Using function object directly
complexity = get_time_complexity(my_function, [10, 15, 20, 25, 30])
print(f"Time complexity: {complexity}")

# Method 2: Using source code
source_code = inspect.getsource(my_function)
complexity = get_time_complexity(source_code, [10, 15, 20, 25, 30])
print(f"Time complexity: {complexity}")
```

### With Visualization

```python
from speedsense.tc_estimator import get_time_complexity
import inspect

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

# Get complexity with visualization
complexity, fig, ax = get_time_complexity(
    bubble_sort, 
    [10, 15, 20, 25, 30], 
    visualize=True
)
print(f"Time complexity: {complexity}")

# Save the plot
complexity, fig, ax = get_time_complexity(
    bubble_sort, 
    [10, 15, 20, 25, 30], 
    visualize=True, 
    save_path="complexity_plot.png"
)
```

### Using compute_complexity (Legacy Method)

```python
from speedsense.tc_estimator import compute_complexity
import inspect

def userfunc(n):
    for i in range(n):
        for j in range(n):
            pass  # Some operation

code = inspect.getsource(userfunc)
compute_complexity(code)  # prints the time complexity

# With visualization
compute_complexity(code, visualize=True)
```

## API Reference

### `get_time_complexity(func, input_sizes, visualize=False, show=True, save_path=None)`

Analyzes the time complexity of a function.

**Parameters:**
- `func`: Function object or source code string to analyze
- `input_sizes`: List of input sizes to test (e.g., [10, 15, 20, 25, 30])
- `visualize`: Boolean, whether to create a visualization plot (default: False)
- `show`: Boolean, whether to display the plot (default: True)
- `save_path`: String, optional path to save the plot image

**Returns:**
- If `visualize=False`: Returns the complexity string (e.g., "O(n²)")
- If `visualize=True`: Returns tuple (complexity, figure, axes)

### `compute_complexity(source_code, visualize=False)`

Legacy function for analyzing source code strings.

**Parameters:**
- `source_code`: String containing the function source code
- `visualize`: Boolean, whether to create a visualization plot

## Examples

### Linear Time Complexity
```python
def linear_function(n):
    for i in range(n):
        pass  # O(n) operation

complexity = get_time_complexity(linear_function, [10, 20, 30, 40, 50])
# Output: O(n)
```

### Quadratic Time Complexity
```python
def quadratic_function(n):
    for i in range(n):
        for j in range(n):
            pass  # O(n²) operation

complexity = get_time_complexity(quadratic_function, [5, 10, 15, 20, 25])
# Output: O(n²)
```

### Logarithmic Time Complexity
```python
def log_function(n):
    i = n
    while i > 1:
        i = i // 2  # O(log n) operation

complexity = get_time_complexity(log_function, [10, 20, 40, 80, 160])
# Output: O(log n)
```

## How It Works

1. **Code Instrumentation**: The library automatically instruments your function by adding counters to loops
2. **Execution**: Runs the instrumented function with different input sizes
3. **Data Collection**: Collects iteration counts for each input size
4. **Curve Fitting**: Fits the data to different complexity models using least squares regression
5. **Analysis**: Determines the best-fitting complexity model
6. **Visualization**: Optionally creates plots showing the data points and fitted curve

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

[MIT](https://choosealicense.com/licenses/mit/)
