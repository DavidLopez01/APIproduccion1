# 📌 API REST con **FastAPI** -  **SQLAlchemy** - **Cors** - **JWT**

# P1SW APIs
Este proyecto implementa una API RESTful con **FastAPI**, utilizando **SQLAlchemy** como ORM y **SQL Server** como motor de base de datos.

Permite gestionar **Usuarios**, **Roles**, **Áreas**, **Asignaturas**, **Notas** y **Préstamos de dispositivos**, con Cors, autenticación JWT y control de acceso por roles.

---

## 🏗️ Arquitectura del Proyecto

La estructura de carpetas es la siguiente:

📂 Proyecto

┣ 📂 database       # Conexión a la base de datos y gestión de sesiones  
┣ 📂 migrate        # Scripts de migración para crear las tablas en la BD  
┣ 📂 schemas         # Modelos Pydantic y SQLAlchemy (tablas + respuestas)  
┣ 📂 routers        # Endpoints (CRUD y lógica de negocio)  
┣ 📂 deps           # Dependencias (auth, db)  
┣ 📂 core           # Configuración del proyecto (SECRET_KEY, ALGORITHM)  
┣ 📜 main.py        # Punto de entrada de la aplicación  
┣ 📜 requirements.txt  
┣ 📜 test_connection.py  # Script para validar la conexión a la BD  

---

## ⚙️ Configuración Inicial

1. **Instalar dependencias**  
   Desde la raíz del proyecto:
    ```bash
    pip install -r requirements.txt

---

2. **Configurar la base de datos**  
    Crea una base de datos llamada P1SW.
    Actualiza las variables de conexión en database/connection.py según tu entorno.

---

3. **Probar la conexión**  
    Ejecuta el script:
    ```bash
    python test_connection.py

    ✅ Si todo está correcto, verás un mensaje confirmando la conexión a SQL Server

---

4. **Migrar las tablas a la BD**  
    Desde la raíz del proyecto, corre:
    ```bash
    python -m migrate.database

---

5. **Levantar el servidor**  
    ```bash
    uvicorn main:app --reload

La API quedará disponible en: 👉 http://127.0.0.1:8000/docs

⚠️ Los endpoints protegidos requieren token JWT válido. Obtén el token con /auth/token o /login/ y agrégalo usando el botón Authorize en Swagger.

---

## 📚 Endpoints Principales

**Usuario para pruebas**

{
  "username": "admin",
  "password": "123456"
}

**Autenticación:**

POST /auth/token: Obtener token JWT.
Body (JSON):

{
  "username": "usuario",
  "password": "contraseña"
}

**Respuesta exitosa (200 OK):**

{
  "access_token": "<token_jwt>",
  "token_type": "bearer"
}

**Usuarios (PROTEGIDOS)**

    GET /users/ → Listar usuarios con paginación (page, size)

    GET /users/{id_user} → Obtener usuario por ID

    POST /users/ → Crear nuevo usuario

    PUT /users/{id_user} → Actualizar usuario existente

    DELETE /users/{id_user} → Desactivar usuario (soft delete)

**Roles**

    CRUD completo similar a usuarios: /roles/

**Áreas (PROTEGIDOS)**

    CRUD completo similar a usuarios: /area/

**Asignaturas**

    CRUD completo similar a usuarios: /subjects/

**Notas**

    CRUD completo similar a usuarios: /notes/

**Préstamos**

    CRUD de préstamos para dispositivos de estudiantes

**Permite validar si un estudiante tiene un préstamo activo**

    Registrar devolución de dispositivos

**Login**

    POST /login/ → Validar credenciales y obtener token JWT


---


🔄 **Flujo de Consumo**

    Obtener token JWT usando /auth/token o /login/.

    Copiar el token y presionar Authorize en Swagger.

    Consumir endpoints protegidos (/users/, /area/) usando el token automáticamente.

    Los endpoints públicos (/roles/, /subjects/, /notes/) se pueden consumir sin token.


🛠️ **Tecnologías Usadas**

    FastAPI 🚀 - Framework principal para la API

    SQLAlchemy 🗄️ - ORM para manejar la BD

    SQL Server 💾 - Motor de base de datos

    Uvicorn ⚡ - Servidor ASGI

    Pydantic 🧩 - Validación de modelos

    Python-dotenv 🔐 - Manejo de variables de entorno

    python-jose 🔑 - Manejo de JWT