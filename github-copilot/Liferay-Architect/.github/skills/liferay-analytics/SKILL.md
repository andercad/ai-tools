---
name: liferay-analytics
description: 'Liferay DXP. Liferay Analytics Cloud: conectar DXP con el token de Analytics Cloud, propiedades y sites o canales de Commerce asignados, sincronización de usuarios y cuentas, entornos separados, red y lista de orígenes permitidos, eventos personalizados, paneles de sites, páginas y activos, segmentos y A/B testing, diagnóstico de la conexión y privacidad. Usar cuando: conectar Liferay con Analytics Cloud, medir el uso de un site, crear segmentos por comportamiento, registrar eventos propios, comprobar que llegan los datos, preparar un A/B test.'
argument-hint: 'Describe qué quieres medir o qué problema hay con la conexión.'
---

# Liferay Analytics Cloud

## Conexión

1. En Analytics Cloud: **Settings → Data Sources → Add Data Source → Liferay DXP** y copia el token.
2. En DXP: **Instance Settings → Analytics Cloud**, pega el token y conecta (versiones 2024.Q1+ con asistente de cuatro pasos).
3. Asigna los **sites** (y, si se usa Commerce, los **canales**) a una **propiedad**. Una propiedad agrupa los datos; un site o canal solo puede estar en una propiedad.
4. Elige qué **usuarios y cuentas** se sincronizan (todos, por grupo de usuarios u organización).

- **Un token por entorno**: si producción y preproducción comparten base de datos (por ejemplo, tras copiar la base de datos), desconecta o cambia el token en el entorno no productivo **antes de arrancarlo**; si no, ambos envían datos a la misma propiedad y las estadísticas dejan de ser fiables.
- Para sincronizar muchos usuarios, aumenta el tamaño de lote del batch engine en Instance Settings.

## Red

- Los eventos se envían **desde el navegador** de cada visitante; los datos de usuarios, **desde el servidor**.
- Permite la salida hacia los dominios de Analytics Cloud que indica la guía de diagnóstico (incluidos los de tu región) tanto en el servidor como, en intranets, en la red de los usuarios.
- La CSP del site debe permitir esos orígenes.

## Qué se puede analizar

- Paneles de **sites, páginas y activos** (contenidos, documentos, blogs...), recorridos, términos de búsqueda e intereses.
- **Individuos y cuentas** (perfiles unificados), incluidos visitantes anónimos.
- **Segmentos** por comportamiento, que se sincronizan con DXP para personalizar (ver `liferay-personalization`).
- **A/B tests** creados en DXP y analizados en Analytics Cloud.
- **Eventos personalizados** (clics, envíos de formulario, reproducciones...) con la API de eventos de Analytics Cloud en el navegador. Define un catálogo de eventos con nombres y propiedades estables antes de instrumentar, y comprueba la API en la documentación de tu versión.

## Diagnóstico

- **Eventos**: en el navegador, pestaña de red, busca las peticiones a `osbasahpublisher` y comprueba el `channelId` del payload.
- **Usuarios**: en los logs del servidor, mensajes de envío de *analytics messages*.
- Los datos tardan en procesarse: los visitantes aparecen en el panel de 24 horas tras unos minutos; otros informes, más tarde.
- Si no llegan datos: token y propiedad, sites asignados, salida de red, CSP y bloqueadores del navegador.

## Privacidad

- Analytics Cloud ofrece herramientas para gestionar datos de individuos, pero **no garantiza por sí solo** el cumplimiento normativo (por ejemplo, RGPD). Configura el consentimiento de cookies y documenta la base legal.
- No envíes datos personales en las propiedades de los eventos personalizados.

## Checklist

- [ ] Token y propiedad configurados; sites y canales asignados
- [ ] Un token por entorno; no productivos desconectados tras copiar bases de datos
- [ ] Salida de red y CSP permiten los dominios de Analytics Cloud
- [ ] Catálogo de eventos personalizados con nombres estables y sin datos personales
- [ ] Datos verificados en el navegador y en los logs
- [ ] Consentimiento y base legal documentados
