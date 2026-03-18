# -------------------------------------IMPORTACIONES---------------------------------------
from fastapi import FastAPI
from app.routers import usuarios, varios

# ---------------------------------INSTANCIA DEL SERVIDOR----------------------------------
app = FastAPI(
    title='¡MI PRIMER API!',
    description='Urbano Zuñiga Yael Alejandro',
    version='1.0.0'
    )

app.include_router(usuarios.router)
app.include_router(varios.router)