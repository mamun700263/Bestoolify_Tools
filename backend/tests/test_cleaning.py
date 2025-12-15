import pytest

from app.scrapers.google_map import card_management


# class TestCardManagement():
@pytest.mark.parametrize(
    "address,expected",
    [
        ("Dhaka, Bangladesh", True),
        (". hell", False),
        ("Closed Today", False),
        (" . ", False),
        ("Open until 9PM", False),
        (" · 16 Chester Rd W", True),  # too short
        ("Mirpur DOHS", True),
    ],
)
def test_valid_address(address, expected):
    assert card_management.valid_address(address) == expected
