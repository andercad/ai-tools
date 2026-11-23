# Validación — Liferay Architect v2 (con la metodología)

## Cómo repetir las pruebas

```
python3 validation/run_tests.py .
python3 validation/scenarios.py .
```

Requiere JDK 17+ (compila `validation/ParseJava.java` automáticamente) y PyYAML.

## Resultados

| Nivel | Contenido | v1 | v2 |
|---|---|---|---|
| 1. Estructura | Frontmatter, nombre igual a carpeta, descripción ≤ 1024 con "Usar cuando" y prefijo "Liferay DXP.", routing a las 22 skills, referencias cruzadas | 113/113 | 113/113 |
| 2. Coherencia | Restricciones críticas en los ejemplos y reglas del agente | 5/5 | 11/11 |
| 3. Sintaxis | Java (parser de `javac`), YAML, JSON, XML, properties y `.config` | 13 Java | 21 Java + 14 de otros formatos |
| 4. Hechos y metodología | Afirmaciones de la documentación oficial y reglas de la metodología | 21 | 35 |
| Escenarios | Peticiones realistas → skill esperada en el top 3 | 41/41 | 55/55 |
| Mutaciones | Errores introducidos a propósito | 12/12 | 13/13 |

### Comprobaciones nuevas de la metodología

- **Ejemplos:**
  - Sin `mavenLocal()` ni plugin `maven`.
  - Sin erratas `SUFIX`/`METHOS` en constantes.
  - Componentes OSGi sin sufijo `Util`/`UtilImpl`.
  - Sin `PortalUtil`/`LanguageUtil` estáticos.
  - JSP: ningún bloque `<% %>` ni declaración `<%! %>`; expresiones `<%= %>` solo en `init.jsp` y `configuration.jsp`, y solo dentro de un `<c:set>` que asigna una constante.
- **Agente:**
  - Restricción de Git.
  - Template Context Contributor.
  - Sin `mavenLocal`.
  - Nombres `Helper`.
  - Valores por nombre y no por ID.
- **Contenido de las skills:**
  - Constantes `PORTLET_PREFERENCE_SUFFIX` y `RESOURCE_METHODS`.
  - Render por defecto como `MVCRenderCommand` y configuración obligatoria comprobada.
  - `isShow`, `portletNamespace` y JSP sin scriptlets.
  - Reglas de `Language.properties` en portlets y resource bundles.
  - Plantillas de resumen y detalle, bloques Variables/Template/Macros/Functions sin Services, ADT que embebe la de resumen y campos sin `SAXReader`.
  - Microservicios disponibles en todos los modelos de despliegue.

### Mutaciones (13/13 detectadas)

De metodología:
- Constante con `SUFIX`.
- Componente `OrdersUtilImpl`.
- Scriptlet en `view.jsp`.
- `GroupLocalServiceUtil`.
- `serviceLocator` en una plantilla.
- Bloque *Services* en las plantillas.
- `mavenLocal()`.
- Regla del resource bundle invertida.
- Restricción de Git debilitada.
- "Por nombre, nunca por ID" debilitada.

Generales:
- Salida sin escapar.
- Tipo de client extension inexistente.
- Referencia sin `_`.

## Defectos encontrados al construir esta versión

| # | Defecto | Corrección |
|---|---|---|
| 1 | El ejemplo de `view.jsp` usaba `<%= ... %>` y la skill lo daba por aceptable "si las guidelines lo permiten", contradiciendo la metodología (constantes en `init.jsp`, sin scriptlets en el resto). El banco no lo detectó: lo encontré revisando a mano | Constantes como variables JSTL en `init.jsp`; `view.jsp` solo con `${...}`; comprobación nueva de scriptlets |

## Lo que no está verificado

- **Ningún ejemplo se ha compilado contra Liferay** ni contra Lombok: el parser de `javac` comprueba la sintaxis, no los tipos ni las anotaciones.
- **`@UtilityClass` en clases anidadas estáticas** (los bloques de constantes): no lo he podido confirmar; la skill indica la alternativa del constructor privado.
- **Template Context Contributor en plantillas de contenido web**: confirmado para temas, ADT y fragments; la skill manda comprobarlo para contenido web.
- **Model listeners sobre entradas de Objects**: la skill manda comprobarlo en la versión.
- **Firma de `ConfigurationProvider.getPortletInstanceConfiguration`, taglib `liferay_journal["journal-article"]` y `getArticle()` del asset renderer**: dependen de la versión; la skill manda comprobarlos.
- **Paquete exportado de Jackson** en tu instalación: se comprueba con `lb jackson`.
- **La selección de skills es una simulación** por palabras, no una prueba en GitHub Copilot.

## Autoevaluación

| Dimensión | Nota | Comentario |
|---|---|---|
| Estructura y routing | 10/10 | Sin fallos |
| Fidelidad a la metodología | 9/10 | Todas las reglas acordadas incluidas y comprobadas; un fallo (scriptlets) encontrado a mano y corregido |
| Exactitud técnica | 7/10 | Lo central está contrastado; varios detalles dependientes de la versión se mandan comprobar |
| Calidad del banco de pruebas | 8/10 | 13/13 mutaciones; no detectaba el fallo de los scriptlets hasta añadir la comprobación |

## Ajuste posterior: regla de scriptlets en JSP

La regla decía "sin scriptlets fuera de `init.jsp` y `configuration.jsp`", pero no limitaba lo que se podía hacer dentro de esos ficheros. Ahora, en la skill y en el agente: solo expresiones `<%= %>` dentro de `<c:set>` para pasar constantes a JSTL; ningún bloque ni declaración en ningún fichero. Las 5 mutaciones nuevas (bloque y declaración en `init.jsp`, expresión que no asigna constante, bloque y expresión en `view.jsp`) se detectan. Total: 126/126 y 55/55.
