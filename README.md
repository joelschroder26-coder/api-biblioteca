# API de la Biblioteca — Proyecto Integrador de Schroder Gonzalo Joel

API REST desarrollada con **FastAPI**  para gestionar el catálogo de libros de una biblioteca (crear, listar, filtrar, paginar, buscar, actualizar, prestar, devolver y eliminar libros) con persistencia automática en archivo JSON .

## Requisitos e instalación

1. Clonar este repositorio y entrar en la carpeta del proyecto:
   ```bash
   git clone https://github.com/TU-USUARIO/api-biblioteca.git
   cd api-biblioteca
   ```

2. Crear y activar el entorno virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instalar las dependencias con `pip install`:
   ```powershell
   pip install -r requirements.txt
   ```

## Cómo correr el servidor

Podés iniciar la API con `fastapi dev` o con `uvicorn`:

```powershell
fastapi dev main.py
```

O bien usando `uvicorn` directamente:

```powershell
uvicorn main:app --reload
```

Una vez iniciado el servidor, la documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.

## Endpoints incluidos

| Método | Ruta | Descripción | Códigos |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Mensaje de bienvenida `{"mensaje": "API de la biblioteca"}` | `200` |
| `GET` | `/libros` | Lista de libros ordenada por `id`, con filtros (`?autor=`, `?disponible=`) y paginación (`?desde=`, `?limite=`) | `200` |
| `GET` | `/libros/buscar` | Búsqueda por texto (`?texto=...`) en `titulo` o `autor` (sin distinguir mayúsculas/minúsculas) | `200`, `422` |
| `GET` | `/libros/estadisticas` | Resumen con `{"total": N, "disponibles": N, "prestados": N}` | `200` |
| `POST` | `/libros` | Crea un libro validando campos y evitando duplicados (`titulo` + `autor`) | `201`, `409`, `422` |
| `GET` | `/libros/{id}` | Obtiene el detalle de un libro por su `id` | `200`, `404`, `422` |
| `PUT` | `/libros/{id}` | Reemplaza todos los campos de un libro manteniendo su `id` | `200`, `404`, `422` |
| `PATCH` | `/libros/{id}` | Actualiza parcialmente solo los campos enviados | `200`, `404`, `422` |
| `DELETE` | `/libros/{id}` | Elimina un libro existente sin devolver cuerpo | `204`, `404` |
| `POST` | `/libros/{id}/prestar` | Marca un libro disponible como prestado (`disponible: false`) | `200`, `404`, `409` |
| `POST` | `/libros/{id}/devolver` | Marca un libro prestado como devuelto (`disponible: true`) | `200`, `404`, `409` |


