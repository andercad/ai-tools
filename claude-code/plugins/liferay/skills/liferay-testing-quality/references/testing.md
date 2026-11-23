# Testing

## Qué tipo de test

| Qué | Tipo | Herramienta |
|---|---|---|
| Lógica Java sin dependencias del contenedor (helpers, display contexts, modelos) | Unitario | JUnit + Mockito (`src/test/java`) |
| Servicios, permisos, persistencia, componentes OSGi | Integración contra Liferay en ejecución | Arquillian (`src/testIntegration/java`, tarea `testIntegration`) |
| API headless o REST Builder | Integración HTTP | Cliente generado por REST Builder o HTTP |
| Custom element | Unitario del framework | Herramientas del framework (ver el agente de ese framework) |
| Microservicio de client extension | Unitario e integración del propio stack | JUnit/Spring Boot, Jest/Vitest... con Liferay simulado |
| Flujo completo en el navegador | Extremo a extremo | Playwright u otra herramienta del proyecto |

Usa el test de **menor alcance** que demuestre el comportamiento. Los tests van en el propio módulo o en un módulo `-test`, según las guidelines.

## Unitarios

```java
public class OrderReferenceValidatorTest {

	@Test
	public void testRejectsEmptyReference() {
		OrderReferenceValidator orderReferenceValidator = new OrderReferenceValidator();

		Assert.assertFalse(orderReferenceValidator.isValid(""));
	}

	@Test
	public void testAcceptsWellFormedReference() {
		OrderReferenceValidator orderReferenceValidator = new OrderReferenceValidator();

		Assert.assertTrue(orderReferenceValidator.isValid("ACME-2025-0001"));
	}

}
```

- Extrae la lógica a clases sin dependencias de Liferay para poder probarla sin contenedor.
- Mockito para las dependencias inyectadas de helpers y componentes; no simules medio Liferay: si hace falta, es un test de integración.

## Integración (Arquillian)

```java
@RunWith(Arquillian.class)
public class AcmeOrderServiceTest {

	@ClassRule
	@Rule
	public static final AggregateTestRule aggregateTestRule = new LiferayIntegrationTestRule();

	@Test(expected = PrincipalException.class)
	public void testGetOrderWithoutPermission() throws Exception {
		User user = UserTestUtil.addUser();

		try (ContextUserReplace contextUserReplace = new ContextUserReplace(
				user, PermissionCheckerFactoryUtil.create(user))) {

			_acmeOrderService.getOrder(_acmeOrder.getOrderId());
		}
	}

	@Inject
	private AcmeOrderService _acmeOrderService;

	private AcmeOrder _acmeOrder;

}
```

- Se ejecutan con `./gradlew testIntegration` contra un Liferay en marcha (bundle local o contenedor), con el módulo desplegado.
- Prueba los **permisos** con usuarios sin y con rol (el caso que más fallos evita).
- Las utilidades de test (`UserTestUtil`, `GroupTestUtil`, `ServiceContextTestUtil`, `ContextUserReplace`...) y las reglas dependen de la versión: cópialas de un test de `liferay-portal` de tu etiqueta.
- Cada test crea y limpia sus datos; no dependas de datos existentes en el entorno.

## APIs

- Casos mínimos por endpoint: 200 con permisos, 401 sin autenticar, 403 sin permiso, 404 de recurso inexistente o ajeno, validación de entrada.
- REST Builder genera un módulo de tests de integración y un cliente Java: úsalos.

## Client extensions

- El microservicio se prueba en su stack con las peticiones de Liferay simuladas, incluido un JWT inválido (debe rechazarse) y la misma petición repetida (idempotencia).
- Prueba de integración en un entorno con Liferay: desplegar la client extension y ejecutar el evento real (crear el registro del Object, aprobar el workflow...).

## Extremo a extremo

- Pocos tests para los flujos críticos (login, alta, compra, aprobación), contra un entorno con datos conocidos (site initializer o batch).
- Selectores estables (atributos `data-*` propios), no clases internas de Liferay que cambian entre versiones.
