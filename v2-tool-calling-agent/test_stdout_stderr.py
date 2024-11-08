from tools.python_executor import python_executor

# Test code that generates both stdout and stderr
test_code = """
import sys

print("This is standard output")
print("This is standard error", file=sys.stderr)

# Generate some computation output
result = 42
print(f"Computation result: {result}")

# Generate an intentional warning
import warnings
warnings.warn("This is a test warning")
"""

print("Testing stdout and stderr capture...")
result = python_executor(code=test_code, filename="stdout_stderr_test.py")

if "error" in result:
    print(f"Test failed: {result['error']}")
else:
    print("\nTest succeeded. Full output:")
    print(result['result'])
