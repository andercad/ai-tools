---
name: liferay-quality
description: 'Liferay DXP. Calidad de código: Source Formatter de Liferay (formatSource, checkSourceFormatting), convenciones de código de Liferay (orden de miembros, nombres, prefijo de campos), Lombok y Source Formatter, baseline de bnd y versionado semántico de paquetes exportados, SonarQube, revisión de dependencias de terceros, calidad de client extensions y checklist antes de un PR. Usar cuando: formatear código Java, JSP o FreeMarker, corregir avisos de Source Formatter o SonarQube, revisar un PR de Liferay, cambiar la API exportada de un módulo.'
argument-hint: 'Describe el problema de calidad o el código a revisar.'
---

# Calidad de código

## Source Formatter

```powershell
./gradlew formatSource                 # aplica las convenciones de Liferay
./gradlew checkSourceFormatting        # solo comprueba (para CI)
```

- Aplica las convenciones de Liferay a Java, JSP, FreeMarker, XML, propiedades y más. Ejecútalo antes de cada PR.
- Comprueba los nombres de las tareas en tu workspace (`./gradlew tasks`).
- Si el proyecto tiene reglas propias, se configuran en el workspace; no desactives comprobaciones sin acuerdo del equipo.

## Convenciones de Liferay (las que más aparecen en revisiones)

- Campos privados con prefijo `_`; constantes en `UPPER_SNAKE_CASE`.
- Orden de miembros: métodos públicos, protegidos y privados, y al final los campos; las referencias `@Reference` al final.
- Variables con el nombre completo del tipo en minúscula (`journalArticle`, no `ja`).
- Tabuladores para sangrar (formato de Liferay); no mezclar con espacios.
- Sin `System.out`, `printStackTrace()` ni imports sin usar.
- Nomenclatura de módulos, paquetes y clases del agente (`PortletKeys`, `MVCRenderCommand`, `DisplayContext`, `Helper`...).

## Lombok

- Source Formatter no conoce el código que genera Lombok: revisa que no marque como errores las clases anotadas (campos "sin usar", orden de miembros) y, si lo hace, ajusta su configuración en el workspace en lugar de quitar Lombok.
- En SonarQube, la configuración de Lombok (`lombok.config` con `lombok.addLombokGeneratedAnnotation = true`) evita que el código generado cuente en la cobertura.

## Versionado de la API exportada

- Los paquetes exportados tienen versión (`packageinfo` o anotación `@Version`). El **baseline de bnd** compara con la versión publicada anterior y falla si un cambio incompatible no sube la versión mayor (o si sobra una subida).
- Exporta lo mínimo: menos API exportada significa menos roturas al cambiar.

## SonarQube y análisis estático

- Sin bugs, vulnerabilidades ni *security hotspots* nuevos sin revisar; complejidad dentro del quality gate.
- Excluye del análisis el **código generado** (Service Builder, REST Builder): no se corrige a mano.
- Revisa especialmente: SQL construido con texto, salida sin escapar en JSP/FreeMarker, secretos en el código, permisos que faltan.

## Dependencias de terceros

- Antes de añadir una librería: ¿la proporciona ya Liferay (`release.dxp.api`, `lb` en Gogo Shell)? Licencia, mantenimiento y vulnerabilidades.
- Incluir una librería dentro del bundle (`compileInclude`) aumenta su tamaño y el riesgo de conflictos de versión: solo si Liferay no la proporciona.
- En client extensions, la auditoría de dependencias del stack correspondiente (npm, Maven/Gradle).

## Client extensions

- Cada client extension sigue las herramientas de calidad de su stack (lint, formato, tests).
- YAML ordenado, con ERC y nombres con prefijo del proyecto.

## Checklist pre-PR

```powershell
./gradlew formatSource
./gradlew build
./gradlew testIntegration        # si hay tests de integración afectados
```

- [ ] Source Formatter aplicado; compilación limpia
- [ ] Baseline de bnd correcto para los paquetes exportados
- [ ] Tests unitarios y de integración afectados en verde
- [ ] Sin avisos nuevos de SonarQube; código generado excluido
- [ ] Sin `System.out`, `printStackTrace()`, SQL concatenado ni salida sin escapar
- [ ] Dependencias nuevas justificadas, sin duplicar las que proporciona Liferay
- [ ] Sin secretos en el código ni en la configuración versionada
