# Diseño del modelo de datos en Liferay: <dominio>

- **Release y modalidad**: <release> · self-hosted | PaaS | SaaS
- **Mecanismo elegido**: Objects | Service Builder | servicio externo (justificación y referencia al ADR)

## 1. Entidades
| Entidad | Descripción | Alcance (compañía o site) | Volumen esperado | Dueño |
|---|---|---|---|---|

## 2. Campos
| Entidad | Campo | Tipo | Obligatorio | Validación | Sensible (sí/no) |
|---|---|---|---|---|---|

## 3. Relaciones
| Origen | Destino | Cardinalidad | Al borrar (restringir, cascada, desvincular) | Notas |
|---|---|---|---|---|

## 4. Permisos
| Rol | Ámbito | Entidad | Ver | Crear | Editar | Borrar | Justificación |
|---|---|---|---|---|---|---|---|

## 5. Reglas, acciones y workflow
| Disparador | Regla o acción | Dentro o fuera de la JVM | Idempotente | Workflow (estados, roles, plazos) |
|---|---|---|---|---|

## 6. Transacciones y consistencia
Qué operaciones deben ser atómicas, dónde está la frontera transaccional y qué se acepta con consistencia eventual.

## 7. Evolución y upgrade
- Cambios de esquema previstos y cómo se migran los datos existentes.
- Puntos de extensión usados y su coste de upgrade (A/M/B).
- Capacidades verificadas en la release: <campos calculados, agregaciones, validaciones…>.

## 8. Pruebas
Recorridos completos (alta, edición, aprobación, rechazo, reasignación), permisos por rol y volumen.

## 9. Riesgos
| Riesgo | Mitigación | Responsable |
|---|---|---|
