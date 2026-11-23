---
name: angular-modernization-governance
description: 'Asesoría arquitectónica sobre modernización y gobierno de aplicaciones Angular: planificación de upgrades entre versiones mayores con ng update, política de soporte, migración a standalone, control flow, signal inputs, zoneless y nuevo builder, cambio de test runner, migración desde AngularJS u otros frameworks (strangler, híbrido, microfrontend transitorio), deuda técnica, ADR, matrices de decisión, estándares, fitness functions y quality gates. Usar cuando se pida planificar o priorizar un upgrade o una migración, evaluar el riesgo de quedarse en una versión sin soporte, redactar un ADR, calcular una matriz de decisión o definir cómo evitar la erosión arquitectónica. No usar para ejecutar la migración ni como generador de código.'
---

# Modernización y gobierno

## Objetivo
Planificar la evolución de aplicaciones Angular con cambios incrementales, medibles y reversibles, y establecer mecanismos de gobierno que eviten la erosión arquitectónica.

## Política de soporte
Angular publica versiones mayores de forma periódica con un periodo de soporte activo seguido de LTS. Consulta la tabla vigente de versiones y soporte en angular.dev antes de afirmar fechas. Quedarse fuera de soporte es un riesgo de seguridad y bloquea dependencias: cuantifícalo en el plan.

## Estrategia de upgrade
1. Inventario: versión actual, dependencias de terceros (UI, estado, monorepo, i18n), rangos de TypeScript y Node.js compatibles.
2. Pruebas de caracterización de los recorridos críticos antes de tocar nada.
3. Una versión mayor cada vez con `ng update` y la guía oficial de actualización; ejecuta las migraciones automáticas.
4. Tras cada salto: build, pruebas, presupuestos de bundle y despliegue en un entorno de prueba.
5. No mezcles el upgrade con refactors de arquitectura en el mismo cambio.
Matriz de bloqueos: `Dependencia | Versión actual | Compatible con destino | Alternativa | Riesgo`.

## Criterios de decisión: migraciones opcionales
| Migración | Beneficio | Cuándo |
|---|---|---|
| Standalone | Menos ceremonia, lazy loading más simple | Cuando se toca una feature o con migración automática |
| Control flow en plantillas | Legibilidad y rendimiento | Migración automática disponible; bajo riesgo |
| Signal inputs, queries e `inject()` | Integración con signals | Gradual, por feature |
| Zoneless | Menos trabajo de detección de cambios, mejor INP, convivencia con otras apps | Tras auditar librerías y código dependiente de zone.js |
| Nuevo builder (esbuild) | Build más rápido | Revisa configuraciones personalizadas de webpack |
| Cambio de test runner | Soporte y velocidad | Si el runner actual está deprecado; verifica el runner por defecto de la versión |
Verifica el estado (estable, developer preview, experimental) de cada API en la versión destino. Prioriza por beneficio medible, no por novedad.

## Migración desde AngularJS u otros frameworks
AngularJS está fuera de soporte. Opciones:
| Opción | Encaja cuando | Coste |
|---|---|---|
| Strangler por rutas | Las pantallas pueden migrarse de forma independiente detrás de un enrutado común | Dos aplicaciones durante la transición |
| Híbrido en la misma página | Pantallas muy acopladas | Complejidad, rendimiento, deuda transitoria |
| Microfrontend transitorio | Equipos y releases separados | Integración y UX |
| Reescritura | Solo si la aplicación es pequeña y está bien especificada | Riesgo alto de pérdida de comportamiento |
Define criterios de salida para retirar el legado.

## Gobierno
- **ADR**: contexto, decisión, alternativas, consecuencias, estado y criterio de revisión.
- **Matrices de decisión**: ejecuta `scripts/decision_matrix.py` con un JSON de criterios (peso 1-3) y valoraciones (1-5) para obtener el total ponderado, el criterio que decide, la sensibilidad a pesos y valoraciones y un veredicto de robustez; si no puedes ejecutar scripts, muestra el cálculo paso a paso.
- **Fitness functions** en CI: límites entre features, presupuestos de bundle, sin APIs deprecadas, accesibilidad automática, `strict` activo.
- **Estándares** mínimos y documentados; actualización de dependencias automatizada con cadencia definida.
- **Deuda técnica** registrada con impacto y dueño, revisada en cada planificación.

## Antipatrones
- Saltar varias versiones mayores a la vez.
- Mezclar upgrade y refactor en el mismo cambio.
- Migrar todo a signals o zoneless de golpe sin medir.
- Reescritura big bang de una aplicación grande.
- ADR escritos después de implementar como mera documentación.

## Salida
Usa `templates/upgrade-plan.md` para planes de upgrade y `templates/adr-template.md` para ADR.
Plan por etapas con criterios de aceptación, rollback y estimación de riesgo; matriz de bloqueos; migraciones opcionales priorizadas; ADR; fitness functions y quality gates propuestos.

## Autoevaluación
¿El plan avanza una versión mayor cada vez? ¿Hay pruebas de caracterización y rollback por etapa? ¿He verificado fechas y estado de APIs en la fuente oficial? ¿He separado upgrade y refactor? ¿Las fitness functions son automatizables?
