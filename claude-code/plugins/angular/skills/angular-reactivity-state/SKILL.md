---
name: angular-reactivity-state
description: 'Asesoría arquitectónica sobre reactividad y gestión de estado en Angular: Signals, computed, linkedSignal, effects, RxJS e interoperabilidad, resource y httpResource, estado local, de feature, global y de URL, stores (servicio con signals, NgRx SignalStore, NgRx Store), estado de servidor y caché, concurrencia y cancelación, zoneless y estrategia de formularios (reactive, template-driven, signal forms). Usar cuando se pregunte dónde debe vivir el estado, si hace falta un store, cómo combinar Signals y RxJS, cómo evitar estado duplicado o condiciones de carrera o qué tipo de formularios usar. No usar como generador de código ni para estructura de carpetas o rendimiento de renderizado.'
---

# Reactividad y gestión de estado

## Objetivo
Decidir dónde vive cada estado, quién es su dueño y con qué primitiva se modela, evitando duplicación, condiciones de carrera y complejidad innecesaria.

## Clasificación del estado
| Tipo | Ejemplo | Fuente de verdad recomendada |
|---|---|---|
| UI local | Panel abierto, pestaña activa | Signal en el componente |
| Feature | Filtros y selección de una pantalla | Servicio de feature con signals o store de feature |
| Servidor | Datos de la API | Caché de datos remotos con invalidación, no copias manuales |
| URL | Página, filtros compartibles | Router (parámetros), derivando el resto |
| Sesión o global | Usuario, idioma, permisos para UX | Servicio raíz de solo lectura hacia fuera |
| Formulario | Borrador de edición | Modelo de formulario, separado del estado de servidor |

## Criterios de decisión: Signals frente a RxJS
| Necesidad | Primitiva |
|---|---|
| Estado síncrono y derivado | `signal` y `computed` |
| Estado dependiente que puede sobrescribirse | `linkedSignal` (verifica su estado en la versión) |
| Carga asíncrona ligada a parámetros | `resource`/`httpResource` si son estables en la versión; si no, RxJS |
| Flujos de eventos, tiempo, cancelación, combinación compleja | RxJS |
| Efectos hacia fuera (logging, sincronizar con APIs del navegador) | `effect`, nunca para derivar estado |
Usa la interoperabilidad (`toSignal`, `toObservable`) en las fronteras, no de forma indiscriminada.

## Escalera de stores
1. Signal en el componente.
2. Servicio de feature con signals privados y API de solo lectura.
3. Store ligero de feature (por ejemplo, NgRx SignalStore).
4. Store global con acciones y reducers (NgRx Store) solo si hay muchos equipos sobre el mismo estado, necesidad de trazabilidad de eventos o devtools, o flujos complejos entre features.
Sube un peldaño solo con un problema demostrado. Bajar después es caro.

## Concurrencia
La política de concurrencia es una decisión de negocio por flujo:
- `switchMap`: búsquedas y lecturas cancelables (la última gana).
- `concatMap`: operaciones que deben respetar el orden.
- `exhaustMap`: evitar doble envío.
- `mergeMap`: operaciones independientes en paralelo con límite.
Define también errores, reintentos (solo idempotentes) y estados de carga.

## Zoneless
Con zoneless, la detección de cambios se dispara por signals, eventos de plantilla y `markForCheck`, no por cualquier tarea asíncrona. Evalúa librerías que dependan de zone.js, pruebas y código que muta estado fuera de Angular. Verifica el estado de soporte en la versión instalada.

## Formularios
| Opción | Encaja cuando | Cuidado con |
|---|---|---|
| Reactive forms | Formularios complejos, validación dinámica, pruebas | Verbosidad; interoperabilidad con signals |
| Template-driven | Formularios simples | Lógica en plantilla, pruebas |
| Signal forms | Modelo basado en signals | Verifica si es experimental en la versión; no lo adoptes en producción sin evaluar el riesgo |
No mezcles estado de formulario con estado de servidor; define validación en cliente como UX y la validación real en el backend.

## Antipatrones
- `effect` para producir estado derivado.
- Convertir todo Observable a Signal o al revés sin motivo.
- Store global para estado local.
- `BehaviorSubject` o signals mutables expuestos públicamente.
- Suscripciones anidadas y sin limpieza.
- Duplicar en un store lo que ya está en la URL o en la caché de servidor.

## Salida
Usa `templates/state-map.md` para el mapa de estado y la decisión de store.
Mapa de estado (`Estado | Tipo | Fuente de verdad | Dueño | Ciclo de vida`), decisión de store según la escalera, política de concurrencia por flujo, estrategia de formularios, trade-offs, riesgos de migración y ADR.

## Autoevaluación
¿Cada estado tiene una única fuente de verdad y un dueño? ¿He subido en la escalera de stores con un problema demostrado? ¿He usado `effect` solo para efectos? ¿He verificado el estado de estabilidad de las APIs citadas? ¿La política de concurrencia está justificada por negocio?
