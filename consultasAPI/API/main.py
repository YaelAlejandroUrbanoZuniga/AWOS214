from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI(
    title="API Usuarios",
    description="API para React Native",
    version="1.0.0"
)

usuarios = [
    {
        "id": 1,
        "nombre": "Fidel",
        "edad": 25,
        "fechaCreacion": datetime.now()
    },
    {
        "id": 2,
        "nombre": "Israel",
        "edad": 22,
        "fechaCreacion": datetime.now()
    }
]


# MODELO
class Usuario(BaseModel):
    id: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=3, max_length=50)
    edad: int = Field(..., gt=0)


# -------------------------
# OBTENER USUARIOS
# -------------------------
@app.get("/v1/usuarios")
async def obtener_usuarios():
    return usuarios


# -------------------------
# CREAR USUARIO
# -------------------------
@app.post("/v1/usuarios", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: Usuario):

    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )

    nuevo_usuario = usuario.dict()
    nuevo_usuario["fechaCreacion"] = datetime.now()

    usuarios.append(nuevo_usuario)

    return nuevo_usuario


# -------------------------
# ACTUALIZAR USUARIO
# -------------------------
@app.put("/v1/usuarios/{id}")
async def actualizar_usuario(id: int, usuario: Usuario):

    for usr in usuarios:

        if usr["id"] == id:
            usr["nombre"] = usuario.nombre
            usr["edad"] = usuario.edad

            return {
                "mensaje": "Usuario actualizado",
                "usuario": usr
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )


# -------------------------
# ELIMINAR USUARIO
# -------------------------
@app.delete("/v1/usuarios/{id}")
async def eliminar_usuario(id: int):

    for usr in usuarios:

        if usr["id"] == id:
            usuarios.remove(usr)

            return {
                "mensaje": "Usuario eliminado"
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )