# Identidad y permisos: <portal>

## 1. Autenticación
| Población de usuarios | IdP | Protocolo (OIDC, SAML, LDAP) | Mapeo de identidad (claim o atributo → usuario) | Verificado en la documentación del IdP |
|---|---|---|---|---|

## 2. Aprovisionamiento y baja
| Fuente de verdad | Momento (JIT, importación, protocolo de aprovisionamiento) | Grupos o roles sincronizados | Baja: plazo y verificación |
|---|---|---|---|

## 3. Estructura
Compañía, sites, organizaciones, grupos de usuarios, cuentas y equipos utilizados, con su propósito.

## 4. Matriz de roles y permisos
| Rol | Tipo (regular, site, organización, cuenta) | Asignado a (grupo, organización) | Recurso | Acciones | Justificación |
|---|---|---|---|---|---|

Mínimo privilegio; nada asignado a usuarios individuales salvo excepción documentada.

## 5. Administradores
| Persona o grupo | Alcance | Justificación | Revisión periódica |
|---|---|---|---|

## 6. Aplicaciones OAuth2
| Integración | Perfil (User Agent, Headless Server) | Scopes | Dueño | Rotación de secretos |
|---|---|---|---|---|

## 7. Protección de APIs
- Service Access Policies aplicadas: <...>
- CORS: orígenes permitidos <...>
- CSRF en llamadas con sesión: <...>

## 8. Sesión
Expiración, cookies, comportamiento en cluster y cierre de sesión coordinado con el IdP.

## 9. Auditoría y datos personales
| Evento auditado | Dónde se registra | Retención | Quién lo revisa |
|---|---|---|---|

Exportación y borrado de datos personales: <procedimiento>.

## 10. Riesgos
| Riesgo (STRIDE) | Mitigación | Riesgo residual | Responsable |
|---|---|---|---|
