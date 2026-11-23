# Workflow

## Diseño

- Empieza por el **editor visual** de workflow y el flujo más simple que cumpla el requisito (por ejemplo, revisión de un paso).
- **Asignaciones a roles**, no a usuarios concretos: los usuarios cambian.
- **Notificaciones** en las tareas (correo o notificación del portal) con texto traducido.
- **Temporizadores** para escalados o recordatorios cuando una tarea lleva demasiado tiempo pendiente.
- Asigna la definición a cada tipo de activo (contenido web, documentos, Objects, pedidos de Commerce...) y, si procede, por site.

## Definición

```xml
<?xml version="1.0"?>

<workflow-definition
	xmlns="urn:liferay.com:liferay-workflow_7.4.0"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="urn:liferay.com:liferay-workflow_7.4.0 http://www.liferay.com/dtd/liferay-workflow-definition_7_4_0.xsd"
>
	<name>Acme Single Approver</name>
	<version>1</version>
	<state>
		<name>created</name>
		<initial>true</initial>
		<transitions>
			<transition>
				<name>review</name>
				<target>review</target>
			</transition>
		</transitions>
	</state>
	<task>
		<name>review</name>
		<assignments>
			<roles>
				<role>
					<role-type>regular</role-type>
					<name>Acme Reviewer</name>
				</role>
			</roles>
		</assignments>
		<transitions>
			<transition>
				<name>approve</name>
				<target>approved</target>
			</transition>
			<transition>
				<name>reject</name>
				<target>created</target>
				<default>false</default>
			</transition>
		</transitions>
	</task>
	<state>
		<name>approved</name>
		<actions>
			<action>
				<name>approve</name>
				<script>
					<![CDATA[
						import com.liferay.portal.kernel.workflow.WorkflowConstants;
						import com.liferay.portal.kernel.workflow.WorkflowStatusManagerUtil;

						WorkflowStatusManagerUtil.updateStatus(
							WorkflowConstants.getLabelStatus("approved"), workflowContext);
					]]>
				</script>
				<script-language>groovy</script-language>
				<execution-type>onEntry</execution-type>
			</action>
		</actions>
	</state>
</workflow-definition>
```

- **Parte siempre de la definición que exporta tu versión** (por ejemplo, *Single Approver*): el espacio de nombres, el esquema y la acción que actualiza el estado cambian entre versiones. El ejemplo muestra la estructura, no una plantilla definitiva.
- Lógica propia en una **acción de workflow como client extension** (microservicio con OAuth2), no en scripts largos dentro de la definición.
- **Scripts** (Groovy) ejecutan código en el servidor: mantenlos mínimos (como la actualización de estado de la definición estándar), solo administradores pueden desplegarlos, y su uso puede estar restringido según el modelo de despliegue y la configuración del motor de scripts.

## Como código

- Versiona las definiciones y despliégalas con una **client extension batch** o un **site initializer** (ver `liferay-client-extensions`), no subiéndolas a mano en cada entorno.
- Al cambiar una definición en uso, las instancias de workflow en curso siguen la versión con la que empezaron: planifica la transición.
