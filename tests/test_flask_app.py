import pytest

from src.app import app


@pytest.fixture(scope="module")
def test_client():
    with app.test_client() as client:
        yield client


def test_home_page_loads(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Rising Waters" in response.data or b"Flood" in response.data


def test_predict_page_loads(test_client):
    response = test_client.get("/predict")
    assert response.status_code == 200
    assert b"Flood risk evaluation" in response.data


def test_predict_route_returns_result(test_client):
    form_data = {
        "temperature": "29",
        "humidity": "70",
        "cloud_cover": "30",
        "annual_rainfall": "3248.6",
        "jan_feb": "73.4",
        "mar_may": "386.2",
        "jun_sep": "2122.8",
        "oct_dec": "666.1",
        "average_june": "274.866667",
        "sub": "649.9",
    }
    response = test_client.post("/predict", data=form_data)
    assert response.status_code == 200
    assert b"No Flood Detected" in response.data or b"Flood Detected" in response.data
    assert b"Input Summary" in response.data


def test_predict_route_returns_error_for_invalid_input(test_client):
    form_data = {
        "temperature": "invalid",
        "humidity": "70",
        "cloud_cover": "30",
        "annual_rainfall": "3248.6",
        "jan_feb": "73.4",
        "mar_may": "386.2",
        "jun_sep": "2122.8",
        "oct_dec": "666.1",
        "average_june": "274.866667",
        "sub": "649.9",
    }
    response = test_client.post("/predict", data=form_data)
    assert response.status_code == 200
    assert b"Invalid numeric value for" in response.data
