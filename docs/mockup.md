# Mockups — Fitness Plus

## 1. Ventana Principal con Menú Lateral

```
+--------------------------------------------------------------------+
|  [Fitness Plus]                      Gimnasio Fitness Plus          |
|  [Sistema de gestión]                                                    |
|  +-----------+                                                     |
|  | [Clientes]|  +---------------------------------------------+    |
|  |-----------|  |  Clientes                                    |    |
|  | Clientes  |  |  ---------------------------------------   |    |
|  |-----------|  |  ID  | Doc  | Nombre | Apellido | ...      |    |
|  |Entrenad.. |  |  1   | 123  | Juan   | Pérez    | ...      |    |
|  |-----------|  |  2   | 456  | María  | López    | ...      |    |
|  |Membresías|  |  3   | 789  | Carlos | Gómez    | ...      |    |
|  |-----------|  |  [≡] [≡] [≡]                              |    |
|  |  Pagos   |  +---------------------------------------------+    |
|  |-----------|                                                     |
|  |  Planes  |  +---------------------------------------------+    |
|  |-----------|  |  [Formulario de cliente]                    |    |
|  | Reportes |  |  Nombre: [__________]  Apellido: [________] |    |
|  +-----------+  |  Doc: [_________] Tel: [________]          |    |
|                 |  Email: [___________________]              |    |
|                 |  [Guardar] [Editar] [Eliminar] [Limpiar]  |    |
|                 +---------------------------------------------+    |
+--------------------------------------------------------------------+
```

---

## 2. Formulario de Clientes

```
+-------------------------------------------+
|  Formulario de cliente                    |
+-------------------------------------------+
|  Nombre *:  [________________]            |
|  Apellido *:[________________]            |
|  Documento: [________________]            |
|  Teléfono:  [________________]            |
|  Email:     [________________]            |
|  Fecha de registro: automática (hoy)      |
|                                           |
|  [Guardar]                                |
|  [Editar]                                 |
|  [Eliminar]                               |
|  [Limpiar]                                |
+-------------------------------------------+
```

---

## 3. Pestaña de Reportes — Vencimientos Próximos

```
+-------------------------------------------------------------+
|  Reportes                                       [+Vencimientos][+Pagos][+Historial] |
+-------------------------------------------------------------+
|  Membresías que vencen en los próximos [  30  ] días  [Consultar] |
|                                                             |
|  ID | Cliente         | Tipo    | Vence     | Días  | Valor |
|-----|-----------------|---------|-----------|-------|-------|
|  1  | Pérez, Juan     | Mensual | 2026-10-05| 20d   | $30k  |
|  2  | López, María    | Anual   | 2026-11-12| 58d   | $288k |
|  3  | Gómez, Carlos   | Mensual | 2026-09-28| 13d   | $30k  |
+-------------------------------------------------------------+

--- Pagos Pendientes ---

| ID Pago | Cliente         | Doc  | Tipo   | Monto  | Fecha    |
|---------|-----------------|------|--------|--------|----------|
|    5    | López, María    | 456  | Anual  | $288k  | 2026-09-01|
|    8    | Gómez, Carlos   | 789  | Mensual| $30k   | 2026-09-10|

--- Historial de Cliente ---

Seleccionar cliente: [ Lopez, Maria        ▾  ]  [Consultar]

Membresías
| ID | Tipo    | Inicio     | Vence      | Estado   | Valor |
|----|---------|------------|------------|----------|-------|
|  2 | Anual   | 2025-11-12 | 2026-11-12 | Activa   | $288k |

Pagos
| ID | Fecha     | Monto   | Estado   |
|----|-----------|---------|----------|
|  5 | 2026-09-01| $288k   | Pendiente|

Planes de Entrenamiento
| ID | Nombre       | Nivel     | Duración  | Entrenador   |
|----|--------------|-----------|-----------|--------------|
|  1 | Fuerza Base  |Intermedio | 8 sem.    | García, Ana  |
+-------------------------------------------------------------+
```