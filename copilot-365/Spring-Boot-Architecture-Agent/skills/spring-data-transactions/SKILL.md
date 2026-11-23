---
name: spring-data-transactions
description: 'Asesoría arquitectónica sobre persistencia, datos y transacciones en Spring Boot: JPA/Hibernate frente a JDBC/R2DBC/NoSQL, límites de @Transactional, consistencia entre servicios (outbox, saga, idempotencia), migraciones Flyway/Liquibase, caché, concurrencia, auditoría, retención y recuperación. Usar cuando se pregunte qué tecnología de datos elegir, cómo evitar inconsistencias, N+1 o transacciones largas, cómo migrar esquemas sin downtime o cómo repartir datos entre módulos o servicios. No usar como generador de código por defecto.'
---

# Datos, persistencia y transacciones

## Objetivo
Decidir cómo se almacenan, acceden y mantienen consistentes los datos, con ownership claro y operación recuperable.

## Selección de tecnología de acceso
- **Spring Data JPA/Hibernate**: dominio con relaciones y ciclo de vida de entidades, CRUD abundante. Coste: complejidad de carga perezosa, N+1, contexto de persistencia.
- **JDBC / `JdbcClient` / Spring Data JDBC**: control de SQL, agregados simples, consultas predecibles, equipos que prefieren SQL explícito.
- **R2DBC**: solo si toda la pila es reactiva y el beneficio de concurrencia está medido; no lo elijas por moda ni mezclado con MVC bloqueante sin motivo.
- **NoSQL / búsqueda**: cuando el modelo de acceso lo justifique (documentos, clave-valor, texto completo). Exige definir consistencia, índices y estrategia de recuperación.
- Es válido combinar: escritura con JPA y lecturas de listados con SQL/proyecciones, sin necesitar CQRS completo.

## Transacciones
- Fija el límite transaccional en el **caso de uso** (capa de aplicación), no en controladores ni repositorios.
- Mantén las transacciones cortas: sin llamadas HTTP, mensajería síncrona ni esperas dentro de ellas.
- Recuerda los límites de `@Transactional`: autoinvocación, métodos no públicos o proxies, propagación y `rollbackFor` para excepciones comprobadas; verifícalo en la versión instalada.
- Concurrencia: bloqueo optimista (`@Version`) por defecto; pesimista solo con contención demostrada; define el nivel de aislamiento por necesidad, no por defecto.
- Evita `open-in-view` activado en APIs sin decidirlo explícitamente.

## Consistencia entre componentes
- Una transacción local por servicio; sin transacciones distribuidas (2PC/XA) salvo restricción justificada.
- Para publicar eventos de forma fiable usa **transactional outbox**, con consumidores **idempotentes** y política de reintentos y dead-letter. Spring Modulith ofrece un registro de publicación de eventos si se usa.
- Para flujos largos entre servicios evalúa **saga** (coreografía u orquestación) y define compensaciones y estados intermedios visibles.
- No compartas una base de datos entre servicios como atajo; si es una transición, documéntala como deuda con fecha de salida.

## Migraciones y evolución del esquema
- Flyway o Liquibase, versionados y ejecutados de forma controlada (no con `ddl-auto=update` en producción).
- Patrón **expand/contract** para cambios compatibles hacia atrás: añadir, migrar datos, cambiar código, retirar. Permite rollback de aplicación sin rollback de esquema.
- Prueba las migraciones sobre copia con volumen realista y estima bloqueos.

## Rendimiento y operación
- Detecta N+1 (fetch join, `EntityGraph`, proyecciones, batch size) y mide consultas por petición.
- Pool de conexiones (HikariCP) dimensionado respecto al límite de la base de datos y al número de instancias.
- Caché solo con política de invalidación, TTL y métricas de acierto; distingue caché local y distribuida.
- Auditoría, retención, borrado (RGPD) y cifrado de datos sensibles definidos por dato.
- RPO/RTO, copias de seguridad y prueba de restauración.

## Anti-patrones
Entidades JPA expuestas como contrato de API; repositorios llamados desde controladores; `EAGER` generalizado; transacciones que abarcan llamadas remotas; esquema modificado manualmente en producción; caché sin invalidación.

## Salida
Para revisar un diseño de datos existente, usa `reference/data-consistency-checklist.md`.
Opción recomendada y alternativas, límites transaccionales, estrategia de consistencia, plan de migración con rollback, pruebas (Testcontainers con el motor real, pruebas de migración, de concurrencia), métricas y ADR.

## Autoevaluación
Comprueba que cada dato tiene un propietario, que no hay transacciones distribuidas implícitas, que el rollback de esquema y aplicación está definido y que no recomiendas tecnologías de datos sin un patrón de acceso que lo justifique.
