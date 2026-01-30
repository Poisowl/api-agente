from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Definimos el modelo de entrada
class Coordenadas(BaseModel):
    latitud: float
    longitud: float

@app.post("/ubicacion")
def recibir_coordenadas(body: Coordenadas):
    mensaje = f"Recibí la ubicación: latitud {body.latitud}, longitud {body.longitud}"
    return {"mensaje": mensaje}
