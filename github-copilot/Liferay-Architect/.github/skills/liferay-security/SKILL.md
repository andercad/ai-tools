---
name: liferay-security
description: 'Liferay DXP. Seguridad: roles (regular, site, organización, cuenta), permisos de recurso y de modelo, PermissionChecker, ModelResourcePermission y PortletResourcePermission, servicios locales frente a remotos, OAuth2 y scopes, SSO (SAML, OpenID Connect), autenticación multifactor, CSRF con p_auth, XSS en JSP y FreeMarker, Service Access Policies, exposición de JSON web services, Gogo Shell y scripts, seguridad de client extensions y configuración del endurecimiento. Usar cuando: comprobar permisos en un servicio o portlet, definir roles, proteger una API, configurar SSO o MFA, revisar vulnerabilidades, preparar una auditoría de seguridad.'
argument-hint: 'Describe el recurso a proteger o el escenario de seguridad a revisar.'
---

# Seguridad

## Modelo de permisos

- **Roles**: regulares (toda la instancia), de site, de organización y de cuenta (B2B). Asigna permisos a roles, no a usuarios.
- **Permisos de recurso**: sobre un tipo de recurso o una instancia concreta (un documento, un registro de Object).
- **Principio de mínimo privilegio**: empieza sin permisos y añade los necesarios; revisa los permisos de *Guest* y *User* en todo lo que crees.
- Objects con permisos por rol y, para datos de cuentas, *account restriction* (ver `liferay-objects`).

## Comprobar permisos en código (módulos)

Aplica a módulos OSGi, que **no existen en SaaS**. En SaaS, la autorización se configura con roles y permisos (incluidos los de Objects) y los microservicios la aplican con los scopes OAuth2 y el usuario del JWT.

```java
@Component(service = AcmeOrderService.class)
public class AcmeOrderServiceImpl implements AcmeOrderService {

	@Override
	public AcmeOrder getOrder(long orderId) throws PortalException {
		_acmeOrderModelResourcePermission.check(
			PermissionThreadLocal.getPermissionChecker(), orderId, ActionKeys.VIEW);

		return _acmeOrderLocalService.getAcmeOrder(orderId);
	}

	@Reference(target = "(model.class.name=com.acme.orders.model.AcmeOrder)")
	private ModelResourcePermission<AcmeOrder> _acmeOrderModelResourcePermission;

	@Reference
	private AcmeOrderLocalService _acmeOrderLocalService;

}
```

- Los `*LocalService` **no** comprueban permisos; los `*Service` (remotos) sí. Desde portlets, APIs y cualquier código que actúe por un usuario, usa el remoto o comprueba antes con `ModelResourcePermission`/`PortletResourcePermission`.
- El usuario sale del contexto (`PermissionChecker`, `ServiceContext`), **nunca** de un parámetro de la petición.
- Acciones personalizadas declaradas en `resource-actions/default.xml` del módulo.
- En listados, filtra por permisos en la consulta (o usa la búsqueda, que filtra por permisos), no después de cargar todo.

## OAuth2

- Una aplicación por integración, con **scopes mínimos** y tipo de cliente adecuado (confidencial para servidores, público con PKCE para navegadores y móviles).
- Como código: client extensions `oAuthApplicationHeadlessServer` y `oAuthApplicationUserAgent` (ver `liferay-client-extensions`).
- Revoca y rota las credenciales periódicamente y cuando cambie el personal o el sistema integrado.

## SSO y autenticación

- **SAML** u **OpenID Connect** contra el proveedor de identidad de la organización; configura el mapeo de atributos y roles, y decide qué pasa con los usuarios locales.
- **Autenticación multifactor** para administradores como mínimo.
- Políticas de contraseña, bloqueo tras intentos fallidos y caducidad de sesión según la política corporativa.
- No desactives la verificación de certificados en las conexiones con el proveedor de identidad.

## CSRF y XSS

- Las acciones de portlet y las llamadas desde el navegador usan el token **`p_auth`** (`Liferay.authToken`, cabecera `x-csrf-token` en llamadas headless con sesión). No desactives su comprobación ni añadas acciones a listas de excepción sin justificación.
- **JSP**: escapa la salida con `HtmlUtil.escape`, `HtmlUtil.escapeAttribute`, `HtmlUtil.escapeJS` y `HtmlUtil.escapeHREF` según el contexto; las etiquetas `liferay-ui`, `aui` y Clay ya escapan sus atributos.
- **FreeMarker** (plantillas, ADT, fragments): `htmlUtil.escape(...)`; servicios solo mediante Template Context Contributor y sin variables restringidas (`serviceLocator`, `staticUtil`...) salvo excepción documentada (ver `liferay-content`).
- **Texto enriquecido**: lo sanea el editor y los sanitizadores de Liferay; no muestres sin escapar HTML que procede de usuarios sin permiso de edición.

## Superficie expuesta

- **Service Access Policies**: controlan qué servicios remotos puede llamar cada tipo de autenticación. No abras la política por defecto para usuarios anónimos.
- **JSON web services** (`/api/jsonws`): exposición heredada de los servicios remotos. Desactívalos o restríngelos si no se usan; para APIs nuevas, headless.
- **Gogo Shell, consola de scripts y scripts Groovy** (incluidos los de workflow, validaciones y acciones de Objects): solo para administradores, y valora desactivarlos en producción. Un script ejecuta código arbitrario en el servidor.
- **Cabeceras de seguridad** (HSTS, CSP, X-Frame-Options...) en el proxy o servidor web, compatibles con los orígenes de las client extensions y del CDN.
- Ficheros subidos: extensiones permitidas, tamaño máximo y antivirus si los usuarios externos pueden subir documentos.

## Client extensions

- Los microservicios validan el **JWT** de cada petición y aplican sus propios controles; no confíes en que la petición viene de Liferay sin verificarlo.
- Custom elements: el frontend no protege nada; la autorización la hacen las APIs.
- CORS de los microservicios restringido a los orígenes del portal.

## Datos personales

- Liferay incluye herramientas para exportar y anonimizar datos de usuarios (gestión de datos personales). Úsalas para atender derechos de los interesados.
- No registres datos personales ni tokens en logs.

## Checklist

- [ ] Permisos por rol con mínimo privilegio; revisados los de Guest y User
- [ ] Servicios remotos o comprobación con `ModelResourcePermission` antes de usar `*LocalService`
- [ ] Usuario tomado del contexto, nunca de la petición
- [ ] OAuth2 con scopes mínimos, una aplicación por integración, credenciales en secretos
- [ ] SSO y MFA según la política; sin certificados sin verificar
- [ ] `p_auth` activo; salida escapada en JSP y FreeMarker; sin variables restringidas
- [ ] JSON web services, Gogo Shell y scripts restringidos en producción
- [ ] JWT validado en microservicios
