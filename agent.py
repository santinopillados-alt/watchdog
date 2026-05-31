import psutil
import time
import requests

BACKEND_URL = "http://127.0.0.1:8000"

def capturar_y_enviar():
    cpu = psutil.cpu_percent(interval=1)
    memoria = psutil.virtual_memory().percent
    timestamp = time.time()
    
    requests.post(f"{BACKEND_URL}/metricas", params={
        "cpu": cpu,
        "memoria": memoria,
        "timestamp": timestamp
    })
    print(f"Enviado — CPU: {cpu}% | Memoria: {memoria}%")

while True:
    capturar_y_enviar()
    time.sleep(1)