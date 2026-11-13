import pytest

from learning_tracker.ielts import ielts_overall, is_valid_band


@pytest.mark.parametrize(
    "skills, expected",
    [
        # Scores from the mockup's practice history
        ((7, 6.5, 6, 6.5), 6.5),  # 6.5 exactly
        ((6.5, 6.5, 6, 6), 6.5),  # 6.25 rounds up to 6.5
        ((6.5, 6, 5.5, 6), 6.0),  # 6.0 exactly
        # Boundaries
        ((6, 6, 6, 6.5), 6.0),  # 6.125 rounds down to 6.0
        ((6, 6.5, 6.5, 6.5), 6.5),  # 6.375 rounds to 6.5
        ((6.5, 7, 7, 6.5), 7.0),  # 6.75 rounds up to 7.0
        ((9, 9, 9, 8.5), 9.0),  # 8.875 rounds up to 9.0
        ((0, 0, 0, 0), 0.0),
        ((9, 9, 9, 9), 9.0),
    ],
)
def test_overall_band(skills, expected):
    assert ielts_overall(*skills) == expected


@pytest.mark.parametrize("value", [0, 0.5, 6, 6.5, 9, "7.5"])
def test_valid_bands(value):
    assert is_valid_band(value)


@pytest.mark.parametrize("value", [-0.5, 9.5, 6.3, 6.25, "abc", None])
def test_invalid_bands(value):
    assert not is_valid_band(value)


def test_overall_rejects_an_invalid_skill():
    with pytest.raises(ValueError):
        ielts_overall(6.3, 6, 6, 6)
