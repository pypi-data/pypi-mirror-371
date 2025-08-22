# fairlib.utils.math_expression_parser.py

import re

def parse_math_expression(expr: str) -> str:
    """
    Converts symbolic math input into structured function call syntax:
    - '∫(x * sin(x**2)) dx'  → 'integral(x * sin(x**2), x)'
    - '∫₀² (x**2 + 1) dx'    → 'integral(x**2 + 1, x, 0, 2)'
    - 'd/dx x**2 + sin(x)'   → 'derivative(x**2 + sin(x), x)'
    """
    expr = expr.strip()

    # Handle derivative: d/dx <expression>
    deriv_match = re.match(r"d/d([a-zA-Z])\s+(.+)", expr)
    if deriv_match:
        var = deriv_match.group(1)
        inner_expr = deriv_match.group(2)
        return f"derivative({inner_expr.strip()}, {var})"

    # Handle indefinite integral: ∫(expr) dx
    indef_match = re.match(r"∫\s*\((.+)\)\s*d([a-zA-Z])", expr)
    if indef_match:
        inner_expr = indef_match.group(1)
        var = indef_match.group(2)
        return f"integral({inner_expr.strip()}, {var})"

    # Handle definite integral: ∫ₐᵇ (expr) dx
    def_match = re.match(r"∫\s*([-\d\.]+)\s*to\s*([-\d\.]+)\s*\((.+)\)\s*d([a-zA-Z])", expr)
    if def_match:
        a = def_match.group(1)
        b = def_match.group(2)
        inner_expr = def_match.group(3)
        var = def_match.group(4)
        return f"integral({inner_expr.strip()}, {var}, {a}, {b})"

    # Handle ∫ₐᵇ form using unicode subscripts (like ∫₀²)
    unicode_def_match = re.match(r"∫₍?([-\d\.]+)?₎?⁽?([-\d\.]+)?⁾?\s*\((.+)\)\s*d([a-zA-Z])", expr)
    if unicode_def_match:
        a = unicode_def_match.group(1)
        b = unicode_def_match.group(2)
        inner_expr = unicode_def_match.group(3)
        var = unicode_def_match.group(4)
        return f"integral({inner_expr.strip()}, {var}, {a}, {b})"

    # No pattern matched
    return expr
