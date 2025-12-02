import math
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    return a - b

@mcp.tool()
def divide(a: float, b: float) -> float:
    return a / b

@mcp.tool()
def power(base: float, exponent: float) -> float:
    return base ** exponent

@mcp.tool()
def sqrt(x: float) -> float:
    return math.sqrt(x)

@mcp.tool()
def average(numbers: list[float]) -> float:
    if not numbers:  # handle empty list
        return 0.0
    return sum(numbers) / len(numbers)

@mcp.tool()
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")

