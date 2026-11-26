---
name: security-checklist
description: Checklist de seguridad genérica con IDs estables (SEC-xx, DB-xx…), independiente de proyecto. Línea base que usa el agente security-auditor cuando el proyecto no tiene su propia references/security/security-checklist.md.
user-invocable: false
---

# Security checklist (genérico)

Línea base para el agente `security-auditor`. Independiente de proyecto. Copiar a `references/security/security-checklist.md` del proyecto y ajustar; lo que el proyecto declare ahí (o en sus specs) prevalece sobre esta lista.

Cada check tiene ID estable para usarlo en la memoria de auditoría. Aplica solo lo que corresponda al stack; el resto → `n/a`.

Estado: `✅` correcto · `❌` hallazgo · `🟡` aceptado/parcial · `manual` confirmar en panel · `n/a` no aplica.
Severidad orientativa si falla: **C**rítico · **A**lto · **M**edio · **B**ajo.

## 1. Secretos (SEC)

| ID | Check | Sev |
| -- | ----- | --- |
| SEC-01 | `.env*` fuera de git (`git ls-files`) y cubiertos por `.gitignore`; solo `.env.example` sin valores reales | C |
| SEC-02 | Sin secretos hardcodeados en el árbol (`AKIA`, `sk_live`, `-----BEGIN`, `password=`, tokens, URLs con credenciales) | C |
| SEC-03 | Sin secretos en historial reciente de git (`git log -p` acotado) | A |
| SEC-04 | Ningún secreto con prefijo público (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`, `PUBLIC_`…) | C |
| SEC-05 | Claves privadas/service-role/admin ausentes de código cliente y de bundles construidos | C |
| SEC-06 | Módulos con secretos marcados solo-servidor (`server-only` u homólogo) | M |
| SEC-07 | Secretos de CI en el gestor de secretos, no en el workflow ni en logs | A |
| SEC-08 | Sin secretos en Dockerfile/imágenes (`ENV`, `ARG`, capas) | A |

## 2. Autenticación y sesión (AUTH)

| ID | Check | Sev |
| -- | ----- | --- |
| AUTH-01 | Rutas/endpoints protegidos cubiertos por middleware/guard central, sin sesión → redirige/401 | A |
| AUTH-02 | Cookies de sesión `HttpOnly`, `Secure`, `SameSite` | M |
| AUTH-03 | Contraseñas hasheadas con algoritmo adecuado (argon2/bcrypt/scrypt) si la app gestiona credenciales | C |
| AUTH-04 | Política de contraseñas coherente entre registro, reset y proveedor | M |
| AUTH-05 | Cambio de contraseña exige la actual y cierra las demás sesiones | M |
| AUTH-06 | Borrado de cuenta usa el id de la sesión (nunca del payload) y pide confirmación | A |
| AUTH-07 | Login/registro/reset sin enumeración de usuarios (salvo riesgo aceptado) | B |
| AUTH-08 | Rate limit o bloqueo en login/reset/registro | M |
| AUTH-09 | Tokens (JWT/reset/magic link) con caducidad corta, un solo uso y firma verificada | A |
| AUTH-10 | OAuth: `state`/PKCE, redirect URLs en allow-list | A |
| AUTH-11 | MFA disponible para cuentas privilegiadas | B |

## 3. Autorización (AUTHZ)

| ID | Check | Sev |
| -- | ----- | --- |
| AUTHZ-01 | Comprobación de propiedad en cada endpoint/acción que accede a datos (sin IDOR) | C |
| AUTHZ-02 | Id de usuario y rol derivados de la sesión, no del cliente | C |
| AUTHZ-03 | Rutas/acciones de administración con comprobación de rol en servidor | A |
| AUTHZ-04 | Clientes admin/privilegiados usados solo donde la spec lo permite, nunca para consultas de datos de usuario | A |
| AUTHZ-05 | Sin mass assignment (campos permitidos explícitos al crear/actualizar) | M |

## 4. Entrada, salida y red (IO)

| ID | Check | Sev |
| -- | ----- | --- |
| IO-01 | Validación de entrada en servidor (esquema/tipos/longitudes) en cada handler/acción | M |
| IO-02 | Sin inyección SQL/NoSQL/comandos/plantillas por concatenación; consultas parametrizadas | C |
| IO-03 | Sin XSS: nada de `dangerouslySetInnerHTML`/`innerHTML`/`v-html`/`|safe` con datos de usuario | A |
| IO-04 | Sin open redirect: callbacks y `redirect` solo a rutas internas | M |
| IO-05 | Sin SSRF: `fetch`/HTTP con URL de usuario validada o en allow-list | A |
| IO-06 | URLs de callback/emails derivadas de config (`SITE_URL`), no de `Origin`/`Host` | M |
| IO-07 | IP de cliente no tomada de la primera entrada de `x-forwarded-for` sin proxy de confianza | B |
| IO-08 | CORS sin `*` con credenciales; orígenes en allow-list | M |
| IO-09 | Subida de ficheros: tipo, tamaño y nombre validados; no ejecutables ni servidos desde el mismo origen | A |
| IO-10 | CSRF: tokens o `SameSite` + comprobación de origen en acciones que cambian estado | M |
| IO-11 | Sin deserialización insegura ni `eval`/`exec` con datos externos | C |

## 5. Cabeceras y transporte (HDR)

| ID | Check | Sev |
| -- | ----- | --- |
| HDR-01 | `X-Content-Type-Options: nosniff` | B |
| HDR-02 | `X-Frame-Options: DENY` o `frame-ancestors` | B |
| HDR-03 | `Referrer-Policy: strict-origin-when-cross-origin` (o más estricta) | B |
| HDR-04 | HTTPS forzado en producción (redirección/HSTS si el proyecto lo contempla) | M |
| HDR-05 | Ruta protegida sin cookie → 307/401 (`curl -I`, si hay servidor) | A |

CSP, HSTS, Permissions-Policy, CAPTCHA: mejora futura salvo que el proyecto los exija.

## 6. Logging y errores (LOG)

| ID | Check | Sev |
| -- | ----- | --- |
| LOG-01 | Sin tokens, contraseñas ni emails en logs (`console.log`/logger) | M |
| LOG-02 | Errores sin stack traces ni detalles internos al cliente | B |
| LOG-03 | Eventos de seguridad (login fallido, cambios de permisos) registrados | B |

## 7. Dependencias y cadena de suministro (DEP)

| ID | Check | Sev |
| -- | ----- | --- |
| DEP-01 | Auditor del gestor (`npm audit --omit=dev`, `pip-audit`, `govulncheck`, OWASP dep-check…) sin high/critical | A |
| DEP-02 | Lockfile presente y versionado | M |
| DEP-03 | Sin dependencias abandonadas/typosquatting evidentes; versiones fijadas razonablemente | B |
| DEP-04 | Scripts `postinstall` de terceros revisados | B |

## 8. Base de datos (DB)

Aplica según proveedor detectado (Supabase, Neon, Postgres propio, MySQL, MongoDB, Firebase…).

| ID | Check | Sev |
| -- | ----- | --- |
| DB-01 | Usuario de la app con mínimo privilegio (no superuser/owner/root) | A |
| DB-02 | Conexión con TLS (`sslmode=require` o equivalente) | M |
| DB-03 | BD no expuesta a Internet sin allow-list (si verificable; si no, `manual`) | A |
| DB-04 | Datos sensibles hasheados/cifrados; sin datos sensibles en seeds/migraciones | A |
| DB-05 | Columna de dueño `not null` + FK + `on delete` coherente | M |
| DB-06 | Deriva: migraciones aplicadas = ficheros del repo | B |
| DB-07 | Postgres con API/rol de cliente: RLS activo en todas las tablas expuestas | C |
| DB-08 | Vistas con `security_invoker = true` (PG15+) | A |
| DB-09 | Sin `using (true)`/`with check (true)` en insert/update/delete salvo justificación | A |
| DB-10 | Policies de escritura ligadas al usuario; sin update/delete donde los datos son inmutables | A |
| DB-11 | `SECURITY DEFINER` con `search_path` fijado y EXECUTE restringido | A |
| DB-12 | Event triggers/hardening declarados por el proyecto, presentes y activos | M |
| DB-13 | Pruebas con rollback: anónimo no escribe; autenticado no escribe con dueño ajeno | A |
| DB-14 | Proveedor: advisors/lints de seguridad sin avisos no aceptados | M |
| DB-15 | No relacional: reglas de acceso (`firestore.rules`, roles Mongo) sin lectura/escritura pública | C |

## 9. Infra y CI (INF)

| ID | Check | Sev |
| -- | ----- | --- |
| INF-01 | Dockerfile sin root, imagen base fijada, sin herramientas innecesarias | M |
| INF-02 | Workflows sin `pull_request_target` inseguro, permisos `GITHUB_TOKEN` mínimos, acciones fijadas | A |
| INF-03 | Protección de rama principal y revisión obligatoria (`manual`) | M |
| INF-04 | Backups de BD configurados y probados (`manual`) | M |

## 10. Panel / proveedor (PAN) — siempre `manual`

| ID | Check |
| -- | ----- |
| PAN-01 | Confirmación de email activa |
| PAN-02 | Política de contraseñas (longitud mínima, requisitos) |
| PAN-03 | Rate limits de auth |
| PAN-04 | Redirect URLs / dominios permitidos |
| PAN-05 | Proveedores OAuth con credenciales propias y scopes mínimos |
| PAN-06 | IP forwarding / proxy de confianza correcto |
| PAN-07 | MFA y acceso al panel limitado (roles, 2FA de los admins) |

## Riesgos aceptados del proyecto

Lista aquí (con referencia a spec) lo que el agente no debe reportar como nuevo:

- (ninguno)
