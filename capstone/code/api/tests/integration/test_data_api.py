import io
from fastapi.testclient import TestClient

def test_upload_csv_success_with_normal_data(client: TestClient):
    """
    Tests successful ingestion of a CSV with valid headers and normal data.
    """
    csv_data = (
        "Lever position (lp),Ship speed (v) [knots],Gas Turbine shaft torque (gtt) [kn/m],Gas Turbine revolutions (gtn) [rpm],Gas Generator revolutions (ggn) [rpm],Starboard Propeller Torque (ts) [kn/m],Port Propeller Torque (tp) [kn/m],HP Turbine exit temperature (t48) [°c],Compressor inlet air temperature (t1) [°c],Compressor outlet air temperature (t2) [°c],HP Turbine exit pressure (p48) [bar],Compressor inlet air pressure (p1) [bar],Compressor outlet air pressure (p2) [bar],Exhaust gas pressure [bar],Turbine Injection Control (tic) [%],Fuel flow (mf) [kg/s],Compressor decay coefficient,Turbine decay coefficient\n"
        "5.1,15,5000,3500,9000,55,56,650,20,500,1.2,1,10,1.01,80,0.25,0.99,0.99\n"
    )
    csv_bytes = io.BytesIO(csv_data.encode('utf-8'))
    file = ("test_normal_upload.csv", csv_bytes, "text/csv")

    response = client.post("/data/upload-data/1", files={"file": file})

    assert response.status_code == 201, f"API returned error: {response.json()}"
    assert "Successfully processed" in response.json()["message"]
    assert response.json()["anomalies_logged_count"] == 0
def test_upload_csv_with_anomalous_data_creates_alert(client: TestClient):
    """
    Tests that uploading a CSV with anomalous data (high T48) successfully creates an alert.
    """
    csv_data = (
        "Lever position (lp),"
        "Ship speed (v) [knots],"
        "Gas Turbine shaft torque (gtt) [kn/m],"
        "Gas Turbine revolutions (gtn) [rpm],"
        "Gas Generator revolutions (ggn) [rpm],"
        "Starboard Propeller Torque (ts) [kn/m],"
        "Port Propeller Torque (tp) [kn/m],"
        "HP Turbine exit temperature (t48) [°c],"
        "Compressor inlet air temperature (t1) [°c],"
        "Compressor outlet air temperature (t2) [°c],"
        "HP Turbine exit pressure (p48) [bar],"
        "Compressor inlet air pressure (p1) [bar],"
        "Compressor outlet air pressure (p2) [bar],"
        "Exhaust gas pressure [bar],"
        "Turbine Injection Control (tic) [%],"
        "Fuel flow (mf) [kg/s],"
        "Compressor decay coefficient,"
        "Turbine decay coefficient\n"
        "6.0,18,6000,3800,9500,60,61,960,25,550,1.5,1,12,1.05,85,0.5,0.98,0.98\n"
    )
    csv_bytes = io.BytesIO(csv_data.encode('utf-8'))
    file = ("test_anomaly_upload.csv", csv_bytes, "text/csv")

    upload_response = client.post("/data/upload-data/1", files={"file": file})

    assert upload_response.status_code == 201, f"API returned error: {upload_response.json()}"
    assert upload_response.json()["anomalies_logged_count"] > 0

    alerts_response = client.get("/data/alerts?turbine_id=1")
    assert alerts_response.status_code == 200
    alerts_data = alerts_response.json()

    assert alerts_data["metadata"]["total_items"] >= 1
    assert any(alert['metric'] == 't48' and alert['alert_type'] == 'Overheat' for alert in alerts_data["data"])

def test_get_sensor_metrics_pagination(client: TestClient):
    # This test is already correct and remains unchanged
    client.post("/data/sensor-reading/1", json={"timestamp": "2025-09-23T16:57:08", "lp": 1, "v": 1, "gtt": 1, "gtn": 1, "ggn": 1, "ts": 1, "tp": 1, "t48": 1, "t1": 1, "t2": 1, "p48": 1, "p1": 1, "p2": 1, "pexh": 1, "tic": 1, "mf": 1, "decay_coeff_comp": 1, "decay_coeff_turbine": 1})
    
    response = client.get("/data/sensor-metrics/1?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["current_page"] == 1
    assert len(data["data"]) == 1