
import sys

print("This is standard output")
print("This is standard error", file=sys.stderr)

# Generate some computation output
result = 42
print(f"Computation result: {result}")

# Generate an intentional warning
import warnings
warnings.warn("This is a test warning")
