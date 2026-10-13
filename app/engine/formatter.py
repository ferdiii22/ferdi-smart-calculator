"""Locale-aware display formatting for calculator results."""

from decimal import Decimal


def format_result(value, max_decimals=10):
    value = value if isinstance(value, Decimal) else Decimal(str(value))
    if not value.is_finite():
        return "Tidak terdefinisi"
    if value != 0 and (abs(value) >= Decimal("1e15") or abs(value) < Decimal("1e-8")):
        return "{:e}".format(value.normalize()).replace(".", ",")
    quantized = value.quantize(Decimal(1).scaleb(-max_decimals))
    text = format(quantized.normalize(), "f")
    integer, dot, fraction = text.partition(".")
    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]
    grouped = []
    while integer:
        grouped.insert(0, integer[-3:])
        integer = integer[:-3]
    return sign + ".".join(grouped or ["0"]) + ("," + fraction if dot else "")


def format_editable(value):
    """Return an ungrouped decimal expression suitable for editing again."""
    value = value if isinstance(value, Decimal) else Decimal(str(value))
    return format(value.normalize(), "f") if value else "0"
