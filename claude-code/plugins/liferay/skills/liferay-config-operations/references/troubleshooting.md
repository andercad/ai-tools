# Diagnóstico

Método: **reproducir → aislar → medir → corregir una cosa cada vez → verificar**. Antes de cambiar nada, recoge evidencias (logs, versiones, configuración).

## Logs

- Log principal en `logs/` de Liferay Home (en contenedores, salida estándar del contenedor).
- **Niveles de log** en caliente desde Control Panel → Server Administration → Log Levels, por paquete o clase; vuelve al nivel original al terminar. De forma persistente, con un fichero de configuración de log propio según la guía de tu versión.
- Busca la **primera** excepción y su causa (`Caused by`), no la última.
- Nunca dejes `DEBUG` activado en producción: genera mucho volumen y puede registrar datos sensibles.

## Módulos y componentes

```
lb acme                    # estado de los bundles (Installed, Resolved, Active)
diag <bundleId>            # por qué un bundle no se resuelve
scr:info <componente>      # referencias no satisfechas de un componente
```

| Síntoma | Causa habitual |
|---|---|
| Bundle en `Installed` | Dependencias no resueltas: paquete no exportado o versión incompatible (`diag`) |
| Bundle `Active`, servicio no disponible | `@Reference` obligatoria no satisfecha (`scr:info`) o configuración que falta |
| Errores de clases con Jackson u otra librería | Dos copias de la librería (una incluida en el módulo y otra en Liferay); usa la de la instalación |
| Funciona en local y no en otro entorno | Distinta versión, configuración (`.config`, propiedades, variables) o módulo no desplegado en todos los nodos |
| Tras un upgrade | Override del núcleo o API eliminada (ver `liferay-workspace`) |

## Client extensions

- Revisa el log al desplegar el LUFFA: errores de YAML, tipo desconocido en la versión o agrupación no permitida.
- Microservicios: comprueba la URL configurada en la aplicación OAuth2, la validación del JWT, los scopes y los logs del propio microservicio.
- Custom elements: consola y red del navegador (recursos que no cargan, CORS, CSP, errores de JavaScript).

## Rendimiento

- **Thread dumps** (varios, separados unos segundos) cuando el servidor está lento o colgado: `jstack <pid>` o la herramienta del entorno; busca hilos bloqueados y esperas comunes.
- **Memoria**: uso del heap y GC; un heap dump si sospechas fugas (puede contener datos sensibles: trátalo como tal).
- **Base de datos**: pool de conexiones agotado, consultas lentas (log del motor), índices.
- **Cachés**: tasas de acierto; en clúster, Cluster Link funcionando.
- **Frontend**: tamaño y número de recursos, Adaptive Media, CDN, JavaScript global pesado.
- Mide antes y después de cada cambio.

## Documentos y previsualizaciones

- Las previsualizaciones y conversiones dependen de herramientas externas configuradas en Server Administration o System Settings: LibreOffice/OpenOffice para ofimática, Ghostscript o PDFBox para PDF (según versión y configuración), ImageMagick para imágenes.
- Problemas típicos:
  - Herramienta no instalada en la imagen o en el servidor, o ruta mal configurada.
  - **Concurrencia**: muchas subidas simultáneas saturan el proceso de conversión (por ejemplo, LibreOffice), con timeouts y colas.
  - Tiempos de espera demasiado cortos para documentos grandes.
  - Diferencias entre local y nube por fuentes, versiones de la herramienta o recursos del contenedor.
- Activa el log de las clases de conversión de tu versión para ver tiempos y errores de cada documento, y prueba con el mismo documento en ambos entornos.

## Búsqueda

- Resultados desactualizados o vacíos: conexión con el motor y logs del conector antes de reindexar (ver `liferay-search`).

## Clúster

- Sesiones que se pierden: sesiones persistentes en el balanceador.
- Datos distintos según el nodo: Cluster Link, cachés, despliegues no realizados en todos los nodos.

## Preparar un caso de soporte

- Versión exacta (`liferay.workspace.product` o la que muestra el portal), modelo de despliegue, base de datos, búsqueda y JDK.
- Pasos para reproducir, logs completos con marca de tiempo, thread dumps si hay bloqueos.
- Personalizaciones implicadas (módulos, overrides, client extensions).
