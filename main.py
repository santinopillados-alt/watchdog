from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

metricas = []
alertas = []

CPU_THRESHOLD = 80
MEMORIA_THRESHOLD = 90

@app.post("/metricas")
def recibir_metrica(cpu: float, memoria: float, timestamp: float):
    hora = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    
    metrica = {
        "cpu": cpu,
        "memoria": memoria,
        "timestamp": timestamp,
        "hora": hora
    }
    metricas.append(metrica)

    if cpu > CPU_THRESHOLD:
        alerta = {
            "tipo": "CPU_ALTA",
            "valor": cpu,
            "threshold": CPU_THRESHOLD,
            "hora": hora,
            "mensaje": f"CPU al {cpu}% — supera el límite de {CPU_THRESHOLD}%"
        }
        alertas.append(alerta)
        print(f"⚠ ALERTA: {alerta['mensaje']}")

    if memoria > MEMORIA_THRESHOLD:
        alerta = {
            "tipo": "MEMORIA_ALTA",
            "valor": memoria,
            "threshold": MEMORIA_THRESHOLD,
            "hora": hora,
            "mensaje": f"Memoria al {memoria}% — supera el límite de {MEMORIA_THRESHOLD}%"
        }
        alertas.append(alerta)
        print(f"⚠ ALERTA: {alerta['mensaje']}")

    return {"status": "ok", "alertas_activas": len(alertas)}

@app.get("/metricas")
def ver_metricas():
    return metricas

@app.get("/alertas")
def ver_alertas():
    return alertas

@app.get("/status")
def ver_status():
    if not metricas:
        return {"status": "sin datos"}
    
    ultima = metricas[-1]
    return {
        "cpu_actual": ultima["cpu"],
        "memoria_actual": ultima["memoria"],
        "total_mediciones": len(metricas),
        "total_alertas": len(alertas),
        "estado": "CRITICO" if len(alertas) > 0 else "OK"
    }