# Checklist de integración frontend-backend

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Responsabilidades
- [ ] Está decidido si hay BFF y por qué; si existe, tiene responsabilidad real (sesión, agregación, adaptación a la UI).
- [ ] La lógica de negocio vive en el backend y el frontend no la duplica.
- [ ] Cada lado del contrato tiene dueño.

## Autenticación
- [ ] Flujo elegido (BFF con cookie o Authorization Code con PKCE) con trade-offs documentados.
- [ ] Sin flujo implícito; tokens fuera del almacenamiento persistente del navegador.
- [ ] Renovación de sesión o tokens definida, incluido el efecto de las restricciones a cookies de terceros.
- [ ] Claims, scopes y endpoints del IdP tomados de su documentación o de sus metadatos.
- [ ] Cierre de sesión coordinado con el IdP.

## Contrato
- [ ] Fuente de verdad (OpenAPI u otra) con cliente o tipos generados, no copiados a mano.
- [ ] Política de versionado y deprecación conocida por ambos equipos.
- [ ] Pruebas de contrato en los pipelines de ambos lados.

## Capa HTTP
- [ ] Interceptores para autenticación, correlación y traducción de errores, sin lógica de negocio.
- [ ] Errores con Problem Details traducidos a estados de UI coherentes.
- [ ] Timeouts explícitos y cancelación al abandonar la pantalla.
- [ ] Reintentos solo en operaciones idempotentes o con clave de idempotencia acordada.
- [ ] Paginación adecuada al volumen (cursor u offset) con tamaño máximo.

## Tiempo real (si aplica)
- [ ] Mecanismo justificado (polling, SSE, WebSocket), autenticación del canal y reconexión definidas.

## Red
- [ ] Mismo origen (BFF o reverse proxy) o CORS con orígenes explícitos, nunca comodín con credenciales.

## Resultado
Decisiones abiertas para el equipo de backend (con remisión al agente de Spring Boot o NestJS), riesgos y acciones con responsable.
