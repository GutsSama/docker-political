import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app

client = TestClient(app)

# On doit SETTER DATABASE_URL avant d'importer l'app (déjà fait en ligne 11-12 via os.environ)

# == ============================== ============================== ==
# FIXTURES
# == ============================== ============================== ==

@pytest.fixture
def commune_data():
    return {
        "id": 1,
        "years": "2022",
        "city": "Armentières",
        "code_insee": "59009",
        "pct_gauche": 40.0,
        "pct_centre": 30.0,
        "pct_droite": 30.0,
        "statistics": {"pct_abstention": 25.0},
        "updated_at": datetime(2022, 1, 1).isoformat(),
    }

@pytest.fixture
def commune_light_data():
    return {"code_insee": "59009", "city": "Armentières"}

@pytest.fixture
def prediction_data():
    return {
        "code_insee": "59009",
        "city": "Lille",
        "prediction_2027": "Gauche",
        "confiance_percent": 85.0,
        "scores": {"Gauche": 85.0, "Centre": 10.0, "Droite": 5.0}
    }

# == ============================== ============================== ==
# TESTS
# == ============================== ============================== ==

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@patch("app.services.communes.CommuneService.get_all")
def test_get_and_search_communes(mock_get_all, commune_data):
    mock_get_all.return_value = (1, [commune_data])
    response = client.get("/communes/?skip=0&limit=50")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["total"] == 1
    assert len(res_json["data"]) == 1
    assert res_json["data"][0]["city"] == "Armentières"

def test_get_commune_by_code_missing_param():
    # Since we modified this endpoint to raise HTTPException, it should return 400
    response = client.get("/communes/commune?code_insee=59009")
    assert response.status_code == 400

@patch("app.services.communes.CommuneService.get_by_insee")
def test_get_commune_by_code_success(mock_get_by_insee, commune_data):
    mock_get_by_insee.return_value = [commune_data]
    response = client.get("/communes/commune?code_insee=59009&year=2022")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code_insee"] == "59009"