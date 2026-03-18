# ----------------------------------------IMPORTACIONES----------------------------------------
from fastapi import status, HTTPException, Depends, APIRouter

from app.models.usuario import usuario_create
from app.data.database import usuarios
from app.security.auth import verificar_Peticion


router = APIRouter(
    prefix = "/v1/usuarios", tags = ["CRUD HTTP"]
)

# ----------------------------------------GET----------------------------------------
@router.get("/")
async def leer_usuarios():
    return{
        "status":"200",
        "total":len(usuarios),
        "usuarios":usuarios
    }

# ----------------------------------------POST----------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
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
@router.put("/{id}", status_code=status.HTTP_200_OK)
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
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id:int, userAuth:str = Depends(verificar_Peticion)):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return{
                "mensaje":f"Usuario Borrado Por: {userAuth}",
                "Usuario":usr
            }
    raise HTTPException(
        status_code=400,
        detail="El ID no existe"
    )