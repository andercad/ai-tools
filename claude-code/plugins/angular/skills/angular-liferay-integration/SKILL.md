---
name: angular-liferay-integration
description: 'Asesoría arquitectónica sobre la integración de Angular con Liferay DXP: elección entre Custom Element Client Extension, IFrame Client Extension, aplicación desacoplada sobre Headless APIs o Fragments, contrato del custom element (atributos, propiedades, eventos), varias instancias y varias aplicaciones Angular en la misma página, configuración runtime, idioma y site del portal, OAuth2 en Liferay, Headless REST y GraphQL, dependencias compartidas, CSP y despliegue según modalidad (self-hosted, PaaS, SaaS). Usar cuando se pregunte cómo llevar una aplicación o widget Angular a Liferay, cómo autenticarlo, cómo convivir varias aplicaciones en una página o qué tipo de Client Extension usar. No usar para decisiones internas de Liferay (Objects, OSGi, Search, upgrades del portal) ni como generador de código.'
---

# Integración de Angular con Liferay

## Objetivo
Decidir cómo se integra una aplicación Angular con Liferay y definir el contrato, la autenticación, la convivencia en página y el despliegue. Las decisiones internas del portal corresponden al agente de arquitectura Liferay.

## Criterios de decisión: mecanismo
| Mecanismo | Encaja cuando | Coste |
|---|---|---|
| Custom Element Client Extension | UI compleja dentro de páginas del portal, configurable por instancia, integrada con el tema | Convivencia con otras aplicaciones en la página, tamaño del bundle |
| IFrame Client Extension | Aplicación existente o de terceros que necesita aislamiento total | UX (altura, navegación), SSO, accesibilidad |
| Aplicación desacoplada + Headless + OAuth2 | La experiencia vive fuera del portal y Liferay actúa como backend de contenido o datos | Hosting y autenticación propios |
| Fragment con JavaScript | Interacción sencilla gestionada por editores | No apto para aplicaciones complejas |
Verifica los tipos de Client Extension disponibles en la release y modalidad del cliente: en Liferay SaaS solo son posibles las extensiones soportadas por la plataforma.

## Contrato del custom element
| Elemento | Decisión |
|---|---|
| Atributos y propiedades | Qué configura el editor por instancia; los atributos son texto, los objetos van como propiedades o JSON validado |
| Eventos | `CustomEvent` con nombre y payload versionados para comunicar con la página u otras aplicaciones |
| Configuración runtime | URLs y parámetros externos al bundle, por instancia o por entorno |
| Contexto del portal | Idioma, site y usuario a través de la API JavaScript pública del portal (verifica el objeto global y sus métodos en la release) |
| Estilos | Coherencia con el tema, Clay y Style Books; decide si Shadow DOM aporta o rompe la herencia de estilos |
| Routing | El path pertenece al portal: usa rutas internas que no colisionen (hash o rutas acotadas) y define deep links |

## Varias instancias y varias aplicaciones
- Sin IDs globales ni singletons con estado de instancia; cada instancia con su propio estado.
- Varias aplicaciones Angular en una página multiplican el runtime cargado y pueden entrar en conflicto (zone.js, versiones distintas). Valora consolidar widgets en una aplicación, alinear versiones o compartir dependencias mediante import maps si la release lo soporta (verifica).
- Zoneless reduce conflictos de zone.js entre aplicaciones; verifica soporte de la versión.
- Limpia recursos en la destrucción del elemento (navegación SPA del portal, edición de páginas).

## Autenticación y APIs
- Dentro de una página del portal: las llamadas a Headless usan la sesión del usuario y el token CSRF del portal; los permisos los aplica Liferay.
- Hacia servicios externos (Spring Boot, NestJS): OAuth2 con aplicaciones registradas en Liferay (perfiles User Agent o Headless Server mediante Client Extensions de configuración); valida scopes mínimos. Detalle en `angular-backend-integration` y en el agente Liferay.
- Usa Headless REST o GraphQL públicos; no uses APIs internas ni JSON Web Services heredados si existe alternativa Headless.
- La autorización reside en Liferay o en el backend, nunca en la aplicación Angular.

## Seguridad y CSP
Alinea la CSP del portal con los orígenes de la aplicación (scripts, APIs, fuentes). Revisa cómo afecta a scripts inline y a librerías de terceros.

## Despliegue
Client Extensions definidas en `client-extension.yaml` dentro de Liferay Workspace, con build reproducible y versión trazable. Diferencias por modalidad (self-hosted, PaaS, SaaS) en despliegue, hosting de assets y rollback: verifica en la documentación de la release.

## Antipatrones
- Una Client Extension por botón: multiplica runtimes y bundles.
- IDs globales o estado en singletons compartidos entre instancias.
- URLs y entornos compilados en el bundle.
- Llamadas a APIs internas o a tablas de Liferay.
- Autorización resuelta en el frontend.

## Salida
Documenta el contrato con `templates/custom-element-contract.md`.
Decisión de mecanismo con matriz, tabla del contrato del elemento, diagrama de autenticación, estrategia de multi-instancia y dependencias, despliegue y rollback, y preguntas abiertas para el agente Liferay.

## Autoevaluación
¿El mecanismo es el más simple que cumple? ¿He verificado los tipos de Client Extension para la release y modalidad? ¿Varias instancias funcionan sin estado compartido? ¿La autorización está en el servidor? ¿He evitado APIs internas?
