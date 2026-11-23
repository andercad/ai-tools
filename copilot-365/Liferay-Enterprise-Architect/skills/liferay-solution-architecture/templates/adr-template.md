# ADR-NNN: <mecanismo elegido para el requisito>

- **Estado**: Propuesto | Aceptado | Rechazado | Sustituido por ADR-XXX
- **Fecha**: AAAA-MM-DD · **Responsables**: <roles> · **Consultados**: <equipos>
- **Release y modalidad**: <release> · self-hosted | PaaS | SaaS (verificado: sí/no)

## Contexto y requisito
Qué se necesita, para quién y con qué NFR (volumen, latencia, disponibilidad, permisos, cumplimiento). Hechos separados de supuestos.

## Escalera de mecanismos
| Peldaño | ¿Cumple el requisito? | Motivo si se descarta |
|---|---|---|
| 1. Configuración estándar | | |
| 2. Low-code (Objects, Fragments, plantillas) | | |
| 3. Client Extensions | | |
| 4. Servicio externo (Spring Boot, NestJS) | | |
| 5. Módulo OSGi | | |
| 6. Service Builder | | |

## Alternativas (máximo tres, incluida la más simple)
| Criterio (peso 1-3) | Opción A | Opción B | Opción C |
|---|---|---|---|
| Ajuste al requisito | | | |
| Dentro o fuera de la JVM | | | |
| Permisos y seguridad | | | |
| Operación y quién la opera | | | |
| Coste de upgrade | | | |
| Disponible en la modalidad | | | |
| Total ponderado | | | |

## Decisión
Se elige **<opción>** (peldaño <n>) porque <criterios>. Cambio que invertiría la decisión: <...>.

## Consecuencias
- **Positivas**:
- **Negativas y costes asumidos** (incluido el coste de upgrade):
- **Riesgos**: <riesgo → mitigación → responsable>

## Contratos y dueños
APIs Headless u OpenAPI, eventos y datos, con el dueño de cada uno.

## Verificación y rollback
Criterios de aceptación, pruebas y procedimiento de vuelta atrás.

## Criterios de revisión
<nueva release con una capacidad estándar equivalente, cambio de modalidad, volumen superior a X>

## Pendiente de verificar
- <tipos de Client Extension, capacidades de Objects, restricciones de la modalidad>
