import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

logger = logging.getLogger("api_biblioteca")
logger.addHandler(logging.NullHandler())

RUTA_DATOS = Path(__file__).parent / "datos" / "libros.json"

app = FastAPI(
    title="API de la Biblioteca",
    description="API REST con FastAPI para gestionar libros.",
    version="1.0.0",
)


class LibroEntrada(BaseModel):
    """Esquema de entrada para crear o reemplazar un libro."""

    titulo: str = Field(..., min_length=3, max_length=100)
    autor: str = Field(..., min_length=3, max_length=60)
    anio: int = Field(..., ge=1000, le=2100)
    disponible: bool = True


class LibroActualizacion(BaseModel):
    """Esquema de entrada para actualizar parcialmente un libro."""

    titulo: Optional[str] = Field(default=None, min_length=3, max_length=100)
    autor: Optional[str] = Field(default=None, min_length=3, max_length=60)
    anio: Optional[int] = Field(default=None, ge=1000, le=2100)
    disponible: Optional[bool] = None


class Libro(BaseModel):
    """Esquema de salida que representa un libro completo."""

    id: int
    titulo: str
    autor: str
    anio: int
    disponible: bool


libros: List[Dict[str, Union[int, str, bool]]] = []
proximo_id: int = 1
_ultimo_contenido_archivo: Optional[str] = None


def _leer_texto_archivo() -> Optional[str]:
    """Lee el contenido de texto del archivo JSON si existe."""
    if not RUTA_DATOS.exists():
        return None
    try:
        return RUTA_DATOS.read_text(encoding="utf-8")
    except OSError:
        return None


def cargar_datos() -> None:
    """Carga los libros desde datos/libros.json y actualiza el contador."""
    global libros, proximo_id, _ultimo_contenido_archivo

    texto = _leer_texto_archivo()
    _ultimo_contenido_archivo = texto

    if not texto or not texto.strip():
        libros = []
        proximo_id = 1
        logger.info("Sin datos previos; iniciando lista vacía.")
        return

    try:
        datos_cargados = json.loads(texto)
        if not isinstance(datos_cargados, list):
            libros = []
            proximo_id = 1
            logger.info("Formato no válido en JSON; iniciando lista vacía.")
            return

        libros_validos: List[Dict[str, Union[int, str, bool]]] = []
        campos_requeridos = {"id", "titulo", "autor", "anio", "disponible"}
        for item in datos_cargados:
            if isinstance(item, dict) and campos_requeridos.issubset(
                item.keys()
            ):
                libros_validos.append(
                    {
                        "id": int(item["id"]),
                        "titulo": str(item["titulo"]),
                        "autor": str(item["autor"]),
                        "anio": int(item["anio"]),
                        "disponible": bool(item["disponible"]),
                    }
                )

        libros = sorted(libros_validos, key=lambda x: int(x["id"]))
        mayor_id = max((int(libro["id"]) for libro in libros), default=0)
        proximo_id = mayor_id + 1
        logger.info("Datos cargados. Próximo ID: %d", proximo_id)
    except (ValueError, TypeError, KeyError):
        libros = []
        proximo_id = 1
        logger.info("Archivo de datos dañado; iniciando lista vacía.")


def guardar_datos() -> None:
    """Guarda la lista actual de libros ordenada por ID en el archivo JSON."""
    global libros, _ultimo_contenido_archivo

    libros.sort(key=lambda x: int(x["id"]))
    RUTA_DATOS.parent.mkdir(parents=True, exist_ok=True)
    contenido = json.dumps(libros, ensure_ascii=False, indent=2)
    RUTA_DATOS.write_text(contenido, encoding="utf-8")
    _ultimo_contenido_archivo = contenido
    logger.info("Datos guardados. Total de libros: %d", len(libros))


def sincronizar_estado() -> None:
    """Recarga desde disco si el archivo fue modificado externamente."""
    texto_actual = _leer_texto_archivo()
    if texto_actual != _ultimo_contenido_archivo:
        cargar_datos()


def buscar_libro_por_id(
    libro_id: int,
) -> Optional[Dict[str, Union[int, str, bool]]]:
    """Busca un libro por su ID dentro de la lista en memoria."""
    for libro in libros:
        if int(libro["id"]) == libro_id:
            return libro
    return None


cargar_datos()


@app.get("/", summary="Mensaje de bienvenida de la API")
def raiz() -> Dict[str, str]:
    """Devuelve el mensaje identificatorio de la API de la biblioteca."""
    return {"mensaje": "API de la biblioteca"}


@app.get(
    "/libros",
    response_model=List[Libro],
    summary="Listar y filtrar libros",
)
def listar_libros(
    autor: Optional[str] = Query(default=None),
    disponible: Optional[bool] = Query(default=None),
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=0),
) -> List[Dict[str, Union[int, str, bool]]]:
    """Lista los libros ordenados por ID con filtros y paginación."""
    sincronizar_estado()
    resultado = sorted(libros, key=lambda x: int(x["id"]))

    if autor is not None:
        autor_buscado = autor.lower()
        resultado = [
            libro
            for libro in resultado
            if str(libro["autor"]).lower() == autor_buscado
        ]

    if disponible is not None:
        resultado = [
            libro
            for libro in resultado
            if bool(libro["disponible"]) is disponible
        ]

    return resultado[desde : desde + limite]


@app.get(
    "/libros/buscar",
    response_model=List[Libro],
    summary="Buscar libros por texto en título o autor",
)
def buscar_libros(
    texto: str = Query(..., min_length=1),
) -> List[Dict[str, Union[int, str, bool]]]:
    """Devuelve los libros cuyo título o autor contiene el texto buscado."""
    sincronizar_estado()
    termino = texto.lower()
    resultado = [
        libro
        for libro in sorted(libros, key=lambda x: int(x["id"]))
        if termino in str(libro["titulo"]).lower()
        or termino in str(libro["autor"]).lower()
    ]
    return resultado


@app.get(
    "/libros/estadisticas",
    summary="Obtener estadísticas de libros de la biblioteca",
)
def obtener_estadisticas() -> Dict[str, int]:
    """Devuelve el total de libros, disponibles y prestados."""
    sincronizar_estado()
    total = len(libros)
    disponibles = sum(1 for libro in libros if bool(libro["disponible"]))
    prestados = total - disponibles
    return {
        "total": total,
        "disponibles": disponibles,
        "prestados": prestados,
    }


@app.post(
    "/libros",
    response_model=Libro,
    status_code=201,
    summary="Crear un nuevo libro",
)
def crear_libro(
    datos: LibroEntrada,
) -> Dict[str, Union[int, str, bool]]:
    """Crea un libro nuevo, asigna ID incremental y persiste en JSON."""
    global proximo_id
    sincronizar_estado()

    titulo_nuevo = datos.titulo.lower()
    autor_nuevo = datos.autor.lower()

    for existente in libros:
        if (
            str(existente["titulo"]).lower() == titulo_nuevo
            and str(existente["autor"]).lower() == autor_nuevo
        ):
            logger.info("Conflicto por libro duplicado: %s", datos.titulo)
            raise HTTPException(
                status_code=409,
                detail="Ya existe un libro con el mismo título y autor.",
            )

    nuevo_libro: Dict[str, Union[int, str, bool]] = {
        "id": proximo_id,
        "titulo": datos.titulo,
        "autor": datos.autor,
        "anio": datos.anio,
        "disponible": datos.disponible,
    }
    proximo_id += 1
    libros.append(nuevo_libro)
    guardar_datos()
    logger.info("Libro creado con ID %d", nuevo_libro["id"])
    return nuevo_libro


@app.get(
    "/libros/{id}",
    response_model=Libro,
    summary="Obtener un libro por su ID",
)
def obtener_libro(id: int) -> Dict[str, Union[int, str, bool]]:
    """Devuelve el libro correspondiente al ID o 404 si no existe."""
    sincronizar_estado()
    libro = buscar_libro_por_id(id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    return libro


@app.put(
    "/libros/{id}",
    response_model=Libro,
    summary="Reemplazar completamente un libro",
)
def reemplazar_libro(
    id: int,
    datos: LibroEntrada,
) -> Dict[str, Union[int, str, bool]]:
    """Reemplaza todos los campos de un libro conservando su ID."""
    sincronizar_estado()
    libro = buscar_libro_por_id(id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    libro["titulo"] = datos.titulo
    libro["autor"] = datos.autor
    libro["anio"] = datos.anio
    libro["disponible"] = datos.disponible
    guardar_datos()
    logger.info("Libro con ID %d reemplazado con PUT.", id)
    return libro


@app.patch(
    "/libros/{id}",
    response_model=Libro,
    summary="Actualizar parcialmente un libro",
)
def actualizar_libro(
    id: int,
    datos: LibroActualizacion,
) -> Dict[str, Union[int, str, bool]]:
    """Actualiza solo los campos enviados en el cuerpo de la petición."""
    sincronizar_estado()
    libro = buscar_libro_por_id(id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if hasattr(datos, "model_dump"):
        cambios = datos.model_dump(exclude_unset=True)
    else:
        cambios = datos.dict(exclude_unset=True)

    for campo, valor in cambios.items():
        if valor is None:
            raise HTTPException(
                status_code=422,
                detail=f"El campo '{campo}' no puede ser nulo.",
            )
        libro[campo] = valor

    guardar_datos()
    logger.info("Libro con ID %d actualizado con PATCH.", id)
    return libro


@app.delete(
    "/libros/{id}",
    status_code=204,
    summary="Eliminar un libro por su ID",
)
def eliminar_libro(id: int) -> Response:
    """Elimina un libro existente y devuelve 204 sin cuerpo."""
    sincronizar_estado()
    libro = buscar_libro_por_id(id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    libros.remove(libro)
    guardar_datos()
    logger.info("Libro con ID %d eliminado.", id)
    return Response(status_code=204)


@app.post(
    "/libros/{id}/prestar",
    response_model=Libro,
    summary="Marcar un libro como prestado",
)
def prestar_libro(id: int) -> Dict[str, Union[int, str, bool]]:
    """Marca un libro disponible como prestado (disponible = false)."""
    sincronizar_estado()
    libro = buscar_libro_por_id(id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if not bool(libro["disponible"]):
        raise HTTPException(
            status_code=409,
            detail="El libro ya se encuentra prestado.",
        )

    libro["disponible"] = False
    guardar_datos()
    logger.info("Libro con ID %d prestado.", id)
    return libro


@app.post(
    "/libros/{id}/devolver",
    response_model=Libro,
    summary="Marcar un libro como devuelto",
)
def devolver_libro(id: int) -> Dict[str, Union[int, str, bool]]:
    """Marca un libro prestado como disponible (disponible = true)."""
    sincronizar_estado()
    libro = buscar_libro_por_id(id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if bool(libro["disponible"]):
        raise HTTPException(
            status_code=409,
            detail="El libro ya se encuentra disponible.",
        )

    libro["disponible"] = True
    guardar_datos()
    logger.info("Libro con ID %d devuelto.", id)
    return libro
