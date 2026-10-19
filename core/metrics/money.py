"""Two-decimal monetary arithmetic with integer minor-unit accumulation.

The V1 CSV contract does not identify a currency. Values are kept as plain
currency-*agnostic* amounts, not USD, converted FX rates or tax accounting.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")
HUNDRED = Decimal(100)
# Guard the numeric JSON boundary: amounts must still round-trip to cents
# when exposed as ordinary numbers to the existing frontend.
MAX_MINOR_UNITS = 10**13


def minor_units(value: object, column: str, row: int) -> int:
    """Validate a row's monetary field; reject unapproved fractional cents."""
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as error:
        raise ValueError(
            f"Column '{column}' has a missing or invalid amount at data row {row}."
        ) from error

    if not amount.is_finite():
        raise ValueError(
            f"Column '{column}' has a missing or non-finite amount at data row {row}."
        )

    scaled = amount * HUNDRED
    if scaled != scaled.to_integral_value():
        raise ValueError(
            f"Column '{column}' contains more than two decimal places "
            f"at data row {row}; no silent rounding is allowed."
        )
    if abs(scaled) > MAX_MINOR_UNITS:
        raise ValueError(
            f"Column '{column}' exceeds the supported amount range at data row {row}."
        )
    return int(scaled)


def sum_minor_units(values, column: str) -> int:
    """Accumulate whole cents, never a sum of binary floating-point values."""
    total = sum(
        minor_units(value, column, position)
        for position, value in enumerate(values, start=1)
    )
    if abs(total) > MAX_MINOR_UNITS:
        raise ValueError(f"Total '{column}' exceeds the supported amount range.")
    return total


def as_amount(cents: int) -> float:
    """Compatibility output: JSON numeric amount, rounded at cent granularity."""
    return float(Decimal(cents) / HUNDRED)


def percent(numerator_cents: int, denominator_cents: int) -> float | None:
    """Return a rounded percentage from exact integers; unknown when denom <= 0."""
    if denominator_cents <= 0:
        return None
    ratio = (Decimal(numerator_cents) / Decimal(denominator_cents)) * HUNDRED
    return float(ratio.quantize(CENT, rounding=ROUND_HALF_UP))


def average(cents: int, count: int) -> float | None:
    """Round once at the final per-order amount, never at individual rows."""
    if count <= 0:
        return None
    value = Decimal(cents) / (HUNDRED * Decimal(count))
    return float(value.quantize(CENT, rounding=ROUND_HALF_UP))
