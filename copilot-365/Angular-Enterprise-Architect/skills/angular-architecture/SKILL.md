---
name: angular-architecture
description: 'Asesoría arquitectónica sobre la estructura de aplicaciones Angular: organización por features, límites y dependencias permitidas, modelo de componentes, routing y lazy loading, estrategia de i18n, design system y librerías compartidas, monorepo (Nx u otros) y microfrontends (federación de módulos, Web Components). Usar cuando se pida decidir cómo estructurar o dividir una aplicación, dónde poner código compartido, si adoptar monorepo o microfrontends, cómo hacer cumplir límites, qué estrategia de i18n seguir o cómo repartir equipos sobre el frontend. No usar como generador de código ni para gestión de estado o estrategia de renderizado.'
---

# Estructura, límites y topología del frontend

## Objetivo
Definir una estructura proporcional al tamaño del producto y del equipo, con límites verificables, dependencias explícitas y una topología (aplicación única, monorepo o microfrontends) justificada por drivers reales.

## Criterios de decisión: topología
| Opción | Encaja cuando | Coste principal |
|---|---|---|
| Aplicación única organizada por features | Opción por defecto; uno o pocos equipos; despliegue conjunto aceptable | Disciplina de límites sin herramienta que la imponga |
| Monorepo con librerías y reglas de límites | Varias aplicaciones comparten código; se quiere build y test afectados y verificación de límites | Tooling, curva de aprendizaje, gobierno del workspace |
| Microfrontends (federación en build o runtime, Web Components) | Equipos autónomos con despliegue independiente real, ciclos de release distintos, integración en un host heterogéneo (por ejemplo, Liferay) | Versionado de dependencias compartidas, consistencia UX, rendimiento, pruebas de integración, observabilidad |
Los microfrontends son una decisión organizativa, no técnica: exige drivers y compara siempre con la aplicación única por features.

## Estructura por features
- `core` o app shell: configuración, layout, interceptores, providers globales.
- `features/<feature>`: rutas lazy, páginas, componentes, acceso a datos y estado de la feature.
- `shared/ui`: componentes presentacionales sin dependencias de dominio.
- `shared/util`: utilidades puras.
Dependencias permitidas: feature → shared; feature ↛ otra feature salvo por su API pública; shared ↛ feature. Verifica los límites en CI como fitness function (reglas de límites de Nx, `eslint-plugin-boundaries`, dependency-cruiser). Standalone es el modelo por defecto en versiones recientes; NgModules solo en legado (ver `angular-modernization-governance`).

## Modelo de componentes
- Separa contenedores (orquestan datos y estado) de componentes de presentación (inputs, outputs, sin servicios de datos).
- `OnPush` como estrategia por defecto; con zoneless, el modelo de detección cambia (ver `angular-reactivity-state`).
- Componentes muy grandes o servicios «dios» indican límites mal definidos, no falta de capas.
- Composición antes que herencia; directivas para comportamiento transversal.

## Routing
- Rutas lazy por feature; estrategia de preloading según patrones de navegación medidos.
- Guards como experiencia de usuario, nunca como autorización.
- Resolvers bloquean la navegación; la carga en el componente con skeleton mejora la percepción. Decide por ruta.
- Deep links, SSR y gestión del foco y del título en cada navegación (accesibilidad).
- Dentro de un portal (Liferay), el routing de la aplicación compite con la URL del portal: ver `angular-liferay-integration`.

## Estrategia de i18n
| Opción | Encaja cuando | Cuidado con |
|---|---|---|
| i18n nativa en compilación | Rendimiento, SEO por idioma, pocos cambios de texto en caliente | Un build por idioma; cambio de idioma con recarga |
| Librería runtime (por ejemplo, Transloco) | Cambio de idioma sin recarga, un único build, textos gestionados fuera | Carga de diccionarios, claves sin tipar, SSR |
Usa ICU para plurales y género, no concatenes fragmentos traducidos y formatea fechas y monedas por locale. Si la aplicación vive en Liferay, el idioma lo decide el portal.

## Design system
Decide entre librería propia, Angular Material/CDK o terceros según requisitos de marca, accesibilidad y capacidad de mantenimiento. Define tokens de diseño, ownership, versionado semántico y accesibilidad incorporada. En Liferay, alinéalo con Clay y Style Books.

## Antipatrones
- `shared` gigante que todos importan; barrels que generan ciclos.
- Capas DDD o Clean Architecture vacías sobre un CRUD.
- Microfrontends para un único equipo o como sustituto de modularidad.
- Modelos de backend duplicados a mano sin contrato.
- Estructura por tipo técnico (`components/`, `services/`) en aplicaciones medianas o grandes.

## Salida
Antes de recomendar monorepo o microfrontends, puntúa `reference/microfrontends-readiness.md`.
Topología recomendada con justificación, árbol conceptual de carpetas o librerías, reglas de dependencias y cómo se verifican, diagrama Mermaid de features y dependencias, alternativas con trade-offs, plan incremental y ADR.

## Autoevaluación
¿La topología responde a drivers de equipo y despliegue? ¿Los límites son verificables en CI? ¿He incluido la opción más simple? ¿He evitado capas sin responsabilidad? ¿La i18n y el design system encajan con el host (por ejemplo, Liferay)?
