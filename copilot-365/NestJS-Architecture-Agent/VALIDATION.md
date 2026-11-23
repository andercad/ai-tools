# Validación

## Resultado de las comprobaciones estáticas
Ejecutadas con `validation/validate.ps1 -Build`: **287 comprobaciones superadas, 0 fallos** (288 cuando hay Python disponible y se ejecuta la prueba de humo del script).

Comprueba los límites oficiales de Agent Builder ([Custom skills in declarative agents](https://learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-skills)):
- Instrucciones del agente: 7046 caracteres (límite 8000).
- 8 skills (límite 8 por agente).
- `SKILL.md` de menos de 20.000 caracteres, con `name` y `description` en el front matter.
- ZIP de 50 MB o menos, con `SKILL.md` en la raíz, como en la documentación.
- Tipos de archivo soportados, profundidad de directorios de 3 o menos y 350 archivos o menos en total.

Y la calidad del contenido:
- Descripciones con "Usar cuando" y "No usar". Cada skill aparece en el enrutamiento del agente.
- Cada recurso (plantilla o checklist) está referenciado desde su `SKILL.md` y existe; cada skill tiene al menos uno.
- Máximo de 3 preguntas aclaratorias en las instrucciones, igual que en los demás agentes.
- Recursos compartidos con otros agentes (`decision_matrix.py`, `eu-regulatory-map.md`, `backend-technology-selection.md`) idénticos byte a byte en todas las copias; prueba de humo del script si hay Python.
- El ZIP coincide con `skills/`. Sin codificación corrupta, sin contenido duplicado entre skills y con los conceptos clave de cada ámbito.
- 22 escenarios de enrutamiento: la skill esperada contiene los disparadores en su descripción.

## Recursos por skill
| Skill | Recurso |
|---|---|
| architecture-assessment | `templates/assessment-report.md` |
| modularity-domain | `reference/microservices-readiness.md` |
| api-integration | `reference/api-production-checklist.md` |
| data-messaging | `templates/event-contract.md` |
| security-identity | `reference/security-review-checklist.md`, `reference/eu-regulatory-map.md` |
| runtime-deployment | `reference/production-readiness-checklist.md` |
| observability-resilience | `templates/slo-and-dependency-policy.md` |
| modernization-governance | `templates/adr-template.md`, `reference/backend-technology-selection.md`, `scripts/decision_matrix.py` |

## Cambios recientes
- Derivaciones a los agentes Angular, Liferay y Spring Boot, y lectura del repositorio cuando hay acceso (VS Code).
- IA generativa: integración (RAG, herramientas, streaming, evaluación), OWASP Top 10 para LLM, cuotas, latencia y coste por tokens.
- Mapa de normativa UE (RGPD, ENS, NIS2, DORA, EAA, AI Act, CRA) y criterio NestJS frente a Spring Boot.
- Script `decision_matrix.py` (total ponderado, criterio que decide, sensibilidad y robustez) y paquete para VS Code (`build-vscode.ps1` en la raíz). Prompts 23 a 25.

## Limitaciones
- La validación es estática: comprueba estructura y contenido, no el comportamiento del agente.
- No se ha ejecutado en un tenant de Microsoft 365 Copilot. Las skills están en preview (programa Frontier) y la selección de skills depende de Agent Builder: usa `validation/test-prompts.md`.
- Durante la preview no se pueden combinar skills con archivos embebidos: el conocimiento debe venir de SharePoint o de sitios web.
- Las recomendaciones sobre versiones, compatibilidades, costes y límites de plataformas deben verificarse con la documentación vigente.
- Riesgo de solapamiento entre seguridad, API y datos en preguntas transversales: se mitiga con la regla de "skill principal más mención de las demás".

## Pendiente
- Subir los ZIP y comprobar que Agent Builder los acepta.
- Ejecutar los 25 prompts de prueba y ajustar las descripciones si el enrutamiento falla.
