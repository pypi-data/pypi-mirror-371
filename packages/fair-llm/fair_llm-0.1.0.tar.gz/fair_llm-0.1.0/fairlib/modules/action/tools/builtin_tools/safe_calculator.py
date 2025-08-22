# action/tools/builtin_tools/safe_calculator.py

import ast
import operator as op
from fairlib.core.interfaces.tools import AbstractTool

class SafeCalculatorTool(AbstractTool):
    """
    A calculator tool that safely evaluates mathematical expressions
    using Python's AST (Abstract Syntax Tree). Supports +, -, *, /, and parentheses.
    """

    name = "safe_calculator"
    description = (
        "A tool to evaluate basic arithmetic expressions. "
        "Input should be a string like '10 + 5 * (2 - 3)'. "
        "Supports +, -, *, / operators and parentheses."
    )

    def __init__(self):
        # Supported operators mapped to their actual implementations
        self._operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.USub: op.neg,  # Unary minus
            ast.UAdd: op.pos   # Unary plus
        }

    def use(self, expression: str) -> str:
        """
        Evaluates a mathematical expression using the AST module.
        """
        try:
            # Parse the expression into an AST
            expr_ast = ast.parse(expression, mode='eval')
            result = self._eval(expr_ast.body)
            return f"The result of '{expression}' is {result}"
        except Exception as e:
            return f"Error: Could not evaluate expression. Details: {e}"

    def _eval(self, node):
        """
        Recursively evaluates an AST node.
        Only allows safe operations: numbers, binary and unary math.
        """
        if isinstance(node, ast.BinOp):
            left = self._eval(node.left)
            right = self._eval(node.right)
            operator_type = type(node.op)
            if operator_type in self._operators:
                return self._operators[operator_type](left, right)
            else:
                raise ValueError(f"Unsupported operator: {operator_type}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval(node.operand)
            operator_type = type(node.op)
            if operator_type in self._operators:
                return self._operators[operator_type](operand)
            else:
                raise ValueError(f"Unsupported unary operator: {operator_type}")

        elif isinstance(node, ast.Num):  # Python 3.8 and earlier
            return node.n

        elif isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Only numeric constants are allowed")

        else:
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")