import ast
import inspect
import numpy as np
#import function_generator

class CodeModifier(ast.NodeTransformer):
    def __init__(self):
        self.counter_id = 0
        self.nesting_level = 0
        self.groups = []  # List of lists, each sublist is a group of nested counters
        self.current_group = []
        self.counter_stack = []
    
    def visit_FunctionDef(self, node):
        node.body = self.process_body(node.body)
        # If there is a group left at the end, add it
        if self.current_group:
            self.groups.append(self.current_group)
        return node
    
    def process_body(self, body):
        new_body = []
        for stmt in body:
            if isinstance(stmt, ast.For):
                self.counter_id += 1
                counter_name = f"for_counter_{self.counter_id}"
                self.counter_stack.append(counter_name)
                self.nesting_level += 1
                
                # If this is a top-level for, start a new group
                if self.nesting_level == 1:
                    if self.current_group:
                        self.groups.append(self.current_group)
                    self.current_group = []
                self.current_group.append(counter_name)
                
                # Counter initialization
                new_body.append(ast.Assign(
                    targets=[ast.Name(id=counter_name, ctx=ast.Store())],
                    value=ast.Constant(value=0)
                ))
                # Insert counter increment at the start of the for body
                stmt.body.insert(0, ast.AugAssign(
                    target=ast.Name(id=counter_name, ctx=ast.Store()),
                    op=ast.Add(),
                    value=ast.Constant(value=1)
                ))
                stmt.body = self.process_body(stmt.body) # recursive call
                self.nesting_level -= 1
                self.counter_stack.pop()
                new_body.append(stmt)
                # If we just finished a top-level for, close the group
                if self.nesting_level == 0:
                    if self.current_group:
                        self.groups.append(self.current_group)
                        self.current_group = []
            
            elif isinstance(stmt, ast.While):
                self.counter_id += 1
                counter_name = f"while_counter_{self.counter_id}"
                self.counter_stack.append(counter_name)
                self.nesting_level += 1
                
                # if this is the top-level while, start a new group
                if self.nesting_level == 1:
                    if self.current_group:
                        self.groups.append(self.current_group)
                    self.current_group = []
                self.current_group.append(counter_name)
                
                # counter initialization
                new_body.append(ast.Assign(
                    targets=[ast.Name(id=counter_name, ctx=ast.Store())],
                    value=ast.Constant(value=0)
                ))
                
                # Insert counter increment at the start of the while body
                stmt.body.insert(0, ast.AugAssign(
                    target=ast.Name(id=counter_name, ctx=ast.Store()),
                    op=ast.Add(),
                    value=ast.Constant(value=1)
                ))
                stmt.body = self.process_body(stmt.body)
                self.nesting_level -= 1
                self.counter_stack.pop()
                new_body.append(stmt)
                # If we just finished a top-level while, close the group
                if self.nesting_level == 0:
                    if self.current_group:
                        self.groups.append(self.current_group)
                        self.current_group = []
            
            elif isinstance(stmt, ast.Return):
                # Build total_iterations expression
                group_exprs = []
                for group in self.groups:
                    if not group:
                        continue
                    expr = ast.Name(id=group[0], ctx=ast.Load())
                    for counter in group[1:]:
                        expr = ast.BinOp(left=expr, op=ast.Mult(), right=ast.Name(id=counter, ctx=ast.Load()))
                    group_exprs.append(expr)
                if group_exprs:
                    total_iterations_expr = group_exprs[0]
                    for expr in group_exprs[1:]:
                        total_iterations_expr = ast.BinOp(left=total_iterations_expr, op=ast.Add(), right=expr)
                else:
                    total_iterations_expr = ast.Constant(value=0)
                # Return tuple (original result, total_iterations)
                new_body.append(ast.Return(
                    value=ast.Tuple(
                        elts=[stmt.value, total_iterations_expr],
                        ctx=ast.Load()
                    )
                ))
            else:
                new_body.append(stmt)
        return new_body
    
tc_map = {
    0 : "O(1)",
    1 : "O(logn)",
    2 : "O(n)",
    3 : "O(nlogn)",
    4 : "O(n^2)",
    5 : "O(n^3)"
}

# Helper: instrument a Python callable so it returns (original_result, iteration_count)
def _instrument_callable(func):
    source_code = inspect.getsource(func)
    tree = ast.parse(source_code)
    modifier = CodeModifier()
    modified_tree = modifier.visit(tree)
    ast.fix_missing_locations(modified_tree)
    # Extract function name
    function_name = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            break
    compiled = compile(modified_tree, '<string>', 'exec')
    namespace = {}
    import math
    namespace['math'] = math
    exec(compiled, namespace)
    return namespace[function_name]

# the curve fitting part
def get_time_complexity(func, input_sizes):
    varying_ops = [0]*len(input_sizes)
    for i, size in enumerate(input_sizes):
        # Convert size to integer before passing to function
        outputs = func(int(size))
        varying_ops[i] = outputs[-1]
    
    # Convert inputs to numpy arrays
    input_sizes = np.array(input_sizes, dtype=np.int64)
    varying_ops = np.array(varying_ops)
    
    # Try different complexity models
    models = {
        'constant': lambda x: np.ones_like(x),
        'log': lambda x: np.log2(x),
        'linear': lambda x: x,
        'nlog': lambda x: x * np.log2(x),
        'quadratic': lambda x: x**2,
        'cubic': lambda x: x**3
    }
    
    best_model = None
    best_error = float('inf')
    error_list = []
    # Fit each model and find the best one
    for name, model in models.items():
        # Create design matrix for the model
        X = model(input_sizes)
        # Add constant term
        X = np.column_stack([np.ones_like(X), X])
        
        # Solve least squares
        coeffs, residuals, _, _ = np.linalg.lstsq(X, varying_ops, rcond=None)
        error = np.sum(residuals) if len(residuals) > 0 else float('inf')
        error_list.append(error)
        if error < best_error:
            best_error = error
            best_model = name
    
    # Map the best model to time complexity
    complexity_map = {
        'constant': 'O(1)',
        'log': 'O(log n)',
        'linear': 'O(n)',
        'nlog': 'O(n log n)',
        'quadratic': 'O(n^2)',
        'cubic': 'O(n^3)'
    }
    #print(error_list)
    # Use a small threshold for floating point comparison
    threshold = 1e-10
    if np.all(np.abs(error_list[1:]) < threshold) and error_list[0]==float('inf'):
        print(f'Best fitting complexity: {complexity_map["constant"]}')
        return complexity_map['constant']
    print(f"Best fitting complexity: {complexity_map[best_model]}")
    return complexity_map[best_model]

def visualize_best_fitting_complexity(func, input_sizes, show=True, save_path=None):
    # Ensure we have an instrumented callable
    input_sizes = [int(s) for s in input_sizes]
    callable_to_use = func
    try:
        probe = callable_to_use(int(input_sizes[0]))
        if not isinstance(probe, (tuple, list)):
            callable_to_use = _instrument_callable(func)
    except Exception:
        callable_to_use = _instrument_callable(func)
    varying_ops = [0]*len(input_sizes)
    for i, size in enumerate(input_sizes):
        outputs = callable_to_use(int(size))
        varying_ops[i] = outputs[-1]
    input_sizes = np.array(input_sizes, dtype=np.int64)
    varying_ops = np.array(varying_ops)
    models = {
        'constant': lambda x: np.ones_like(x),
        'log': lambda x: np.log2(x),
        'linear': lambda x: x,
        'nlog': lambda x: x * np.log2(x),
        'quadratic': lambda x: x**2,
        'cubic': lambda x: x**3
    }
    fitted = {}
    errors = {}
    best_model = None
    best_error = float('inf')
    error_list = []
    for name, model in models.items():
        X = model(input_sizes)
        X = np.column_stack([np.ones_like(X), X])
        coeffs, residuals, _, _ = np.linalg.lstsq(X, varying_ops, rcond=None)
        error = np.sum(residuals) if len(residuals) > 0 else float('inf')
        error_list.append(error)
        errors[name] = error
        fitted[name] = {
            'coeffs': coeffs,
            'pred': X @ coeffs
        }
        if error < best_error:
            best_error = error
            best_model = name
    complexity_map = {
        'constant': 'O(1)',
        'log': 'O(log n)',
        'linear': 'O(n)',
        'nlog': 'O(n log n)',
        'quadratic': 'O(n^2)',
        'cubic': 'O(n^3)'
    }
    threshold = 1e-10
    if np.all(np.abs(error_list[1:]) < threshold) and error_list[0]==float('inf'):
        best_model = 'constant'
    import matplotlib.pyplot as plt
    sort_idx = np.argsort(input_sizes)
    xs = input_sizes[sort_idx]
    ys = varying_ops[sort_idx]
    best_pred = fitted[best_model]['pred'][sort_idx]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(xs, ys, color='tab:blue', label='Observed iterations')
    ax.plot(xs, best_pred, color='tab:orange', linewidth=2, label=f'Best fit: {complexity_map[best_model]}')
    ax.set_xlabel('Input size (n)')
    ax.set_ylabel('Iteration count (varying ops)')
    ax.set_title('Best-fitting time complexity')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend()
    if save_path:
        fig.savefig(save_path, bbox_inches='tight')
    if show:
        plt.show()
    return complexity_map[best_model], fig, ax

def compute_complexity(source_code):
    tree = ast.parse(source_code)
    modifier = CodeModifier()
    modified_tree = modifier.visit(tree)
    ast.fix_missing_locations(modified_tree)
    print(modified_tree)
    # Extract function name from the AST
    function_name = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            break
    
    print("code has been modified now moving on to exec")
    
    compiled = compile(modified_tree, '<string>', 'exec')
    
    print("Code has been compiled")
    namespace = {}
    import math
    namespace['math'] = math
    exec(compiled, namespace)
    modified_func = namespace[function_name]  # Use the extracted function name
    input_sizes = [10, 15, 20, 25, 30]  # These are already integers
    print(modified_func)
    get_time_complexity(modified_func, input_sizes)
    
# test_code = inspect.getsource(function_generator.mixed_complexity)
# compute_complexity(test_code)
# best, fig, ax = visualize_best_fitting_complexity(function_generator.mixed_complexity, [10, 15, 20, 25, 30], show=True, save_path="fit.png")