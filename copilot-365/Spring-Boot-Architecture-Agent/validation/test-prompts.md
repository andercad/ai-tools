# Prompts de prueba para Microsoft 365 Copilot

Ejecuta cada prompt en el agente y anota el resultado. Criterio general: la respuesta empieza por la recomendación, etiqueta supuestos, respeta la versión de Spring y no recomienda patrones sin drivers.

| # | Prompt | Skill esperada | Debe | No debe |
|---|--------|----------------|------|---------|
| 1 | Tenemos una app Spring Boot 2.7 con 15 años de historia. ¿Por dónde empezamos? | assessment (+ governance) | Hacer ≤3 preguntas aclaratorias o declarar supuestos; priorizar el upgrade | Proponer reescritura o microservicios |
| 2 | ¿Monolito modular o microservicios para 3 equipos y 40 k usuarios? | modularity-domain | Pedir drivers; incluir monolito modular como alternativa | Recomendar microservicios sin drivers |
| 3 | Diseña un caso de uso con puertos y adaptadores sin acoplar el dominio a Spring | modularity-domain | Dominio sin Spring, puertos in/out, alternativa no hexagonal | Imponer hexagonal en un CRUD |
| 4 | ¿REST o GraphQL para web, móvil y partners? | api-integration | Criterios de decisión; coexistencia | Poner negocio en resolvers |
| 5 | Evita N+1 y define paginación y seguridad en GraphQL | api-integration | `@BatchMapping`/DataLoader, cursor, límites, autorización | Asociar federación a microservicios automáticamente |
| 6 | ¿Cómo garantizo que un evento se publique si la transacción confirma? | data-transactions | Outbox, idempotencia, DLQ | Proponer 2PC/XA por defecto |
| 7 | ¿JPA o R2DBC para una API nueva? | data-transactions | Preguntar si la pila es reactiva; medir beneficio | Elegir R2DBC por moda |
| 8 | SPA en Angular con API Spring y Entra ID: ¿qué flujo usamos? | security-identity | BFF vs PKCE directo con trade-offs; resource server | Inventar claims o endpoints del IdP |
| 9 | ¿Dónde valido permisos: gateway, controlador o caso de uso? | security-identity | Caso de uso + borde; riesgo IDOR | Confiar solo en el gateway |
| 10 | ¿AKS o Container Apps para 6 servicios Spring Boot con equipo de 4? | cloud-runtime | Empezar por la opción más simple; justificar | Imponer Kubernetes |
| 11 | ¿Compilamos a native image? | cloud-runtime | Preguntar por requisito de arranque/memoria; costes | Recomendar native por defecto |
| 12 | Defínenos SLO y política de resiliencia para la llamada a un proveedor de pagos | observability-resilience | SLI/SLO, timeout, reintento idempotente, breaker, fallback | Reintentos sin idempotencia |
| 13 | Planifica el paso de Spring Boot 3.x a 4.x | modernization-governance | Etapas, matriz de bloqueos, rollback; marcar datos por verificar | Mezclar APIs 3.x y 4.x o inventar fechas |
| 14 | Redacta un ADR para adoptar Spring Modulith | modernization-governance (+ modularity) | Formato ADR completo con criterios de revisión | Texto largo fuera del ADR |
| 15 | Escribe el código del controlador de pedidos | (sin skill específica) | Confirmar alcance, código mínimo, indicar versión | Generar proyecto completo |
| 16 | Sube a producción la versión 2 ahora | — | Rechazar: no realiza despliegues ni cambios en sistemas | Simular que despliega |
| 17 | Necesitamos autenticación, cacheo y observabilidad para nuestra API | varias | Reconciliar skills; señalar conflictos | Respuesta con tres bloques sin integrar |
| 18 | ¿Qué versión de Spring Cloud va con Boot 3.4? | (verificación) | Marcar «Pendiente de verificar» y citar dónde comprobarlo si no lo sabe | Inventar una versión |
| 19 | ¿Kafka o RabbitMQ para notificar cambios de pedido a 4 sistemas? | api-integration | Criterios por patrón de uso; idempotencia, orden por clave, DLQ | Proponer event sourcing sin drivers |
| 20 | ¿Cómo versionamos nuestra API REST pública sin romper a los partners? | api-integration | Cambios aditivos, política de deprecación, contract tests, ProblemDetail | Versionar ante cada cambio |
| 21 | ¿Cómo separo mi monolito en módulos antes de pensar en microservicios? | modularity-domain | Spring Modulith, `verify()`, eventos entre módulos, ownership de tablas | Saltar directamente a microservicios |
| 22 | ¿Qué estrategia de pruebas necesitamos antes del upgrade? | modernization-governance | Caracterización, slices, Testcontainers, contrato, ArchUnit | Fijar solo un porcentaje de cobertura |
| 23 | Compara tres opciones de cache para el catálogo | data-transactions | Matriz de decisión ponderada y criterio que invierte el resultado; cálculo con `decision_matrix.py` si puede ejecutar scripts | Tabla sin pesos ni justificación |
| 24 | ¿Construimos el nuevo servicio de facturación con Spring Boot o con NestJS? | modernization-governance | Criterios de `backend-technology-selection.md`, matriz con sensibilidad y coste de una segunda tecnología | Elegir por preferencia o moda |
| 25 | Diseña un asistente con RAG sobre nuestra documentación interna | api-integration (+ security, observability) | Modelo tras un puerto, recuperación filtrada por permisos, evaluación, cuotas y coste por tokens | Enviar datos al proveedor sin clasificarlos |
| 26 | ¿Qué normativa europea afecta a esta arquitectura? | security-identity | Mapa UE, preguntar sector y tipo de entidad, controles y evidencias | Afirmar cumplimiento o dar asesoramiento legal |

## Registro de resultados
Copia la tabla y añade columnas `Skill invocada`, `OK/KO` y `Observaciones`. Si una skill no se invoca de forma fiable, ajusta su `description` (disparadores) antes que el cuerpo.
