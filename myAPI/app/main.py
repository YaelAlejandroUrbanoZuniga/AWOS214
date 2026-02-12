# -------------------------------------IMPORTACIONES---------------------------------------
from fastapi import FastAPI
import asyncio
from typing import Optional

# ---------------------------------INSTANCIA DEL SERVIDOR----------------------------------
app = FastAPI(
    title='¡MI PRIMER API!',
    description='Urbano Zuñiga Yael Alejandro',
    version='1.0.0'
    )

usuarios=[
    {"id":1,"nombre":"Fidel","edad":21},
    {"id":2,"nombre":"Israel","edad":19},
    {"id":3,"nombre":"Abdiel","edad":19},
]

# ----------------------------------------ENDPOINTS----------------------------------------
@app.get("/", tags=['Inicio'])
async def bienvenida():
    return{"mensaje": "¡Bienvenido a mi API!"}


@app.get("/HolaMundo", tags=['Bienvenida Asincrona'])
async def hola():
    await asyncio.sleep(4) #Simulación de una petición
    return{
        "mensaje": "¡Hola Mundo FastAPI!",
        "estatus": "200"}


@app.get("/v1/usuario/{id}", tags=['Parametro Obligatorio'])
async def consultaUno(id:int):
    return{"Se encontró usuario": id}

@app.get("/v1/usuarios/", tags=['Parametro Opcional'])
async def consultaTodos(id:Optional[int]=None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return{"mensaje":"usuario encontrado","usuario": usuario}
        return{"mensaje":"usuario no encontrado","usuario": id} 
    else:
        return{"mensaje":"NO SE PROPORCIONO ID"}     
        