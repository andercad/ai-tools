# Contrato del custom element: <nombre-del-elemento>

- **Release de Liferay y modalidad**: <release> · self-hosted | PaaS | SaaS (verificado: sí/no)
- **Versión de Angular**: <v> · zone.js | zoneless
- **Tipo de Client Extension**: Custom Element | IFrame | otro (justificación)
- **Dueño**: <equipo>

## 1. Propósito
Qué hace el elemento, en qué páginas se usa y si admite varias instancias por página.

## 2. Configuración por instancia
| Propiedad o atributo | Tipo | Obligatorio | Valor por defecto | Quién la fija (editor, entorno) | Validación |
|---|---|---|---|---|---|

## 3. Eventos emitidos y escuchados
| Evento | Dirección | Payload (versión) | Consumidores | Compatibilidad |
|---|---|---|---|---|

## 4. Contexto del portal
| Dato | Origen (API JavaScript pública del portal, atributo, configuración) | Verificado en la release |
|---|---|---|
| Idioma | | |
| Site | | |
| Usuario autenticado | | |

## 5. APIs y autenticación
| API | Tipo (Headless de Liferay, servicio externo) | Autenticación (sesión + CSRF, OAuth2 User Agent, otra) | Scopes | Quién aplica los permisos |
|---|---|---|---|---|

## 6. Convivencia en la página
- Otras aplicaciones Angular en la misma página: <cuáles y con qué versión>.
- Estrategia de dependencias: <consolidar, alinear versiones, compartir mediante import maps si la release lo soporta>.
- Routing: <hash o rutas acotadas>; deep links: <sí/no>.
- Estilos: <tema, Clay, Style Books; Shadow DOM sí/no y motivo>.
- Limpieza al destruir el elemento: <recursos que se liberan>.

## 7. Seguridad
- Orígenes que deben figurar en la CSP del portal: <...>.
- Datos sensibles mostrados o enviados: <...>.

## 8. Despliegue y rollback
- Definición en `client-extension.yaml` y build en Liferay Workspace: <proyecto>.
- Versionado y promoción entre entornos: <...>.
- Rollback: <procedimiento>.

## 9. Preguntas abiertas para el agente Liferay
- <...>
