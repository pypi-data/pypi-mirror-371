# My Library

A simple example Python library that provides basic mathematical and string utilities.

## Installation

```bash
pip install my_library
```

## Usage

```python
from my_library import Calculator, StringUtils, fibonacci, factorial

# Calculator usage
calc = Calculator()
print(calc.add(5, 3))  # Output: 8
print(calc.multiply(4, 7))  # Output: 28

# String utilities
utils = StringUtils()
print(utils.reverse("hello"))  # Output: "olleh"
print(utils.is_palindrome("racecar"))  # Output: True

# Math functions
print(fibonacci(5))  # Output: [0, 1, 1, 2, 3]
print(factorial(5))  # Output: 120
```

## Features

- **Calculator**: Basic arithmetic operations
- **StringUtils**: String manipulation utilities
- **Math Functions**: Fibonacci sequence and factorial calculations
- **Error Handling**: Proper error handling for edge cases

## Development

To build and install locally:

```bash
python setup.py sdist bdist_wheel
pip install -e .
```

## License

MIT License