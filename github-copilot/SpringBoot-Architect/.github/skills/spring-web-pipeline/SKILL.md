---
name: spring-web-pipeline
description: 'Ciclo de vida de la petición en Spring MVC: filtros de servlet (OncePerRequestFilter), cadena de Spring Security, HandlerInterceptor, argument resolvers, ResponseBodyAdvice, @ControllerAdvice y AOP (@Aspect); cuándo usar cada uno y en qué orden se ejecutan. Usar cuando: añadir correlation ID, logging de peticiones, cabeceras comunes, medir tiempos, crear un argumento de controlador personalizado o aplicar lógica transversal con aspectos.'
argument-hint: 'Describe la lógica transversal que necesitas implementar.'
---

# Filtros, interceptores y AOP

## Orden de ejecución (Spring MVC)

Petición → **Filtros de servlet** (incluida la cadena de **Spring Security**) → `DispatcherServlet` → **`HandlerInterceptor.preHandle`** → resolución y validación de argumentos → **Controlador** (con **aspectos** si los hay) → **`ResponseBodyAdvice`** → `postHandle` → `afterCompletion`. Si hay excepción → **`@ExceptionHandler`** (ver `spring-error-handling`).

| Necesidad                                               | Usa                             |
| ------------------------------------------------------- | ------------------------------- |
| Actuar sobre toda petición antes de la seguridad (correlation ID, logging de acceso) | Filtro (`OncePerRequestFilter`) |
| Autenticar o autorizar                                  | Spring Security (ver `spring-auth`) |
| Lógica que necesita saber qué controlador se ejecuta    | `HandlerInterceptor`            |
| Inyectar un argumento propio en los controladores       | `HandlerMethodArgumentResolver` |
| Modificar el cuerpo de todas las respuestas             | `ResponseBodyAdvice`            |
| Lógica transversal sobre métodos de servicio (tiempos, auditoría) | Aspecto (`@Aspect`)    |
| Convertir excepciones en respuestas                     | `@RestControllerAdvice`         |

Los filtros e interceptores solo actúan en peticiones HTTP. Los listeners de mensajes no pasan por ellos (ver `spring-messaging`).

## Filtros

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
class CorrelationIdFilter extends OncePerRequestFilter {

    private static final String HEADER = "X-Correlation-Id";
    private static final Pattern VALID = Pattern.compile("^[\\w-]{1,64}$");

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String incoming = request.getHeader(HEADER);
        // Aceptar solo valores con formato válido para evitar inyección en logs
        String correlationId = incoming != null && VALID.matcher(incoming).matches()
                ? incoming : UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        response.setHeader(HEADER, correlationId);
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.remove("correlationId"); // los hilos se reutilizan: limpiar siempre
        }
    }
}
```

- Extiende `OncePerRequestFilter` para no ejecutarse dos veces (reenvíos, errores).
- Limpia siempre el `MDC` y cualquier `ThreadLocal` en un `finally`.
- Un `@Component` que extiende `Filter` se registra automáticamente para todas las rutas. Para limitar rutas u orden, regístralo con un `FilterRegistrationBean` en lugar de `@Component`.
- **Filtros de seguridad**: si el filtro debe ir dentro de la cadena de Spring Security, añádelo con `http.addFilterBefore/After(...)` y **no** lo anotes también con `@Component` (se ejecutaría dos veces).
- Si el proyecto usa trazas (Micrometer Tracing), el `traceId` ya se propaga al MDC; un correlation ID propio puede ser redundante (ver `spring-observability`).
- No leas el cuerpo de la petición en un filtro sin envolverlo (`ContentCachingRequestWrapper`): el stream solo se puede leer una vez. Y no registres cuerpos completos (datos sensibles).

## HandlerInterceptor

```java
@Component
class ApiDeprecationInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        if (handler instanceof HandlerMethod method && method.hasMethodAnnotation(Deprecated.class)) {
            response.setHeader("Deprecation", "true");
        }
        return true; // false detiene la petición: en ese caso, escribe tú la respuesta
    }
}

@Configuration(proxyBeanMethods = false)
class WebConfig implements WebMvcConfigurer {

    private final ApiDeprecationInterceptor apiDeprecationInterceptor;

    WebConfig(ApiDeprecationInterceptor apiDeprecationInterceptor) {
        this.apiDeprecationInterceptor = apiDeprecationInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(apiDeprecationInterceptor).addPathPatterns("/api/**");
    }
}
```

- `postHandle` no se ejecuta si el controlador lanza una excepción; `afterCompletion` sí.
- No uses interceptores para autorización: es responsabilidad de Spring Security.

## Argumentos personalizados

Para inyectar en los controladores un valor derivado de la petición (p. ej. el tenant actual):

```java
class CurrentTenantArgumentResolver implements HandlerMethodArgumentResolver {

    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasParameterAnnotation(CurrentTenant.class);
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mav,
                                  NativeWebRequest request, WebDataBinderFactory binderFactory) {
        return TenantId.from(request.getHeader("X-Tenant-Id")); // validado; y comprobado contra el usuario
    }
}
// Registro: WebMvcConfigurer.addArgumentResolvers(...)
```

Para el usuario autenticado, usa `@AuthenticationPrincipal` (ver `spring-auth`), no un resolver propio.

## ResponseBodyAdvice

Permite envolver o modificar todas las respuestas. Un envoltorio global (`{ data, timestamp }`) cambia el contrato de toda la API: aplícalo solo si las guidelines lo definen, y no envuelvas las respuestas de error (`ProblemDetail`) ni las de Actuator.

## Aspectos (AOP)

- Para lógica transversal sobre beans (medir tiempos, auditoría declarativa). Requiere el starter de AspectJ (`spring-boot-starter-aspectj` en Spring Boot 4; `spring-boot-starter-aop` en 3.x).
- Los aspectos de Spring funcionan **por proxy**: no interceptan llamadas internas dentro del mismo bean ni métodos privados.
- Puntos de corte precisos (por anotación propia), no `execution(* com.example..*(..))` amplios.
- Antes de crear un aspecto, comprueba si ya existe una solución: métricas y trazas con `@Observed`/Micrometer (ver `spring-observability`), reintentos con `@Retryable` (ver `spring-http-clients`), caché con `@Cacheable`.

```java
@Aspect
@Component
class AuditAspect {

    private final AuditService auditService;

    AuditAspect(AuditService auditService) {
        this.auditService = auditService;
    }

    @AfterReturning("@annotation(audited)")
    void audit(JoinPoint joinPoint, Audited audited) {
        auditService.record(audited.action(), joinPoint.getSignature().toShortString());
    }
}
```

## Checklist

- [ ] Cada pieza en la capa correcta del ciclo de vida
- [ ] Filtros con `OncePerRequestFilter`; `MDC`/`ThreadLocal` limpiados en `finally`
- [ ] Filtros de seguridad añadidos a la cadena sin `@Component` duplicado
- [ ] Sin autorización en interceptores
- [ ] Sin lectura ni registro de cuerpos completos
- [ ] Aspectos con puntos de corte precisos, conscientes de las limitaciones del proxy
- [ ] Envoltorio global de respuesta solo si las guidelines lo definen
