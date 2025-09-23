from fastapi.testclient import TestClient

def test_create_turbine(client: TestClient):
    response = client.post("/turbines/", json={"location": "Test Site", "manufacturer": "Test Inc.", "model": "T-1000"})
    assert response.status_code == 201
    data = response.json()
    assert data["location"] == "Test Site"
    assert "turbine_id" in data

def test_get_all_turbines(client: TestClient):
    response = client.get("/turbines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_turbine_by_id(client: TestClient):
    response = client.get("/turbines/1")
    assert response.status_code == 200
    data = response.json()
    assert data["turbine_id"] == 1
    assert data["location"] == "North Sea"

def test_get_turbine_not_found(client: TestClient):
    response = client.get("/turbines/999")
    assert response.status_code == 404

def test_update_turbine(client: TestClient):
    response = client.put("/turbines/1", json={"location": "North Sea Updated", "manufacturer": "Siemens", "model": "V90"})
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "North Sea Updated"