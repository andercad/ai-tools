
# Estructura y módulos

## Paquetes por funcionalidad

Organiza por **funcionalidad de negocio**, no por capa técnica global:

```
// ✅ Por funcionalidad
com.example.app.user        (UserController, UserService, UserRepository, UserEntity, dto/)
com.example.app.order       (OrderController, OrderService, ...)
com.example.app.common      (config, error, security, web)

// ❌ Por capa técnica global
com.example.app.controller  (todos los controladores)
com.example.app.service     (todos los servicios)
com.example.app.repository  (todos los repositorios)
```

- Una funcionalidad se entiende, se cambia y se borra en un solo paquete.
- `common` solo contiene lo realmente transversal (configuración global, manejo de errores, seguridad, utilidades web). No es un cajón de sastre para lógica de negocio compartida.
- Si las convenciones del proyecto definen otra organización (capas dentro de cada funcionalidad, hexagonal...), respétala.

## Visibilidad

- Por defecto, las clases internas de una funcionalidad son **package-private** (sin modificador): entidad, repositorio, mapper, implementaciones.
- Solo es `public` lo que otras funcionalidades usan: típicamente el servicio de la funcionalidad (o una interfaz/fachada) y sus DTOs.
- Spring puede inyectar beans package-private sin problema; JPA también admite entidades package-private.

```java
// order/OrderService.java — API pública de la funcionalidad
@Service
public class OrderService { ... }

// order/OrderRepository.java — interno
interface OrderRepository extends JpaRepository<OrderEntity, UUID> { }
```

- Otra funcionalidad nunca usa el repositorio ni la entidad de una funcionalidad ajena: llama a su servicio.

## Límites verificables (opcional: Spring Modulith)

Si el proyecto usa Spring Modulith (o las convenciones del proyecto lo piden), cada subpaquete directo del paquete raíz es un módulo y sus límites se verifican en un test:

```java
class ModularityTest {

    private final ApplicationModules modules = ApplicationModules.of(Application.class);

    @Test
    void verifiesModularStructure() {
        modules.verify(); // falla si hay ciclos o accesos a paquetes internos de otro módulo
    }
}
```

- Comunicación entre módulos preferentemente por eventos de aplicación (ver `spring-integration`).
- Sin Spring Modulith, se puede verificar con ArchUnit si el proyecto lo usa.

## Clases de configuración y beans

- Las clases propias (`@Service`, `@Repository`, `@Component`, `@Controller`) se registran por escaneo de componentes.
- Las clases de librerías o los beans con construcción no trivial se declaran en una clase `@Configuration` con métodos `@Bean`:

```java
@Configuration(proxyBeanMethods = false)
class ClockConfig {

    @Bean
    Clock clock() {
        return Clock.systemUTC();
    }
}
```

- `proxyBeanMethods = false` cuando los métodos `@Bean` no se llaman entre sí: evita el proxy CGLIB y arranca más rápido. Si un `@Bean` necesita otro, recíbelo como parámetro del método en lugar de llamar al otro método.
- Una clase de configuración por área (`SecurityConfig`, `JacksonConfig`, `HttpClientConfig`), en el paquete de la funcionalidad o en `common/config`.
- Activa beans condicionalmente con `@ConditionalOnProperty` o `@Profile` solo cuando haya una necesidad real (ver `spring-config-observability`).
- No uses `@ComponentScan` adicionales ni `scanBasePackages` salvo que haya código fuera del paquete raíz.

## Dependencias circulares

- Spring Boot **prohíbe por defecto** las referencias circulares entre beans (`spring.main.allow-circular-references=false`). No lo actives para "arreglar" un ciclo.
- Un ciclo indica un problema de diseño. Resuélvelo:
  - Extrayendo la lógica compartida a un tercer bean del que dependan ambos.
  - Comunicando mediante eventos de aplicación en lugar de llamadas directas (ver `spring-integration`).
  - Revisando si uno de los servicios tiene más de una responsabilidad (ver `spring-solid`).
- `@Lazy` en un parámetro del constructor rompe el ciclo técnicamente, pero oculta el problema: úsalo solo como medida temporal documentada.

## Arranque

- Lógica de arranque (cargar datos, comprobar dependencias) en un `ApplicationRunner` o escuchando `ApplicationReadyEvent`, no en constructores ni en `@PostConstruct` con I/O pesado.
- Si una dependencia externa no está disponible al arrancar, falla rápido con un mensaje claro, o arranca degradado y repórtalo por health check (ver `spring-config-observability`), según las convenciones del proyecto.

## Checklist

- [ ] Paquete por funcionalidad, con `common` solo para lo transversal
- [ ] Clases internas package-private; API pública mínima
- [ ] Ninguna funcionalidad accede al repositorio o entidad de otra
- [ ] Beans de librerías en `@Configuration(proxyBeanMethods = false)`
- [ ] Sin dependencias circulares ni `allow-circular-references`
- [ ] Límites verificados (Spring Modulith o ArchUnit) si el proyecto lo usa
