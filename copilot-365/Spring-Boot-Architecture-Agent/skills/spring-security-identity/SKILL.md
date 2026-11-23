---
name: spring-security-identity
description: 'Asesoría arquitectónica sobre seguridad e identidad en Spring Boot: Spring Security, OAuth 2.0/OIDC, resource server, BFF, mTLS, autorización (roles, scopes, ABAC), gestión de secretos, threat modeling, protección de APIs y datos sensibles, seguridad de aplicaciones con IA generativa (OWASP Top 10 para LLM), cumplimiento y normativa UE (RGPD, ENS, NIS2, DORA, AI Act) y dependencias. Usar cuando se pregunte cómo autenticar o autorizar usuarios y servicios, qué flujo OAuth usar, dónde validar permisos, cómo proteger secretos y datos personales, cómo modelar amenazas o qué normativa aplica. No usar como generador de código por defecto ni para inventar configuración de un proveedor de identidad.'
---

# Seguridad, identidad y cumplimiento

## Objetivo
Definir una arquitectura de seguridad proporcional al riesgo, con identidad centralizada, mínimo privilegio y trazabilidad.

## Decisiones de identidad
- **Usuarios web con SPA**: preferir patrón **BFF** (el backend gestiona la sesión y los tokens; el navegador no guarda tokens de acceso) frente a tokens en almacenamiento del navegador. Alternativa: Authorization Code con PKCE directo desde la SPA, aceptando el riesgo de exposición del token.
- **Aplicación con renderizado servidor**: Spring Security `oauth2Login` con OIDC.
- **API como resource server**: valida JWT (firma, `iss`, `aud`, expiración) o introspección de tokens opacos. Los opacos permiten revocación inmediata a costa de latencia y dependencia del IdP; los JWT son autónomos pero se revocan peor. Decide según requisitos de revocación.
- **Servicio a servicio**: `client_credentials` con scopes mínimos; mTLS o identidad de plataforma (workload identity) cuando exista; propagación de identidad de usuario solo si el caso lo exige (token exchange).
- **Proveedor de identidad**: externo (Entra ID, Keycloak, Okta, etc.) antes que construir uno propio. No inventes claims, endpoints ni configuración del IdP: pide los metadatos reales.

## Autorización
- Aplícala en el **caso de uso** además de en el borde HTTP; el filtrado en la capa web no basta.
- Modelo: roles para permisos gruesos, scopes para clientes de API, ABAC/permisos por recurso cuando la decisión depende del dato. Evita explosión de roles.
- Métodos con `@PreAuthorize` solo si las reglas son legibles y testeables; reglas complejas en un servicio de políticas propio.
- GraphQL: autorización por operación y recurso, no solo por campo.

## Superficie de ataque (revisa en este orden)
1. Autenticación y gestión de sesión/token (caducidad, rotación, logout).
2. Autorización rota (IDOR, acceso horizontal) —riesgo principal en APIs—.
3. Validación de entrada y salida; no devolver entidades ni errores internos.
4. CSRF/CORS configurados según el modelo (sesión con cookie frente a token en cabecera).
5. Secretos: fuera del repositorio, en gestor (Key Vault u equivalente), rotación, sin secretos en imágenes ni logs.
6. Datos sensibles: clasificación, cifrado en tránsito y en reposo, enmascarado en logs, minimización.
7. Dependencias y cadena de suministro: SBOM, análisis de vulnerabilidades, actualización periódica.
8. Actuator y herramientas operativas: expón solo lo necesario, protegido y en puerto/red de gestión.
9. Limitación de tasa, protección de fuerza bruta y abuso.

## Threat modeling
Usa STRIDE sobre el diagrama de contenedores: activos, límites de confianza, flujos, amenazas, mitigaciones, riesgo residual y propietario. Prioriza por probabilidad × impacto.

## Cumplimiento
Mapea requisitos (RGPD, ENS, NIS2, DORA, EAA, AI Act, CRA, PCI DSS, ISO 27001, etc.) a controles técnicos concretos y evidencias con `reference/eu-regulatory-map.md`. No afirmes que una arquitectura «cumple» una norma: indica qué controles cubre y qué requiere revisión del equipo de cumplimiento.

## IA generativa
Revisa el OWASP Top 10 para aplicaciones con LLM: inyección de prompts (prompt injection) directa e indirecta a través de documentos recuperados, divulgación de información sensible, manejo inseguro de la salida (es entrada no confiable), agencia excesiva de las herramientas, fuga del prompt de sistema (sin secretos en prompts), debilidades de vectores y embeddings (fugas entre usuarios o tenants si la recuperación no filtra por permisos) y consumo no acotado. Define qué datos pueden salir al proveedor (clasificación, residencia, retención y uso para entrenamiento según contrato) y clasifica el caso de uso frente al AI Act con cumplimiento.

## Versiones
Spring Security cambia APIs entre líneas mayores (p. ej. la configuración con `SecurityFilterChain` y lambdas sustituyó a `WebSecurityConfigurerAdapter`). Detecta la versión y verifica las clases y propiedades antes de citarlas.

## Salida
Para una revisión de seguridad, usa `reference/security-review-checklist.md`.
Modelo de identidad, flujo de autenticación/autorización, modelo de amenazas resumido, gestión de secretos, controles de cumplimiento, pruebas de seguridad (unitarias con `spring-security-test`, DAST/SAST, pruebas de autorización por rol), riesgos y ADR.

## Autoevaluación
Comprueba que no hay confianza implícita entre servicios, que la autorización no depende solo de la UI o del gateway, que no se inventó configuración del IdP y que los secretos y datos personales tienen tratamiento explícito.
