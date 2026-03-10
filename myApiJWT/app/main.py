# -------------------------------------IMPORTACIONES---------------------------------------
from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from pydantic import BaseModel, Field

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# ---------------------------------INSTANCIA DEL SERVIDOR----------------------------------
app = FastAPI(
    title='¡API w/ JWT!',
    description='Urbano Zuñiga Yael Alejandro',
    version='1.0.0'
    )

usuarios=[
    {"id":1,"nombre":"Fidel","edad":21},
    {"id":2,"nombre":"Israel","edad":19},
    {"id":3,"nombre":"Abdiel","edad":19},
]



# ----------------------------------MODELO DE VALIDACIÓN-----------------------------------
class usuario_create(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador de usuario" )
    nombre: str = Field(..., min_length = 3, max_length = 50, example = "Ruth")
    edad: int = Field(..., ge = 1, le = 123, description = "Edad valida entre 1 y 123")

class usuario_delete(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador de usuario" )



# -----------------------------------CONFIGURACIÓN JWT------------------------------------
SECRET_KEY = "ContraseñaExtrema"
ALGORITHM = "HS256"                    
ACCESS_TOKEN_EXPIRE_MINUTES = 30        

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def crear_access_token(data:dict, expires_delta:Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt



# ----------------------------------------ENDPOINT DE LOGIN----------------------------------------
@app.post("/token", tags=['Autenticación'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario_valido = "ivanisay"
    clave_valida = "123456"

    if not (form_data.username == usuario_valido and form_data.password == clave_valida):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": form_data.username}, 
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



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



# ----------------------------------------GET----------------------------------------

@app.get("/v1/usuarios/", tags=['CRUD HTTP'])
async def leer_usuarios():
    return{
        "status":"200",
        "total":len(usuarios),
        "usuarios":usuarios
    }



# ----------------------------------------POST----------------------------------------

@app.post("/v1/usuarios/", tags=['CRUD HTTP'],status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario:usuario_create):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario Agregado",
        "Usuario":usuario
    }



# ----------------------------------------PUT----------------------------------------

@app.put("/v1/usuarios/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_200_OK)
async def actualizar_usuario(id:int, usuario:dict):
    for usr in usuarios:
        if usr["id"] == id:
            usr.update(usuario)
            return{
                "mensaje":"Usuario Actualizado",
                "Usuario":usr
            }
    raise HTTPException(
        status_code=400,
        detail="El ID no existe"
    )



# ----------------------------------------DELETE----------------------------------------

@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_200_OK)
async def eliminar_usuario(id:int):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return{
                "mensaje":"Usuario Borrado",
                "Usuario":usr
            }
    raise HTTPException(
        status_code=400,
        detail="El ID no existe"
    )