# Checklist de preparación para producción del frontend

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Build y código
- [ ] TypeScript `strict` activo (`strict: true`, o TS ≥ 6 sin `strict: false`; en TS < 6 debe estar explícito) sin supresiones generalizadas; sin `any` en contratos.
- [ ] Presupuestos de bundle cumplidos y comprobados en CI.
- [ ] Límites entre features verificados en CI.

## Pruebas
- [ ] Recorridos críticos cubiertos por pruebas E2E estables.
- [ ] Pruebas de contrato con las APIs consumidas.
- [ ] Sin pruebas inestables silenciadas; duración de la suite aceptable.

## Accesibilidad
- [ ] Objetivo declarado (p. ej. WCAG 2.2 AA) y normativa aplicable verificada.
- [ ] Sin incidencias críticas en el análisis automático.
- [ ] Revisión manual de teclado, foco y lector de pantalla en los flujos clave.
- [ ] Componentes del design system con accesibilidad incorporada.

## Seguridad
- [ ] Sin `bypassSecurityTrust*` ni `innerHTML` con datos externos sin revisión documentada.
- [ ] CSP activa sin `unsafe-inline` ni `unsafe-eval`; Trusted Types valorado.
- [ ] Tokens fuera de `localStorage`: BFF, o PKCE con tokens en memoria.
- [ ] CSRF tratado si hay cookies de sesión; CORS con orígenes explícitos.
- [ ] Ningún secreto en el bundle ni en ficheros de entorno.
- [ ] Dependencias auditadas, lockfile, SBOM y control de scripts de terceros.
- [ ] Autorización real en el servidor para cada operación.

## Operación
- [ ] Build único con configuración runtime por entorno.
- [ ] Captura de errores en cliente, RUM y correlación con el backend.
- [ ] Cabeceras de caché correctas para `index.html` y assets.
- [ ] Rollback probado y assets de la versión anterior disponibles.

## Resultado
Hallazgos por severidad (BLOCKER, MAJOR, MINOR, OPCIONAL) con evidencia, responsable y forma de verificarlo. Riesgos aceptados con responsable y fecha de revisión.
