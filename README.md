# API de la Biblioteca — Proyecto Integrador Módulo 3

API REST desarrollada con **FastAPI** y **Pydantic** para gestionar el catálogo de libros de una biblioteca (crear, listar, filtrar, paginar, buscar, actualizar, prestar, devolver y eliminar libros) con persistencia automática en archivo JSON (`datos/libros.json`).

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

## Guía paso a paso para entregar (GitHub + Formulario)

Si descargaste el archivo `api-biblioteca.zip`, al descomprimirlo ya tenés la carpeta lista con `.gitignore`, `README.md`, `requirements.txt`, `main.py` y un historial de **6 commits progresivos** listos para subir (cumpliendo la condición **E6**):

1. Creá un repositorio **Público** vacío en GitHub llamado `api-biblioteca` (sin marcar "Add a README" ni `.gitignore`).
2. Abrí PowerShell dentro de la carpeta descomprimida `api-biblioteca` y ejecutá:
   ```powershell
   python -c "import main"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/api-biblioteca.git
   git push -u origin main
   ```
3. Abrí la URL `https://github.com/TU-USUARIO/api-biblioteca` en una ventana de incógnito para verificar que sea pública y que no figuren `.venv` ni `__pycache__`.
4. Completá el formulario de entrega antes del **lunes 16 de noviembre de 2026 a las 19:30 hs** en `https://edemake.com/entrega-backend-integrador-1` con tu DNI, correo electrónico, nombre completo (**Gonzalo Joel Schröder**) y la URL del repositorio.
