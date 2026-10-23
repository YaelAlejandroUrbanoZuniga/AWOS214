# -------------------------------------IMPORTACIONES---------------------------------------
from fastapi import FastAPI, status, HTTPException, Depends, Request
from typing import Optional
import time
import os
from pydantic import BaseModel, Field

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader

# ---------------------------------INSTANCIA DEL SERVIDOR----------------------------------
app = FastAPI(
    title='¡Seguridad Informática | API!',
    description='Sierra Martinez Andre Alexander\n\nUrbano Zuñiga Yael Alejandro',
    version='1.0.0'
    )

usuarios=[
    {"id":1,"nombre":"Yayo","edad":20,"username":"yayo","password":"123456","rol":"admin"},
    {"id":2,"nombre":"Andre","edad":20,"username":"andre","password":"123456","rol":"usuario"},
    {"id":3,"nombre":"Alejandro","edad":19,"username":"alejandro","password":"123456","rol":"usuario"},
]



# ----------------------------------MODELO DE VALIDACIÓN-----------------------------------
class usuario_create(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador de usuario" )
    nombre: str = Field(..., min_length = 3, max_length = 50, example = "Ruth")
    edad: int = Field(..., ge = 1, le = 123, description = "Edad valida entre 1 y 123")
    username: str = Field(..., min_length = 3, max_length = 30, example = "ruth")
    password: str = Field(..., min_length = 6, max_length = 50, description = "Contraseña de minimo 6 caracteres")

class usuario_update(BaseModel):
    nombre: Optional[str] = Field(None, min_length = 3, max_length = 50, example = "Ruth")
    edad: Optional[int] = Field(None, ge = 1, le = 123, description = "Edad valida entre 1 y 123")
    password: Optional[str] = Field(None, min_length = 6, max_length = 50, description = "Contraseña de minimo 6 caracteres")



# --------------------------------OCULTAR DATOS SENSIBLES---------------------------------
def usuario_publico(usr:dict):
    return {
        "id":usr["id"],
        "nombre":usr["nombre"],
        "edad":usr["edad"],
        "username":usr["username"],
        "rol":usr["rol"]
    }



# -----------------------------------CONFIGURACIÓN JWT------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta la variable de entorno SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def crear_access_token(data:dict, expires_delta:Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credenciales_invalidas
    except JWTError:
        raise credenciales_invalidas

    for usr in usuarios:
        if usr["username"] == username:
            return usr
    raise credenciales_invalidas



# -----------------------------------CONFIGURACIÓN API KEY------------------------------------
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Falta la variable de entorno API_KEY")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validar_api_key(api_key: str = Depends(api_key_header)):
    if api_key is None or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key invalida o faltante",
        )
    return api_key



# -----------------------------------CONFIGURACIÓN ROLES------------------------------------
async def verificar_admin(usuario_actual: dict = Depends(obtener_usuario_actual)):
    if usuario_actual["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta accion",
        )
    return usuario_actual

def verificar_dueno_o_admin(id:int, usuario_actual:dict):
    if usuario_actual["rol"] != "admin" and usuario_actual["id"] != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes acceder a la informacion de otro usuario",
        )



# ---------------------------------CONFIGURACIÓN RATE LIMITER---------------------------------
LIMITE_PETICIONES = 5
VENTANA_SEGUNDOS = 60

registro_peticiones = {}

async def limitar_peticiones(request: Request):
    clave = request.client.host + " " + request.url.path
    ahora = time.time()

    peticiones_recientes = []
    for momento in registro_peticiones.get(clave, []):
        if ahora - momento < VENTANA_SEGUNDOS:
            peticiones_recientes.append(momento)

    if len(peticiones_recientes) >= LIMITE_PETICIONES:
        espera = int(VENTANA_SEGUNDOS - (ahora - peticiones_recientes[0])) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas peticiones, intenta de nuevo en " + str(espera) + " segundos",
            headers={"Retry-After": str(espera)},
        )

    peticiones_recientes.append(ahora)
    registro_peticiones[clave] = peticiones_recientes



# ----------------------------------------ENDPOINT DE LOGIN----------------------------------------
@app.post("/token", tags=['Autenticación'])
async def login_for_access_token(rate_limit = Depends(limitar_peticiones), form_data: OAuth2PasswordRequestForm = Depends()):
    usuario_valido = None
    for usr in usuarios:
        if usr["username"] == form_data.username and usr["password"] == form_data.password:
            usuario_valido = usr

    if usuario_valido is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": usuario_valido["username"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



# ----------------------------------------ENDPOINTS----------------------------------------
@app.get("/", tags=['Inicio'])
async def bienvenida():
    return{"mensaje": "¡Bienvenido a mi API!"}



# ----------------------------------------GET----------------------------------------

@app.get("/v1/usuarios/", tags=['CRUD HTTP'])
async def leer_usuarios(usuario_actual: dict = Depends(verificar_admin)):
    lista_usuarios = []
    for usr in usuarios:
        lista_usuarios.append(usuario_publico(usr))
    return{
        "status":"200",
        "total":len(usuarios),
        "usuarios":lista_usuarios
    }


@app.get("/v1/usuarios/{id}", tags=['CRUD HTTP'])
async def leer_usuario(id:int, usuario_actual: dict = Depends(obtener_usuario_actual)):
    verificar_dueno_o_admin(id, usuario_actual)
    for usr in usuarios:
        if usr["id"] == id:
            return{
                "mensaje":"Usuario Encontrado",
                "Usuario":usuario_publico(usr)
            }
    raise HTTPException(
        status_code=404,
        detail="El ID no existe"
    )



# ----------------------------------------POST----------------------------------------

@app.post("/v1/usuarios/", tags=['CRUD HTTP'],status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario:usuario_create, rate_limit = Depends(limitar_peticiones), api_key: str = Depends(validar_api_key)):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
        if usr["username"] == usuario.username:
            raise HTTPException(
                status_code=400,
                detail="El username ya existe"
            )
    nuevo_usuario = usuario.model_dump()
    nuevo_usuario["rol"] = "usuario"
    usuarios.append(nuevo_usuario)
    return{
        "mensaje":"Usuario Agregado",
        "Usuario":usuario_publico(nuevo_usuario)
    }



# ----------------------------------------PUT----------------------------------------

@app.put("/v1/usuarios/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_200_OK)
async def actualizar_usuario(id:int, usuario:usuario_update, usuario_actual: dict = Depends(obtener_usuario_actual)):
    verificar_dueno_o_admin(id, usuario_actual)
    for usr in usuarios:
        if usr["id"] == id:
            usr.update(usuario.model_dump(exclude_unset=True))
            return{
                "mensaje":"Usuario Actualizado",
                "Usuario":usuario_publico(usr)
            }
    raise HTTPException(
        status_code=404,
        detail="El ID no existe"
    )



# ----------------------------------------DELETE----------------------------------------

@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_200_OK)
async def eliminar_usuario(id:int, usuario_actual: dict = Depends(verificar_admin)):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return{
                "mensaje":"Usuario Borrado",
                "Usuario":usuario_publico(usr)
            }
    raise HTTPException(
        status_code=404,
        detail="El ID no existe"
    )
