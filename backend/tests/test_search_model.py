import pytest
from pydantic import ValidationError

from app.models import GoogleMapSearch


class TestGoogleMapSearch:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_data = {
            "name": "KFC Liverpool",
            "link": "https://maps.google.com/kfc",
            "address": "12 Bold St, Liverpool, UK",
            "image": "https://example.com/kfc.jpg",
            "rating": 4.5,
            "reviews": 230,
            "query": "KFC near Liverpool",
        }

    def test_valid_model_creation(self):
        model = GoogleMapSearch(**self.base_data)
        assert model.name == "KFC Liverpool"
        assert model.rating == 4.5

    def test_invalid_rating(self):
        bad = self.base_data | {"rating": "bad"}
        with pytest.raises(ValidationError):
            GoogleMapSearch(**bad)

    def test_invalid_text_rating(self):
        bad = self.base_data["rating"] = "4.3"
        assert bad == 4.3

    def test_missing_required_field(self):
        bad = self.base_data.copy()
        del bad["link"]
        with pytest.raises(ValidationError):
            GoogleMapSearch(**bad)
