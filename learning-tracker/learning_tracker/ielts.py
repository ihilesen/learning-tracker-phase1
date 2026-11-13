"""IELTS scoring rules.

The overall band is the average of the four skill bands, rounded to the
nearest half band. Averages that end in .25 round up to the next half band
and averages that end in .75 round up to the next whole band, which is how
IELTS reports overall scores.
"""

from decimal import Decimal
import math

BAND_MIN = Decimal("0")
BAND_MAX = Decimal("9")
BAND_STEP = Decimal("0.5")


def is_valid_band(value) -> bool:
    """True if value is a band from 0 to 9 in steps of 0.5."""
    try:
        band = Decimal(str(value))
    except Exception:
        return False
    if band < BAND_MIN or band > BAND_MAX:
        return False
    return (band / BAND_STEP) == (band / BAND_STEP).to_integral_value()


def ielts_overall(listening, reading, writing, speaking) -> float:
    """Return the overall band for four skill bands.

    Uses Decimal so values such as 6.25 are never affected by float error.
    Raises ValueError if any skill is not a valid band.
    """
    skills = (listening, reading, writing, speaking)
    for skill in skills:
        if not is_valid_band(skill):
            raise ValueError(
                f"{skill!r} is not a valid band (0 to 9 in steps of 0.5)"
            )
    average = sum(Decimal(str(s)) for s in skills) / Decimal(4)
    # Round half up to the nearest 0.5: floor(average * 2 + 0.5) / 2
    doubled = average * 2 + Decimal("0.5")
    return float(Decimal(math.floor(doubled)) / 2)
