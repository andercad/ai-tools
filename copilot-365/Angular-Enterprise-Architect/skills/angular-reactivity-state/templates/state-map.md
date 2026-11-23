# Mapa de estado y decisión de store: <feature o aplicación>

## 1. Inventario de estado
| Estado | Tipo (UI local, feature, servidor, URL, sesión, formulario) | Fuente de verdad | Dueño | Ciclo de vida | Consumidores | Primitiva propuesta |
|---|---|---|---|---|---|---|
| p. ej. Filtros del listado | URL | Parámetros de ruta | Feature Pedidos | Navegación | Listado, exportación | Router + `computed` |

Reglas: una fuente de verdad por estado; el estado de servidor no se copia a mano en stores; lo que se comparte por enlace vive en la URL.

## 2. Escalera de stores
| Peldaño | ¿Suficiente? | Problema demostrado que obliga a subir |
|---|---|---|
| 1. Signal en el componente | | |
| 2. Servicio de feature con signals de solo lectura hacia fuera | | |
| 3. Store ligero de feature | | |
| 4. Store global con acciones | | |

Decisión: <peldaño> porque <problema demostrado>.

## 3. Flujos asíncronos y concurrencia
| Flujo | Disparador | Política (switchMap, concatMap, exhaustMap, mergeMap) | Motivo de negocio | Errores y reintentos | Cancelación |
|---|---|---|---|---|---|

## 4. Formularios
| Formulario | Complejidad | Opción (reactive, template-driven, signal forms) | Estado de la API en la versión | Validación en servidor |
|---|---|---|---|---|

## 5. Zoneless (si aplica)
Librerías o código que dependen de zone.js, impacto en pruebas y plan de adopción.

## 6. Riesgos y decisiones abiertas
| Riesgo o decisión | Mitigación u opciones | Responsable |
|---|---|---|
