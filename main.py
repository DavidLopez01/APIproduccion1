from fastapi import FastAPI
from routers import auth_r, roles, users, area, subjects, notes, login
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="P1SW APIs",
    version="1.0.0",
)

# =============================
#   🔐 CORS SOLO PARA TU FRONT
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],   # SOLO tu frontend
    allow_credentials=True,                    # Ahora SÍ puede ser True
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
#   📌 Routers del proyecto
# =============================
app.include_router(auth_r.router)
app.include_router(roles.router)
app.include_router(users.router)
app.include_router(area.router)
app.include_router(subjects.router)
app.include_router(notes.router)
app.include_router(login.router)

# =============================
#   🔑 JWT en Swagger
# =============================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="P1SW APIs",
        version="1.0.0",
        description="Documentación de las APIs del proyecto P1SW",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
