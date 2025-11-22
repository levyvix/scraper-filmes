import pytest
from scrapers.utils.parse_utils import parse_rating, parse_year, parse_int


class TestParseRating:
    """Test parse_rating function."""

    def test_valid_rating(self):
        assert parse_rating("8.5") == 8.5
        assert parse_rating("7,5") == 7.5  # Comma separator

    def test_invalid_rating(self):
        assert parse_rating("invalid") is None
        assert parse_rating("") is None
        assert parse_rating(None) is None

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("9.0", 9.0),
            ("10", 10.0),
            ("0.5", 0.5),
        ],
    )
    def test_rating_variations(self, input_val, expected):
        assert parse_rating(input_val) == expected


class TestParseYear:
    """Test parse_year function."""

    def test_valid_year(self):
        assert parse_year("2023") == 2023
        assert parse_year(" 1999 ") == 1999

    def test_invalid_year(self):
        assert parse_year("invalid") is None
        assert parse_year("20.23") is None
        assert parse_year("") is None
        assert parse_year(None) is None


class TestParseInt:
    """Test parse_int function."""

    def test_valid_int(self):
        assert parse_int("120") == 120
        assert parse_int(" -50 ") == -50

    def test_invalid_int(self):
        assert parse_int("invalid") is None
        assert parse_int("12.5") is None
        assert parse_int("") is None
        assert parse_int(None) is None
