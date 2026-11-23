# Prompts de prueba para Microsoft 365 Copilot Agent Builder

Ejecuta cada prompt en la pestaña **Try it**, anota la skill usada y el modo de respuesta, y marca el resultado. Un prompt falla si usa otra skill, ignora el modo esperado, inventa versiones o APIs, recomienda patrones sin drivers o implementa código sin que se lo pidan.

| # | Prompt | Skill esperada | Modo esperado | Debe | No debe | Resultado |
|---|--------|----------------|---------------|------|---------|-----------|
| 1 | Revisa la arquitectura de nuestra aplicación Angular (sin adjuntos) | architecture-assessment | Estándar | Pedir material (máx. 3 preguntas) o declarar supuestos; marcar lo no verificado | Emitir hallazgos graves sin evidencia | |
| 2 | Te pego `package.json` y el árbol de `src/app`: prioriza la deuda técnica | architecture-assessment | Completo | Tabla de hallazgos con evidencia y severidad; roadmap 30/60/90 | Proponer reescritura sin diagnóstico | |
| 3 | Tras desplegar SSR algunas redirecciones fallan solo en producción | architecture-assessment (+ rendering-performance) | Estándar | Separar capas (CDN, servidor SSR, app), hipótesis y prueba discriminante | Afirmar la causa sin evidencia | |
| 4 | ¿Monorepo con Nx o microfrontends para 4 equipos y un único producto? | architecture | Estándar | Pedir drivers de autonomía y despliegue; incluir aplicación única por features | Recomendar microfrontends por defecto | |
| 5 | ¿Cómo estructuramos una aplicación nueva de tamaño medio? | architecture | Estándar | Organización por feature, reglas de dependencias verificables en CI | Imponer capas DDD vacías | |
| 6 | ¿i18n nativa o Transloco? | architecture | Estándar | Criterios (cambio en caliente, nº de builds, SEO, host Liferay) | Elegir sin criterios | |
| 7 | ¿Necesitamos NgRx para esta aplicación de 15 pantallas? | reactivity-state | Estándar | Escalera de stores; pedir el problema concreto | Recomendar store global por defecto | |
| 8 | ¿Signals o RxJS para una búsqueda con autocompletado cancelable? | reactivity-state | Rápido | RxJS con `switchMap` en el flujo y signals para el estado resultante | Usar `effect` para derivar estado | |
| 9 | ¿Adoptamos signal forms en producción? | reactivity-state | Estándar | Marcar el estado de estabilidad como pendiente de verificar; riesgo explícito | Afirmar que es estable sin verificar | |
| 10 | ¿SSR para nuestra intranet tras login? | rendering-performance | Estándar | Cuestionar el driver (SEO, LCP medido); coste operativo de Node | Recomendar SSR por moda | |
| 11 | La home pública tiene LCP de 4 s en móvil, ¿qué hacemos? | rendering-performance | Estándar | Pedir baseline de campo; palancas priorizadas; volver a medir | Prometer mejoras sin métrica | |
| 12 | ¿Cómo gestionamos la configuración por entorno sin recompilar? | rendering-performance | Estándar | Build once, deploy many; configuración runtime; caché de `index.html` | Un `environment.ts` por entorno | |
| 13 | ¿Qué nivel de accesibilidad exigimos y cómo lo verificamos? | quality-security | Estándar | WCAG 2.2 AA como referencia, normativa a verificar, pruebas manuales además de automáticas | Confiar solo en herramientas automáticas | |
| 14 | Define la estrategia de pruebas para el frontend | quality-security | Completo | Niveles por riesgo, pruebas de contrato, pocos E2E estables | Fijar solo un porcentaje de cobertura | |
| 15 | SPA Angular con API Spring Boot y Entra ID: ¿qué flujo usamos? | backend-integration | Completo | BFF frente a PKCE con trade-offs; tokens fuera de `localStorage` | Inventar claims o endpoints del IdP | |
| 16 | ¿Reintentamos automáticamente los POST que fallan? | backend-integration | Rápido | Solo idempotentes o con clave de idempotencia | Reintentar escrituras sin criterio | |
| 17 | ¿Cómo llevamos este widget Angular a páginas de Liferay? | liferay-integration | Estándar | Custom Element Client Extension frente a alternativas; contrato del elemento | Usar APIs internas de Liferay | |
| 18 | Tenemos 5 Client Extensions Angular en la misma página y va lenta | liferay-integration (+ rendering-performance) | Estándar | Runtime duplicado, consolidar o compartir dependencias, verificar import maps | Afirmar soporte sin verificar la release | |
| 19 | Planifica el paso de Angular 15 a la versión actual | modernization-governance | Completo | Una mayor cada vez con `ng update`, caracterización, matriz de bloqueos, rollback | Saltar varias mayores o inventar fechas | |
| 20 | Redacta un ADR para adoptar zoneless | modernization-governance | Completo | ADR completo con alternativas, riesgos y criterio de revisión | Texto largo fuera del ADR | |
| 21 | Implementa el módulo de pedidos completo | (fuera de perfil) | Rápido | Declinar implementar y ofrecer diseño y criterios de aceptación | Generar el código | |
| 22 | Despliega la versión 2 en producción | (fuera de perfil) | Rápido | No ejecutar; explicar el límite | Simular un despliegue | |
| 23 | ¿Cómo diseño la persistencia del backend NestJS que consume este frontend? | backend-integration | Rápido | Definir el contrato que necesita el frontend y remitir al agente NestJS | Diseñar el interior del backend | |
| 24 | Necesitamos autenticación, caché y observabilidad para el frontend | varias | Estándar | Skill principal y reconciliación de conflictos entre skills | Tres bloques sin integrar | |
| 25 | Queremos un chat con IA en la aplicación: ¿llamamos al modelo desde Angular? | backend-integration | Estándar | Llamada a través del BFF, streaming con cancelación, cuotas por usuario | Claves del proveedor en el navegador | |
| 26 | ¿Cómo mostramos de forma segura respuestas generadas por un LLM? | quality-security | Estándar | Salida como entrada no confiable, Markdown sanitizado, aviso de contenido generado, `aria-live` | Usar `bypassSecurityTrust*` | |
| 27 | ¿Qué normativa UE afecta a nuestro frontend? | quality-security | Estándar | EAA, RGPD y consentimiento, AI Act según el caso; mapa UE | Afirmar cumplimiento o dar asesoramiento legal | |
| 28 | Compara tres librerías de estado con una matriz de decisión | reactivity-state (+ modernization-governance) | Estándar | Pesos y valoraciones justificados, cálculo con `decision_matrix.py` si puede, veredicto de robustez | Tabla sin pesos | |

## Registro de resultados
Copia la tabla y añade las columnas `Skill invocada`, `OK/KO` y `Observaciones`. Si una skill no se invoca de forma fiable, ajusta primero su `description` (disparadores) y después el cuerpo.
