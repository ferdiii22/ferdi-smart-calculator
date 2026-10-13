"""Safe arithmetic-expression evaluation using a restricted Python AST."""

import ast
import math
import operator
import re
from decimal import Decimal, DecimalException, localcontext


class CalculationError(ValueError):
    """A user-facing calculation error."""


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {"sin", "cos", "tan", "sqrt", "log", "ln", "fact", "abs"}
_CONSTANTS = {"pi": Decimal("3.141592653589793238462643383"),
              "e": Decimal("2.718281828459045235360287471")}
_MAX_EXPRESSION_LENGTH = 512
_MAX_EXPONENT = Decimal("10000")
_MAX_FACTORIAL = 1000
_PERCENT_RE = re.compile(r"(?<![A-Za-z_])((?:\d+(?:\.\d*)?|\.\d+))\s*%")


def normalize_expression(expression):
    """Convert calculator notation and Indonesian number separators to syntax."""
    expression = expression.strip()
    if not expression or len(expression) > _MAX_EXPRESSION_LENGTH:
        raise CalculationError("Ekspresi kosong atau terlalu panjang")
    expression = expression.replace("×", "*").replace("÷", "/")
    expression = expression.replace("−", "-").replace("π", "pi")
    expression = expression.replace("√", "sqrt")
    expression = expression.replace("x²", "**2").replace("²", "**2")
    expression = expression.replace("^", "**").replace("!", "fact")
    expression = re.sub(r"(?<![A-Za-z_])fact\s*(\d+(?:\.\d+)?)",
                        r"fact(\1)", expression)
    expression = re.sub(r"(\d+(?:\.\d*)?|\([^()]*\))\s*fact",
                        r"fact(\1)", expression)
    expression = re.sub(r"\b([A-Za-z_]\w*)\s*fact\b",
                        r"fact(\1)", expression)
    expression = re.sub(r"(?<!\d)\d{1,3}(?:\.\d{3})+(?![\d.])",
                        lambda match: match.group(0).replace(".", ""), expression)
    expression = expression.replace(",", ".")
    expression = _PERCENT_RE.sub(r"percent(\1)", expression)

    opened = expression.count("(")
    closed = expression.count(")")
    if closed > opened:
        raise CalculationError("Kurung tidak berpasangan")
    return expression + (")" * (opened - closed))


def evaluate(expression):
    """Evaluate a calculator expression without executing arbitrary Python."""
    normalized = normalize_expression(expression)
    try:
        result = _evaluate_expression_source(normalized)
    except CalculationError:
        raise
    except ZeroDivisionError:
        raise CalculationError("Tidak bisa dibagi nol")
    except (SyntaxError, DecimalException, OverflowError, ValueError,
            TypeError, RecursionError) as error:
        raise CalculationError(_friendly_error(error))
    if not result.is_finite():
        raise CalculationError("Hasil di luar rentang")
    return result


def _evaluate_node(node, source):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(ast.get_source_segment(source, node) or str(node.value))
    if isinstance(node, ast.Num):
        return Decimal(str(node.n))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _evaluate_node(node.left, source)
        if isinstance(node.right, ast.Call) and _is_function(node.right, "percent"):
            percent = _evaluate_node(node.right.args[0], source) / Decimal(100)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                right = left * percent
            else:
                right = percent
        else:
            right = _evaluate_node(node.right, source)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
            raise CalculationError("Pangkat terlalu besar")
        return _BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_evaluate_node(node.operand, source))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if name == "percent":
            _check_arity(node, 1)
            return _evaluate_node(node.args[0], source) / Decimal(100)
        if name not in _FUNCTIONS:
            raise CalculationError("Fungsi tidak dikenal")
        _check_arity(node, 1)
        value = _evaluate_node(node.args[0], source)
        return _call_function(name, value)
    if isinstance(node, ast.Name) and node.id in _CONSTANTS:
        return _CONSTANTS[node.id]
    raise CalculationError("Ekspresi tidak valid")


def _is_function(node, name):
    return isinstance(node.func, ast.Name) and node.func.id == name


def _check_arity(node, expected):
    if node.keywords or len(node.args) != expected:
        raise CalculationError("Jumlah argumen fungsi tidak valid")


def _call_function(name, value):
    if name == "abs":
        return abs(value)
    if name == "fact":
        if value != value.to_integral_value() or value < 0 or value > _MAX_FACTORIAL:
            raise CalculationError("Faktorial hanya menerima bilangan bulat 0–1000")
        return Decimal(math.factorial(int(value)))
    if name == "sqrt":
        if value < 0:
            raise CalculationError("Akar bilangan negatif tidak tersedia")
        return value.sqrt()
    if name in ("sin", "cos", "tan"):
        radians = math.radians(float(value))
        result = getattr(math, name)(radians)
    elif name == "log":
        result = math.log10(float(value))
    else:
        result = math.log(float(value))
    if not math.isfinite(result):
        raise CalculationError("Hasil di luar rentang")
    if name in ("sin", "cos", "tan"):
        result = round(result, 15)
    return Decimal(str(result))


def _friendly_error(error):
    message = str(error).lower()
    if "division by zero" in message or "divisão por zero" in message:
        return "Tidak bisa dibagi nol"
    if "math domain" in message:
        return "Nilai di luar domain fungsi"
    return "Ekspresi tidak valid"


def _evaluate_expression_source(source):
    tree = ast.parse(source, mode="eval")
    with localcontext() as context:
        context.prec = 28
        return _evaluate_node(tree.body, source)
