# Selección de tecnología backend: Spring Boot o NestJS

Úsalo para decidir con qué tecnología construir un servicio nuevo o reconstruir uno existente. Ninguna es mejor en abstracto: decide el contexto.

## 1. Preguntas que suelen decidir
| Pregunta | Inclina hacia Spring Boot | Inclina hacia NestJS |
|---|---|---|
| ¿Qué domina el equipo que lo mantendrá? | Java o Kotlin | TypeScript |
| ¿Qué plataforma existe ya en la organización? | Plataforma, librerías y operación Java consolidadas | Plataforma Node.js consolidada |
| ¿Cuál es el papel del servicio? | Dominio complejo, transaccional, integración empresarial | BFF de un frontend TypeScript, agregación, APIs ligeras |
| ¿Qué perfil de carga tiene? | Mixto con CPU intensiva, procesos por lotes, concurrencia con hilos | Mayoritariamente E/S; la CPU intensiva exige workers o colas |
| ¿Qué ecosistema necesita? | Integración empresarial madura (mensajería, transacciones, seguridad, batch) | Ecosistema npm y tipos o contratos compartidos con el frontend |
| ¿Cómo se integra con Liferay? | Afinidad con el ecosistema Java del portal (no implica OSGi) | Encaja como Client Extension de microservicio o como BFF |
| ¿Hay requisitos estrictos de arranque o memoria? | Valorar CDS, AOT o native image si son críticos | Arranque rápido y menor huella por defecto |

## 2. Coste de una segunda tecnología
Si la organización ya usa una, la otra debe justificar su coste: formación, pipelines de CI/CD, imágenes base, observabilidad, gestión de dependencias y vulnerabilidades, guardias y contratación.

## 3. Matriz de decisión
Criterios mínimos: competencias del equipo, coste de operación y soporte, ajuste al papel del servicio, ecosistema e integraciones, rendimiento para el perfil de carga y coherencia con la plataforma existente. Pesos de 1 a 3 y valoraciones de 1 a 5; si puedes ejecutar scripts, calcula el resultado y su sensibilidad con `scripts/decision_matrix.py`.

## 4. Antipatrones
- Elegir por preferencia personal o por moda.
- Introducir una segunda tecnología backend sin equipo ni plataforma que la sostengan.
- Suponer que compartir lenguaje con el frontend sustituye a un contrato explícito.
- Reescribir un servicio estable solo para unificar tecnología.

## 5. Resultado
Recomendación, criterio que decide, condiciones que la invertirían y ADR.
