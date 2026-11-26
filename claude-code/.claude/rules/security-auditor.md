---
paths:
  - "**/migrations/**"
  - "**/*auth*/**"
  - "**/*auth*.*"
  - "**/*login*/**"
  - "**/*session*.*"
  - "**/*middleware*.*"
  - "**/*proxy*.*"
  - "**/*policy*.*"
  - "**/*policies*.*"
  - "**/*security*.*"
  - "**/*config*.*"
  - "**/.env*"
  - "**/Dockerfile*"
  - "**/package.json"
  - "**/pom.xml"
  - "**/build.gradle*"
  - "**/requirements*.txt"
---

# Regla: security-auditor

- Tras modificar archivos sensibles (esquema/migraciones de BD, permisos/policies, autenticación/autorización, middleware/proxy, cabeceras y config de seguridad, secretos/env, dependencias), al terminar el cambio/spec y antes del merge o la PR: proponer lanzar el subagente `security-auditor`. No lanzarlo sin confirmación.
- Lanzarlo con la app en ejecución (si no, los checks sobre endpoints/cabeceras quedan "no verificado").
- Solo si la rama/spec tocó alguno de estos archivos: como máximo una auditoría, al final, no a mitad de cambio ni una por archivo editado.
- Es de solo lectura: no pedirle que corrija. Hallazgo Crítico/Alto → crear spec con `/spec` y corregir con `/spec-impl`.
- Tras la auditoría, recordar al usuario los checks `manual` (consolas/paneles externos del proveedor de BD, auth o hosting).
- No usarlo para cambios sin impacto en seguridad (solo UI/estilos/rendimiento/lógica sin tocar datos, auth ni config).
