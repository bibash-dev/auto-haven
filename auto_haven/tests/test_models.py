import pytest
from auto_haven.models.car import Car, CarCollection
from pydantic import ValidationError


# Fixture for test data
@pytest.fixture
def test_car1():
    return Car(
        brand="Ford", model="Fiesta", year=2019, cm3=1500, kw=85, km=40000, price=10000,
        image_url="http://example.com/new-image.jpg"
    )


@pytest.fixture
def test_car2():
    return Car(
        brand="Fiat", model="Stilo", year=2003, cm3=1600, kw=85, km=80000, price=3000,
        image_url="http://example.com/new-image2.jpg"
    )


@pytest.fixture
def car_collection(test_car1, test_car2):
    return CarCollection(cars=[test_car1, test_car2])


# Test cases
def test_car_creation(test_car1):
    assert test_car1.brand == "Ford"
    assert test_car1.model == "Fiesta"
    assert test_car1.year == 2019
    assert test_car1.cm3 == 1500
    assert test_car1.kw == 85
    assert test_car1.km == 40000
    assert test_car1.price == 10000
    assert str(test_car1.image_url) == "http://example.com/new-image.jpg"


def test_car_invalid_year():
    with pytest.raises(ValidationError):
        Car(
            brand="Ford", model="Fiesta", year=1899, cm3=1500, kw=85, km=40000, price=10000,
            image_url="http://example.com/new-image.jpg"
        )


def test_car_collection(car_collection):
    cars = car_collection.model_dump()
    assert len(cars["cars"]) == 2
    assert cars["cars"][0]["brand"] == "Ford"
    assert cars["cars"][1]["brand"] == "Fiat"


def test_car_collection_empty():
    collection = CarCollection(cars=[])
    assert collection.model_dump() == {"cars": []}


def test_car_invalid_url():
    with pytest.raises(ValidationError):
        Car(
            brand="Ford", model="Fiesta", year=2019, cm3=1500, kw=85, km=40000, price=10000,
            image_url="invalid-url"
        )
