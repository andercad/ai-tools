---
name: angular-rendering-performance
description: 'Asesoría arquitectónica sobre estrategia de renderizado, rendimiento y entrega de aplicaciones Angular: CSR, SSR, SSG o prerender, modos de render por ruta, hydration e incremental hydration, deferrable views, presupuestos de bundle, Core Web Vitals (LCP, INP, CLS), imágenes, caché HTTP y CDN, hosting (estático, Node, contenedor), configuración runtime por entorno y pipeline de build y despliegue. Usar cuando se pregunte si adoptar SSR o SSG, por qué una aplicación es lenta, cómo reducir el bundle, dónde alojar el frontend o cómo promover un mismo build entre entornos. No usar como generador de código ni para auditar accesibilidad o seguridad.'
---

# Renderizado, rendimiento y entrega

## Objetivo
Elegir la estrategia de renderizado por ruta según requisitos medibles (SEO, primer render, coste operativo) y gobernar el rendimiento y la entrega con métricas, presupuestos y rollback.

## Criterios de decisión por ruta
| Estrategia | Encaja cuando | Coste |
|---|---|---|
| CSR | Aplicaciones tras login, sin SEO, alta interactividad | LCP depende del bundle y de la API |
| SSG / prerender | Rutas públicas conocidas y estables | Rebuild o regeneración al cambiar contenido |
| SSR | SEO o social previews en contenido dinámico, LCP crítico en campo | Runtime Node que operar, escalar y observar; caché más compleja |
Decide por ruta, no por aplicación. No afirmes que hay SSR solo porque existe un artefacto de servidor: verifica qué se sirve realmente.

## Reglas de SSR e hydration
- Aísla APIs de navegador (`window`, `localStorage`, `document`) y código dependiente de plataforma.
- Evita doble petición entre servidor y cliente con transfer state o caché HTTP de hydration.
- No caches HTML personalizado en una caché compartida; separa respuestas públicas y por usuario.
- Autenticación en SSR: cookies del propio dominio; no reenvíes tokens de usuario a servicios de terceros sin necesidad.
- Hydration requiere DOM coherente entre servidor y cliente; la manipulación directa del DOM la rompe.
- Incremental hydration y `@defer` reducen trabajo inicial; verifica su estado de estabilidad en la versión instalada.

## Rendimiento basado en medición
1. Baseline: datos de laboratorio (Lighthouse) y de campo (CrUX o RUM). Los de campo mandan.
2. Objetivos: umbrales de Core Web Vitals (LCP, INP, CLS) y presupuestos de bundle en `angular.json` que fallen el build.
3. Palancas habituales: lazy loading por ruta, `@defer`, imágenes optimizadas (`NgOptimizedImage`), fuentes, preconnect, reducción de dependencias, `OnPush` o zoneless para INP.
4. Vuelve a medir y conserva el antes y el después.
No optimices sin baseline ni prometas mejoras sin métrica.

## Entrega y configuración
- **Build once, deploy many**: el mismo artefacto se promueve entre entornos. La configuración por entorno se carga en runtime (fichero de configuración servido o inyectado por el servidor), no con un `environment.ts` por entorno.
- Caché: assets con hash y `Cache-Control: immutable`; `index.html` sin caché o con revalidación.
- Rollback: conserva los assets de la versión anterior para clientes con chunks antiguos (evita errores de carga de chunks) y define cómo volver atrás en minutos.
- Observabilidad del frontend: captura de errores, RUM y correlación con el backend.

## Hosting
| Opción | Encaja cuando |
|---|---|
| Estático + CDN (por ejemplo, Azure Static Web Apps o Storage con Front Door) | CSR o SSG |
| Contenedor o servicio Node (App Service, Container Apps, AKS) | SSR, con probes, escalado y logs |
| Dentro de Liferay (Client Extension) | Widget o aplicación en páginas del portal (ver `angular-liferay-integration`) |
Elige la opción más simple que cumpla los NFR; SSR añade una pieza a operar.

## Antipatrones
- SSR para aplicaciones privadas sin requisito de SEO ni LCP medido.
- Un build por entorno o secretos en el bundle.
- Optimizar sin baseline o con solo datos de laboratorio.
- Caché compartida de páginas personalizadas.
- Despliegues que borran los assets anteriores.

## Salida
Usa `templates/rendering-strategy.md` para la estrategia por ruta y la entrega.
Matriz de renderizado por ruta, métricas objetivo y presupuestos, topología de hosting y caché, pipeline build-once con promoción entre entornos, estrategia de rollback, riesgos y ADR.

## Autoevaluación
¿He decidido por ruta y con drivers medibles? ¿Hay baseline y métrica de éxito? ¿He considerado el coste operativo de SSR? ¿El build es único y la configuración runtime? ¿Existe rollback viable?
