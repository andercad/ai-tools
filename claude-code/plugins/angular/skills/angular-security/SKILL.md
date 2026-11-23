---
name: angular-security
description: Seguridad Angular a nivel de código. Usar al implementar login/logout o sesión, decidir dónde guardar tokens, manejar PII o datos sensibles, renderizar HTML dinámico (sanitización, XSS, bypassSecurityTrust), validar entradas, CSRF o auditar dependencias antes de instalarlas. No usar para elegir BFF/OAuth a nivel arquitectura (agente angular-architect).
---

# Seguridad del frontend

## Reglas clave
- La validación y autorización reales viven en el backend; guards y ocultar UI son UX.
- Sin tokens ni datos sensibles en `localStorage`/`sessionStorage`; prefiere cookies HttpOnly vía BFF o memoria.
- Nunca `bypassSecurityTrust*` ni `innerHTML` con contenido no confiable sin sanitizar.
- Identificadores en URL no sustituyen la autorización por recurso.
- Audita dependencias (`npm audit`, metadatos y licencia) antes y después de instalar.
- Respeta las restricciones del dominio descritas en el `CLAUDE.md` del proyecto (PII, retención).

## Referencias
- [security.md](references/security.md): sanitización, tokens, validación de inputs, autorización, auditoría de dependencias, CSRF.
