# Checklist de revisión de seguridad para Spring Boot

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Identidad
- [ ] Proveedor de identidad externo (Entra ID, Keycloak u otro); sin gestión propia de contraseñas salvo requisito justificado.
- [ ] SPA: BFF con sesión en servidor y cookies `HttpOnly`/`Secure`/`SameSite`, o PKCE con el riesgo aceptado por escrito.
- [ ] Resource server: JWT validado (firma, `iss`, `aud`, expiración) o introspección si se requiere revocación inmediata.
- [ ] Servicio a servicio: `client_credentials` con scopes mínimos, mTLS o identidad de plataforma; sin secretos compartidos estáticos.
- [ ] Claims, endpoints y configuración del IdP tomados de sus metadatos reales, no supuestos.

## Autorización
- [ ] Autorización en el caso de uso además de en el borde; el gateway no es la única barrera.
- [ ] Control por recurso (propietario o tenant) para evitar IDOR y acceso horizontal.
- [ ] Modelo de roles, scopes y permisos por recurso sin explosión de roles.
- [ ] Mismos controles en REST, GraphQL, mensajería y jobs.
- [ ] Pruebas de autorización por rol y por recurso.

## Configuración de Spring Security
- [ ] Configuración con `SecurityFilterChain` acorde a la versión instalada; sin APIs eliminadas.
- [ ] CSRF y CORS decididos según el modelo (cookie de sesión frente a token en cabecera).
- [ ] Respuestas de error de seguridad sin detalles internos.

## Superficie operativa
- [ ] Actuator: solo endpoints necesarios, autenticados y en puerto o red de gestión.
- [ ] Rate limiting y protección de fuerza bruta en login y operaciones sensibles.

## Secretos y datos
- [ ] Secretos en gestor dedicado con rotación; nada en repositorio, imagen ni logs.
- [ ] Datos personales clasificados, minimizados, cifrados en tránsito y en reposo y enmascarados en logs.
- [ ] Auditoría de acciones sensibles con correlación y retención definida.

## Cadena de suministro
- [ ] SBOM, análisis de vulnerabilidades y actualización automatizada de dependencias.
- [ ] Imagen mínima, sin root y escaneada.

## Modelo de amenazas (STRIDE resumido)
| Activo o flujo | Amenaza | Mitigación | Riesgo residual | Responsable |
|---|---|---|---|---|

## Resultado
Riesgos priorizados (crítico, alto, medio, bajo) con control recomendado, responsable y verificación. Indica qué controles de cumplimiento cubre la arquitectura y cuáles requieren revisión del equipo de cumplimiento.
