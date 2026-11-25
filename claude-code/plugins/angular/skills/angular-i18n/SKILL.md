---
name: angular-i18n
description: 'Internacionalización con Transloco en Angular. Usar al añadir texto visible, crear componentes con cadenas, gestionar scopes de traducción, títulos de página o sincronizar ficheros de idioma, cuando el proyecto use Transloco o se defina i18n en su CLAUDE.md. No usar si el proyecto es monolingüe ni para elegir estrategia de i18n a nivel arquitectura (agente angular-architect).'
---

# i18n con Transloco

## Reglas clave
- Todo texto visible va por i18n; sin literales en plantillas si el proyecto es multilingüe.
- Añade la clave en **todos** los idiomas definidos en el `CLAUDE.md` del proyecto (`i18n: es,en,...`).
- Claves jerárquicas por feature/scope; sin concatenar frases traducidas.
- Títulos de página y atributos accesibles (`aria-label`, `alt`) también se traducen.

## Referencia
- [i18n.md](references/i18n.md): scopes, organización de claves, uso en templates y TypeScript, títulos de página y checklist. Asume Transloco; si el proyecto usa otra librería, adapta.
