# ----------------------------------------IMPORTACIONES----------------------------------------
from app.data.database import usuarios

import asyncio

from typing import Optional

from fastapi import APIRouter

router = APIRouter(tags = ['Varios'])

# ----------------------------------------ENDPOINTS----------------------------------------
@router.get("/")
async def bienvenida():
    return{"mensaje": "¡Bienvenido a mi API!"}

@router.get("/HolaMundo")
async def hola():
    await asyncio.sleep(4) #Simulación de una petición
    return{
        "mensaje": "¡Hola Mundo FastAPI!",
        "estatus": "200"}

@router.get("/v1/parametroOB/{id}")
async def consultaUno(id:int):
    return{"Se encontró usuario": id}

@router.get("/v1/parametroOP/")
async def consultaTodos(id:Optional[int]=None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return{"mensaje":"usuario encontrado","usuario": usuario}
        return{"mensaje":"usuario no encontrado","usuario": id} 
    else:
        return{"mensaje":"NO SE PROPORCIONO ID"}     