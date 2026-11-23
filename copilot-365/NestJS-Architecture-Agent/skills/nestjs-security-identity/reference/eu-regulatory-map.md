# Mapa de normativa UE y controles de arquitectura

Orientativo: no es asesoramiento legal. Confirma con el área legal o de cumplimiento qué normas aplican a la organización y al sistema, y su calendario vigente.

## Normas frecuentes
| Norma | A quién aplica | Qué exige, en esencia | Controles de arquitectura típicos | Evidencias |
|---|---|---|---|---|
| RGPD | Tratamientos de datos personales de personas en la UE | Licitud, minimización, seguridad, derechos de los interesados, notificación de brechas, evaluación de impacto | Clasificación y minimización de datos, cifrado, seudonimización, retención y borrado, exportación de datos, registros de acceso, residencia de datos y control de encargados | Registro de actividades, evaluación de impacto, contratos con encargados, pruebas de borrado |
| ENS (RD 311/2022) | Sector público español y proveedores que le prestan servicios | Medidas de seguridad según la categoría del sistema | Control de acceso, registro de actividad, cifrado, continuidad, gestión de configuración y de vulnerabilidades | Declaración de aplicabilidad, auditoría o certificación |
| NIS2 | Entidades esenciales e importantes de los sectores incluidos | Gestión de riesgos de ciberseguridad, notificación de incidentes, seguridad de la cadena de suministro | Gestión de vulnerabilidades, MFA, cifrado, copias y continuidad, monitorización y respuesta a incidentes, evaluación de proveedores | Análisis de riesgos, registro de incidentes, políticas. Depende de la transposición nacional: verifícala |
| DORA | Entidades financieras y sus proveedores TIC | Gestión del riesgo TIC, notificación de incidentes, pruebas de resiliencia, riesgo de terceros | Inventario de activos y dependencias, RTO y RPO, pruebas de resiliencia, registro de proveedores TIC, estrategia de salida | Registro de terceros TIC, resultados de pruebas, notificaciones. Aplica desde enero de 2025 |
| Ley Europea de Accesibilidad (EAA) | Productos y servicios incluidos (por ejemplo, comercio electrónico, banca, transporte) | Accesibilidad de productos y servicios digitales | Requisitos de EN 301 549 (basada en WCAG), design system accesible, pruebas manuales con tecnologías de apoyo | Declaración de accesibilidad, informes de auditoría. Aplica desde junio de 2025 |
| Reglamento de IA (AI Act) | Proveedores y responsables del despliegue de sistemas de IA | Obligaciones según el nivel de riesgo y de transparencia | Clasificación del caso de uso, aviso al usuario de que interactúa con IA, supervisión humana, registro y trazabilidad, gobierno de datos, evaluación | Clasificación documentada, documentación técnica, registros. Aplicación escalonada: verifica el calendario vigente |
| Ley de Ciberresiliencia (CRA) | Fabricantes de productos con elementos digitales comercializados en la UE | Seguridad desde el diseño y gestión de vulnerabilidades durante todo el ciclo de vida | SBOM, gestión y divulgación coordinada de vulnerabilidades, actualizaciones de seguridad, configuración segura por defecto | SBOM, política de divulgación, evaluación de conformidad. Aplicación escalonada: verifica el calendario vigente |
| PCI DSS (estándar del sector, no UE) | Quien almacena, procesa o transmite datos de tarjetas | Protección de los datos de titulares de tarjetas | Reducir el alcance (tokenización o pasarela externa), segmentación de red, cifrado, control de acceso, registro | Informe o cuestionario de cumplimiento |

## Cómo usarlo
1. Identifica con cumplimiento qué normas aplican y a qué sistemas.
2. Traduce cada obligación aplicable en requisitos no funcionales y controles concretos.
3. Asigna cada control a una capa (frontend, backend, datos, plataforma, proceso) y a un responsable.
4. Define la evidencia que demuestra cada control y dónde se genera.
5. No afirmes que el sistema «cumple»: indica qué controles cubre la arquitectura y qué queda para procesos u organización.

## Matriz de trazabilidad
| Norma y obligación | Control | Capa | Responsable | Evidencia | Estado |
|---|---|---|---|---|---|
