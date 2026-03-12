# ----------------------- IMPORTACIONES -----------------------

from fastapi import FastAPI, status, HTTPException, Depends

from typing import Optional

from pydantic import BaseModel, Field

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets



# ----------------------- INSTANCIAS -----------------------

app = FastAPI(
    title='¡API Sistema de Tickets de Soporte Técnico!',
    description='Urbano Zuñiga Yael Alejandro',
    version='1.0.0'
    )

tickets = [
    {"id":1, "usuario":"Fidel", "descripción":"Al querer realizar mi Examen del Segundo Parcial, no se me abrió el ChatGPT", "prioridad":"Baja", "estado":"Pendiente"}
]



# ----------------------- VERIFICACIONES -----------------------

security = HTTPBasic()
def verificar_Peticion(credenciales:HTTPBasicCredentials = Depends(security)):
    userAuth = secrets.compare_digest(credenciales.username,"soporte")
    passAuth = secrets.compare_digest(credenciales.password,"4321")

    if not(userAuth and passAuth):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciales no Autorizadas"
        )
    return credenciales.username

class ticket_create(BaseModel):
    id: int = Field(..., gt = 0, description = "Identificador único del ticket")
    usuario: str = Field(..., min_length = 5, max_length = 50, example = "Fidel")
    descripción: str = Field(..., min_length = 20, max_length = 200, example = "Cuando hice mi examen de cálculo con la calculadora, todas las respuestas me dieron SINTAX ERROR")
    prioridad: str = Field(..., pattern = "^(Baja|Media|Alta)$", example = "Baja")
    estado: str = Field(..., pattern = "^(Pendiente|Resuelto)$", example = "Pendiente")



# ----------------------- ENDPOINTS -----------------------

# --- CREAR
@app.post("/v1/Crear_Ticket/", tags=['EndPoints'],status_code=status.HTTP_201_CREATED)
async def crear_ticket(ticket: ticket_create):
    for tck in tickets:
        if tck["id"] == ticket.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
    tickets.append(ticket.dict())
    return{
        "mensaje":"Ticket Creado",
        "Ticket":ticket.dict()
    }

# --- LISTAR
@app.get("/v1/Listar_Tickets/", tags=['EndPoints'])
async def listar_tickets():
    return{
        "status":"200",
        "Total":len(tickets),
        "Tickets":tickets
    }

# --- CONSULTAR x ID
@app.get("/v1/Consultar_Ticket/{id}", tags=['EndPoints'])
async def consultar_ticket(id:int, userAuth:str = Depends(verificar_Peticion)):
    if id is not None:
        for cid in tickets:
            if cid["id"] == id:
                return {
                    "Mensaje": "Ticket encontrado",
                    "Mensaje": f"Ticket Consultado Por: {userAuth}",
                    "Ticket": cid
                }
        return {
                "Mensaje": "Ticket no encontrado"
            }
    else:
        return {
            "Mensaje": "NO SE PROPORCIONO ID"
        }



# --- CAMBIAR ESTADO
@app.put("/v1/Cambiar_Estado/{id}", tags=['EndPoints'], status_code=status.HTTP_200_OK)
async def cambiar_estado(id: int, estado: str, userAuth:str = Depends(verificar_Peticion)):
    for tck in tickets:
        if tck["id"] == id:
            tck["estado"] = estado
            return {
                "Mensaje": "Estado cambiado correctamente",
                "Mensaje": f"Estado Cambiado Por: {userAuth}",
            }
    if estado not in ["Pendiente", "Resuelto"]:
        raise HTTPException(
            status_code=400,
            detail="Estado inválido"
        )

# --- ELIMINAR TICKET
@app.delete("/v1/Eliminar_Ticket/{id}", tags=['EndPoints'])
async def eliminar_usuario(id:int):
    for eid in tickets:
        if eid["id"] == id:
            if eid["estado"] == "Resuelto":
                raise HTTPException(
                    status_code = 400,
                    detail = "No se pueden eliminar tickets con estado: Resuelto"
                    )
            tickets.remove(eid)
            return{
                "Mensaje":"Ticket Borrado",
                "Ticket": eid
            }
    raise HTTPException(
        status_code = 400,
        detail = "El ID no existe"
    )