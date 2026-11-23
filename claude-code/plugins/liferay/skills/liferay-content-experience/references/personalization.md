# Personalización y segmentación

## Segmentos

- Un **segmento** agrupa usuarios por características comunes. Liferay evalúa la pertenencia **en el servidor**, antes de enviar la página.
- Criterios habituales: atributos del usuario (incluidos campos personalizados), organización, rol, grupo de usuarios, datos de sesión (idioma, dispositivo, URL...) y, con Analytics Cloud, comportamiento.
- **Analytics Cloud**: la documentación actual indica que los segmentos se crean cada vez más en Analytics Cloud y se sincronizan con DXP; solo se sincronizan los que tienen al menos un miembro (ver `liferay-content-experience`). Comprueba en tu versión qué criterios están disponibles en cada lado.
- Puedes **asignar roles a un segmento**: los miembros reciben los permisos del rol mientras pertenecen al segmento. Úsalo con cuidado y revísalo como cualquier asignación de permisos.
- Define pocos segmentos con significado de negocio; demasiados segmentos solapados hacen imposible predecir qué ve cada usuario.

## Experiencias en páginas de contenido

- Una **experiencia** es una versión alternativa de toda la página de contenido para un segmento: puede cambiar layout, fragments y contenido.
- Cada página tiene una experiencia **por defecto**; las demás tienen **prioridad**: si el usuario pertenece a varios segmentos, ve la de mayor prioridad.
- Mantén la experiencia por defecto completa: es la que ven los usuarios que no pertenecen a ningún segmento.
- **Simulación**: el botón de simulación del editor muestra la página como la vería cada segmento. Úsalo antes de publicar.

## Colecciones personalizadas

- Una colección puede tener **variaciones personalizadas** por segmento (filtran o sustituyen sus elementos). La variación *Anyone* es la de por defecto y no se puede borrar.
- Si un usuario pertenece a varios segmentos, se aplica la variación prioritaria o se combinan las entradas, según la configuración de la colección.
- Útil para destacar contenidos o productos por perfil sin duplicar páginas.

## A/B testing

- Compara la página actual con una **variante** sobre un objetivo (por ejemplo, tasa de rebote o clics en un elemento).
- **Requiere Analytics Cloud** conectado. El test se crea en DXP, se sincroniza con Analytics Cloud y allí se analizan los resultados.
- **No está soportado con staging activado.**
- Define el objetivo y la duración antes de empezar; publica la variante ganadora solo con resultados significativos.

## Funciones en beta

- Las **audiencias** y **variaciones de elementos** (evaluadas en el navegador) son una funcionalidad beta tras una *feature flag*. No las uses salvo petición explícita (restricción del agente).

## Privacidad

- La personalización por comportamiento y Analytics Cloud tratan datos de usuarios: respeta el consentimiento de cookies y la normativa aplicable. Las herramientas de Liferay ayudan, pero no garantizan el cumplimiento por sí solas.
- No uses datos sensibles como criterio de segmento sin base legal.
