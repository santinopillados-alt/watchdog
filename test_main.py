from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)


def test_status_sin_datos():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "sin datos"


def test_recibir_metrica():
    response = client.post("/metricas", params={
        "cpu": 45.2,
        "memoria": 70.0,
        "timestamp": time.time()
    })
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ver_metricas():
    response = client.get("/metricas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_status_con_datos():
    response = client.get("/status")
    data = response.json()
    assert "cpu_actual" in data
    assert "memoria_actual" in data
    assert "estado" in data


def test_alerta_cpu_alta():
    response = client.post("/metricas", params={
        "cpu": 95.0,
        "memoria": 50.0,
        "timestamp": time.time()
    })
    assert response.json()["alertas_activas"] > 0


def test_alerta_memoria_alta():
    response = client.post("/metricas", params={
        "cpu": 10.0,
        "memoria": 95.0,
        "timestamp": time.time()
    })
    assert response.json()["alertas_activas"] > 0


def test_ver_alertas():
    response = client.get("/alertas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)