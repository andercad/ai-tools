# Estrategia de renderizado y entrega: <aplicación>

## 1. Matriz por ruta
| Ruta o grupo | Pública o privada | SEO o social preview | Frecuencia de cambio del contenido | Estrategia (CSR, SSG, SSR) | Hydration / `@defer` | Caché (CDN, navegador) | Justificación |
|---|---|---|---|---|---|---|---|

## 2. Baseline y objetivos
| Métrica | Fuente (campo o laboratorio) | Baseline | Objetivo | Fecha de medición |
|---|---|---|---|---|
| LCP (p75) | CrUX o RUM | | | |
| INP (p75) | CrUX o RUM | | | |
| CLS (p75) | CrUX o RUM | | | |
| Bundle inicial | Informe de build | | Presupuesto | |

Los datos de campo mandan; sin baseline no se aprueban optimizaciones.

## 3. Presupuestos y palancas
| Palanca | Ruta afectada | Métrica que debe mejorar | Resultado medido |
|---|---|---|---|

Presupuestos configurados en el build y comprobados en CI.

## 4. Hosting y caché
| Elemento | Decisión | Motivo |
|---|---|---|
| Hosting (estático + CDN, Node para SSR, Liferay) | | |
| `index.html` | Sin caché o con revalidación | |
| Assets con hash | `immutable`, larga duración | |
| HTML generado por SSR | Público cacheable o por usuario no cacheable | |

## 5. Entrega
- Build único promovido entre entornos; configuración runtime en: <fichero servido o inyección del servidor>.
- Retención de assets de la versión anterior: <tiempo>.
- Rollback: <procedimiento y tiempo objetivo>.
- Observabilidad del cliente: <errores, RUM, correlación con el backend>.

## 6. Riesgos
| Riesgo | Probabilidad | Impacto | Mitigación | Señal de alerta |
|---|---|---|---|---|
