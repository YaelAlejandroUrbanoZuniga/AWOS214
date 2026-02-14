# -------------------------------------IMPORTACIONES---------------------------------------
from fastapi import FastAPI, status, HTTPException
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


@app.get("/v1/parametroOB/{id}", tags=['Parametro Obligatorio'])
async def consultaUno(id:int):
    return{"Se encontró usuario": id}

@app.get("/v1/parametroOP/", tags=['Parametro Opcional'])
async def consultaTodos(id:Optional[int]=None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return{"mensaje":"usuario encontrado","usuario": usuario}
        return{"mensaje":"usuario no encontrado","usuario": id} 
    else:
        return{"mensaje":"NO SE PROPORCIONO ID"}     
    
@app.get("/v1/usuarios/", tags=['CRUD HTTP'])
async def leer_usuarios():
    return{
        "status":"200",
        "total":len(usuarios),
        "usuarios":usuarios
    }

@app.post("/v1/usuarios/", tags=['CRUD HTTP'],status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario:dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario Agregado",
        "Usuario":usuario
    }








@app.put("/v1/usuarios/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_usuario(id:int, usuario:dict):
    for usr in usuarios:
        if usr["id"] == id:
            usr.update(usuario)
            return{
                "mensaje":"Usuario Actualizado",
                "Usuario":usuario
            }
    raise HTTPException(
        status_code=400,
        detail="El ID no existe"
    )
