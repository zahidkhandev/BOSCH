import pytest
import io
from fastapi.testclient import TestClient

pytestmark = pytest.mark.performance

def test_benchmark_upload_csv(client: TestClient, benchmark):
    header = "Lever position (Lp),Ship speed (V) [knots],Gas Turbine shaft torque (GTT) [kN/m],Gas Turbine revolutions (GTN) [rpm],Gas Generator revolutions (GGN) [rpm],Starboard Propeller Torque (Ts) [kN/m],Port Propeller Torque (Tp) [kN/m],HP Turbine exit temperature (T48) [°C],Compressor inlet air temperature (T1) [°C],Compressor outlet air temperature (T2) [°C],HP Turbine exit pressure (P48) [bar],Compressor inlet air pressure (P1) [bar],Compressor outlet air pressure (P2) [bar],Exhaust gas pressure (Pexh) [bar],Turbine Injecton Control (TIC) [%],Fuel flow (mf) [kg/s],Compressor decay coefficient,Turbine decay coefficient\n"
    row = "5.1,15,5000,3500,9000,55,56,650,20,500,1.2,1,10,1.01,80,0.4,0.99,0.99\n"
    csv_data = header + (row * 500)
    csv_bytes = io.BytesIO(csv_data.encode('utf-8'))
    file = ("benchmark_upload.csv", csv_bytes, "text/csv")
    
    benchmark(client.post, "/data/upload-data/1", files={"file": file})

def test_benchmark_analytics_report(client: TestClient, benchmark):
    filters = {"turbine_ids": [1]}
    benchmark(client.post, "/data/analytics-report", json=filters)