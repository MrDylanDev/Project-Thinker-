# Diagrama de Clases — Fitness Plus

```mermaid
classDiagram
    class Persona {
        <<abstract>>
        -_nombre: str
        -_apellido: str
        -_telefono: str
        -_email: str
        +nombre: str
        +apellido: str
        +telefono: str
        +email: str
        +nombre_completo() str
        +__str__() str
        +guardar()* 
    }
    class Cliente {
        -_id_cliente: int
        -_documento: str
        -_fecha_registro: str
        +id_cliente: int
        +documento: str
        +fecha_registro: str
        +guardar() int
        +eliminar() void
        +listar_todos() list
        +buscar_por_id(id) Cliente
        +buscar_por_texto(texto) list
    }
    class Entrenador {
        -_id_entrenador: int
        -_especialidad: str
        +id_entrenador: int
        +especialidad: str
        +guardar() int
        +eliminar() void
        +listar_todos() list
        +buscar_por_id(id) Entrenador
        +buscar_por_texto(texto) list
    }
    class Membresia {
        -_id_membresia: int
        -_id_cliente: int
        -_tipo: str
        -_fecha_inicio: date
        -_fecha_vencimiento: date
        -_estado: str
        +tipo: str
        +valor: float
        +estado: str  {dynamic}
        +guardar() int
        +eliminar() void
        +renovar() void
        +cancelar() void
        +listar_todas() list
        +listar_por_cliente(id) list
        +listar_proximas_a_vencer(dias) list
        +listar_vencidas() list
    }
    class Pago {
        -_id_pago: int
        -_id_membresia: int
        -_monto: float
        -_fecha_pago: date
        -_estado: str
        +monto: float
        +estado: str
        +guardar() int
        +eliminar() void
        +listar_todas() list
        +listar_por_membresia(id) list
        +listar_por_cliente(id) list
        +clientes_con_pagos_pendientes() list
    }
    class PlanEntrenamiento {
        -_id_plan: int
        -_nombre: str
        -_descripcion: str
        -_nivel: str
        -_duracion_semanas: int
        -_id_entrenador: int
        -_id_cliente: int
        +nivel: str
        +duracion_semanas: int
        +guardar() int
        +eliminar() void
        +listar_todos() list
        +listar_por_cliente(id) list
        +listar_por_entrenador(id) list
    }

    Cliente --|> Persona : hereda
    Entrenador --|> Persona : hereda
    Cliente "1" -- "0..*" Membresia : tiene
    Membresia "1" -- "0..*" Pago : recibe
    Cliente "1" -- "0..*" PlanEntrenamiento : recibe
    Entrenador "1" -- "0..*" PlanEntrenamiento : crea
```