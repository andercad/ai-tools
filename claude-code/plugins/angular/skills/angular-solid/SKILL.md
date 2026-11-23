---
name: angular-solid
description: Diseño previo SOLID para código Angular nuevo o refactorizado. Usar antes de escribir componentes, servicios, directivas o pipes para decidir responsabilidades, dependencias y puntos de extensión. No usar para sintaxis o APIs de Angular (skill angular-developer) ni para decisiones de arquitectura de aplicación (agente angular-architect).
---

# Diseño SOLID previo (antes de escribir)

El objetivo es acertar a la primera: decide la estructura **antes** de generar código para no tener que revisar y rehacer.

## Paso previo obligatorio: mini-diseño (5–8 líneas)
Antes de escribir, anota mentalmente (o en la respuesta si la tarea es grande):
1. **Piezas y responsabilidad única** de cada una (una razón de cambio por clase). Un componente presenta; un servicio orquesta datos/negocio; lógica pura en funciones.
2. **Contenedor vs presentacional**: el contenedor obtiene datos y decide; el presentacional recibe `input()` y emite `output()`.
3. **Dependencias**: hacia abstracciones (tokens `InjectionToken`/clases abstractas) solo si hay o habrá ≥2 implementaciones reales o hace falta sustituir en tests. Sin interfaces vacías.
4. **Extensión sin modificación**: si hay variantes (estrategias, renderers por tipo), usa configuración, composición o proyección de contenido, no `if/switch` crecientes.
5. **Interfaces pequeñas**: inputs mínimos; no pases el objeto entero si el hijo usa 2 campos.
6. **Contratos sustituibles** (Liskov): subclases/implementaciones que cumplan el mismo contrato sin sorpresas.

## Límites (proporcionalidad)
- Cambio trivial o pieza de ≤30 líneas: no hace falta mini-diseño.
- No añadas capas, fábricas ni abstracciones prematuras; SOLID es para reducir coste de cambio, no para sumar ficheros.

## Referencia
- [solid.md](references/solid.md): síntomas de violación, aplicación en Angular y checklist de diseño. Léela solo si dudas.
