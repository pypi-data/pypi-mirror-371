# action/tools/builtin_tools/advanced_calculus_tool.py

from sympy import symbols, sympify, diff, integrate
from sympy.core.sympify import SympifyError
from fairlib.core.interfaces.tools import AbstractTool

class AdvancedCalculusTool(AbstractTool):
    """
    AdvancedCalculusTool enables symbolic differentiation and integration 
    of mathematical expressions using the SymPy library.

    Supported operations:
    - Derivative:       derivative(expr, var)
    - Indefinite integral: integral(expr, var)
    - Definite integral:   integral(expr, var, lower_bound, upper_bound)

    Example expressions:
        "derivative(x**2 + sin(x), x)"
        "integral(x**2, x)"
        "integral(x**2, x, 0, 1)"

    Note:
    - Only supports one-variable expressions.
    - All inputs must be valid Python-style math syntax.
    """

    name = "advanced_calculus_tool"
    description = (
        "A tool for computing derivatives and integrals using symbolic math. "
        "Supports:\n"
        "  - Derivatives: 'derivative(expr, x)'\n"
        "  - Indefinite integrals: 'integral(expr, x)'\n"
        "  - Definite integrals: 'integral(expr, x, a, b)'\n"
        "Examples:\n"
        "  derivative(x**2, x)\n"
        "  integral(sin(x), x)\n"
        "  integral(x**2, x, 0, 2)"
    )

    def use(self, expression: str) -> str:
        """
        Parses and executes a calculus command string.
        
        Parameters:
        expression (str): The user command, such as 'derivative(x**2, x)' or
                          'integral(x**2, x, 0, 1)'.
                          
        Returns:
        str: Result of symbolic computation or error message.
        """
        try:
            # Trim whitespace and normalize expression
            expression = expression.strip()

            # Determine if this is a derivative or integral request
            if expression.startswith("derivative("):
                return self._handle_derivative(expression)
            elif expression.startswith("integral("):
                return self._handle_integral(expression)
            else:
                return "Error: Unsupported command. Use 'derivative(...)' or 'integral(...)'."
        except Exception as e:
            return f"Error: Failed to compute expression. Details: {e}"

    def _handle_derivative(self, command: str) -> str:
        """
        Handles derivative computation.

        Parameters:
        command (str): A string like 'derivative(expr, x)'

        Returns:
        str: The derivative result or an error message.
        """
        try:
            # Remove wrapper: derivative(...)
            inner = command[len("derivative("):-1]

            # Split by comma to extract expression and variable
            expr_str, var_str = [s.strip() for s in inner.split(',')]

            # Define variable symbol
            var = symbols(var_str)

            # Convert expression string to a symbolic expression
            expr = sympify(expr_str)

            # Compute the symbolic derivative
            derivative = diff(expr, var)

            return f"The derivative of {expr_str} with respect to {var_str} is:\n{derivative}"

        except (ValueError, SympifyError) as e:
            return f"Error parsing derivative expression. Details: {e}"

    def _handle_integral(self, command: str) -> str:
        """
        Handles integral computation (indefinite or definite).

        Parameters:
        command (str): A string like 'integral(expr, x)' or 'integral(expr, x, a, b)'

        Returns:
        str: The integral result or an error message.
        """
        try:
            # Remove wrapper: integral(...)
            inner = command[len("integral("):-1]

            # Split by comma to extract parts
            parts = [s.strip() for s in inner.split(',')]

            # Extract expression and variable name
            expr_str, var_str = parts[0], parts[1]
            var = symbols(var_str)

            # Convert expression to a symbolic expression
            expr = sympify(expr_str)

            if len(parts) == 2:
                # Indefinite integral
                result = integrate(expr, var)
                return f"The indefinite integral of {expr_str} with respect to {var_str} is:\n{result}"
            elif len(parts) == 4:
                # Definite integral
                a = sympify(parts[2])  # Lower bound
                b = sympify(parts[3])  # Upper bound
                result = integrate(expr, (var, a, b))
                return f"The definite integral of {expr_str} from {a} to {b} with respect to {var_str} is:\n{result}"
            else:
                return "Error: Invalid number of arguments for 'integral'. Expected 2 or 4."

        except (ValueError, SympifyError) as e:
            return f"Error parsing integral expression. Details: {e}"