"""Acceso a la base de datos SQLite de Gimnasio Fitness Plus."""
import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "fitness_plus.db")

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS entrenador (
    id_entrenador INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    especialidad TEXT
);

CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    documento TEXT,
    fecha_registro TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plan_entrenamiento (
    id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    nivel TEXT NOT NULL,
    duracion_semanas INTEGER NOT NULL,
    id_entrenador INTEGER NOT NULL,
    id_cliente INTEGER NOT NULL,
    FOREIGN KEY (id_entrenador) REFERENCES entrenador (id_entrenador) ON DELETE CASCADE,
    FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS membresia (
    id_membresia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_vencimiento TEXT NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pago (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_membresia INTEGER NOT NULL,
    monto REAL NOT NULL,
    fecha_pago TEXT NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY (id_membresia) REFERENCES membresia (id_membresia) ON DELETE CASCADE
);
"""


def get_connection():
    """Devuelve una conexión a la base de datos con FK activas y filas tipo Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def conexion():
    """Contexto que abre una conexión, confirma los cambios y la cierra."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_base_datos():
    """Crea la base de datos y las tablas si aún no existen."""
    with conexion() as conn:
        conn.executescript(_ESQUEMA)