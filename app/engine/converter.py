"""Unit conversion helpers for length, mass, temperature, and data."""

from decimal import Decimal


UNITS = {
    "Panjang": {
        "Meter": Decimal("1"), "Kilometer": Decimal("1000"),
        "Sentimeter": Decimal("0.01"), "Milimeter": Decimal("0.001"),
        "Mil": Decimal("1609.344"), "Kaki": Decimal("0.3048"),
        "Inci": Decimal("0.0254"),
    },
    "Berat": {
        "Kilogram": Decimal("1"), "Gram": Decimal("0.001"),
        "Miligram": Decimal("0.000001"), "Ton": Decimal("1000"),
        "Pon": Decimal("0.45359237"), "Ons": Decimal("0.1"),
    },
    "Data": {
        "Byte": Decimal("1"), "Kilobyte": Decimal("1000"),
        "Megabyte": Decimal("1000000"), "Gigabyte": Decimal("1000000000"),
        "Kibibyte": Decimal("1024"), "Mebibyte": Decimal("1048576"),
        "Gibibyte": Decimal("1073741824"),
    },
    "Suhu": {
        "Celsius": None, "Fahrenheit": None, "Kelvin": None,
    },
}


def convert(value, category, source, target):
    """Convert a Decimal value between units in one supported category."""
    value = value if isinstance(value, Decimal) else Decimal(str(value))
    if category not in UNITS:
        raise ValueError("Kategori satuan tidak dikenal")
    if source not in UNITS[category] or target not in UNITS[category]:
        raise ValueError("Satuan tidak tersedia pada kategori ini")
    if category == "Suhu":
        return _convert_temperature(value, source, target)
    base_value = value * UNITS[category][source]
    return base_value / UNITS[category][target]


def _convert_temperature(value, source, target):
    if source == target:
        return value
    if source == "Celsius":
        celsius = value
    elif source == "Fahrenheit":
        celsius = (value - Decimal(32)) * Decimal(5) / Decimal(9)
    else:
        celsius = value - Decimal("273.15")
    if target == "Celsius":
        return celsius
    if target == "Fahrenheit":
        return celsius * Decimal(9) / Decimal(5) + Decimal(32)
    return celsius + Decimal("273.15")
