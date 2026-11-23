# Checklist de preparación para producción (runtime y despliegue)

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Imagen y build
- [ ] Una imagen por versión, reproducible y promovida entre entornos sin recompilar.
- [ ] Imagen mínima (capas de Spring Boot o buildpacks), usuario no root y escaneada.
- [ ] JVM o native justificada por requisitos medidos de arranque o memoria.

## Configuración y secretos
- [ ] Configuración externa por entorno; perfiles solo para variaciones reales.
- [ ] Secretos en gestor dedicado; ninguno en imagen, repositorio ni logs.
- [ ] Servidor de configuración o descubrimiento solo si la plataforma no lo ofrece ya.

## Ciclo de vida
- [ ] Readiness y liveness separadas (grupos de health de Actuator); liveness no depende de servicios externos.
- [ ] Arranque largo cubierto (probe de arranque o retardo inicial adecuado).
- [ ] Graceful shutdown activado y ventana de terminación mayor que la petición más larga, alineada con el balanceador.

## Capacidad y disponibilidad
- [ ] Límites de CPU y memoria fijados y respetados por la JVM, con margen para memoria no-heap.
- [ ] Al menos dos réplicas repartidas por zonas y presupuesto de interrupción definido.
- [ ] Aplicación sin estado o sesión externalizada; métricas y límites de escalado definidos.
- [ ] Dimensionado validado con pruebas de carga.

## Despliegue y rollback
- [ ] Estrategia (rolling, blue/green, canary) acorde al riesgo.
- [ ] Esquema y mensajes compatibles entre versiones (expand/contract).
- [ ] Rollback probado; feature flags para separar despliegue de activación.

## Recuperación
- [ ] RPO y RTO acordados con negocio; copias y restauración probadas.
- [ ] Región secundaria solo si el requisito lo exige; conmutación documentada y ensayada.

## Coste
- [ ] Estimación relativa; cifras concretas marcadas como pendientes de verificar con la calculadora del proveedor.

## Resultado
Bloqueantes para producción, riesgos aceptados con responsable y acciones con fecha.
