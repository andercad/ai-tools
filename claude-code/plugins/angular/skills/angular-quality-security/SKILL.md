---
name: angular-quality-security
description: 'Asesoría arquitectónica sobre calidad, accesibilidad y seguridad del frontend Angular: estrategia de pruebas por riesgo (unitarias, de componente, de contrato, E2E, visuales) y elección de herramientas, accesibilidad WCAG 2.2 y EN 301 549, threat modeling del frontend, XSS y sanitización, CSP y Trusted Types, almacenamiento de tokens, CSRF y CORS, dependencias, SBOM, contenido generado por IA (LLM), normativa UE (EAA, RGPD, AI Act) y quality gates de producción. Usar cuando se pregunte cómo probar una aplicación Angular, qué nivel de accesibilidad exigir y cómo verificarlo, cómo proteger el frontend, cómo mostrar respuestas de un LLM de forma segura, qué normativa UE aplica o qué criterios debe cumplir para salir a producción. No usar como generador de tests ni para diseñar la autenticación entre servicios backend.'
---

# Calidad, accesibilidad y seguridad del frontend

## Objetivo
Definir controles proporcionales al riesgo para que la aplicación sea verificable, accesible y segura, y fijar quality gates objetivos para producción.

## Criterios de decisión: estrategia de pruebas por riesgo
| Nivel | Qué cubre | Cuándo invertir más |
|---|---|---|
| Unitarias | Lógica pura, servicios, estado derivado | Reglas de negocio en cliente, transformaciones |
| De componente | Comportamiento visible, accesibilidad básica, interacción | Design system y componentes reutilizados |
| De contrato | Acuerdo con la API (esquema OpenAPI o consumer-driven) | Varios equipos o backends que evolucionan por separado |
| E2E | Recorridos críticos de negocio | Pocos y estables; no para cubrir casos límite |
| Visuales | Regresiones de estilo | Design system y marca |
Prioriza por riesgo de negocio, no por porcentaje de cobertura. Elige herramientas según la versión (Vitest, Jest, Playwright, Cypress) y verifica el runner por defecto y las deprecaciones en la versión instalada antes de recomendar una migración.

## Accesibilidad
- Objetivo típico: WCAG 2.2 nivel AA; en la UE, verifica las obligaciones aplicables (EN 301 549, European Accessibility Act) con el área legal.
- HTML semántico primero; ARIA no sustituye a elementos nativos.
- Teclado, gestión del foco en navegación y diálogos, contraste, textos alternativos, mensajes de error asociados.
- La automatización (por ejemplo, axe) detecta solo una parte de los problemas: combina con pruebas manuales de teclado y lector de pantalla.
- La accesibilidad se incorpora en el design system, no se audita al final.

## Seguridad
- **Modelo de amenazas**: límites de confianza navegador, CDN, servidor SSR, BFF, APIs y terceros (scripts, widgets). El navegador es territorio hostil.
- **El frontend no autoriza**: guards y ocultar botones son UX; cada API valida permisos.
- **XSS**: Angular sanitiza por defecto; cualquier `bypassSecurityTrust*`, `innerHTML` con datos externos o manipulación directa del DOM es un punto de revisión obligatorio.
- **CSP** estricta (con nonce si hay SSR) y Trusted Types cuando sea viable; evita `unsafe-inline` y `unsafe-eval`.
- **Tokens**: preferir BFF con cookies `HttpOnly`, `Secure` y `SameSite`; si la SPA gestiona tokens (PKCE), mantenlos en memoria, nunca en `localStorage`. Detalle en `angular-backend-integration`.
- **CSRF**: necesario con autenticación por cookies; usa el soporte XSRF de `HttpClient` alineado con el backend.
- **CORS** es un control del servidor; evítalo sirviendo frontend y API bajo el mismo origen cuando sea posible.
- **Secretos**: nada secreto en el bundle; todo lo que se envía al navegador es público.
- **Cadena de suministro**: lockfile, auditoría de dependencias, actualizaciones automatizadas, SBOM (por ejemplo, CycloneDX), licencias y control de scripts de terceros (SRI cuando aplique).
- **Contenido generado por IA**: trátalo como entrada no confiable; renderiza Markdown con sanitización (sin `bypassSecurityTrust*`), controla enlaces e imágenes externos e indica al usuario que el contenido es generado. Anuncia el contenido en streaming de forma accesible (`aria-live` sin saturar).
- **Normativa**: usa `reference/eu-regulatory-map.md` para traducir EAA, RGPD, AI Act y otras normas aplicables en controles del frontend (accesibilidad, consentimiento, transparencia).

## Quality gates de producción
| Gate | Criterio de ejemplo |
|---|---|
| Build | Sin errores de tipos con `strict`; presupuestos de bundle cumplidos |
| Pruebas | Recorridos críticos en verde; sin pruebas inestables silenciadas |
| Accesibilidad | Sin incidencias críticas automáticas; revisión manual de flujos clave |
| Seguridad | Sin vulnerabilidades críticas abiertas; CSP activa; sin secretos |
| Operación | Captura de errores, RUM y rollback probados |
Ajusta los umbrales a cada organización; sin dueño ni excepción documentada, un gate no sirve.

## Antipatrones
- Cobertura como objetivo en sí mismo.
- E2E para todo; ausencia de pruebas de contrato con varios equipos.
- ARIA para arreglar HTML no semántico.
- Tokens en `localStorage`; secretos en `environment.ts`.
- Confiar en el frontend para autorizar.

## Salida
Para revisar la preparación para producción, usa `reference/production-readiness-checklist.md`.
Matriz `Riesgo | Control | Verificación | Responsable`, estrategia de pruebas por nivel, nivel de accesibilidad objetivo y cómo se verifica, hallazgos por severidad, checklist de production readiness y quality gates.

## Autoevaluación
¿Los controles son proporcionales al riesgo? ¿He separado UX de autorización? ¿La accesibilidad tiene verificación manual? ¿He citado herramientas verificando su estado en la versión? ¿Cada gate tiene criterio y responsable?
