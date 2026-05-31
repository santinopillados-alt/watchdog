from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CPU_THRESHOLD = 80
MEMORIA_THRESHOLD = 90

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metricas (
            id SERIAL PRIMARY KEY,
            cpu FLOAT,
            memoria FLOAT,
            timestamp FLOAT,
            hora TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id SERIAL PRIMARY KEY,
            tipo TEXT,
            valor FLOAT,
            threshold FLOAT,
            hora TEXT,
            mensaje TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.post("/metricas")
def recibir_metrica(cpu: float, memoria: float, timestamp: float):
    hora = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO metricas (cpu, memoria, timestamp, hora) VALUES (%s, %s, %s, %s)",
        (cpu, memoria, timestamp, hora)
    )

    alertas_generadas = 0

    if cpu > CPU_THRESHOLD:
        mensaje = f"CPU al {cpu}% — supera el límite de {CPU_THRESHOLD}%"
        cur.execute(
            "INSERT INTO alertas (tipo, valor, threshold, hora, mensaje) VALUES (%s, %s, %s, %s, %s)",
            ("CPU_ALTA", cpu, CPU_THRESHOLD, hora, mensaje)
        )
        alertas_generadas += 1
        print(f"⚠ ALERTA: {mensaje}")

    if memoria > MEMORIA_THRESHOLD:
        mensaje = f"Memoria al {memoria}% — supera el límite de {MEMORIA_THRESHOLD}%"
        cur.execute(
            "INSERT INTO alertas (tipo, valor, threshold, hora, mensaje) VALUES (%s, %s, %s, %s, %s)",
            ("MEMORIA_ALTA", memoria, MEMORIA_THRESHOLD, hora, mensaje)
        )
        alertas_generadas += 1
        print(f"⚠ ALERTA: {mensaje}")

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "alertas_generadas": alertas_generadas}

@app.get("/metricas")
def ver_metricas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cpu, memoria, timestamp, hora FROM metricas ORDER BY id DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"cpu": r[0], "memoria": r[1], "timestamp": r[2], "hora": r[3]} for r in rows]

@app.get("/alertas")
def ver_alertas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT tipo, valor, threshold, hora, mensaje FROM alertas ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"tipo": r[0], "valor": r[1], "threshold": r[2], "hora": r[3], "mensaje": r[4]} for r in rows]

@app.get("/status")
def ver_status():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cpu, memoria FROM metricas ORDER BY id DESC LIMIT 1")
    ultima = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM metricas")
    total_metricas = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM alertas")
    total_alertas = cur.fetchone()[0]
    cur.close()
    conn.close()

    if not ultima:
        return {"status": "sin datos"}

    return {
        "cpu_actual": ultima[0],
        "memoria_actual": ultima[1],
        "total_mediciones": total_metricas,
        "total_alertas": total_alertas,
        "estado": "CRITICO" if total_alertas > 0 else "OK"
    }