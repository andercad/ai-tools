# Prompts de prueba para Microsoft 365 Copilot Agent Builder

Ejecuta cada prompt en el agente, anota la skill usada y el modo de respuesta, y marca el resultado. Un prompt falla si usa otra skill, ignora el modo esperado, inventa datos o implementa código sin que se lo pidan.

| # | Prompt | Skill esperada | Modo esperado | Debe incluir | Resultado |
|---|--------|----------------|---------------|--------------|-----------|
| 1 | ¿Monolito modular o microservicios para un sistema de pedidos con 3 equipos? | modularity-domain | Estándar | Drivers, comparación con la opción simple, riesgos | |
| 2 | Diseña un caso de uso con puertos y adaptadores sin acoplar el dominio a NestJS | modularity-domain | Completo | Tokens de inyección, estructura, coste de la hexagonal | |
| 3 | Tengo dependencias circulares con forwardRef en 6 módulos | modularity-domain | Estándar | Causa en fronteras, alternativas (eventos, inversión) | |
| 4 | ¿REST o GraphQL para web y móvil? | api-integration | Estándar | Criterios, coste operativo, casos de uso compartidos | |
| 5 | Evita el N+1 y define paginación y límites en GraphQL | api-integration | Estándar | DataLoader por petición, cursor, profundidad/complejidad | |
| 6 | ¿Debemos federar nuestro grafo? | api-integration | Estándar | No asociarlo automáticamente a microservicios | |
| 7 | Diseña autenticación con Entra ID para una SPA y una API NestJS | security-identity | Completo | PKCE/BFF, validación de JWT, denegar por defecto | |
| 8 | Revisa estos endpoints contra OWASP API Top 10 (pegar lista) | security-identity | Estándar | BOLA, autorización por recurso, límites | |
| 9 | ¿TypeORM o Prisma para un dominio con reglas complejas? | data-messaging | Estándar | Criterios, ORM solo en adaptadores, pregunta aclaratoria | |
| 10 | Necesito publicar un evento al guardar un pedido sin perderlo | data-messaging | Estándar | Outbox, idempotencia, DLQ | |
| 11 | ¿Kafka o RabbitMQ para notificaciones? | data-messaging | Estándar | Comando vs evento, orden, operación | |
| 12 | ¿Container Apps o AKS para 5 APIs NestJS? | runtime-deployment | Estándar | Opción gestionada simple, coste operativo de AKS | |
| 13 | Nuestras réplicas se reinician en cascada cuando cae la BD | runtime-deployment | Estándar | Liveness vs readiness, shutdown | |
| 14 | Define SLO y observabilidad para el flujo de checkout | observability-resilience | Completo | SLI/SLO, OTel, burn rate, alertas | |
| 15 | La API se bloquea con picos de carga y llamadas lentas a un tercero | observability-resilience | Estándar | Event loop, timeouts, breaker, backpressure | |
| 16 | Plan para pasar de NestJS 9 a la versión actual | modernization-governance | Completo | Una mayor cada vez, pruebas de caracterización, rollback | |
| 17 | Redacta un ADR para pasar de Express a Fastify | modernization-governance | Completo | Plantilla ADR, consecuencias, medición previa | |
| 18 | Revisa la arquitectura de nuestra aplicación NestJS (sin adjuntos) | architecture-assessment | Estándar | Pide material (máx. 3 preguntas), marca lo no verificado | |
| 19 | Implementa el módulo de pedidos completo | (fuera de perfil) | Rápido | Rechaza implementar y ofrece diseño y criterios de aceptación | |
| 20 | ¿Qué es un guard en NestJS? | (cualquiera) | Rápido | Respuesta breve, sin formato completo | |
| 21 | Quiero microservicios porque es lo moderno | modularity-domain | Estándar | Cuestiona la falta de drivers, alternativa simple | |
| 22 | Despliega esto en producción | (fuera de perfil) | Rápido | No ejecuta, explica el límite | |
| 23 | ¿NestJS o Spring Boot para el nuevo servicio de facturación? | modernization-governance | Estándar | Criterios de selección, matriz con sensibilidad (`decision_matrix.py` si puede), coste de una segunda tecnología | |
| 24 | Diseña un asistente con RAG sobre nuestra documentación | api-integration | Completo | Modelo tras un puerto, permisos en la recuperación, streaming, evaluación, cuotas y coste | |
| 25 | ¿Qué normativa UE afecta a nuestra API? | security-identity | Estándar | Mapa UE, preguntas sobre sector y datos, controles y evidencias, sin afirmar cumplimiento | |
