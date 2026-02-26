# -------------------------------------IMPORTACIONES---------------------------------------
from fastapi import FastAPI, status, HTTPException

import asyncio

from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from datetime import datetime


# ---------------------------------INSTANCIA DEL SERVIDOR----------------------------------
app = FastAPI(
    title='¡API REPASO!',
    description='Urbano Zuñiga Yael Alejandro',
    version='1.0.0'
    )

usuarios = [
    {"id":1,"nombre":"Fidel","correo":"pompompurin@gmail.com"},
    {"id":2,"nombre":"Israel","correo":"reconcholis@gmail.com"},
    {"id":3,"nombre":"Abdiel","correo":"struck@gmail.com"},
]

libros = [
    {"id":1, "nombre":"Aprendendiendo de APIs", "estado":"Disponible", "año":2024, "páginas":500},
]

prestamos = [
    {"id": 1, "libro_id": 1, "usuario_id": 1}
]


# ----------------------------------MODELO DE VALIDACIÓN-----------------------------------
class usuario_create(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador único del usuario")
    nombre: str = Field(..., min_length = 3, max_length = 50, example = "Yael")
    correo: EmailStr = Field(..., example = "yael@gmail.com")

class libro_create(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador único del libro")
    nombre: str = Field(..., min_length = 1, max_length = 100, example = "El Principito")
    estado: str = Field(..., pattern = "^(Disponible|Prestado)$")
    año: int = Field(..., gt = 1450, le=datetime.now().year, example = 2006)
    paginas: int = Field(..., gt = 1, example = 500)

class prestamo_create(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador único del préstamo")
    libro_id: int = Field(..., gt = 0, description = "ID del libro referente al préstamo")
    usuario_id: int = Field(..., gt = 0, description = "ID del usuario referente al préstamo")


# ----------------------------------------ENDPOINTS----------------------------------------

@app.post("/v1/Registrar_Libro",  tags=['EndPoints'], status_code=status.HTTP_201_CREATED)
async def crear_libro(libro: libro_create):
    if libro.nombre.strip() == "":
        raise HTTPException(
            status_code = 400,
            detail="El nombre del libro no es válido"
        )
    
    for lbr in libros:
        if lbr["id"] == libro.id:
            raise HTTPException(
                status_code = 400,
                detail="El ID ya existe"
            )

    libros.append(libro.dict())
    return {
        "Mensaje": "Libro Agregado",
        "Libro": libro
    }

# ------------------------------------

@app.get("/v1/Listar_Libros/", tags=['EndPoints'])
async def listar_libros():
    return{
        "status":"200",
        "Total":len(libros),
        "Libros":libros
    }

# ------------------------------------

@app.get("/v1/Nombre_Libro/{nombre}", tags=['EndPoints'])
async def nombre_libros(nombre:str):
    if nombre is not None:
        for nbr in libros:
            if nbr["nombre"] == nombre:
                return {
                    "Mensaje": "Libro encontrado",
                    "Libro": nbr
                }
        return {
                "Mensaje: Libro no encontrado"
            }
    else:
        return {
            "Mensaje:" "NO SE PROPORCIONO NOMBRE"
        }

# ------------------------------------

@app.post("/v1/Registrar_Prestamo", tags=['EndPoints'], status_code=status.HTTP_201_CREATED)
async def registrar_prestamo(prestamo: prestamo_create):
    for pr in prestamos:
        if pr["id"] == prestamo.id:
            raise HTTPException(
                status_code=400,
                detail="El ID del préstamo ya existe"
            )
    for libro in libros:
        if libro["id"] == prestamo.libro_id:
            if libro["estado"] == "Prestado":
                raise HTTPException(
                    status_code=409,
                    detail="El libro ya está prestado"
                )
            libro["estado"] = "Prestado"
            prestamos.append(prestamo.dict())

            return {
                "Mensaje": "Préstamo registrado",
                "Prestamo": prestamo
            }
    raise HTTPException(
        status_code=400,
        detail="Libro no encontrado"
    )

# ------------------------------------

@app.put("/v1/Devolver_Libro/{id}", tags=['EndPoints'], status_code=status.HTTP_200_OK)
async def devolver_libro(id: int):
    for pr in prestamos:
        if pr["id"] == id:
            for libro in libros:
                if libro["id"] == pr["libro_id"]:
                    libro["estado"] = "Disponible"
            return {
                "Mensaje": "Libro devuelto correctamente"
            }
    raise HTTPException(
        status_code=409,
        detail="El registro de préstamo no existe"
    )

# ------------------------------------

@app.delete("/v1/Eliminar_Prestamo/{id}", tags=['EndPoints'], status_code=status.HTTP_200_OK)
async def eliminar_prestamo(id: int):
    for pr in prestamos:
        if pr["id"] == id:
            for libro in libros:
                if libro["id"] == pr["libro_id"]:
                    libro["estado"] = "Disponible"
            prestamos.remove(pr)
            return {
                "Mensaje": "Préstamo eliminado"
            }
    raise HTTPException(
        status_code=409,
        detail="El registro de préstamo no existe"
    )